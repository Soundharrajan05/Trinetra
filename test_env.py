#!/usr/bin/env python3
"""
Test script to verify the TRINETRA AI virtual environment is working correctly.
"""

import sys
import os

def test_virtual_environment():
    """Test that the virtual environment is properly configured."""
    print("=== TRINETRA AI Virtual Environment Test ===")
    print()
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()
    
    # Check if we're in virtual environment
    venv_active = 'trinetra_env' in sys.executable
    print(f"Virtual environment active: {venv_active}")
    
    if venv_active:
        print("✅ Virtual environment is properly activated!")
    else:
        print("❌ Virtual environment is NOT activated!")
        return False
    
    print()
    
    # Check Python version compatibility
    version_info = sys.version_info
    if version_info.major == 3 and version_info.minor >= 8:
        print(f"✅ Python {version_info.major}.{version_info.minor}.{version_info.micro} meets requirement (3.8+)")
    else:
        print(f"❌ Python {version_info.major}.{version_info.minor}.{version_info.micro} does not meet requirement (3.8+)")
        return False
    
    print()
    
    # Test basic imports that should work without additional packages
    try:
        import json
        import csv
        import datetime
        print("✅ Basic Python modules import successfully")
    except ImportError as e:
        print(f"❌ Failed to import basic modules: {e}")
        return False
    
    print()
    print("=== Environment Setup Complete ===")
    print("Next steps:")
    print("1. Install packages: pip install -r requirements.txt")
    print("2. Configure Gemini API key")
    print("3. Run the application: python main.py")
    
    return True

if __name__ == "__main__":
    success = test_virtual_environment()
    sys.exit(0 if success else 1)