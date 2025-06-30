#!/usr/bin/env python3
"""
Main entry point for TrackMate SPT Analyzer GUI
==============================================

This allows running the package as a module: python -m trackmate_spt_analyzer
"""

import sys
import tkinter as tk

from .gui.app import TrackMateSPTAnalyzer

def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = TrackMateSPTAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 