#!/usr/bin/env python3
"""
Test all dashboard functionality that was failing
"""

import requests
import json

API_BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test an endpoint and return success status."""
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}{endpoint}", json=data or {}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {description}: {result.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return False

def main():
    """Test all dashboard functionality."""
    print("🧪 Testing Dashboard Functionality")
    print("=" * 50)
    
    tests = [
        # Basic endpoints
        ("/health", "GET", None, "Health Check"),
        ("/transactions?limit=10", "GET", None, "Load Transactions"),
        ("/suspicious", "GET", None, "Suspicious Transactions"),
        ("/fraud", "GET", None, "Fraud Transactions"),
        ("/stats", "GET", None, "Dashboard Statistics"),
        
        # Transaction explanation (the failing functionality)
        ("/explain/TXN00100", "POST", {"force_ai": False}, "Transaction Explanation (Fallback)"),
        ("/explain/TXN00100", "POST", {"force_ai": True}, "Transaction Explanation (AI)"),
        
        # Session and alerts
        ("/session/info", "GET", None, "Session Information"),
        ("/alerts/active", "GET", None, "Active Alerts"),
        
        # Natural language query
        ("/query", "POST", {"query": "What is the fraud rate?"}, "Natural Language Query"),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, method, data, description in tests:
        if test_endpoint(endpoint, method, data, description):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL DASHBOARD FUNCTIONALITY WORKING!")
        print("✅ Transaction explanations should now work in the browser")
        print("✅ Dashboard should load all data successfully")
    else:
        print(f"⚠️ {total - passed} tests failed")
    
    print(f"\n🌐 Dashboard URL: http://127.0.0.1:8505")
    print("💡 Try clicking 'Get Fallback Explanation' or 'Get AI Explanation' on any transaction")

if __name__ == "__main__":
    main()