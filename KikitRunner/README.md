# KiKit Runner

A user-friendly GUI application for running KiKit panelization commands with KiCad PCB files. This tool simplifies the process of panelizing PCB designs by providing an intuitive interface for KiKit operations.

## Overview

KiKit Runner is a Python-based GUI application that wraps KiKit functionality, making it easier to panelize PCB designs without remembering complex command-line syntax. It integrates seamlessly with KiCad's environment and provides features like auto-detection of panel files, file conflict handling, and automatic KiKit installation.

## Features

### 🎯 Core Functionality
- **Graphical Interface**: Easy-to-use GUI for running KiKit commands
- **File Management**: Browse and select input PCB files, output files, and preset configurations
- **Command Templates**: Customizable command templates with placeholder support
- **Real-time Output**: Live command output display with scrollable text area
- **Settings Persistence**: Automatically saves and loads KiCad path settings

### 🔍 Smart Auto-Detection
- **Panel Folder Detection**: Automatically detects panel folders when selecting input files
- **File Path Suggestions**: Smart suggestions for output files and preset configurations
- **KiCad Integration**: Automatic detection of KiCad installation paths

### 🛠️ Advanced Features
- **File Conflict Resolution**: Detects and handles open PCB files with options to close them automatically
- **KiKit Installation**: Automatic KiKit installation if not found in KiCad environment
- **Process Management**: Proper cleanup of background processes when closing the application
- **Error Handling**: Comprehensive error handling with user-friendly messages

### 🔧 Development Features
- **Multiple Launch Methods**: Batch file, PowerShell script, and direct Python execution
- **Environment Validation**: Validates KiCad installation and Python environment
- **Configuration Management**: JSON-based configuration storage

## Requirements

### System Requirements
- **Operating System**: Windows (primary), with cross-platform Python support
- **Python**: Python 3.6 or higher
- **KiCad**: KiCad 6.0 or higher (tested with KiCad 9.0)

### Python Dependencies
- `tkinter` (usually included with Python)
- `subprocess` (standard library)
- `json` (standard library)
- `os` (standard library)

## Installation

### Quick Start
1. **Clone or Download**: Get the KiKit Runner files
2. **Install KiCad**: Ensure KiCad is installed on your system
3. **Run**: Execute one of the launcher files

### Launch Methods

#### Method 1: Batch File (Recommended for Windows)
```batch
# Double-click or run from command line
run_kikit_runner.bat
```

#### Method 2: PowerShell Script
```powershell
# Run from PowerShell
./run_kikit_runner.ps1
```

#### Method 3: Direct Python Execution
```bash
# Run directly with Python
python gui_script_runner.py
# or
python kikitRunner.py
```

## Usage

### Basic Workflow

1. **Set KiCad Path** (First Time Setup)
   - Click "Browse..." next to "KiCad Bin Path"
   - Navigate to your KiCad installation bin folder
   - Example: `C:\Program Files\KiCad\9.0\bin`

2. **Select Input File**
   - Click "Browse..." next to "Input File"
   - Select your `.kicad_pcb` file
   - The application will auto-detect panel folders and suggest output paths

3. **Configure Output**
   - Output file path is usually auto-suggested
   - Modify if needed using the "Browse..." button

4. **Select Preset** (Optional)
   - Choose a KiKit preset JSON file
   - The application will search for common preset file names

5. **Customize Command** (Optional)
   - Modify the command template if needed
   - Use placeholders: `{input_file}`, `{output_file}`, `{preset_file}`

6. **Run Command**
   - Click "Run Command"
   - Monitor progress in the output area
   - Handle any file conflicts if prompted

### Command Templates

The default command template is:
```
kikit panelize --preset "{preset_file}" "{input_file}" "{output_file}"
```

You can customize this template using these placeholders:
- `{input_file}` - Path to the input PCB file
- `{output_file}` - Path to the output panelized PCB file
- `{preset_file}` - Path to the KiKit preset JSON file

