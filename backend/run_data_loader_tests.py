#!/usr/bin/env python3
"""
Test runner for data loader unit tests.

This script runs the comprehensive unit tests for the data loading functions
and provides a summary of the test results.
"""

import subprocess
import sys
import os

def run_tests():
    """Run the data loader unit tests."""
    print("=" * 70)
    print("RUNNING TRINETRA AI DATA LOADER UNIT TESTS")
    print("=" * 70)
    
    # Change to the backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_data_loader.py", 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print("=" * 70)
        if result.returncode == 0:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Data loader functions are working correctly")
        else:
            print("❌ SOME TESTS FAILED")
            print("⚠️  Please review the test output above")
        print("=" * 70)
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())