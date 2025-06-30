"""
Core analysis functions for TrackMate SPT analysis.

Contains XML parsing, MSD calculations, and motion state classification.
"""

import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from pathlib import Path
from typing import Tuple, Dict, Optional

def _get_calibration(root: ET.Element) -> Tuple[float, Optional[float]]:
    """Helper: read pixel size + (optional) global dt from <ImageData>"""
    img = root.find("ImageData")
    if img is None:
        return 1.0, None
    px = float(img.get("pixel-width", "1"))
    dt_global = img.get("time-interval")
    return px, (float(dt_global) if dt_global is not None else None)

def parse_trackmate_xml(xml_path: Path) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Parse TrackMate *Full XML* → (tidy DataFrame, metadata dict).

    DataFrame columns
    -----------------
    track_id | frame | t_abs | t | x | y | z | intensity
    (t_abs = acquisition time in s; t = t_abs – t_abs.min())
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # ---- calibration ----
    px_size, dt_global = _get_calibration(root)

    # ---- collect spots ----
    spots: dict[int, dict] = {}
    for sp in root.findall(".//SpotsInFrame/Spot"):
        sid = int(sp.get("ID"))
        spots[sid] = {
            "frame": int(sp.get("FRAME")),
            "t_abs": float(sp.get("POSITION_T", np.nan)),
            "x": float(sp.get("POSITION_X")) * px_size,
            "y": float(sp.get("POSITION_Y")) * px_size,
            "z": float(sp.get("POSITION_Z", 0)) * px_size,
            "intensity": float(sp.get("MEAN_INTENSITY_CH1", sp.get("MEAN_INTENSITY", np.nan))),
        }

    # ---- build per-frame rows ----
    rows: list[dict] = []
    for trk in root.findall(".//Track"):
        tid = int(trk.get("TRACK_ID"))
        for edge in trk.findall("Edge"):
            for sid in (edge.get("SPOT_SOURCE_ID"), edge.get("SPOT_TARGET_ID")):
                sdata = spots.get(int(sid))
                if sdata:
                    rows.append({**sdata, "track_id": tid})

    df = (pd.DataFrame(rows)
            .drop_duplicates(subset=["track_id", "frame"])
            .sort_values(["track_id", "frame"]))

    # ---- infer dt ----
    if df["t_abs"].notna().sum() >= 2:
        # median Δt between consecutive frames *inside each track*
        dt_series = (df.groupby("track_id")["t_abs"]
                       .apply(lambda s: s.diff().median()))
        dt_val = dt_series.median()
    elif dt_global is not None:
        dt_val = dt_global
        df["t_abs"] = df["frame"] * dt_val
    else:
        dt_val = 1.0
        df["t_abs"] = df["frame"] * dt_val  # still populate t_abs for consistency

    # relative time starting at zero
    df["t"] = df["t_abs"] - df["t_abs"].min()

    meta = dict(pixel_size=px_size,
                dt=dt_val,
                n_tracks=df.track_id.nunique(),
                n_frames=int(df.frame.max()) + 1)
    return df, meta

def _fit_msd(tau: np.ndarray, msd: np.ndarray) -> Tuple[float, float]:
    """Log-log fit MSD ≈ 4D·τ^α  → returns D, α."""
    if len(tau) < 2 or np.any(msd <= 0):
        return np.nan, np.nan
    try:
        popt, _ = curve_fit(lambda lnt, logD, alpha: logD + alpha * lnt,
                            np.log(tau), np.log(msd), maxfev=2000)
        logD, alpha = popt
        return np.exp(logD) / 4, alpha
    except Exception:
        return np.nan, np.nan

def msd_per_track(df: pd.DataFrame, dt: float, max_lag: Optional[int] = None) -> pd.DataFrame:
    """Calculate MSD and related metrics for each track."""
    records = []
    for tid, g in df.groupby("track_id"):
        g = g.sort_values("frame")
        coords = g[["x", "y"]].to_numpy()
        n = len(coords)
        if n < 3:
            continue
        max_tau = max_lag or (n - 1)
        msd = np.array([(np.square(coords[i:] - coords[:-i]).sum(1)).mean()
                        for i in range(1, max_tau + 1)])
        tau = np.arange(1, len(msd) + 1) * dt
        D, alpha = _fit_msd(tau, msd)

        v_inst = np.linalg.norm(np.diff(coords, axis=0), axis=1) / dt
        rg = np.sqrt(((coords - coords.mean(0)) ** 2).sum(1).mean())

        records.append(dict(track_id=tid, n_pts=n, D=D, alpha=alpha,
                            Rg=rg, v_mean=v_inst.mean(), v_max=v_inst.max(),
                            dur_s=n*dt))
    return pd.DataFrame.from_records(records)

def rolling_window_analysis(df: pd.DataFrame, window: int, step: int,
                            dt: float, a_thr: Tuple[float, float]) -> pd.DataFrame:
    """Perform sliding window analysis for motion state classification."""
    records = []
    alo, ahi = a_thr
    for tid, g in df.groupby("track_id"):
        g = g.sort_values("frame").reset_index(drop=True)
        coords = g[["x", "y"]].to_numpy()
        n = len(coords)
        for i0 in range(0, n - window + 1, step):
            seg = coords[i0:i0 + window]
            msd = np.array([
                np.square(seg[j:] - seg[:-j]).sum(axis=1).mean()
                for j in range(1, window)
            ])
            tau = np.arange(1, len(msd) + 1) * dt
            _, alpha = _fit_msd(tau, msd)
            if np.isnan(alpha):
                state = "undetermined"
            elif alpha <= alo:
                state = "static"
            elif alpha <= ahi:
                state = "diffusive"
            else:
                state = "active"
            records.append(dict(track_id=tid,
                                frame_start=int(g.loc[i0, "frame"]),
                                alpha=alpha, state=state))
    return pd.DataFrame.from_records(records) 