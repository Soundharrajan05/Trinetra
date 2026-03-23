# TRINETRA AI - Deployment Scripts Documentation

## Overview

This document describes all deployment scripts created for easy setup, execution, and maintenance of the TRINETRA AI system.

## Available Scripts

### Setup Scripts

#### `setup.bat` (Windows Batch)
Automated setup script for Windows Command Prompt.

**What it does:**
- Checks Python installation and version (3.8+ required)
- Creates virtual environment (`trinetra_env`)
- Upgrades pip to latest version
- Installs all dependencies from `requirements.txt`
- Creates `.env` file from template
- Creates necessary directories (`models/`, `logs/`, `data/`)
- Verifies installation

**Usage:**
```batch
setup.bat
```

#### `setup.ps1` (Windows PowerShell)
Automated setup script for Windows PowerShell with enhanced formatting.

**What it does:**
- Same functionality as `setup.bat`
- Colored output for better readability
- Enhanced error messages
- Progress indicators

**Usage:**
```powershell
.\setup.ps1
```

**Note:** If you get execution policy errors, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### `setup.sh` (Linux/Mac Bash)
Automated setup script for Unix-like systems.

**What it does:**
- Same functionality as Windows scripts
- Uses `python3` command
- Creates virtual environment with `venv`
- Bash-compatible syntax

**Usage:**
```bash
chmod +x setup.sh
./setup.sh
```

### Run Scripts

#### `run.bat` (Windows Batch)
Starts the TRINETRA AI system on Windows.

**What it does:**
- Checks if virtual environment exists
- Activates virtual environment
- Verifies `.env` file exists
- Checks for dataset file
- Runs `main.py` to start the system

**Usage:**
```batch
run.bat
```

#### `run.ps1` (Windows PowerShell)
Starts the TRINETRA AI system with PowerShell.

**What it does:**
- Same functionality as `run.bat`
- Enhanced visual feedback
- Colored status messages

**Usage:**
```powershell
.\run.ps1
```

#### `run.sh` (Linux/Mac Bash)
Starts the TRINETRA AI system on Unix-like systems.

**What it does:**
- Same functionality as Windows scripts
- Activates virtual environment
- Runs the application

**Usage:**
```bash
./run.sh
```

### Cleanup Scripts

#### `cleanup.bat` (Windows Batch)
Removes generated files and virtual environment on Windows.

**What it does:**
- Prompts for confirmation
- Removes virtual environment (`trinetra_env/`)
- Deletes model files (`models/*.pkl`)
- Deletes log files (`logs/*.log`)
- Removes Python cache (`__pycache__/`, `*.pyc`)
- Removes test artifacts (`.pytest_cache`, `.coverage`, `.hypothesis`)
- **Preserves:** `.env` file and dataset

**Usage:**
```batch
cleanup.bat
```

#### `cleanup.sh` (Linux/Mac Bash)
Removes generated files and virtual environment on Unix-like systems.

**What it does:**
- Same functionality as `cleanup.bat`
- Unix-compatible file operations

**Usage:**
```bash
./cleanup.sh
```

### Validation Script

#### `validate_deployment.py` (Cross-platform Python)
Validates that the deployment is ready to run.

**What it checks:**
- Python version (3.8+)
- Virtual environment exists
- Core dependencies installed (fastapi, streamlit, pandas, etc.)
- Project structure (directories and files)
- Backend modules present
- Frontend dashboard present
- `.env` file configured
- Dataset file exists
- Deployment scripts present

**Usage:**
```bash
python validate_deployment.py
```

**Output:**
- ✅ Green checkmarks for passed checks
- ❌ Red X marks for failed checks
- Detailed messages for each check
- Final summary with next steps

## Quick Start Workflow

### First Time Setup

1. **Run Setup Script**
   ```bash
   # Windows (Command Prompt)
   setup.bat
   
   # Windows (PowerShell)
   .\setup.ps1
   
   # Linux/Mac
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure Environment**
   - Edit `.env` file
   - Add your Gemini API key to `GEMINI_API_KEY`

3. **Verify Setup**
   ```bash
   python validate_deployment.py
   ```

4. **Run Application**
   ```bash
   # Windows (Command Prompt)
   run.bat
   
   # Windows (PowerShell)
   .\run.ps1
   
   # Linux/Mac
   ./run.sh
   ```

### Subsequent Runs

Just run the application:
```bash
# Windows
run.bat

# Linux/Mac
./run.sh
```

### Cleanup and Reinstall

```bash
# Clean everything
cleanup.bat  # or ./cleanup.sh

# Setup again
setup.bat    # or ./setup.sh

