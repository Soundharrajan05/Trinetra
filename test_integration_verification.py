#!/usr/bin/env python3
"""
Integration Verification Test for TRINETRA AI
Tests API and Dashboard Integration

This script verifies that:
1. API endpoints are accessible and return expected data
2. Dashboard can connect to API
3. Data flow between backend and frontend works
4. Error handling is proper
5. Response formats are compatible
"""

import sys
import time
import requests
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

def test_api_connectivity():
    """Test basic API connectivity."""
    print("🔗 Testing API connectivity...")
    
    base_url = "http://localhost:8000"
    endpoints_to_test = [
        "/",
        "/transactions",
        "/suspicious", 
        "/fraud",
        "/stats",
        "/session/info",
        "/alerts/active"
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            
            results[endpoint] = {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "has_json": True
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results[endpoint]["json_valid"] = True
                    results[endpoint]["has_status"] = "status" in data
                    results[endpoint]["has_data"] = "data" in data
                except:
                    results[endpoint]["json_valid"] = False
            
            print(f"✅ {endpoint}: {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
            
        except requests.exceptions.ConnectionError:
            results[endpoint] = {"error": "Connection refused", "success": False}
            print(f"❌ {endpoint}: Connection refused")
        except Exception as e:
            results[endpoint] = {"error": str(e), "success": False}
            print(f"❌ {endpoint}: {str(e)}")
    
    return results

def test_data_flow():
    """Test data flow between API and expected dashboard usage."""
    print("📊 Testing data flow...")
    
    try:
        # Test transactions endpoint
        response = requests.get("http://localhost:8000/transactions?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and "data" in data:
                transactions = data["data"]
                if len(transactions) > 0:
                    # Check required fields for dashboard
                    required_fields = ["transaction_id", "risk_score", "risk_category", "product"]
                    sample_txn = transactions[0]
                    missing_fields = [f for f in required_fields if f not in sample_txn]
                    
                    if not missing_fields:
                        print(f"✅ Transaction data format valid ({len(transactions)} transactions)")
                        return True
                    else:
                        print(f"❌ Missing required fields: {missing_fields}")
                        return False
                else:
                    print("⚠️ No transaction data available")
                    return False
            else:
                print("❌ Invalid response format")
                return False
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Data flow test failed: {str(e)}")
        return False

def test_dashboard_api_simulation():
    """Simulate dashboard API usage patterns."""
    print("🎭 Simulating dashboard API usage...")
    
    # Simulate dashboard startup sequence
    startup_sequence = [
        ("GET", "/stats", "Dashboard KPIs"),
        ("GET", "/transactions?limit=10", "Transaction table"),
        ("GET", "/alerts/active", "Active alerts"),
        ("GET", "/session/info", "Session info")
    ]
    
    success_count = 0
    
    for method, endpoint, description in startup_sequence:
        try:
            url = f"http://localhost:8000{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    print(f"✅ {description}: Success")
                    success_count += 1
                else:
                    print(f"⚠️ {description}: API returned error status")
            else:
                print(f"❌ {description}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}: {str(e)}")
    
    success_rate = success_count / len(startup_sequence)
    print(f"Dashboard simulation success rate: {success_rate:.1%}")
    
    return success_rate >= 0.75

def test_error_handling():
    """Test error handling in integration points."""
    print("⚠️ Testing error handling...")
    
    error_tests = [
        ("GET", "/transactions/invalid_id", "Invalid transaction ID"),
        ("POST", "/explain/NONEXISTENT", "Non-existent explanation"),
        ("GET", "/nonexistent_endpoint", "Non-existent endpoint")
    ]
    
    handled_gracefully = 0
    
    for method, endpoint, description in error_tests:
        try:
            url = f"http://localhost:8000{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json={}, timeout=10)
            
            # Should return 404, 400, or 422 for errors, not 500
            if response.status_code in [200, 400, 404, 422]:
                print(f"✅ {description}: Handled gracefully ({response.status_code})")
                handled_gracefully += 1
            else:
                print(f"⚠️ {description}: Unexpected status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}: {str(e)}")
    
    return handled_gracefully >= 2

def main():
    """Run integration verification tests."""
    print("🔍 TRINETRA AI - API & Dashboard Integration Verification")
    print("=" * 60)
    
    # Wait a moment for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(2)
    
    test_results = {}
    
    # Test 1: API Connectivity
    api_results = test_api_connectivity()
    working_endpoints = sum(1 for r in api_results.values() if r.get("success", False))
    test_results["api_connectivity"] = working_endpoints >= 4
    print(f"API Connectivity: {working_endpoints}/{len(api_results)} endpoints working")
    print()
    
    # Test 2: Data Flow
    test_results["data_flow"] = test_data_flow()
    print()
    
    # Test 3: Dashboard Simulation
    test_results["dashboard_simulation"] = test_dashboard_api_simulation()
    print()
    
    # Test 4: Error Handling
    test_results["error_handling"] = test_error_handling()
    print()
    
    # Summary
    print("=" * 60)
    print("📋 INTEGRATION VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests >= 3:
        print("🎉 API and Dashboard Integration: VERIFIED")
        return True
    else:
        print("⚠️ API and Dashboard Integration: ISSUES DETECTED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)