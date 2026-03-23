#!/usr/bin/env python3
"""
Focused Dashboard Component Integration Test for TRINETRA AI

This test validates dashboard component integration with the FastAPI backend
without requiring a full system startup. Tests individual dashboard sections
and their API integration patterns.

**Validates: Task 12.2 Integration Testing - Test dashboard component integration**
"""

import sys
import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.data_loader import load_dataset, validate_schema
    from backend.feature_engineering import engineer_features
    from backend.model import train_model, save_model, load_model
    from backend.fraud_detection import score_transactions, classify_risk
    from backend.api import app
    from fastapi.testclient import TestClient
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all backend modules are available")
    sys.exit(1)


class TestDashboardComponentIntegration:
    """Focused integration tests for dashboard components."""
    
    def __init__(self):
        """Initialize test client and prepare test data."""
        # Initialize the API system before creating test client
        from backend.api import initialize_system
        initialize_system()
        
        self.client = TestClient(app)
        self.test_data = None
        self.setup_test_data()
    
    def setup_test_data(self):
        """Set up test data for integration tests."""
        print("🔧 Setting up test data for dashboard integration...")
        
        try:
            # The system is already initialized in __init__, so we can get the data
            from backend.api import _transactions_df
            
            if _transactions_df is not None and not _transactions_df.empty:
                self.test_data = _transactions_df
                print(f"✅ Test data prepared: {len(_transactions_df)} transactions")
                return True
            else:
                print("❌ No transaction data available from API initialization")
                return False
            
        except Exception as e:
            print(f"❌ Error setting up test data: {e}")
            return False
    
    def test_1_api_connectivity(self):
        """Test 1: Basic API connectivity for dashboard."""
        print("\n📡 Test 1: API Connectivity...")
        
        try:
            response = self.client.get("/")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert "message" in data, "Response should contain message"
            
            print("✅ API connectivity test passed")
            return True
            
        except Exception as e:
            print(f"❌ API connectivity test failed: {e}")
            return False
    
    def test_2_kpi_metrics_endpoint(self):
        """Test 2: KPI metrics endpoint for dashboard overview."""
        print("\n📊 Test 2: KPI Metrics Endpoint...")
        
        try:
            response = self.client.get("/stats")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert data["status"] == "success", "Stats should return success status"
            
            stats = data["data"]
            
            # Verify all KPI fields required by dashboard
            required_fields = [
                "total_transactions", "fraud_rate", "total_trade_value", 
                "high_risk_countries", "suspicious_count", "fraud_count"
            ]
            
            for field in required_fields:
                assert field in stats, f"Missing required KPI field: {field}"
                assert isinstance(stats[field], (int, float)), f"KPI field {field} should be numeric"
            
            # Verify reasonable values
            assert stats["total_transactions"] > 0, "Should have transactions"
            assert 0 <= stats["fraud_rate"] <= 100, "Fraud rate should be percentage"
            assert stats["total_trade_value"] > 0, "Should have trade value"
            
            print(f"✅ KPI metrics test passed - {stats['total_transactions']} transactions, {stats['fraud_rate']:.1f}% fraud rate")
            return True
            
        except Exception as e:
            print(f"❌ KPI metrics test failed: {e}")
            return False
    
    def test_3_fraud_alerts_endpoint(self):
        """Test 3: Fraud alerts endpoint for dashboard alerts section."""
        print("\n🚨 Test 3: Fraud Alerts Endpoint...")
        
        try:
            response = self.client.get("/fraud")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert data["status"] == "success", "Fraud endpoint should return success"
            
            fraud_transactions = data["data"]
            assert isinstance(fraud_transactions, list), "Fraud data should be a list"
            
            if fraud_transactions:
                # Verify fraud transaction structure
                fraud_tx = fraud_transactions[0]
                required_fields = ["transaction_id", "risk_score", "risk_category"]
                
                for field in required_fields:
                    assert field in fraud_tx, f"Missing field in fraud transaction: {field}"
                
                assert fraud_tx["risk_category"] == "FRAUD", "Should only return FRAUD transactions"
                
                print(f"✅ Fraud alerts test passed - {len(fraud_transactions)} fraud cases found")
            else:
                print("✅ Fraud alerts test passed - no fraud cases (acceptable)")
            
            return True
            
        except Exception as e:
            print(f"❌ Fraud alerts test failed: {e}")
            return False
    
    def test_4_transactions_endpoint(self):
        """Test 4: Transactions endpoint for dashboard table."""
        print("\n📋 Test 4: Transactions Endpoint...")
        
        try:
            # Test basic transactions endpoint
            response = self.client.get("/transactions")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert data["status"] == "success", "Transactions should return success"
            
            transactions = data["data"]
            assert isinstance(transactions, list), "Transactions should be a list"
            assert len(transactions) > 0, "Should have transactions"
            
            # Verify transaction structure for dashboard table
            tx = transactions[0]
            required_fields = [
                "transaction_id", "product", "unit_price", "market_price", 
                "price_deviation", "risk_score", "risk_category"
            ]
            
            for field in required_fields:
                assert field in tx, f"Missing field in transaction: {field}"
            
            # Test pagination (dashboard table feature)
            response_paginated = self.client.get("/transactions?limit=10&offset=0")
            assert response_paginated.status_code == 200, "Pagination should work"
            
            paginated_data = response_paginated.json()["data"]
            assert len(paginated_data) <= 10, "Pagination limit should be respected"
            
            print(f"✅ Transactions endpoint test passed - {len(transactions)} total transactions")
            return True
            
        except Exception as e:
            print(f"❌ Transactions endpoint test failed: {e}")
            return False
    
    def test_5_explanation_endpoint(self):
        """Test 5: Explanation endpoint for dashboard AI assistant."""
        print("\n🤖 Test 5: Explanation Endpoint...")
        
        try:
            # Get a transaction to explain
            response = self.client.get("/transactions?limit=1")
            transactions = response.json()["data"]
            
            if not transactions:
                print("⚠️ No transactions available for explanation test")
                return True
            
            tx_id = transactions[0]["transaction_id"]
            
            # Test explanation endpoint
            response = self.client.post(f"/explain/{tx_id}")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert data["status"] == "success", "Explanation should return success"
            
            explanation_data = data["data"]
            assert "explanation" in explanation_data, "Should contain explanation"
            assert "transaction_id" in explanation_data, "Should contain transaction ID"
            
            explanation = explanation_data["explanation"]
            assert isinstance(explanation, str), "Explanation should be string"
            assert len(explanation) > 0, "Explanation should not be empty"
            
            print(f"✅ Explanation endpoint test passed - explanation generated for {tx_id}")
            return True
            
        except Exception as e:
            print(f"❌ Explanation endpoint test failed: {e}")
            return False
    
    def test_6_query_endpoint(self):
        """Test 6: Query endpoint for dashboard AI assistant."""
        print("\n💬 Test 6: Query Endpoint...")
        
        try:
            # Test natural language query
            test_query = "How many suspicious transactions are there?"
            
            response = self.client.post("/query", json={"query": test_query})
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert data["status"] == "success", "Query should return success"
            
            query_data = data["data"]
            assert "response" in query_data, "Should contain response"
            assert "query" in query_data, "Should contain original query"
            
            response_text = query_data["response"]
            assert isinstance(response_text, str), "Response should be string"
            assert len(response_text) > 0, "Response should not be empty"
            
            print(f"✅ Query endpoint test passed - query processed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Query endpoint test failed: {e}")
            return False
    
    def test_7_session_management_endpoint(self):
        """Test 7: Session management for dashboard quota system."""
        print("\n🔐 Test 7: Session Management...")
        
        try:
            # Test session info endpoint
            response = self.client.get("/session/info")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert data["status"] == "success", "Session info should return success"
            
            session_data = data["data"]
            required_fields = ["explanations_used", "queries_used", "explanations_remaining", "queries_remaining"]
            
            for field in required_fields:
                assert field in session_data, f"Missing session field: {field}"
                assert isinstance(session_data[field], int), f"Session field {field} should be integer"
            
            # Test session reset endpoint
            response = self.client.post("/session/reset")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            reset_data = response.json()
            assert reset_data["status"] == "success", "Session reset should return success"
            
            print("✅ Session management test passed")
            return True
            
        except Exception as e:
            print(f"❌ Session management test failed: {e}")
            return False
    
    def test_8_error_handling(self):
        """Test 8: Error handling for dashboard robustness."""
        print("\n🛡️ Test 8: Error Handling...")
        
        try:
            # Test invalid transaction ID for explanation
            response = self.client.post("/explain/INVALID_ID")
            assert response.status_code in [404, 400], "Should handle invalid transaction ID"
            
            # Test invalid query format
            response = self.client.post("/query", json={})
            assert response.status_code == 422, "Should validate query format"
            
            # Test invalid endpoint
            response = self.client.get("/invalid_endpoint")
            assert response.status_code == 404, "Should return 404 for invalid endpoints"
            
            print("✅ Error handling test passed")
            return True
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
    
    def test_9_data_consistency(self):
        """Test 9: Data consistency across dashboard components."""
        print("\n🔄 Test 9: Data Consistency...")
        
        try:
            # Get stats
            stats_response = self.client.get("/stats")
            stats = stats_response.json()["data"]
            
            # Get all transactions
            tx_response = self.client.get("/transactions")
            transactions = tx_response.json()["data"]
            
            # Get suspicious transactions
            suspicious_response = self.client.get("/suspicious")
            suspicious = suspicious_response.json()["data"]
            
            # Get fraud transactions
            fraud_response = self.client.get("/fraud")
            fraud = fraud_response.json()["data"]
            
            # Verify consistency
            assert stats["total_transactions"] == len(transactions), "Transaction count should match"
            assert stats["suspicious_count"] == len(suspicious), "Suspicious count should match"
            assert stats["fraud_count"] == len(fraud), "Fraud count should match"
            
            # Verify risk categories
            fraud_from_all = [tx for tx in transactions if tx["risk_category"] == "FRAUD"]
            assert len(fraud_from_all) == len(fraud), "Fraud transactions should be consistent"
            
            suspicious_from_all = [tx for tx in transactions if tx["risk_category"] == "SUSPICIOUS"]
            assert len(suspicious_from_all) == len(suspicious), "Suspicious transactions should be consistent"
            
            print("✅ Data consistency test passed")
            return True
            
        except Exception as e:
            print(f"❌ Data consistency test failed: {e}")
            return False
    
    def test_10_performance_benchmarks(self):
        """Test 10: Performance benchmarks for dashboard responsiveness."""
        print("\n⚡ Test 10: Performance Benchmarks...")
        
        try:
            # Test API response times (dashboard requirement: <1 second)
            endpoints_to_test = [
                "/stats",
                "/transactions?limit=100",
                "/suspicious",
                "/fraud"
            ]
            
            for endpoint in endpoints_to_test:
                start_time = time.time()
                response = self.client.get(endpoint)
                end_time = time.time()
                
                response_time = end_time - start_time
                assert response.status_code == 200, f"Endpoint {endpoint} should be accessible"
                assert response_time < 1.0, f"Endpoint {endpoint} took {response_time:.2f}s (should be <1s)"
                
                print(f"   📊 {endpoint}: {response_time:.3f}s")
            
            print("✅ Performance benchmarks test passed")
            return True
            
        except Exception as e:
            print(f"❌ Performance benchmarks test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all dashboard integration tests."""
        print("🧪 Running Dashboard Component Integration Tests...")
        print("=" * 70)
        
        if not self.test_data is not None:
            print("❌ Test data setup failed - cannot run integration tests")
            return False
        
        tests = [
            self.test_1_api_connectivity,
            self.test_2_kpi_metrics_endpoint,
            self.test_3_fraud_alerts_endpoint,
            self.test_4_transactions_endpoint,
            self.test_5_explanation_endpoint,
            self.test_6_query_endpoint,
            self.test_7_session_management_endpoint,
            self.test_8_error_handling,
            self.test_9_data_consistency,
            self.test_10_performance_benchmarks
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
                failed += 1
        
        print("\n" + "=" * 70)
        print(f"📊 Dashboard Integration Test Results:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
        
        if failed == 0:
            print("\n🎉 All dashboard component integration tests passed!")
            print("✅ Dashboard is ready for production use")
            return True
        else:
            print(f"\n⚠️ {failed} test(s) failed - dashboard integration needs attention")
            return False


def run_focused_integration_tests():
    """Main function to run focused dashboard integration tests."""
    print("=" * 80)
    print("🔍 TRINETRA AI - Focused Dashboard Component Integration Test")
    print("=" * 80)
    
    test_instance = TestDashboardComponentIntegration()
    
    success = test_instance.run_all_tests()
    
    print("\n" + "=" * 80)
    if success:
        print("🎯 Dashboard component integration validation: PASSED")
        print("✅ All dashboard sections properly integrate with FastAPI backend")
    else:
        print("❌ Dashboard component integration validation: FAILED")
        print("⚠️ Some dashboard components need attention")
    
    return success


if __name__ == "__main__":
    success = run_focused_integration_tests()
    sys.exit(0 if success else 1)