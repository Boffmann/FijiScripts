#!/usr/bin/env python3
"""
TrackMate SPT Analyzer - GUI Application
========================================

A standalone GUI application for analyzing TrackMate XML files for Single Particle Tracking (SPT) analysis.

This application provides a user-friendly interface for:
- Loading TrackMate XML files
- Configuring analysis parameters
- Running MSD analysis and motion classification
- Viewing results and quality control reports
"""

import tkinter as tk
from trackmate_spt_analyzer.gui.app import TrackMateSPTAnalyzer

def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = TrackMateSPTAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 