#!/usr/bin/env python3
"""
Test script to validate TRINETRA AI API performance fixes
"""

import requests
import time
import json

API_BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, description):
    """Test an API endpoint and measure response time."""
    print(f"\n🔍 Testing {description}...")
    
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}: {response_time:.2f}ms - Status: {data.get('status', 'unknown')}")
            
            if 'data' in data and 'transactions' in data['data']:
                print(f"   📊 Returned {len(data['data']['transactions'])} transactions")
            elif 'data' in data and isinstance(data['data'], list):
                print(f"   📊 Returned {len(data['data'])} items")
                
            return True
        else:
            print(f"❌ {description}: HTTP {response.status_code} - {response_time:.2f}ms")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏱️ {description}: TIMEOUT (>10s)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"🔌 {description}: CONNECTION FAILED")
        return False
    except Exception as e:
        print(f"💥 {description}: ERROR - {str(e)}")
        return False

def main():
    """Run all API performance tests."""
    print("🛡️ TRINETRA AI - API Performance Validation")
    print("=" * 50)
    
    tests = [
        ("/health", "Health Check"),
        ("/transactions?limit=5", "Transactions (5 records)"),
        ("/transactions?limit=50", "Transactions (50 records)"),
        ("/transactions/quick?limit=10", "Quick Transactions"),
        ("/suspicious", "Suspicious Transactions"),
        ("/fraud", "Fraud Transactions"),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, description in tests:
        if test_endpoint(endpoint, description):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! API is performing well.")
        print("✅ Dashboard should now load transactions successfully.")
    else:
        print("⚠️ Some tests failed. Check API server status.")
    
    print(f"\n🌐 Dashboard URL: http://localhost:8505")
    print(f"📚 API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()