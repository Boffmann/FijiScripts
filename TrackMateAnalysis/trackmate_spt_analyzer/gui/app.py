"""
Main GUI application for TrackMate SPT Analyzer.

Contains the tkinter-based GUI application with all user interface components.
"""

import os
import sys
import threading
import queue
from pathlib import Path
from typing import List
from datetime import datetime

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter import font as tkfont

from ..core.analysis import parse_trackmate_xml, msd_per_track, rolling_window_analysis
from ..core.utils import build_readme_text, qc_report_html, save_with_suffix
import pandas as pd

class TrackMateSPTAnalyzer:
    """Main GUI application for TrackMate SPT analysis."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TrackMate SPT Analyzer")
        self.root.geometry("800x600")
        
        # Data storage
        self.xml_files = []
        self.warnings = []
        self.analysis_queue = queue.Queue()
        
        # Configure style
        self.setup_styles()
        
        # Create GUI
        self.create_widgets()
        
        # Set default path to current working directory
        self.set_default_path()
        
        # Start message processing
        self.process_messages()
    
    def setup_styles(self):
        """Configure ttk styles for better appearance."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure fonts
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=10)
        
        # Configure colors
        style.configure("Title.TLabel", font=("TkDefaultFont", 14, "bold"))
        style.configure("Header.TLabel", font=("TkDefaultFont", 12, "bold"))
        style.configure("Success.TButton", background="green")
    
    def create_widgets(self):
        """Create and arrange all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="TrackMate SPT Analyzer", 
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        self.create_file_section(main_frame)
        
        # Parameters section
        self.create_parameters_section(main_frame)
        
        # Control buttons
        self.create_control_buttons(main_frame)
        
        # Progress bar
        self.create_progress_section(main_frame)
        
        # Output area
        self.create_output_section(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def set_default_path(self):
        """Set the default path to the current working directory and scan for XML files."""
        current_dir = Path.cwd()
        self.folder_var.set(str(current_dir))
        self.scan_folder()
    
    def create_file_section(self, parent):
        """Create file selection widgets."""
        # File section header
        file_header = ttk.Label(parent, text="File Selection", style="Header.TLabel")
        file_header.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Folder selection
        ttk.Label(parent, text="Input Folder:").grid(row=2, column=0, sticky=tk.W)
        
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(parent, textvariable=self.folder_var, width=50)
        self.folder_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        
        self.browse_button = ttk.Button(parent, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=2, column=2, sticky=tk.W)
        
        # Scan button
        self.scan_button = ttk.Button(parent, text="Scan for XML Files", 
                                     command=self.scan_folder)
        self.scan_button.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
    
    def create_parameters_section(self, parent):
        """Create analysis parameters widgets."""
        # Parameters section header
        param_header = ttk.Label(parent, text="Analysis Parameters", style="Header.TLabel")
        param_header.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(20, 10))
        
        # Create parameters frame
        param_frame = ttk.LabelFrame(parent, text="Settings", padding="10")
        param_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        param_frame.columnconfigure(1, weight=1)
        param_frame.columnconfigure(3, weight=1)
        
        # Window parameters
        ttk.Label(param_frame, text="Window Length (frames):").grid(row=0, column=0, sticky=tk.W)
        self.window_var = tk.StringVar(value="5")
        self.window_entry = ttk.Entry(param_frame, textvariable=self.window_var, width=10)
        self.window_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(param_frame, text="Step Size (frames):").grid(row=0, column=2, sticky=tk.W)
        self.step_var = tk.StringVar(value="1")
        self.step_entry = ttk.Entry(param_frame, textvariable=self.step_var, width=10)
        self.step_entry.grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        # Alpha thresholds
        ttk.Label(param_frame, text="α Static ≤:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.alpha_low_var = tk.StringVar(value="0.2")
        self.alpha_low_entry = ttk.Entry(param_frame, textvariable=self.alpha_low_var, width=10)
        self.alpha_low_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 20), pady=(10, 0))
        
        ttk.Label(param_frame, text="α Active >:").grid(row=1, column=2, sticky=tk.W, pady=(10, 0))
        self.alpha_high_var = tk.StringVar(value="1.2")
        self.alpha_high_entry = ttk.Entry(param_frame, textvariable=self.alpha_high_var, width=10)
        self.alpha_high_entry.grid(row=1, column=3, sticky=tk.W, padx=(5, 0), pady=(10, 0))
        
        # Checkboxes
        self.intensity_var = tk.BooleanVar(value=True)
        self.intensity_check = ttk.Checkbutton(param_frame, text="Include Intensity Metrics", 
                                              variable=self.intensity_var)
        self.intensity_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        self.merge_windows_var = tk.BooleanVar(value=False)
        self.merge_windows_check = ttk.Checkbutton(param_frame, text="Merge Window Tables", 
                                                  variable=self.merge_windows_var)
        self.merge_windows_check.grid(row=2, column=2, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def create_control_buttons(self, parent):
        """Create control buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        self.help_button = ttk.Button(button_frame, text="Help", command=self.show_help)
        self.help_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.run_button = ttk.Button(button_frame, text="Run Analysis", 
                                   command=self.run_analysis, style="Success.TButton")
        self.run_button.pack(side=tk.LEFT)
    
    def create_progress_section(self, parent):
        """Create progress bar."""
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def create_output_section(self, parent):
        """Create output text area."""
        output_frame = ttk.LabelFrame(parent, text="Output", padding="5")
        output_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_status_bar(self, parent):
        """Create status bar."""
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E))
    
    def browse_folder(self):
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.folder_var.set(folder)
            self.scan_folder()
    
    def scan_folder(self):
        """Scan selected folder for XML files."""
        folder = self.folder_var.get()
        if not folder:
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
        
        folder_path = Path(folder)
        xml_files = sorted(folder_path.glob("*.xml"))
        self.xml_files = xml_files
        
        self.output_text.delete(1.0, tk.END)
        if not xml_files:
            self.output_text.insert(tk.END, "No *.xml files found in the selected folder.\n")
        else:
            self.output_text.insert(tk.END, f"Found {len(xml_files)} XML files:\n")
            for xml_file in xml_files[:10]:
                self.output_text.insert(tk.END, f" • {xml_file.name}\n")
            if len(xml_files) > 10:
                self.output_text.insert(tk.END, " ...\n")
        
        self.status_var.set(f"Found {len(xml_files)} XML files")
    
    def show_help(self):
        """Show help dialog with metric explanations."""
        help_text = """
Metric Glossary

• α (anomalous exponent) – slope of log MSD vs log τ
  0 → static · 1 → Brownian · >1 → directed

• D – effective diffusion coefficient from MSD fit (µm²/s)

• Rg – radius of gyration (spatial footprint, µm)

• v_mean / v_max – instantaneous velocity stats (µm/s)

• Intensity – TrackMate MEAN_INTENSITY averaged over the track

Sliding-window MSD uses the same α-classification inside each window
to label static / diffusive / active segments.
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Metric Glossary")
        help_window.geometry("500x400")
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, help_text.strip())
        text_widget.config(state=tk.DISABLED)
    
    def run_analysis(self):
        """Start the analysis in a separate thread."""
        if not self.xml_files:
            messagebox.showwarning("Warning", "No XML files found. Please scan a folder first.")
            return
        
        # Validate parameters
        try:
            window = int(self.window_var.get())
            step = int(self.step_var.get())
            alpha_low = float(self.alpha_low_var.get())
            alpha_high = float(self.alpha_high_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric parameters.")
            return
        
        # Disable controls during analysis
        self.run_button.config(state=tk.DISABLED)
        self.scan_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=self._run_analysis_thread,
                                         args=(window, step, alpha_low, alpha_high))
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def _run_analysis_thread(self, window: int, step: int, alpha_low: float, alpha_high: float):
        """Run analysis in background thread."""
        try:
            # Get parameters
            use_intensity = self.intensity_var.get()
            merge_windows = self.merge_windows_var.get()
            
            # Create timestamped run directory
            timestamp = datetime.now().strftime("%Y%m%d-%H%M")
            src_folder = Path(self.folder_var.get())
            out_root = src_folder / "analysis" / f"run_{timestamp}"
            
            # Create subdirectories
            for sub in ["all_tracks", "bins", "windows", "qc_reports", "logs"]:
                (out_root / sub).mkdir(parents=True, exist_ok=True)
            
            # Initialize data storage
            summary_rows = []
            summary_rows_windows = []
            self.warnings = []
            
            # Process each XML file
            for i, xml_file in enumerate(self.xml_files):
                # Update progress
                self.analysis_queue.put(("progress", i + 1, len(self.xml_files), f"Processing {xml_file.name}"))
                
                try:
                    df, meta = parse_trackmate_xml(xml_file)
                except Exception as e:
                    self.warnings.append(f"Failed to parse {xml_file.name}: {e}")
                    continue
                
                # Perform analysis
                per_track = msd_per_track(df, meta["dt"])
                per_track["file"] = xml_file.name
                
                per_window = rolling_window_analysis(df, window, step, meta["dt"], (alpha_low, alpha_high))
                per_window["file"] = xml_file.name
                
                # Save individual files
                per_window.to_csv(
                    save_with_suffix(out_root / "windows" / f"{xml_file.stem}__windows.csv"),
                    index=False)
                
                per_track.to_csv(
                    save_with_suffix(out_root / "all_tracks" / f"{xml_file.stem}__tracks.csv"),
                    index=False)
                
                if use_intensity and df["intensity"].notna().any():
                    inten_stats = (df.groupby("track_id")["intensity"]
                                     .agg(["mean", "max", "std"])
                                     .reset_index())
                    inten_stats.to_csv(
                        save_with_suffix(out_root / "all_tracks" / f"{xml_file.stem}__intensity.csv"),
                        index=False)
                
                # Collect for summary
                pt = per_track.assign(pixel=meta["pixel_size"], dt=meta["dt"])
                cols = ["file"] + [c for c in pt.columns if c != "file"]
                summary_rows.append(pt[cols])
                
                if merge_windows:
                    summary_rows_windows.append(per_window)
            
            # Create summary files
            if summary_rows:
                summary_all = pd.concat(summary_rows, ignore_index=True)
                summary_all.to_csv(save_with_suffix(out_root / "summary_all.csv"), index=False)
                
                if merge_windows and summary_rows_windows:
                    windows_all = pd.concat(summary_rows_windows, ignore_index=True)
                    windows_all.to_csv(save_with_suffix(out_root / "windows_all.csv"), index=False)
                
                # Generate QC report
                qc_html = qc_report_html(summary_all, meta, self.warnings)
                (save_with_suffix(out_root / "qc_reports" / "QC_report.html")).write_text(qc_html, encoding="utf8")
                
                # Save README
                readme_path = save_with_suffix(out_root / "summary_README.txt")
                readme_path.write_text(build_readme_text(), encoding="utf8")
            
            # Signal completion
            self.analysis_queue.put(("complete", out_root))
            
        except Exception as e:
            self.analysis_queue.put(("error", str(e)))
    
    def process_messages(self):
        """Process messages from the analysis thread."""
        try:
            while True:
                msg_type, *args = self.analysis_queue.get_nowait()
                
                if msg_type == "progress":
                    current, total, description = args
                    self.progress_bar["maximum"] = total
                    self.progress_bar["value"] = current
                    self.progress_var.set(description)
                    self.status_var.set(f"Processing: {current}/{total}")
                
                elif msg_type == "complete":
                    out_root = args[0]
                    self.progress_bar["value"] = self.progress_bar["maximum"]
                    self.progress_var.set("Analysis Complete")
                    self.status_var.set("Analysis finished successfully")
                    
                    # Re-enable controls
                    self.run_button.config(state=tk.NORMAL)
                    self.scan_button.config(state=tk.NORMAL)
                    self.browse_button.config(state=tk.NORMAL)
                    
                    # Show completion message
                    self.output_text.insert(tk.END, f"\nAnalysis finished. Outputs in: {out_root.resolve()}\n")
                    if self.warnings:
                        self.output_text.insert(tk.END, "\nWarnings:\n")
                        for warning in self.warnings:
                            self.output_text.insert(tk.END, f" • {warning}\n")
                    
                    messagebox.showinfo("Success", f"Analysis completed successfully!\nOutputs saved to: {out_root}")
                
                elif msg_type == "error":
                    error_msg = args[0]
                    self.progress_var.set("Error occurred")
                    self.status_var.set("Analysis failed")
                    
                    # Re-enable controls
                    self.run_button.config(state=tk.NORMAL)
                    self.scan_button.config(state=tk.NORMAL)
                    self.browse_button.config(state=tk.NORMAL)
                    
                    messagebox.showerror("Error", f"Analysis failed: {error_msg}")
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)

def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = TrackMateSPTAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 