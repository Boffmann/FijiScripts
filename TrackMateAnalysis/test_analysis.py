#!/usr/bin/env python3
"""
Test script for TrackMate SPT Analyzer
======================================

Tests the core analysis functions with the existing XML file.
Updated to use the new modular structure.
"""

import sys
from pathlib import Path

# Import our analysis functions from the new modular structure
from trackmate_spt_analyzer.core.analysis import (
    parse_trackmate_xml, 
    msd_per_track, 
    rolling_window_analysis
)
from trackmate_spt_analyzer.core.utils import build_readme_text

def test_analysis():
    """Test the analysis functions with the existing XML file."""
    
    # Find the XML file
    xml_file = Path("20241210_PK15_PrV1024_No3_18_40-01_CGT-1_BGD.xml")
    
    if not xml_file.exists():
        print(f"Error: XML file {xml_file} not found!")
        return False
    
    print(f"Testing with file: {xml_file}")
    print("=" * 50)
    
    try:
        # Test XML parsing
        print("1. Testing XML parsing...")
        df, meta = parse_trackmate_xml(xml_file)
        print(f"   ✓ Parsed successfully")
        print(f"   - Tracks: {meta['n_tracks']}")
        print(f"   - Frames: {meta['n_frames']}")
        print(f"   - Pixel size: {meta['pixel_size']} µm/px")
        print(f"   - dt: {meta['dt']} s")
        print(f"   - DataFrame shape: {df.shape}")
        
        # Test MSD analysis
        print("\n2. Testing MSD analysis...")
        per_track = msd_per_track(df, meta["dt"])
        print(f"   ✓ MSD analysis completed")
        print(f"   - Analyzed tracks: {len(per_track)}")
        if len(per_track) > 0:
            print(f"   - Mean D: {per_track['D'].mean():.3e} µm²/s")
            print(f"   - Mean α: {per_track['alpha'].mean():.3f}")
            print(f"   - Mean Rg: {per_track['Rg'].mean():.3f} µm")
        
        # Test sliding window analysis
        print("\n3. Testing sliding window analysis...")
        window_results = rolling_window_analysis(df, window=5, step=1, 
                                               dt=meta["dt"], a_thr=(0.2, 1.2))
        print(f"   ✓ Window analysis completed")
        print(f"   - Window segments: {len(window_results)}")
        if len(window_results) > 0:
            states = window_results['state'].value_counts()
            print(f"   - Motion states: {dict(states)}")
        
        # Test README generation
        print("\n4. Testing README generation...")
        readme_text = build_readme_text()
        print(f"   ✓ README generated ({len(readme_text)} characters)")
        
        print("\n" + "=" * 50)
        print("✓ All tests passed! The analysis functions are working correctly.")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analysis()
    sys.exit(0 if success else 1) 