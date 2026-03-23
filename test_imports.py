#!/usr/bin/env python3
"""
TRINETRA AI - Import Dependencies Test
Tests that all required dependencies can be imported successfully.
"""

import sys
import importlib
from typing import List, Tuple

def test_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """
    Test if a module can be imported successfully.
    
    Args:
        module_name: Name of the module to import
        package_name: Optional package name for display
        
    Returns:
        Tuple of (success, message)
    """
    try:
        importlib.import_module(module_name)
        display_name = package_name or module_name
        return True, f"✅ {display_name} imported successfully"
    except ImportError as e:
        display_name = package_name or module_name
        return False, f"❌ {display_name} import failed: {str(e)}"
    except Exception as e:
        display_name = package_name or module_name
        return False, f"❌ {display_name} unexpected error: {str(e)}"

def main():
    """Test all required dependencies for TRINETRA AI system."""
    
    print("🔍 TRINETRA AI - Testing Dependencies Import")
    print("=" * 50)
    
    # Define all required dependencies
    dependencies = [
        # Backend Framework
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        
        # Data Processing
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        
        # Machine Learning
        ("sklearn", "scikit-learn"),
        ("joblib", "Joblib"),
        
        # AI Integration
        ("google.generativeai", "Google Generative AI"),
        
        # Data Validation
        ("pydantic", "Pydantic"),
        
        # Frontend Framework
        ("streamlit", "Streamlit"),
        
        # Visualization
        ("plotly", "Plotly"),
        ("plotly.graph_objects", "Plotly Graph Objects"),
        ("plotly.express", "Plotly Express"),
        
        # HTTP Client
        ("requests", "Requests"),
        
        # Environment Management
        ("dotenv", "Python-dotenv"),
        
        # Additional utilities
        ("multipart", "Python-multipart"),
        
        # Standard library (should always work)
        ("os", "OS"),
        ("sys", "Sys"),
        ("json", "JSON"),
        ("logging", "Logging"),
        ("threading", "Threading"),
        ("asyncio", "AsyncIO"),
    ]
    
    # Test each dependency
    results = []
    failed_imports = []
    
    for module_name, display_name in dependencies:
        success, message = test_import(module_name, display_name)
        results.append((success, message))
        print(message)
        
        if not success:
            failed_imports.append(display_name)
    
    print("\n" + "=" * 50)
    
    # Summary
    total_deps = len(dependencies)
    successful_imports = sum(1 for success, _ in results if success)
    failed_count = total_deps - successful_imports
    
    print(f"📊 Import Test Summary:")
    print(f"   Total dependencies tested: {total_deps}")
    print(f"   Successful imports: {successful_imports}")
    print(f"   Failed imports: {failed_count}")
    
    if failed_count == 0:
        print("\n🎉 All dependencies imported successfully!")
        print("✅ Environment is properly configured for TRINETRA AI")
        return True
    else:
        print(f"\n⚠️  {failed_count} dependencies failed to import:")
        for failed_dep in failed_imports:
            print(f"   - {failed_dep}")
        print("\n💡 To fix missing dependencies, run:")
        print("   pip install -r requirements.txt")
        return False

def test_specific_functionality():
    """Test specific functionality that will be used in the system."""
    
    print("\n🔧 Testing Specific Functionality")
    print("-" * 30)
    
    functionality_tests = []
    
    # Test FastAPI creation
    try:
        from fastapi import FastAPI
        app = FastAPI()
        functionality_tests.append("✅ FastAPI app creation works")
    except Exception as e:
        functionality_tests.append(f"❌ FastAPI app creation failed: {e}")
    
    # Test pandas DataFrame creation
    try:
        import pandas as pd
        df = pd.DataFrame({'test': [1, 2, 3]})
        functionality_tests.append("✅ Pandas DataFrame creation works")
    except Exception as e:
        functionality_tests.append(f"❌ Pandas DataFrame creation failed: {e}")
    
    # Test scikit-learn IsolationForest
    try:
        from sklearn.ensemble import IsolationForest
        model = IsolationForest(n_estimators=10)
        functionality_tests.append("✅ IsolationForest model creation works")
    except Exception as e:
        functionality_tests.append(f"❌ IsolationForest model creation failed: {e}")
    
    # Test Plotly figure creation
    try:
        import plotly.graph_objects as go
        fig = go.Figure()
        functionality_tests.append("✅ Plotly figure creation works")
    except Exception as e:
        functionality_tests.append(f"❌ Plotly figure creation failed: {e}")
    
    # Test Streamlit (basic import, can't test full functionality without running)
    try:
        import streamlit as st
        functionality_tests.append("✅ Streamlit import works")
    except Exception as e:
        functionality_tests.append(f"❌ Streamlit import failed: {e}")
    
    # Test Google Generative AI
    try:
        import google.generativeai as genai
        functionality_tests.append("✅ Google Generative AI import works")
    except Exception as e:
        functionality_tests.append(f"❌ Google Generative AI import failed: {e}")
    
    # Print functionality test results
    for test_result in functionality_tests:
        print(test_result)
    
    successful_functionality = sum(1 for result in functionality_tests if result.startswith("✅"))
    total_functionality = len(functionality_tests)
    
    print(f"\n📊 Functionality Test Summary:")
    print(f"   Successful: {successful_functionality}/{total_functionality}")
    
    return successful_functionality == total_functionality

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()
    
    # Run import tests
    imports_successful = main()
    
    # Run functionality tests
    functionality_successful = test_specific_functionality()
    
    # Final result
    print("\n" + "=" * 50)
    if imports_successful and functionality_successful:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Environment is ready for TRINETRA AI development")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️  Please install missing dependencies before proceeding")
        sys.exit(1)