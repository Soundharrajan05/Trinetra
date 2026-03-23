#!/usr/bin/env python3
"""
TRINETRA AI Demo Verification Script

This script verifies that the TRINETRA AI system meets all success criteria
and is ready for hackathon demonstration.
"""

import requests
import time
import sys
from pathlib import Path

def test_dataset_loading():
    """Test if dataset is properly loaded."""
    print("🔍 Testing dataset loading...")
    dataset_path = Path("data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
    if dataset_path.exists():
        print("✅ Dataset file exists")
        return True
    else:
        print("❌ Dataset file missing")
        return False

def test_model_existence():
    """Test if ML model exists."""
    print("🤖 Testing ML model...")
    model_path = Path("models/isolation_forest.pkl")
    if model_path.exists():
        print("✅ ML model file exists")
        return True
    else:
        print("❌ ML model file missing")
        return False

def test_api_connectivity():
    """Test API server connectivity and endpoints."""
    print("🌐 Testing API server...")
    
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("✅ API root endpoint responding")
        else:
            print(f"❌ API root endpoint error: {response.status_code}")
            return False
            
        # Test transactions endpoint
        response = requests.get("http://localhost:8000/transactions", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and len(data.get('data', [])) > 0:
                print(f"✅ Transactions endpoint working ({len(data['data'])} transactions)")
            else:
                print("❌ Transactions endpoint returned no data")
                return False
        else:
            print(f"❌ Transactions endpoint error: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API connectivity failed: {e}")
        return False

def test_dashboard_connectivity():
    """Test Streamlit dashboard connectivity."""
    print("📱 Testing dashboard...")
    
    try:
        response = requests.get("http://localhost:8502/", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard responding")
            return True
        else:
            print(f"❌ Dashboard error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard connectivity failed: {e}")
        return False

def test_fraud_detection():
    """Test fraud detection functionality."""
    print("🔍 Testing fraud detection...")
    
    try:
        response = requests.get("http://localhost:8000/fraud", timeout=15)
        if response.status_code == 200:
            data = response.json()
            fraud_count = len(data.get('data', []))
            print(f"✅ Fraud detection working ({fraud_count} fraud cases detected)")
            return fraud_count > 0
        else:
            print(f"❌ Fraud endpoint error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Fraud detection test failed: {e}")
        return False

def test_suspicious_transactions():
    """Test suspicious transaction detection."""
    print("⚠️ Testing suspicious transaction detection...")
    
    try:
        response = requests.get("http://localhost:8000/suspicious", timeout=15)
        if response.status_code == 200:
            data = response.json()
            suspicious_count = len(data.get('data', []))
            print(f"✅ Suspicious detection working ({suspicious_count} suspicious cases)")
            return suspicious_count > 0
        else:
            print(f"❌ Suspicious endpoint error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Suspicious detection test failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🛡️ TRINETRA AI Demo Verification")
    print("=" * 50)
    
    tests = [
        ("Dataset Loading", test_dataset_loading),
        ("ML Model", test_model_existence),
        ("API Connectivity", test_api_connectivity),
        ("Dashboard", test_dashboard_connectivity),
        ("Fraud Detection", test_fraud_detection),
        ("Suspicious Detection", test_suspicious_transactions),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 TRINETRA AI is DEMO-READY!")
        print("\n🚀 System Access URLs:")
        print("   📱 Dashboard: http://localhost:8502")
        print("   🌐 API: http://localhost:8000")
        return True
    else:
        print("❌ System not ready for demo")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)