#!/usr/bin/env python3
"""
Test script to verify TRINETRA AI system startup components
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        # Add backend to path
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        # Test backend imports
        from data_loader import load_dataset, validate_schema
        from feature_engineering import engineer_features
        from model import train_model, save_model, load_model
        from fraud_detection import score_transactions, classify_risk
        from ai_explainer import initialize_gemini, test_fallback_system
        
        print("✅ Backend imports successful")
        
        # Test external dependencies
        import pandas as pd
        import numpy as np
        import sklearn
        import fastapi
        import streamlit
        import plotly
        import requests
        
        print("✅ External dependencies available")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_file_structure():
    """Test that required files and directories exist."""
    print("🔍 Testing file structure...")
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "README.md",
        "backend/data_loader.py",
        "backend/feature_engineering.py",
        "backend/model.py",
        "backend/fraud_detection.py",
        "backend/ai_explainer.py",
        "backend/api.py",
        "frontend/dashboard.py",
        "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True


def test_dataset():
    """Test that the dataset can be loaded."""
    print("🔍 Testing dataset loading...")
    
    try:
        # Add backend to path
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from data_loader import load_dataset, validate_schema
        
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        df = load_dataset(dataset_path)
        
        if df is None or df.empty:
            print("❌ Dataset is empty or failed to load")
            return False
        
        if not validate_schema(df):
            print("❌ Dataset schema validation failed")
            return False
        
        print(f"✅ Dataset loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        return True
        
    except Exception as e:
        print(f"❌ Dataset test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 TRINETRA AI System Startup Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Dataset Loading", test_dataset)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to start.")
        print("\nTo start TRINETRA AI, run:")
        print("  python main.py")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues before starting the system.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)