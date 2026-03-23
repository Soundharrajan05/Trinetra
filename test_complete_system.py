#!/usr/bin/env python3
"""
Complete system test for TRINETRA AI - Tests API, Dashboard, and Integration
"""

import requests
import time
import json

API_BASE_URL = "http://127.0.0.1:8000"
DASHBOARD_URL = "http://127.0.0.1:8505"

def test_api_endpoint(endpoint, description, method="GET", data=None):
    """Test an API endpoint and measure response time."""
    print(f"\n🔍 Testing {description}...")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}{endpoint}", json=data or {}, timeout=10)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {description}: {response_time:.2f}ms - Status: {result.get('status', 'unknown')}")
            
            # Additional info based on endpoint
            if 'data' in result:
                data_info = result['data']
                if isinstance(data_info, dict):
                    if 'transactions' in data_info:
                        print(f"   📊 Returned {len(data_info['transactions'])} transactions")
                    elif 'count' in data_info:
                        print(f"   📊 Count: {data_info['count']}")
                elif isinstance(data_info, list):
                    print(f"   📊 Returned {len(data_info)} items")
                    
            return True, response_time
        else:
            print(f"❌ {description}: HTTP {response.status_code} - {response_time:.2f}ms")
            return False, response_time
            
    except requests.exceptions.Timeout:
        print(f"⏱️ {description}: TIMEOUT (>10s)")
        return False, 10000
    except requests.exceptions.ConnectionError:
        print(f"🔌 {description}: CONNECTION FAILED")
        return False, 0
    except Exception as e:
        print(f"💥 {description}: ERROR - {str(e)}")
        return False, 0

def test_dashboard_connectivity():
    """Test dashboard connectivity."""
    print(f"\n🔍 Testing Dashboard Connectivity...")
    
    try:
        start_time = time.time()
        response = requests.get(DASHBOARD_URL, timeout=10)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            print(f"✅ Dashboard: {response_time:.2f}ms - Streamlit app accessible")
            return True, response_time
        else:
            print(f"❌ Dashboard: HTTP {response.status_code} - {response_time:.2f}ms")
            return False, response_time
            
    except Exception as e:
        print(f"💥 Dashboard: ERROR - {str(e)}")
        return False, 0

def main():
    """Run complete system tests."""
    print("🛡️ TRINETRA AI - Complete System Validation")
    print("=" * 60)
    
    # API Tests
    api_tests = [
        ("/health", "Health Check"),
        ("/", "Root Endpoint"),
        ("/transactions?limit=5", "Transactions (5 records)"),
        ("/transactions?limit=100", "Transactions (100 records)"),
        ("/transactions/quick?limit=10", "Quick Transactions"),
        ("/suspicious", "Suspicious Transactions"),
        ("/fraud", "Fraud Transactions"),
        ("/stats", "Dashboard Statistics"),
        ("/session/info", "Session Information"),
        ("/alerts/active", "Active Alerts"),
    ]
    
    # POST Tests
    post_tests = [
        ("/query", "Natural Language Query", {"query": "What is the fraud rate?"}),
    ]
    
    passed = 0
    total = len(api_tests) + len(post_tests) + 1  # +1 for dashboard
    total_time = 0
    
    # Test API endpoints
    print("\n📡 API ENDPOINT TESTS")
    print("-" * 40)
    
    for endpoint, description in api_tests:
        success, response_time = test_api_endpoint(endpoint, description)
        if success:
            passed += 1
        total_time += response_time
    
    # Test POST endpoints
    print("\n📤 POST ENDPOINT TESTS")
    print("-" * 40)
    
    for endpoint, description, data in post_tests:
        success, response_time = test_api_endpoint(endpoint, description, "POST", data)
        if success:
            passed += 1
        total_time += response_time
    
    # Test Dashboard
    print("\n🖥️ DASHBOARD TESTS")
    print("-" * 40)
    
    success, response_time = test_dashboard_connectivity()
    if success:
        passed += 1
    total_time += response_time
    
    # Results Summary
    print("\n" + "=" * 60)
    print(f"📊 SYSTEM TEST RESULTS")
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"⏱️ Total Response Time: {total_time:.2f}ms")
    print(f"📈 Average Response Time: {total_time/total:.2f}ms")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! TRINETRA AI system is fully operational.")
        print("✅ API server responding correctly")
        print("✅ Dashboard accessible")
        print("✅ All endpoints working")
        print("✅ Transaction loading should work in browser")
    else:
        print(f"\n⚠️ {total - passed} tests failed. System may have issues.")
    
    print(f"\n🌐 Access URLs:")
    print(f"   API Server: http://127.0.0.1:8000")
    print(f"   Dashboard: http://127.0.0.1:8505")
    print(f"   API Docs: http://127.0.0.1:8000/docs")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)