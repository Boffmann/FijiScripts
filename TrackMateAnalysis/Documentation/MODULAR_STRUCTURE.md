# TrackMate SPT Analyzer - Modular Structure

## Overview

The TrackMate SPT Analyzer has been refactored into a proper Python package with a modular structure for better maintainability, extensibility, and code organization.

## New Package Structure

```
trackmate_spt_analyzer/
├── __init__.py              # Main package exports
├── __main__.py              # Module entry point (python -m trackmate_spt_analyzer)
├── core/                    # Core analysis functionality
│   ├── __init__.py
│   ├── analysis.py          # XML parsing, MSD calculations, motion classification
│   └── utils.py             # Helper functions, file operations, report generation
├── gui/                     # Graphical user interface
│   ├── __init__.py
│   └── app.py               # Main GUI application (tkinter)
└── cli/                     # Command-line interface
    ├── __init__.py
    └── batch_analyzer.py    # Batch processing functionality
```

## Module Responsibilities

### Core Module (`trackmate_spt_analyzer.core`)

**Purpose**: Contains all the core analysis logic, independent of user interface.

#### `analysis.py`
- **XML Parsing**: `parse_trackmate_xml()` - Parse TrackMate XML files
- **MSD Analysis**: `msd_per_track()` - Calculate MSD and diffusion coefficients
- **Motion Classification**: `rolling_window_analysis()` - Sliding window analysis
- **MSD Fitting**: `_fit_msd()` - Internal function for curve fitting

#### `utils.py`
- **File Operations**: `save_with_suffix()` - Safe file saving with timestamps
- **Report Generation**: `qc_report_html()` - HTML quality control reports
- **Documentation**: `build_readme_text()` - Generate metric explanations
- **Timestamps**: `timestamp()` - Generate formatted timestamps

### GUI Module (`trackmate_spt_analyzer.gui`)

**Purpose**: Provides the graphical user interface using tkinter.

#### `app.py`
- **Main Application**: `TrackMateSPTAnalyzer` class
- **Widget Management**: File selection, parameter configuration, progress tracking
- **Threading**: Background analysis with responsive GUI
- **User Interaction**: Help dialogs, error handling, status updates

### CLI Module (`trackmate_spt_analyzer.cli`)

**Purpose**: Provides command-line interface for batch processing.

#### `batch_analyzer.py`
- **Batch Processing**: `analyze_files()` - Process multiple XML files
- **Command Parsing**: `main()` - Argument parsing and validation
- **File Validation**: Automatic detection of XML files
- **Output Management**: Organized output directory structure

## Benefits of the Modular Structure

### 1. **Separation of Concerns**
- **Core Logic**: Analysis functions are independent of UI
- **UI Layer**: GUI and CLI are separate implementations
- **Utilities**: Common functions are centralized

### 2. **Maintainability**
- **Focused Files**: Each file has a single responsibility
- **Clear Dependencies**: Import structure shows relationships
- **Easier Testing**: Individual modules can be tested separately

### 3. **Extensibility**
- **New Analysis**: Add functions to `core.analysis`
- **New UI**: Create new modules in `gui/` or `cli/`
- **New Utilities**: Extend `core.utils` with helper functions

### 4. **Reusability**
- **Core Functions**: Can be imported and used in other projects
- **Multiple Interfaces**: Same analysis logic supports GUI and CLI
- **API Design**: Clean interfaces for external use

### 5. **Testing**
- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test module interactions
- **Mock Testing**: Easy to mock dependencies

## Usage Examples

### Importing Core Functions
```python
from trackmate_spt_analyzer.core.analysis import parse_trackmate_xml, msd_per_track
from trackmate_spt_analyzer.core.utils import save_with_suffix

# Use in your own analysis scripts
df, meta = parse_trackmate_xml("data.xml")
results = msd_per_track(df, meta["dt"])
```

### Using the GUI
```python
from trackmate_spt_analyzer.gui.app import TrackMateSPTAnalyzer
import tkinter as tk

root = tk.Tk()
app = TrackMateSPTAnalyzer(root)
root.mainloop()
```

### Using the CLI
```python
from trackmate_spt_analyzer.cli.batch_analyzer import analyze_files

# Programmatic batch processing
success = analyze_files(
    xml_files=["file1.xml", "file2.xml"],
    window=10,
    alpha_low=0.3,
    alpha_high=1.5
)
```

### Running as Module
```bash
# GUI application
python -m trackmate_spt_analyzer

# CLI application
python -m trackmate_spt_analyzer.cli.batch_analyzer file.xml
```

## Backward Compatibility

The original files have been updated to maintain backward compatibility:

- `trackmate_spt_analyzer.py` - Simple launcher for GUI
- `batch_analyzer.py` - Simple launcher for CLI
- `test_analysis.py` - Updated to use new structure

All existing functionality is preserved while using the new modular structure internally.

## Future Extensions

The modular structure makes it easy to add new features:

### New Analysis Methods
```python
# Add to trackmate_spt_analyzer/core/analysis.py
def new_analysis_method(df: pd.DataFrame) -> pd.DataFrame:
    """New analysis method."""
    # Implementation
    return results
```

### New GUI Components
```python
# Create trackmate_spt_analyzer/gui/visualization.py
class PlotWindow:
    """New visualization component."""
    def __init__(self, parent):
        # Implementation
        pass
```

### New CLI Commands
```python
# Add to trackmate_spt_analyzer/cli/batch_analyzer.py
def export_to_excel(xml_files: List[Path]) -> bool:
    """Export results to Excel format."""
    # Implementation
    return True
```

## Development Guidelines

### Adding New Features
1. **Identify Module**: Choose appropriate module (core/gui/cli)
2. **Create Function**: Implement in the relevant file
3. **Update Exports**: Add to `__init__.py` if needed
4. **Add Tests**: Create corresponding test functions
5. **Update Documentation**: Document new functionality

### Code Organization
- **Core Logic**: Keep analysis functions pure and testable
- **UI Logic**: Separate UI concerns from business logic
- **Error Handling**: Centralize error handling in appropriate modules
- **Configuration**: Use consistent parameter patterns across modules

### Testing Strategy
- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test module interactions
- **End-to-End Tests**: Test complete workflows
- **Mock Testing**: Mock external dependencies

## Conclusion

The modular structure transforms the TrackMate SPT Analyzer from a monolithic script into a professional, maintainable Python package. This structure provides:

- **Better Organization**: Clear separation of concerns
- **Easier Maintenance**: Focused, single-responsibility modules
- **Enhanced Extensibility**: Easy to add new features
- **Improved Testing**: Modular testing capabilities
- **Professional Quality**: Industry-standard package structure

The refactoring maintains all existing functionality while providing a solid foundation for future development and enhancement. 