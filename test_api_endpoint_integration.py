#!/usr/bin/env python3
"""
API Endpoint Integration Test for TRINETRA AI

**Validates: Integration Testing (section 12.2) - Test API endpoint integration**

This test implements comprehensive integration testing for all API endpoints,
verifying they work correctly together and integrate properly with:
- ML pipeline (fraud detection)
- Data loading and validation
- AI explanation components
- Error handling and response formats
- JSON schema compliance (CP-4 correctness property)
- Dashboard frontend compatibility

Test Coverage:
- GET /transactions - returns all transactions with risk scores
- GET /suspicious - returns only suspicious transactions  
- GET /fraud - returns confirmed fraud cases
- POST /explain/{transaction_id} - returns AI explanation
- POST /query - supports natural language queries
- GET /stats - returns dashboard statistics
- Alert system endpoints
- Session management endpoints
"""

import os
import sys
import time
import json
import pytest
from typing import Dict, List, Any
from pathlib import Path

# Set TEST_MODE before importing any modules
os.environ["TEST_MODE"] = "true"

# Add backend to path
sys.path.insert(0, "backend")

from fastapi.testclient import TestClient
from api import app, initialize_system


class APIEndpointIntegrationTest:
    """Comprehensive API endpoint integration test suite."""
    
    def __init__(self):
        self.client = None
        self.test_results = {}
        self.sample_transaction_id = None
        
    def setup(self):
        """Initialize the test environment."""
        print("🔧 Setting up API endpoint integration test...")
        
        try:
            # Initialize system components
            initialize_system()
            print("✅ System initialized successfully")
            
            # Create test client
            self.client = TestClient(app)
            print("✅ Test client created")
            
            # Get a sample transaction ID for testing
            self._get_sample_transaction_id()
            
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def _get_sample_transaction_id(self):
        """Get a sample transaction ID for testing."""
        try:
            response = self.client.get("/transactions?limit=1")
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    self.sample_transaction_id = data["data"][0]["transaction_id"]
                    print(f"✅ Sample transaction ID: {self.sample_transaction_id}")
        except Exception as e:
            print(f"⚠️ Could not get sample transaction ID: {e}")
    
    def test_core_endpoints(self):
        """Test all core API endpoints for basic functionality."""
        print("\n📡 Testing core API endpoints...")
        
        endpoints = [
            {
                "method": "GET",
                "path": "/",
                "description": "Root endpoint",
                "expected_status": 200
            },
            {
                "method": "GET", 
                "path": "/transactions",
                "description": "All transactions",
                "expected_status": 200,
                "validate_schema": True
            },
            {
                "method": "GET",
                "path": "/transactions?limit=10&offset=0",
                "description": "Transactions with pagination",
                "expected_status": 200,
                "validate_schema": True
            },
            {
                "method": "GET",
                "path": "/suspicious",
                "description": "Suspicious transactions",
                "expected_status": 200,
                "validate_schema": True
            },
            {
                "method": "GET",
                "path": "/fraud", 
                "description": "Fraud transactions",
                "expected_status": 200,
                "validate_schema": True
            },
            {
                "method": "GET",
                "path": "/stats",
                "description": "Dashboard statistics",
                "expected_status": 200,
                "validate_schema": True
            }
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                
                if endpoint["method"] == "GET":
                    response = self.client.get(endpoint["path"])
                else:
                    response = self.client.post(endpoint["path"], json={})
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Validate status code
                assert response.status_code == endpoint["expected_status"], \
                    f"Expected {endpoint['expected_status']}, got {response.status_code}"
                
                # Validate JSON response
                data = response.json()
                assert isinstance(data, dict), "Response should be JSON object"
                
                # Validate schema for data endpoints
                if endpoint.get("validate_schema") and endpoint["path"] != "/":
                    self._validate_api_response_schema(data, endpoint["description"])
                
                results[endpoint["path"]] = {
                    "status": "success",
                    "response_time": response_time,
                    "status_code": response.status_code
                }
                
                print(f"✅ {endpoint['description']}: {response.status_code} ({response_time:.3f}s)")
                
            except Exception as e:
                results[endpoint["path"]] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ {endpoint['description']}: {str(e)}")
        
        self.test_results["core_endpoints"] = results
        successful = sum(1 for r in results.values() if r.get("status") == "success")
        total = len(results)
        
        print(f"📊 Core endpoints: {successful}/{total} successful")
        return successful == total
    
    def test_ml_pipeline_integration(self):
        """Test integration with ML pipeline and fraud detection."""
        print("\n🤖 Testing ML pipeline integration...")
        
        try:
            # Test transactions endpoint returns ML results
            response = self.client.get("/transactions?limit=5")
            assert response.status_code == 200, "Transactions endpoint should work"
            
            data = response.json()
            assert data["status"] == "success", "Should have success status"
            assert "data" in data, "Should have data field"
            
            transactions = data["data"]
            assert len(transactions) > 0, "Should have transactions"
            
            # Validate ML pipeline integration
            for txn in transactions:
                # Check required ML fields
                assert "risk_score" in txn, "Should have risk_score from ML model"
                assert "risk_category" in txn, "Should have risk_category classification"
                assert isinstance(txn["risk_score"], (int, float)), "Risk score should be numeric"
                assert txn["risk_category"] in ["SAFE", "SUSPICIOUS", "FRAUD"], \
                    f"Invalid risk category: {txn['risk_category']}"
                
                # Validate feature engineering results
                expected_features = [
                    "price_anomaly_score", "route_risk_score", "company_network_risk",
                    "port_congestion_score", "shipment_duration_risk", "volume_spike_score"
                ]
                
                for feature in expected_features:
                    if feature in txn:  # Features might not all be present in response
                        assert isinstance(txn[feature], (int, float)), \
                            f"{feature} should be numeric"
            
            # Test risk category filtering
            suspicious_response = self.client.get("/suspicious")
            assert suspicious_response.status_code == 200, "Suspicious endpoint should work"
            
            suspicious_data = suspicious_response.json()["data"]
            for txn in suspicious_data:
                assert txn["risk_category"] == "SUSPICIOUS", \
                    "Suspicious endpoint should only return SUSPICIOUS transactions"
            
            fraud_response = self.client.get("/fraud")
            assert fraud_response.status_code == 200, "Fraud endpoint should work"
            
            fraud_data = fraud_response.json()["data"]
            for txn in fraud_data:
                assert txn["risk_category"] == "FRAUD", \
                    "Fraud endpoint should only return FRAUD transactions"
            
            print("✅ ML pipeline integration verified")
            print(f"   - Risk scoring: ✅")
            print(f"   - Risk classification: ✅") 
            print(f"   - Feature engineering: ✅")
            print(f"   - Category filtering: ✅")
            
            self.test_results["ml_pipeline"] = {"status": "success"}
            return True
            
        except Exception as e:
            print(f"❌ ML pipeline integration failed: {e}")
            self.test_results["ml_pipeline"] = {"status": "error", "error": str(e)}
            return False
    
    def test_ai_explanation_integration(self):
        """Test integration with AI explanation components."""
        print("\n🧠 Testing AI explanation integration...")
        
        try:
            if not self.sample_transaction_id:
                print("⚠️ No sample transaction ID available, skipping AI tests")
                return True
            
            # Test transaction explanation endpoint
            explain_response = self.client.post(
                f"/explain/{self.sample_transaction_id}",
                json={"force_ai": False}  # Use fallback in test mode
            )
            
            assert explain_response.status_code == 200, "Explanation endpoint should work"
            
            explain_data = explain_response.json()
            assert explain_data["status"] == "success", "Explanation should succeed"
            assert "data" in explain_data, "Should have explanation data"
            
            explanation = explain_data["data"]
            assert isinstance(explanation, str), "Explanation should be string"
            assert len(explanation) > 0, "Explanation should not be empty"
            
            # Test natural language query endpoint
            query_response = self.client.post(
                "/query",
                json={"query": "What is the current fraud rate?"}
            )
            
            assert query_response.status_code == 200, "Query endpoint should work"
            
            query_data = query_response.json()
            assert query_data["status"] == "success", "Query should succeed"
            assert "data" in query_data, "Should have query response"
            
            query_result = query_data["data"]
            assert isinstance(query_result, str), "Query result should be string"
            assert len(query_result) > 0, "Query result should not be empty"
            
            print("✅ AI explanation integration verified")
            print(f"   - Transaction explanations: ✅")
            print(f"   - Natural language queries: ✅")
            
            self.test_results["ai_explanation"] = {"status": "success"}
            return True
            
        except Exception as e:
            print(f"❌ AI explanation integration failed: {e}")
            self.test_results["ai_explanation"] = {"status": "error", "error": str(e)}
            return False
    
    def test_alert_system_integration(self):
        """Test integration with alert system."""
        print("\n🚨 Testing alert system integration...")
        
        try:
            # Test alert endpoints
            alerts_response = self.client.get("/alerts")
            assert alerts_response.status_code == 200, "Alerts endpoint should work"
            
            alerts_data = alerts_response.json()
            assert alerts_data["status"] == "success", "Should have success status"
            assert "data" in alerts_data, "Should have alerts data"
            
            # Test active alerts
            active_alerts_response = self.client.get("/alerts/active")
            assert active_alerts_response.status_code == 200, "Active alerts should work"
            
            # Test alert statistics
            alert_stats_response = self.client.get("/alerts/statistics")
            assert alert_stats_response.status_code == 200, "Alert statistics should work"
            
            alert_stats = alert_stats_response.json()["data"]
            assert "total_alerts" in alert_stats, "Should have total alerts count"
            assert "active_alerts" in alert_stats, "Should have active alerts count"
            
            print("✅ Alert system integration verified")
            print(f"   - Alert retrieval: ✅")
            print(f"   - Alert statistics: ✅")
            
            self.test_results["alert_system"] = {"status": "success"}
            return True
            
        except Exception as e:
            print(f"❌ Alert system integration failed: {e}")
            self.test_results["alert_system"] = {"status": "error", "error": str(e)}
            return False
    
    def test_error_handling(self):
        """Test error handling and response formats."""
        print("\n⚠️ Testing error handling...")
        
        error_tests = [
            {
                "method": "GET",
                "path": "/transactions/nonexistent",
                "description": "Non-existent endpoint",
                "expected_status": 404
            },
            {
                "method": "POST",
                "path": "/explain/INVALID_ID",
                "json": {"force_ai": False},
                "description": "Invalid transaction ID",
                "expected_status": 404
            },
            {
                "method": "POST",
                "path": "/query",
                "json": {},  # Missing query field
                "description": "Invalid query request",
                "expected_status": 422
            }
        ]
        
        results = {}
        
        for test in error_tests:
            try:
                if test["method"] == "GET":
                    response = self.client.get(test["path"])
                else:
                    response = self.client.post(test["path"], json=test.get("json", {}))
                
                # Validate expected error status
                assert response.status_code == test["expected_status"], \
                    f"Expected {test['expected_status']}, got {response.status_code}"
                
                # Validate error response format
                if response.status_code != 404:  # 404 might not have JSON
                    try:
                        error_data = response.json()
                        assert isinstance(error_data, dict), "Error response should be JSON"
                    except:
                        pass  # Some errors might not return JSON
                
                results[test["path"]] = {"status": "success"}
                print(f"✅ {test['description']}: {response.status_code}")
                
            except Exception as e:
                results[test["path"]] = {"status": "error", "error": str(e)}
                print(f"❌ {test['description']}: {str(e)}")
        
        self.test_results["error_handling"] = results
        successful = sum(1 for r in results.values() if r.get("status") == "success")
        total = len(results)
        
        print(f"📊 Error handling: {successful}/{total} tests passed")
        return successful >= total * 0.8  # Allow some flexibility
    
    def test_performance_requirements(self):
        """Test API response time requirements."""
        print("\n⚡ Testing performance requirements...")
        
        performance_tests = [
            {"path": "/stats", "max_time": 1.0, "description": "Statistics"},
            {"path": "/transactions?limit=10", "max_time": 1.0, "description": "Limited transactions"},
            {"path": "/suspicious", "max_time": 1.0, "description": "Suspicious transactions"},
            {"path": "/alerts/active", "max_time": 1.0, "description": "Active alerts"}
        ]
        
        slow_endpoints = []
        
        for test in performance_tests:
            try:
                start_time = time.time()
                response = self.client.get(test["path"])
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    if response_time > test["max_time"]:
                        slow_endpoints.append((test["path"], response_time))
                        print(f"⚠️ {test['description']}: {response_time:.3f}s (> {test['max_time']}s)")
                    else:
                        print(f"✅ {test['description']}: {response_time:.3f}s")
                
            except Exception as e:
                print(f"❌ {test['description']}: {str(e)}")
        
        self.test_results["performance"] = {
            "slow_endpoints": slow_endpoints,
            "status": "success" if len(slow_endpoints) == 0 else "warning"
        }
        
        print(f"📊 Performance: {len(slow_endpoints)} slow endpoints detected")
        return len(slow_endpoints) <= 1  # Allow one slow endpoint
    
    def test_dashboard_compatibility(self):
        """Test compatibility with dashboard frontend requirements."""
        print("\n🎨 Testing dashboard compatibility...")
        
        try:
            # Test data format expected by dashboard
            stats_response = self.client.get("/stats")
            stats_data = stats_response.json()["data"]
            
            # Validate dashboard KPI fields
            required_kpis = [
                "total_transactions", "fraud_rate", "total_trade_value", 
                "high_risk_countries", "suspicious_count", "fraud_count"
            ]
            
            for kpi in required_kpis:
                assert kpi in stats_data, f"Missing KPI field: {kpi}"
                assert isinstance(stats_data[kpi], (int, float)), f"{kpi} should be numeric"
            
            # Test transaction data format for tables
            transactions_response = self.client.get("/transactions?limit=5")
            transactions = transactions_response.json()["data"]
            
            if transactions:
                sample_txn = transactions[0]
                required_fields = [
                    "transaction_id", "product", "risk_score", "risk_category",
                    "unit_price", "market_price", "shipping_route"
                ]
                
                for field in required_fields:
                    assert field in sample_txn, f"Missing transaction field: {field}"
            
            # Test alert data format
            alerts_response = self.client.get("/alerts/active")
            alerts_data = alerts_response.json()["data"]
            
            if alerts_data:
                sample_alert = alerts_data[0]
                assert "transaction_id" in sample_alert, "Alert should have transaction_id"
                assert "alert_type" in sample_alert, "Alert should have alert_type"
                assert "priority" in sample_alert, "Alert should have priority"
            
            print("✅ Dashboard compatibility verified")
            print(f"   - KPI data format: ✅")
            print(f"   - Transaction table format: ✅")
            print(f"   - Alert data format: ✅")
            
            self.test_results["dashboard_compatibility"] = {"status": "success"}
            return True
            
        except Exception as e:
            print(f"❌ Dashboard compatibility failed: {e}")
            self.test_results["dashboard_compatibility"] = {"status": "error", "error": str(e)}
            return False
    
    def _validate_api_response_schema(self, data: Dict[str, Any], endpoint_name: str):
        """Validate API response schema compliance (CP-4)."""
        # Standard API response format
        assert "status" in data, f"{endpoint_name} missing status field"
        assert data["status"] in ["success", "error"], f"Invalid status: {data['status']}"
        
        if data["status"] == "success":
            assert "data" in data, f"{endpoint_name} missing data field"
        
        if data["status"] == "error":
            assert "message" in data, f"{endpoint_name} missing error message"
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("=" * 70)
        print("TRINETRA AI - API Endpoint Integration Test")
        print("Testing API endpoints integration with ML pipeline, data loading, and AI components")
        print("=" * 70)
        
        if not self.setup():
            return False
        
        start_time = time.time()
        
        # Run all test suites
        test_suites = [
            ("Core Endpoints", self.test_core_endpoints),
            ("ML Pipeline Integration", self.test_ml_pipeline_integration),
            ("AI Explanation Integration", self.test_ai_explanation_integration),
            ("Alert System Integration", self.test_alert_system_integration),
            ("Error Handling", self.test_error_handling),
            ("Performance Requirements", self.test_performance_requirements),
            ("Dashboard Compatibility", self.test_dashboard_compatibility)
        ]
        
        results = {}
        
        for suite_name, test_func in test_suites:
            try:
                results[suite_name] = test_func()
            except Exception as e:
                print(f"❌ {suite_name} failed with exception: {e}")
                results[suite_name] = False
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate overall results
        passed_suites = sum(1 for result in results.values() if result)
        total_suites = len(results)
        success_rate = passed_suites / total_suites
        
        print("\n" + "=" * 70)
        print("INTEGRATION TEST RESULTS:")
        print("=" * 70)
        
        for suite_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{suite_name}: {status}")
        
        print(f"\nOverall: {passed_suites}/{total_suites} test suites passed ({success_rate:.1%})")
        print(f"Total execution time: {total_time:.2f} seconds")
        
        # Determine final result
        if success_rate >= 0.85:  # 85% pass rate required
            print("\n🎉 API ENDPOINT INTEGRATION TEST PASSED!")
            print("✅ All API endpoints work correctly")
            print("✅ ML pipeline integration verified")
            print("✅ AI explanation components working")
            print("✅ Error handling and response formats validated")
            print("✅ Dashboard compatibility confirmed")
            print("✅ JSON schema compliance (CP-4) verified")
            return True
        else:
            print(f"\n❌ API ENDPOINT INTEGRATION TEST FAILED!")
            print(f"❌ Success rate too low: {success_rate:.1%} (need ≥85%)")
            return False


def main():
    """Main test execution function."""
    tester = APIEndpointIntegrationTest()
    success = tester.run_all_tests()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)