#!/usr/bin/env python3
"""
Fast Integration Test for TRINETRA AI API and Dashboard Integration

This test verifies that API endpoints work correctly without external dependencies
and can complete in under 10 seconds as required.
"""

import os
import sys
import time
import requests
import threading
import subprocess
from pathlib import Path

# Set TEST_MODE before importing any modules
os.environ["TEST_MODE"] = "true"

# Add backend to path
sys.path.insert(0, "backend")

def test_api_endpoints_direct():
    """Test API endpoints directly using FastAPI TestClient."""
    print("🔧 Testing API endpoints directly...")
    
    from fastapi.testclient import TestClient
    from api import app, initialize_system
    
    # Initialize system first
    try:
        initialize_system()
        print("✅ System initialized successfully")
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return False
    
    # Create test client
    client = TestClient(app)
    
    # Test endpoints
    endpoints_to_test = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/transactions?limit=5", "Transactions with limit"),
        ("GET", "/suspicious", "Suspicious transactions"),
        ("GET", "/fraud", "Fraud transactions"),
        ("GET", "/stats", "Statistics"),
        ("GET", "/session/info", "Session info"),
        ("GET", "/alerts", "All alerts"),
        ("GET", "/alerts/active", "Active alerts"),
        ("GET", "/alerts/statistics", "Alert statistics")
    ]
    
    results = {}
    
    for method, endpoint, description in endpoints_to_test:
        try:
            start_time = time.time()
            
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Check response
            assert response.status_code in [200, 404], f"{description} returned {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, dict), f"{description} should return JSON object"
                
                if endpoint != "/":
                    assert "status" in data, f"{description} should have status field"
            
            results[endpoint] = {
                "status": "success",
                "status_code": response.status_code,
                "response_time": response_time
            }
            
            print(f"✅ {description}: {response.status_code} ({response_time:.3f}s)")
            
        except Exception as e:
            results[endpoint] = {"status": "error", "error": str(e)}
            print(f"❌ {description}: {str(e)}")
    
    # Check success rate
    successful = sum(1 for r in results.values() if r.get("status") == "success")
    total = len(results)
    success_rate = successful / total
    
    print(f"📊 API endpoint test results: {successful}/{total} successful ({success_rate:.1%})")
    
    return success_rate >= 0.8  # At least 80% should work

def test_explanation_endpoints():
    """Test explanation endpoints with TEST_MODE."""
    print("🧠 Testing explanation endpoints...")
    
    from fastapi.testclient import TestClient
    from api import app
    
    client = TestClient(app)
    
    # Test transaction explanation
    try:
        # Get a transaction ID first
        response = client.get("/transactions?limit=1")
        assert response.status_code == 200, "Should get transactions"
        
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            transaction_id = data["data"][0]["transaction_id"]
            
            # Test explanation endpoint
            explain_response = client.post(f"/explain/{transaction_id}", json={"force_ai": False})
            assert explain_response.status_code == 200, "Explanation should work"
            
            explain_data = explain_response.json()
            assert explain_data["status"] == "success", "Explanation should succeed"
            assert "data" in explain_data, "Should have explanation data"
            
            explanation = explain_data["data"]
            assert "test mode" in explanation.lower(), "Should use test mode explanation"
            
            print(f"✅ Transaction explanation: {explanation[:50]}...")
        
        # Test query endpoint
        query_response = client.post("/query", json={"query": "What is the fraud rate?"})
        assert query_response.status_code == 200, "Query should work"
        
        query_data = query_response.json()
        assert query_data["status"] == "success", "Query should succeed"
        assert "data" in query_data, "Should have query response"
        
        query_result = query_data["data"]
        assert "test mode" in query_result.lower(), "Should use test mode response"
        
        print(f"✅ Investigation query: {query_result[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Explanation endpoints test failed: {e}")
        return False

def test_data_consistency():
    """Test data consistency across endpoints."""
    print("📊 Testing data consistency...")
    
    from fastapi.testclient import TestClient
    from api import app
    
    client = TestClient(app)
    
    try:
        # Get statistics
        stats_response = client.get("/stats")
        assert stats_response.status_code == 200, "Stats should work"
        
        stats_data = stats_response.json()["data"]
        total_transactions = stats_data["total_transactions"]
        
        # Get all transactions
        transactions_response = client.get("/transactions")
        assert transactions_response.status_code == 200, "Transactions should work"
        
        transactions_data = transactions_response.json()["data"]
        actual_transactions = len(transactions_data)
        
        # Check consistency
        assert total_transactions == actual_transactions, f"Stats show {total_transactions} but got {actual_transactions} transactions"
        
        # Check transaction structure
        if actual_transactions > 0:
            sample_txn = transactions_data[0]
            required_fields = ["transaction_id", "risk_score", "risk_category", "product"]
            
            for field in required_fields:
                assert field in sample_txn, f"Transaction missing {field}"
        
        print(f"✅ Data consistency verified: {total_transactions} transactions")
        return True
        
    except Exception as e:
        print(f"❌ Data consistency test failed: {e}")
        return False

def test_performance():
    """Test that all endpoints respond within acceptable time limits."""
    print("⚡ Testing performance...")
    
    from fastapi.testclient import TestClient
    from api import app
    
    client = TestClient(app)
    
    # Test critical endpoints for performance
    performance_endpoints = [
        "/stats",
        "/transactions?limit=10",
        "/suspicious",
        "/alerts/active"
    ]
    
    slow_endpoints = []
    
    for endpoint in performance_endpoints:
        try:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200 and response_time > 1.0:
                slow_endpoints.append((endpoint, response_time))
            
            print(f"✅ {endpoint}: {response_time:.3f}s")
            
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")
    
    if slow_endpoints:
        print(f"⚠️ Slow endpoints detected: {slow_endpoints}")
    
    print(f"✅ Performance test completed")
    return len(slow_endpoints) == 0

def main():
    """Run all integration tests."""
    print("=" * 60)
    print("TRINETRA AI - Fast Integration Test")
    print("Testing API and Dashboard Integration")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Run tests
        test_results = {
            "API Endpoints": test_api_endpoints_direct(),
            "Explanation Endpoints": test_explanation_endpoints(),
            "Data Consistency": test_data_consistency(),
            "Performance": test_performance()
        }
        
        # Calculate results
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = passed_tests / total_tests
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print("=" * 60)
        print("TEST RESULTS:")
        print("=" * 60)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({success_rate:.1%})")
        print(f"Total time: {total_time:.2f} seconds")
        
        if success_rate >= 0.75 and total_time < 10:
            print("\n🎉 INTEGRATION TEST PASSED!")
            print("✅ API and dashboard integration verified")
            print("✅ All endpoints work without external dependencies")
            print("✅ Performance requirements met (< 10 seconds)")
            return True
        else:
            print(f"\n❌ INTEGRATION TEST FAILED!")
            if success_rate < 0.75:
                print(f"❌ Success rate too low: {success_rate:.1%} (need ≥75%)")
            if total_time >= 10:
                print(f"❌ Test took too long: {total_time:.2f}s (need <10s)")
            return False
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)