### Example Commands
```bash
# Basic panelization with preset
kikit panelize --preset "panel_config.json" "input.kicad_pcb" "output_panel.kicad_pcb"

# Panelization with custom grid
kikit panelize --layout "grid; rows: 2; cols: 3" "input.kicad_pcb" "output_panel.kicad_pcb"

# Advanced panelization with mouse bites
kikit panelize --preset "config.json" --tabs "mousebites" "input.kicad_pcb" "panel.kicad_pcb"
```

## File Structure

```
KikitRunner/
├── gui_script_runner.py      # Main GUI application
├── kikitRunner.py             # Alternative launcher with error handling
├── run_kikit_runner.bat       # Windows batch launcher
├── run_kikit_runner.ps1       # PowerShell launcher
├── kicad_runner_config.json   # Configuration file (auto-generated)
└── README.md                  # This file
```

## Configuration

### Settings File
The application automatically creates and manages a `kicad_runner_config.json` file to store:
- KiCad installation path
- User preferences

### KiCad Path Configuration
The application will attempt to auto-detect KiCad in these locations:
- `C:\Program Files\KiCad\9.0\bin`
- `C:\Program Files (x86)\KiCad\9.0\bin`
- `C:\KiCad\9.0\bin`

## Advanced Features

### File Conflict Resolution
When the output file is open in KiCad:
- **Detection**: Automatically detects if files are in use
- **Options**: Offers to close files automatically or continue anyway
- **Safety**: Prevents data loss by handling file locks properly

### Auto-Detection Logic
When selecting an input file, the application:
1. Looks for a "panel" folder in the same directory
2. Suggests appropriate output file names
3. Searches for common preset file names (`kikit.json`, `preset.json`, etc.)

### Process Management
- **Background Processes**: Proper handling of long-running KiKit operations
- **Cleanup**: Automatic termination of processes when closing the application
- **Progress Monitoring**: Real-time output display

## Troubleshooting

### Common Issues

#### "KiKit is not installed"
- **Solution**: The application will offer to install KiKit automatically
- **Manual Installation**: Open KiCad Command Prompt and run `pip install kikit`

#### "The system cannot find the path specified"
- **Cause**: Incorrect KiCad path or missing KiCad installation
- **Solution**: Verify KiCad installation and set the correct bin path

#### "File is open" Warning
- **Cause**: Output file is open in KiCad or another application
- **Solution**: Close the file or let the application handle it automatically

#### Permission Errors
- **Cause**: Insufficient permissions or antivirus interference
- **Solution**: Run as administrator or add exception to antivirus

### Debug Mode
For troubleshooting, run the Python script directly to see detailed error messages:
```bash
python gui_script_runner.py
```

## Development

### Code Structure
- **ScriptRunner Class**: Main GUI application class
- **Event Handlers**: File browsing, command execution, window management
- **Process Management**: Background process handling and cleanup
- **Configuration**: Settings persistence and auto-detection

### Key Methods
- `run_command()`: Executes KiKit commands with proper environment setup
- `auto_detect_panel_files()`: Smart file path detection
- `on_closing()`: Cleanup when application closes
- `validate_kicad_path()`: KiCad installation validation

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for educational and personal use. Please respect KiCad and KiKit licensing terms.

## Acknowledgments

- **KiCad**: Open-source EDA software suite
- **KiKit**: PCB panelization tool by Jan Mrázek
- **Python**: Programming language and standard libraries
- **tkinter**: GUI framework

## Version History

- **v1.0**: Initial release with basic GUI functionality
- **v1.1**: Added auto-detection features and file conflict handling
- **v1.2**: Improved process management and cleanup
- **v1.3**: Enhanced error handling and KiKit installation support

## Support

For issues, suggestions, or contributions:
1. Check the troubleshooting section
2. Review error messages in the output area
3. Run in debug mode for detailed information
4. Report issues with specific error messages and steps to reproduce

---

**Happy Panelizing!** 🔧⚡