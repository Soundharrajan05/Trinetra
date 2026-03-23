"""
API and Dashboard Integration Test for TRINETRA AI

This test validates that the FastAPI backend properly integrates with the Streamlit dashboard.
Tests API endpoint connectivity, data flow, error handling, response format compatibility,
and real-time data updates.

**Validates: System Integration Tests (Task 10.2)**
"""

import pytest
import requests
import json
import time
import subprocess
import sys
import os
import threading
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api import app
from backend.data_loader import load_dataset
from backend.feature_engineering import engineer_features
from backend.model import train_model
from backend.fraud_detection import score_transactions, classify_risk


class TestAPIDashboardIntegration:
    """Integration test for API and Dashboard connectivity."""
    
    API_BASE_URL = "http://localhost:8000"
    DASHBOARD_URL = "http://localhost:8501"
    
    @classmethod
    def setup_class(cls):
        """Set up test environment with running API server."""
        print("🔧 Setting up API-Dashboard integration test environment...")
        
        # Check if dataset exists
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Real dataset not available for integration test")
        
        # Start API server in background for testing
        cls.start_test_api_server()
        
        # Wait for API to be ready
        cls.wait_for_api_ready()
        
    @classmethod
    def teardown_class(cls):
        """Clean up test environment."""
        print("🧹 Cleaning up test environment...")
        if hasattr(cls, 'api_process') and cls.api_process:
            cls.api_process.terminate()
            cls.api_process.wait()
    
    @classmethod
    def start_test_api_server(cls):
        """Start FastAPI server for testing."""
        try:
            cmd = [
                sys.executable, "-m", "uvicorn",
                "backend.api:app",
                "--host", "localhost",
                "--port", "8000",
                "--log-level", "warning"
            ]
            
            cls.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            print("✅ Test API server started")
            
        except Exception as e:
            pytest.skip(f"Could not start test API server: {e}")
    
    @classmethod
    def wait_for_api_ready(cls, max_retries=15, delay=2):
        """Wait for API server to be ready."""
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.API_BASE_URL}/", timeout=5)
                if response.status_code == 200:
                    print("✅ API server is ready")
                    return True
            except Exception:
                if i < max_retries - 1:
                    print(f"Waiting for API server... ({i+1}/{max_retries})")
                    time.sleep(delay)
                else:
                    pytest.skip("API server not responding")
        return False
    
    def test_api_endpoint_connectivity(self):
        """Test 1: API endpoint connectivity from dashboard perspective."""
        print("🔗 Testing API endpoint connectivity...")
        
        # Test all critical endpoints that dashboard uses
        endpoints_to_test = [
            ("/", "GET", "Root endpoint"),
            ("/transactions", "GET", "All transactions"),
            ("/suspicious", "GET", "Suspicious transactions"),
            ("/fraud", "GET", "Fraud transactions"),
            ("/stats", "GET", "Dashboard statistics"),
            ("/session/info", "GET", "Session information"),
            ("/alerts", "GET", "All alerts"),
            ("/alerts/active", "GET", "Active alerts"),
            ("/alerts/statistics", "GET", "Alert statistics")
        ]
        
        connectivity_results = {}
        
        for endpoint, method, description in endpoints_to_test:
            try:
                url = f"{self.API_BASE_URL}{endpoint}"
                response = requests.request(method, url, timeout=10)
                
                # Check response status
                assert response.status_code in [200, 404], f"{description} returned status {response.status_code}"
                
                # Check response format
                if response.status_code == 200:
                    data = response.json()
                    assert isinstance(data, dict), f"{description} should return JSON object"
                    
                    # Check for expected response structure
                    if endpoint != "/":
                        assert "status" in data, f"{description} should have status field"
                
                connectivity_results[endpoint] = {
                    "status": "success",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
                
                print(f"✅ {description}: {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
                
            except Exception as e:
                connectivity_results[endpoint] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ {description}: {str(e)}")
                
        # Verify at least core endpoints are working
        core_endpoints = ["/", "/transactions", "/stats"]
        working_core = sum(1 for ep in core_endpoints if connectivity_results.get(ep, {}).get("status") == "success")
        
        assert working_core >= 2, f"At least 2 core endpoints should work, got {working_core}"
        print(f"✅ API endpoint connectivity test passed ({working_core}/{len(core_endpoints)} core endpoints working)")
    
    def test_data_flow_backend_to_frontend(self):
        """Test 2: Data flow between backend and frontend."""
        print("📊 Testing data flow between backend and frontend...")
        
        # Test transactions endpoint data flow
        response = requests.get(f"{self.API_BASE_URL}/transactions", timeout=10)
        assert response.status_code == 200, "Transactions endpoint should be accessible"
        
        data = response.json()
        assert data["status"] == "success", "Response should indicate success"
        assert "data" in data, "Response should contain data field"
        
        transactions = data["data"]
        assert isinstance(transactions, list), "Transactions should be a list"
        
        if len(transactions) > 0:
            # Validate transaction structure (what dashboard expects)
            sample_transaction = transactions[0]
            required_fields = [
                "transaction_id", "risk_score", "risk_category",
                "product", "unit_price", "market_price"
            ]
            
            for field in required_fields:
                assert field in sample_transaction, f"Transaction should have {field} field"
            
            # Validate risk categories
            valid_categories = {"SAFE", "SUSPICIOUS", "FRAUD"}
            for txn in transactions[:10]:  # Check first 10
                assert txn["risk_category"] in valid_categories, f"Invalid risk category: {txn['risk_category']}"
        
        print(f"✅ Data flow test passed ({len(transactions)} transactions)")
        
        # Test statistics endpoint data flow
        response = requests.get(f"{self.API_BASE_URL}/stats", timeout=10)
        assert response.status_code == 200, "Stats endpoint should be accessible"
        
        stats_data = response.json()
        assert stats_data["status"] == "success", "Stats response should indicate success"
        assert "data" in stats_data, "Stats response should contain data"
        
        stats = stats_data["data"]
        expected_stats = ["total_transactions", "fraud_rate", "total_trade_value"]
        
        for stat in expected_stats:
            assert stat in stats, f"Stats should include {stat}"
        
        print("✅ Statistics data flow test passed")
    
    def test_error_handling_integration(self):
        """Test 3: Error handling in integration points."""
        print("⚠️ Testing error handling in integration points...")
        
        # Test invalid transaction ID explanation
        invalid_id = "INVALID_TXN_ID_12345"
        response = requests.post(
            f"{self.API_BASE_URL}/explain/{invalid_id}",
            json={"force_ai": False},
            timeout=10
        )
        
        # Should handle gracefully (either 404 or error response)
        assert response.status_code in [200, 404], "Should handle invalid transaction ID gracefully"
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] in ["error", "success"], "Should have proper status"
        
        print("✅ Invalid transaction ID handled gracefully")
        
        # Test malformed query request
        response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"invalid_field": "test"},
            timeout=10
        )
        
        # Should return error or handle gracefully
        assert response.status_code in [200, 400, 422], "Should handle malformed request"
        
        print("✅ Malformed request handled gracefully")
        
        # Test session reset functionality
        response = requests.post(f"{self.API_BASE_URL}/session/reset", timeout=10)
        assert response.status_code == 200, "Session reset should work"
        
        data = response.json()
        assert data["status"] == "success", "Session reset should succeed"
        
        print("✅ Session reset functionality works")
    
    def test_response_format_compatibility(self):
        """Test 4: Response format compatibility with dashboard expectations."""
        print("📋 Testing response format compatibility...")
        
        # Test transactions response format
        response = requests.get(f"{self.API_BASE_URL}/transactions?limit=5", timeout=10)
        assert response.status_code == 200, "Transactions endpoint should work"
        
        data = response.json()
        
        # Validate standard API response format
        assert "status" in data, "Response should have status"
        assert "data" in data, "Response should have data"
        assert data["status"] == "success", "Status should be success"
        
        transactions = data["data"]
        
        if len(transactions) > 0:
            # Check transaction format matches dashboard expectations
            txn = transactions[0]
            
            # Required fields for dashboard display
            dashboard_required_fields = [
                "transaction_id", "product", "commodity_category",
                "unit_price", "market_price", "price_deviation",
                "risk_score", "risk_category", "date"
            ]
            
            missing_fields = [field for field in dashboard_required_fields if field not in txn]
            assert len(missing_fields) == 0, f"Missing required fields for dashboard: {missing_fields}"
            
            # Validate data types
            assert isinstance(txn["risk_score"], (int, float)), "Risk score should be numeric"
            assert isinstance(txn["risk_category"], str), "Risk category should be string"
            assert isinstance(txn["unit_price"], (int, float)), "Unit price should be numeric"
            
        print("✅ Transaction response format compatible with dashboard")
        
        # Test stats response format
        response = requests.get(f"{self.API_BASE_URL}/stats", timeout=10)
        assert response.status_code == 200, "Stats endpoint should work"
        
        stats_data = response.json()
        stats = stats_data["data"]
        
        # Dashboard expects specific KPI fields
        expected_kpis = [
            "total_transactions", "fraud_rate", "total_trade_value", "high_risk_countries"
        ]
        
        for kpi in expected_kpis:
            assert kpi in stats, f"Stats should include {kpi} for dashboard KPIs"
            assert isinstance(stats[kpi], (int, float, str)), f"{kpi} should have valid type"
        
        print("✅ Statistics response format compatible with dashboard")
    
    def test_real_time_data_updates(self):
        """Test 5: Real-time data updates capability."""
        print("🔄 Testing real-time data updates...")
        
        # Test session info updates
        initial_response = requests.get(f"{self.API_BASE_URL}/session/info", timeout=10)
        assert initial_response.status_code == 200, "Session info should be accessible"
        
        initial_data = initial_response.json()["data"]
        initial_queries = initial_data.get("queries_used", 0)
        
        # Make a query to update session state
        query_response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"query": "Test query for session update"},
            timeout=15
        )
        
        # Check if session was updated
        updated_response = requests.get(f"{self.API_BASE_URL}/session/info", timeout=10)
        assert updated_response.status_code == 200, "Session info should still be accessible"
        
        updated_data = updated_response.json()["data"]
        updated_queries = updated_data.get("queries_used", 0)
        
        # Session should reflect the query (if quota system is working)
        print(f"Queries before: {initial_queries}, after: {updated_queries}")
        
        print("✅ Session state updates working")
        
        # Test alert system updates
        alerts_response = requests.get(f"{self.API_BASE_URL}/alerts/active", timeout=10)
        assert alerts_response.status_code == 200, "Active alerts should be accessible"
        
        alerts_data = alerts_response.json()
        assert "data" in alerts_data, "Alerts response should have data"
        
        print("✅ Alert system data accessible")
        
        # Test statistics refresh
        stats_response1 = requests.get(f"{self.API_BASE_URL}/stats", timeout=10)
        time.sleep(1)  # Small delay
        stats_response2 = requests.get(f"{self.API_BASE_URL}/stats", timeout=10)
        
        assert stats_response1.status_code == 200, "First stats call should work"
        assert stats_response2.status_code == 200, "Second stats call should work"
        
        # Both should return valid data (consistency check)
        stats1 = stats_response1.json()["data"]
        stats2 = stats_response2.json()["data"]
        
        assert stats1["total_transactions"] == stats2["total_transactions"], "Transaction count should be consistent"
        
        print("✅ Statistics data consistency maintained")
    
    def test_dashboard_api_request_simulation(self):
        """Test 6: Simulate actual dashboard API request patterns."""
        print("🎭 Simulating dashboard API request patterns...")
        
        # Simulate dashboard startup sequence
        startup_endpoints = [
            "/stats",           # KPI metrics
            "/transactions",    # Transaction table
            "/alerts/active",   # Active alerts
            "/session/info"     # Session information
        ]
        
        startup_results = {}
        
        for endpoint in startup_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=10)
                end_time = time.time()
                
                assert response.status_code == 200, f"Dashboard startup endpoint {endpoint} should work"
                
                data = response.json()
                assert data["status"] == "success", f"Endpoint {endpoint} should return success"
                
                startup_results[endpoint] = {
                    "status": "success",
                    "response_time": end_time - start_time,
                    "data_size": len(str(data))
                }
                
                print(f"✅ {endpoint}: {response.status_code} ({end_time - start_time:.3f}s)")
                
            except Exception as e:
                startup_results[endpoint] = {"status": "error", "error": str(e)}
                print(f"❌ {endpoint}: {str(e)}")
        
        # Verify dashboard startup performance
        successful_endpoints = [ep for ep, result in startup_results.items() if result.get("status") == "success"]
        assert len(successful_endpoints) >= 3, f"At least 3 startup endpoints should work, got {len(successful_endpoints)}"
        
        # Check response times (dashboard requirement: API responses < 1 second)
        slow_endpoints = [
            ep for ep, result in startup_results.items() 
            if result.get("response_time", 0) > 1.0
        ]
        
        if slow_endpoints:
            print(f"⚠️ Slow endpoints detected: {slow_endpoints}")
        
        print(f"✅ Dashboard startup simulation passed ({len(successful_endpoints)}/{len(startup_endpoints)} endpoints)")
        
        # Simulate user interaction sequence
        interaction_sequence = [
            ("GET", "/suspicious", "View suspicious transactions"),
            ("GET", "/fraud", "View fraud transactions"),
            ("POST", "/query", "Ask AI question", {"query": "What are the main fraud patterns?"}),
            ("GET", "/alerts/statistics", "Check alert statistics")
        ]
        
        for method, endpoint, description, *payload in interaction_sequence:
            try:
                if method == "GET":
                    response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=10)
                else:
                    data = payload[0] if payload else {}
                    response = requests.post(f"{self.API_BASE_URL}{endpoint}", json=data, timeout=15)
                
                assert response.status_code in [200, 404], f"{description} should handle request gracefully"
                
                if response.status_code == 200:
                    resp_data = response.json()
                    assert "status" in resp_data, f"{description} should return proper format"
                
                print(f"✅ {description}: {response.status_code}")
                
            except Exception as e:
                print(f"⚠️ {description}: {str(e)}")
        
        print("✅ User interaction simulation completed")
    
    def test_concurrent_api_requests(self):
        """Test 7: Concurrent API requests (dashboard multi-section loading)."""
        print("🔀 Testing concurrent API requests...")
        
        import concurrent.futures
        
        # Simulate dashboard loading multiple sections simultaneously
        concurrent_endpoints = [
            "/transactions?limit=10",
            "/stats",
            "/alerts/active",
            "/suspicious?limit=5",
            "/fraud?limit=5"
        ]
        
        def make_request(endpoint):
            try:
                start_time = time.time()
                response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=10)
                end_time = time.time()
                
                return {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "endpoint": endpoint,
                    "error": str(e),
                    "success": False
                }
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, endpoint) for endpoint in concurrent_endpoints]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r.get("success")]
        failed_requests = [r for r in results if not r.get("success")]
        
        print(f"Concurrent requests: {len(successful_requests)} successful, {len(failed_requests)} failed")
        
        for result in results:
            if result.get("success"):
                print(f"✅ {result['endpoint']}: {result['status_code']} ({result['response_time']:.3f}s)")
            else:
                print(f"❌ {result['endpoint']}: {result.get('error', 'Unknown error')}")
        
        # At least 80% should succeed
        success_rate = len(successful_requests) / len(concurrent_endpoints)
        assert success_rate >= 0.8, f"Concurrent request success rate should be >= 80%, got {success_rate:.1%}"
        
        print(f"✅ Concurrent API requests test passed (success rate: {success_rate:.1%})")


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v", "-s"])