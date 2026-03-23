#!/usr/bin/env python3
"""
TRINETRA AI - Dependency Version Report
Generates a detailed report of all installed dependencies and their versions.
"""

import sys
import importlib
import importlib.metadata
from typing import Dict, List

def get_package_version(package_name: str) -> str:
    """Get the version of an installed package."""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return "Not installed"
    except Exception:
        return "Version unknown"

def generate_dependency_report():
    """Generate a comprehensive dependency report."""
    
    print("📋 TRINETRA AI - Dependency Version Report")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print()
    
    # Define expected dependencies with their package names
    dependencies = {
        "Backend Framework": [
            ("fastapi", "FastAPI"),
            ("uvicorn", "Uvicorn"),
        ],
        "Data Processing": [
            ("pandas", "Pandas"),
            ("numpy", "NumPy"),
        ],
        "Machine Learning": [
            ("scikit-learn", "scikit-learn"),
            ("joblib", "Joblib"),
        ],
        "AI Integration": [
            ("google-generativeai", "Google Generative AI"),
        ],
        "Data Validation": [
            ("pydantic", "Pydantic"),
        ],
        "Frontend Framework": [
            ("streamlit", "Streamlit"),
        ],
        "Visualization": [
            ("plotly", "Plotly"),
        ],
        "HTTP Client": [
            ("requests", "Requests"),
        ],
        "Environment Management": [
            ("python-dotenv", "Python-dotenv"),
        ],
        "Additional Utilities": [
            ("python-multipart", "Python-multipart"),
        ]
    }
    
    all_packages_ok = True
    
    for category, packages in dependencies.items():
        print(f"📦 {category}")
        print("-" * 40)
        
        for package_name, display_name in packages:
            version = get_package_version(package_name)
            if version == "Not installed":
                print(f"❌ {display_name:<25} : {version}")
                all_packages_ok = False
            else:
                print(f"✅ {display_name:<25} : v{version}")
        
        print()
    
    # Test critical functionality
    print("🔧 Critical Functionality Tests")
    print("-" * 40)
    
    functionality_ok = True
    
    # Test ML pipeline components
    try:
        from sklearn.ensemble import IsolationForest
        import pandas as pd
        import numpy as np
        
        # Create sample data
        data = np.random.randn(100, 5)
        df = pd.DataFrame(data, columns=['f1', 'f2', 'f3', 'f4', 'f5'])
        
        # Test model training
        model = IsolationForest(n_estimators=10, random_state=42)
        model.fit(df)
        scores = model.decision_function(df)
        
        print("✅ ML Pipeline (IsolationForest + Pandas) : Working")
    except Exception as e:
        print(f"❌ ML Pipeline : Failed - {e}")
        functionality_ok = False
    
    # Test API framework
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        
        app = FastAPI()
        
        class TestModel(BaseModel):
            name: str
            value: float
        
        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}
        
        print("✅ API Framework (FastAPI + Pydantic) : Working")
    except Exception as e:
        print(f"❌ API Framework : Failed - {e}")
        functionality_ok = False
    
    # Test visualization
    try:
        import plotly.graph_objects as go
        import plotly.express as px
        
        # Create a simple figure
        fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
        fig.update_layout(title="Test Plot")
        
        print("✅ Visualization (Plotly) : Working")
    except Exception as e:
        print(f"❌ Visualization : Failed - {e}")
        functionality_ok = False
    
    # Test AI integration (import only, no API call)
    try:
        import google.generativeai as genai
        print("✅ AI Integration (Google Generative AI) : Import OK")
        print("   Note: API key required for actual functionality")
    except Exception as e:
        print(f"❌ AI Integration : Failed - {e}")
        functionality_ok = False
    
    print()
    print("=" * 60)
    print("📊 FINAL REPORT SUMMARY")
    print("=" * 60)
    
    if all_packages_ok and functionality_ok:
        print("🎉 STATUS: ALL SYSTEMS GO!")
        print("✅ All required dependencies are installed and working")
        print("✅ Critical functionality tests passed")
        print("✅ Environment is ready for TRINETRA AI development")
        print()
        print("🚀 You can now proceed with:")
        print("   - Data loading and processing")
        print("   - ML model training")
        print("   - API development")
        print("   - Dashboard creation")
        print("   - AI explanation integration")
        return True
    else:
        print("❌ STATUS: ISSUES DETECTED!")
        if not all_packages_ok:
            print("⚠️  Some required packages are missing")
        if not functionality_ok:
            print("⚠️  Some critical functionality tests failed")
        print()
        print("🔧 To fix issues:")
        print("   pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = generate_dependency_report()
    sys.exit(0 if success else 1)