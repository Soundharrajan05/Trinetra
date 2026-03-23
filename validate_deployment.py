#!/usr/bin/env python3
"""
TRINETRA AI - Deployment Validation Script
This script validates that the deployment is ready for use.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Tuple, List

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_check(name: str, passed: bool, message: str = ""):
    """Print a check result"""
    status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if passed else f"{Colors.RED}❌ FAIL{Colors.RESET}"
    print(f"{status} - {name}")
    if message:
        print(f"       {Colors.YELLOW}{message}{Colors.RESET}")

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (3.8+ required)"

def check_file_exists(filepath: str) -> Tuple[bool, str]:
    """Check if a file exists"""
    path = Path(filepath)
    if path.exists():
        return True, f"Found at {filepath}"
    return False, f"Missing: {filepath}"

def check_directory_exists(dirpath: str) -> Tuple[bool, str]:
    """Check if a directory exists"""
    path = Path(dirpath)
    if path.exists() and path.is_dir():
        return True, f"Found at {dirpath}"
    return False, f"Missing: {dirpath}"

def check_virtual_environment() -> Tuple[bool, str]:
    """Check if virtual environment exists"""
    venv_paths = [
        Path("trinetra_env"),
        Path("venv"),
        Path(".venv")
    ]
    
    for venv_path in venv_paths:
        if venv_path.exists():
            return True, f"Found at {venv_path}"
    
    return False, "No virtual environment found (trinetra_env, venv, or .venv)"

def check_package_installed(package: str) -> Tuple[bool, str]:
    """Check if a Python package is installed"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Extract version from output
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split(':')[1].strip()
                    return True, f"{package} {version}"
            return True, f"{package} installed"
        return False, f"{package} not installed"
    except Exception as e:
        return False, f"Error checking {package}: {str(e)}"

def check_env_file() -> Tuple[bool, str]:
    """Check if .env file exists and has API key"""
    if not Path(".env").exists():
        return False, ".env file not found"
    
    try:
        with open(".env", "r") as f:
            content = f.read()
            if "GEMINI_API_KEY" in content:
                # Check if it's not the placeholder
                if "your_gemini_api_key_here" not in content and "your_api_key_here" not in content:
                    return True, ".env configured with API key"
                return False, ".env exists but API key is placeholder"
            return False, ".env exists but missing GEMINI_API_KEY"
    except Exception as e:
        return False, f"Error reading .env: {str(e)}"

def check_dataset() -> Tuple[bool, str]:
    """Check if dataset file exists"""
    dataset_path = Path("data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
    if dataset_path.exists():
        size_mb = dataset_path.stat().st_size / (1024 * 1024)
        return True, f"Dataset found ({size_mb:.2f} MB)"
    return False, "Dataset not found in data/ directory"

def check_deployment_scripts() -> List[Tuple[str, bool, str]]:
    """Check if all deployment scripts exist"""
    scripts = [
        "setup.bat",
        "setup.ps1",
        "setup.sh",
        "run.bat",
        "run.ps1",
        "run.sh",
        "cleanup.bat",
        "cleanup.sh"
    ]
    
    results = []
    for script in scripts:
        passed, message = check_file_exists(script)
        results.append((script, passed, message))
    
    return results

def main():
    """Main validation function"""
    print_header("TRINETRA AI - Deployment Validation")
    
    all_passed = True
    
    # Check Python version
    print_header("Python Environment")
    passed, message = check_python_version()
    print_check("Python Version", passed, message)
    all_passed = all_passed and passed
    
    # Check virtual environment
    passed, message = check_virtual_environment()
    print_check("Virtual Environment", passed, message)
    all_passed = all_passed and passed
    
    # Check core dependencies
    print_header("Core Dependencies")
    core_packages = [
        "fastapi",
        "uvicorn",
        "streamlit",
        "pandas",
        "scikit-learn",
        "plotly",
        "google-generativeai"
    ]
    
    for package in core_packages:
        passed, message = check_package_installed(package)
        print_check(package, passed, message)
        all_passed = all_passed and passed
    
    # Check project structure
    print_header("Project Structure")
    
    # Check directories
    directories = ["backend", "frontend", "data", "models", "logs"]
    for directory in directories:
        passed, message = check_directory_exists(directory)
        print_check(f"Directory: {directory}/", passed, message)
        all_passed = all_passed and passed
    
    # Check key files
    key_files = [
        "main.py",
        "requirements.txt",
        ".env.example"
    ]
    for filepath in key_files:
        passed, message = check_file_exists(filepath)
        print_check(f"File: {filepath}", passed, message)
        all_passed = all_passed and passed
    
    # Check backend modules
    backend_modules = [
        "backend/api.py",
        "backend/data_loader.py",
        "backend/feature_engineering.py",
        "backend/fraud_detection.py",
        "backend/model.py",
        "backend/ai_explainer.py"
    ]
    for module in backend_modules:
        passed, message = check_file_exists(module)
        print_check(f"Module: {module}", passed, message)
        all_passed = all_passed and passed
    
    # Check frontend
    passed, message = check_file_exists("frontend/dashboard.py")
    print_check("Frontend: dashboard.py", passed, message)
    all_passed = all_passed and passed
    
    # Check configuration
    print_header("Configuration")
    
    passed, message = check_env_file()
    print_check("Environment Configuration", passed, message)
    if not passed:
        all_passed = False
        print(f"       {Colors.YELLOW}Run setup script and edit .env file{Colors.RESET}")
    
    passed, message = check_dataset()
    print_check("Dataset", passed, message)
    if not passed:
        all_passed = False
        print(f"       {Colors.YELLOW}Place dataset in data/ directory{Colors.RESET}")
    
    # Check deployment scripts
    print_header("Deployment Scripts")
    
    script_results = check_deployment_scripts()
    for script_name, passed, message in script_results:
        print_check(f"Script: {script_name}", passed, message)
        all_passed = all_passed and passed
    
    # Final summary
    print_header("Validation Summary")
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ All checks passed!{Colors.RESET}")
        print(f"\n{Colors.CYAN}Your deployment is ready.{Colors.RESET}")
        print(f"{Colors.CYAN}Run the application with:{Colors.RESET}")
        print(f"  {Colors.YELLOW}Windows: run.bat{Colors.RESET}")
        print(f"  {Colors.YELLOW}Linux/Mac: ./run.sh{Colors.RESET}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some checks failed!{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please address the issues above before running.{Colors.RESET}")
        print(f"{Colors.YELLOW}Common fixes:{Colors.RESET}")
        print(f"  1. Run setup script: setup.bat or ./setup.sh")
        print(f"  2. Edit .env and add Gemini API key")
        print(f"  3. Place dataset in data/ directory")
        print(f"  4. Install missing dependencies: pip install -r requirements.txt")
    
    print()
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
