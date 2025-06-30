# TrackMate SPT Analyzer

A standalone Python GUI application for analyzing TrackMate XML files to perform Single Particle Tracking (SPT) analysis.

## Overview

This application converts TrackMate XML export files into comprehensive analysis results including:
- Mean Squared Displacement (MSD) calculations
- Diffusion coefficient estimation
- Motion state classification (static, diffusive, active)
- Velocity statistics
- Intensity metrics
- Quality control reports

## Features

- **User-friendly GUI**: Intuitive interface built with tkinter
- **Modular Architecture**: Professional package structure for extensibility
- **Batch Processing**: Analyze multiple XML files simultaneously
- **Comprehensive Analysis**: MSD fitting, diffusion coefficients, motion classification
- **Quality Control**: Automated QC reports and warnings
- **Flexible Output**: Multiple CSV formats and HTML reports
- **Progress Tracking**: Real-time progress updates during analysis

## Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Application

**Launch the GUI:**
```bash
# Method 1: Direct execution
python trackmate_spt_analyzer.py

# Method 2: Module execution
python -m trackmate_spt_analyzer

```

**GUI Workflow:**
1. Click "Browse" to select a folder containing TrackMate XML files
2. Configure analysis parameters:
   - **Window Length**: Number of frames for sliding window analysis
   - **Step Size**: Frame increment between windows
   - **α Static ≤**: Threshold for static motion classification
   - **α Active >**: Threshold for active motion classification
   - **Include Intensity Metrics**: Option to include intensity statistics
   - **Merge Window Tables**: Option to combine all window data into one file
3. Click "Run Analysis" to start processing
4. View results in the generated `analysis/` folder

### Programmatic Usage (For Developers)

**Import and use core functions:**
```python
from trackmate_spt_analyzer.core.analysis import parse_trackmate_xml, msd_per_track
from trackmate_spt_analyzer.core.utils import save_with_suffix

# Parse XML file
df, meta = parse_trackmate_xml("data.xml")

# Perform analysis
results = msd_per_track(df, meta["dt"])

# Save results
results.to_csv("output.csv", index=False)
```

### Testing

**Run the test suite:**
```bash
python test_analysis.py
```

## Package Structure

The application is organized into a modular package structure:

```
trackmate_spt_analyzer/
├── core/                    # Core analysis functionality
│   ├── analysis.py          # XML parsing, MSD calculations
│   └── utils.py             # Helper functions, file operations
└── gui/                     # Graphical user interface
    └── app.py               # Main GUI application
```

**Benefits of the modular structure:**
- **Separation of Concerns**: Core logic independent of UI
- **Maintainability**: Focused, single-responsibility modules
- **Extensibility**: Easy to add new features
- **Reusability**: Core functions can be used in other projects
- **Testing**: Individual modules can be tested separately

For detailed information about the modular structure, see [MODULAR_STRUCTURE.md](MODULAR_STRUCTURE.md).

## Output Files

The analysis creates the following output structure:

```
analysis/
├── all_tracks/           # Individual track CSV files
│   ├── file1__tracks.csv
│   ├── file1__intensity.csv
│   └── ...
├── windows/              # Sliding window analysis results
│   ├── file1__windows.csv
│   └── ...
├── qc_reports/           # Quality control reports
│   └── QC_report.html
├── summary_all.csv       # Combined results from all files
├── windows_all.csv       # Combined window results (if enabled)
└── summary_README.txt    # Detailed explanation of metrics
```

## Metrics Explained

### Core Metrics
- **D**: Effective diffusion coefficient (µm²/s) from MSD fit
- **α (alpha)**: Anomalous scaling exponent (0=static, 1=Brownian, >1=directed)
- **Rg**: Radius of gyration (spatial footprint, µm)
- **v_mean/v_max**: Mean and maximum instantaneous velocities (µm/s)

### Motion States
- **Static**: α ≤ α_low (default: 0.2)
- **Diffusive**: α_low < α ≤ α_high (default: 0.2-1.2)
- **Active**: α > α_high (default: 1.2)

## Technical Details

### MSD Calculation
The application fits the Mean Squared Displacement using:
```
MSD(τ) ≈ 4D·τ^α
```

### File Format Support
- Input: TrackMate Full XML export files
- Output: CSV files with comprehensive metrics

### Performance
- Multi-threaded processing for responsive GUI
- Memory-efficient processing of large datasets
- Progress tracking for long-running analyses

## Troubleshooting

### Common Issues
1. **No XML files found**: Ensure your input folder contains TrackMate XML export files
2. **Analysis fails**: Check that XML files are valid TrackMate exports
3. **Memory errors**: For very large datasets, process files in smaller batches

### Error Messages
- **"Failed to parse"**: XML file may be corrupted or not a valid TrackMate export
- **"No tracks found"**: XML file may not contain valid track data

## Dependencies

- **numpy**: Numerical computations
- **pandas**: Data manipulation and CSV export
- **scipy**: Scientific computing (curve fitting)
- **matplotlib**: Plotting (for future visualization features)
- **tkinter**: GUI framework (included with Python)

## Version History

- **v1.0**: Initial release with core SPT analysis functionality
- Converted from Jupyter notebook to standalone GUI application
- **v1.1**: Refactored into modular package structure for better maintainability
- **v1.2**: Simplified to GUI-only application

## License

This project is based on work by Saskia Sanders, Bosse Lab, Medizinische Hochschule Hannover (2025).

## Support

For issues or questions, please check the troubleshooting section above or examine the generated QC reports for detailed analysis information.

## Development

For developers interested in extending the application, see [MODULAR_STRUCTURE.md](MODULAR_STRUCTURE.md) for detailed information about the package structure and development guidelines. 
