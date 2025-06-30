"""
TrackMate SPT Analyzer Package
==============================

A comprehensive GUI application for analyzing TrackMate XML files for Single Particle Tracking (SPT) analysis.

Main components:
- Core analysis functions
- GUI application
- Utility functions
"""

from .core.analysis import (
    parse_trackmate_xml,
    msd_per_track,
    rolling_window_analysis,
    _fit_msd
)

from .core.utils import (
    build_readme_text,
    timestamp,
    save_with_suffix,
    qc_report_html
)

from .gui.app import TrackMateSPTAnalyzer

__version__ = "1.0.0"
__author__ = "Saskia Sanders, Bosse Lab, Medizinische Hochschule Hannover"

__all__ = [
    # Core analysis functions
    "parse_trackmate_xml",
    "msd_per_track", 
    "rolling_window_analysis",
    "_fit_msd",
    
    # Utility functions
    "build_readme_text",
    "timestamp",
    "save_with_suffix",
    "qc_report_html",
    
    # GUI
    "TrackMateSPTAnalyzer",
] 