# Run
run.bat      # or ./run.sh
```

## Script Features

### Error Handling

All scripts include:
- **Prerequisite checks**: Verify Python, virtual environment, files
- **Error messages**: Clear, actionable error descriptions
- **Exit codes**: Non-zero exit on failure for automation
- **Confirmation prompts**: For destructive operations (cleanup)

### Visual Feedback

Scripts provide:
- **Progress indicators**: Step-by-step progress (1/6, 2/6, etc.)
- **Status symbols**: ✅ (success), ❌ (error), ⚠️ (warning)
- **Colored output**: (PowerShell and bash scripts)
- **Formatted headers**: Clear section separation

### Cross-Platform Support

- **Windows**: Batch (`.bat`) and PowerShell (`.ps1`) versions
- **Unix-like**: Bash (`.sh`) versions for Linux and Mac
- **Python**: Cross-platform validation script

## File Locations

After running setup scripts:

```
project_root/
├── trinetra_env/          # Virtual environment (created by setup)
├── models/                # ML models (created by setup)
│   └── isolation_forest.pkl  # Generated on first run
├── logs/                  # Application logs (created by setup)
│   └── trinetra_main.log     # Generated on run
├── data/                  # Dataset directory (created by setup)
│   └── trinetra_trade_fraud_dataset_1000_rows_complex.csv
├── .env                   # Your configuration (created by setup)
└── [deployment scripts]   # All .bat, .ps1, .sh files
```

## Environment Variables

The `.env` file created by setup scripts contains:

```env
# Required
GEMINI_API_KEY=your_api_key_here

# Optional (with defaults)
API_HOST=localhost
API_PORT=8000
STREAMLIT_PORT=8501
LOG_LEVEL=INFO
DATASET_PATH=data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
MODEL_PATH=models/isolation_forest.pkl
```

## Troubleshooting

### Setup Script Issues

**Problem:** "Python not found"
- **Solution:** Install Python 3.8+ and add to PATH

**Problem:** "Failed to create virtual environment"
- **Solution:** Ensure `python -m venv` works, install `python3-venv` on Linux

**Problem:** "Failed to install dependencies"
- **Solution:** Check internet connection, try manual install: `pip install -r requirements.txt`

### Run Script Issues

**Problem:** "Virtual environment not found"
- **Solution:** Run setup script first

**Problem:** ".env file not found"
- **Solution:** Run setup script or copy `.env.example` to `.env`

**Problem:** "Dataset not found"
- **Solution:** Place dataset in `data/` directory

**Problem:** "Port already in use"
- **Solution:** Edit `.env` and change `API_PORT` or `STREAMLIT_PORT`

### Cleanup Script Issues

**Problem:** "Permission denied"
- **Solution:** Close all applications using files, run as administrator

**Problem:** "Files still present after cleanup"
- **Solution:** Manually delete stubborn files/directories

### Validation Script Issues

**Problem:** "Package not found"
- **Solution:** Activate virtual environment first, then run validation

**Problem:** "All checks fail"
- **Solution:** Run setup script first

## Advanced Usage

### Custom Virtual Environment Name

Edit scripts to use different virtual environment name:

```bash
# Change 'trinetra_env' to your preferred name
python -m venv my_custom_env
```

### Custom Installation Path

Run scripts from any directory:

```bash
cd /path/to/trinetra-ai
./setup.sh
./run.sh
```

### Automated Deployment

Use scripts in CI/CD pipelines:

```bash
#!/bin/bash
# CI/CD deployment script
./setup.sh
python validate_deployment.py
if [ $? -eq 0 ]; then
    ./run.sh
fi
```

### Silent Installation

For automated setups, modify scripts to skip prompts:

```bash
# Remove 'pause' commands in .bat files
# Remove 'Read-Host' in .ps1 files
# Remove 'read -p' in .sh files
```

## Best Practices

1. **Always run setup first** on new installations
2. **Validate deployment** before running in production
3. **Keep .env secure** - never commit to version control
4. **Regular cleanup** to save disk space
5. **Update dependencies** periodically
6. **Test scripts** before hackathon/demo
7. **Have backup plan** if scripts fail

## Integration with Main Application

The deployment scripts integrate with `main.py`:

1. **Setup scripts** prepare the environment
2. **Run scripts** execute `main.py`
3. **main.py** orchestrates:
   - Data loading
   - Feature engineering
   - Model training/loading
   - API server startup
   - Dashboard launch
4. **Cleanup scripts** remove generated artifacts

## Documentation Files

- **DEPLOYMENT.md**: Comprehensive deployment guide
- **QUICKSTART.md**: Quick start guide (3 steps)
- **DEPLOYMENT_CHECKLIST.md**: Pre/post deployment checklist
- **DEPLOYMENT_SCRIPTS_README.md**: This file

## Support

For issues with deployment scripts:

1. Check script output for error messages
2. Review logs at `logs/trinetra_main.log`
3. Run validation script: `python validate_deployment.py`
4. Consult DEPLOYMENT.md for detailed troubleshooting
5. Check TROUBLESHOOTING_GUIDE.md for common issues

## Version History

- **v1.0**: Initial deployment scripts
  - Setup scripts for Windows/Linux/Mac
  - Run scripts for all platforms
  - Cleanup scripts
  - Validation script
  - Comprehensive documentation

## License

These deployment scripts are part of the TRINETRA AI project and follow the same license.
