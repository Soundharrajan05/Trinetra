#!/usr/bin/env python3
"""
Package Installation Verification Script
TRINETRA AI - Trade Fraud Intelligence System

This script verifies that all required packages are properly installed.
"""

import sys
import importlib

def check_package(package_name, import_name=None):
    """Check if a package is installed and can be imported."""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'Unknown')
        print(f"✓ {package_name}: {version}")
        return True
    except ImportError as e:
        print(f"✗ {package_name}: Not installed or import failed - {e}")
        return False

def main():
    """Main verification function."""
    print("TRINETRA AI - Package Installation Verification")
    print("=" * 50)
    
    # Core packages for the project
    packages = [
        ('FastAPI', 'fastapi'),
        ('Uvicorn', 'uvicorn'),
        ('Streamlit', 'streamlit'),
        ('Plotly', 'plotly'),
        ('Pandas', 'pandas'),
        ('NumPy', 'numpy'),
        ('Scikit-learn', 'sklearn'),
        ('Requests', 'requests'),
        ('Google Generative AI', 'google.generativeai'),
        ('Python-dotenv', 'dotenv'),
        ('Joblib', 'joblib'),
        ('Python-multipart', 'multipart'),
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package_name, import_name in packages:
        if check_package(package_name, import_name):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"Installation Summary: {success_count}/{total_count} packages successfully installed")
    
    if success_count == total_count:
        print("🎉 All packages are ready for TRINETRA AI development!")
        return 0
    else:
        print("⚠️  Some packages are missing. Please check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())