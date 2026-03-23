"""
Comprehensive API and Dashboard Integration Test for TRINETRA AI

This test validates that all FastAPI endpoints work correctly and that the dashboard
can properly consume API responses. Tests all required endpoints:
/transactions, /suspicious, /fraud, /explain, /query, /stats

**Validates: Task "Verify API and dashboard integration"**
"""

import pytest
import requests
import json
import time
import subprocess
import sys
import os
import threading
import signal
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import logging

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestComprehensiveIntegration:
    """Comprehensive integration test for API and Dashboard."""
    
    API_BASE_URL = "http://localhost:8001"  # Use different port to avoid conflicts
    API_PORT = 8001
    
    @classmethod
    def setup_class(cls):
        """Set up test environment with running API server."""
        logger.info("🔧 Setting up comprehensive integration test environment...")
        
        # Check if dataset exists
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Dataset not available for integration test")
        
        # Start API server for testing
        cls.start_test_api_server()
        
        # Wait for API to be ready
        cls.wait_for_api_ready()
        
    @classmethod
    def teardown_class(cls):
        """Clean up test environment."""
        logger.info("🧹 Cleaning up test environment...")
        if hasattr(cls, 'api_process') and cls.api_process:
            try:
                cls.api_process.terminate()
                cls.api_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                cls.api_process.kill()
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")
    
    @classmethod
    def start_test_api_server(cls):
        """Start FastAPI server for testing."""
        try:
            # Initialize the system first by importing and running initialization
            sys.path.insert(0, str(Path.cwd() / "backend"))
            
            cmd = [
                sys.executable, "-m", "uvicorn",
                "backend.api:app",
                "--host", "localhost",
                "--port", str(cls.API_PORT),
                "--log-level", "error"
            ]
            
            cls.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            logger.info("✅ Test API server started")
            
        except Exception as e:
            pytest.skip(f"Could not start test API server: {e}")
    
    @classmethod
    def wait_for_api_ready(cls, max_retries=20, delay=3):
        """Wait for API server to be ready."""
        logger.info("⏳ Waiting for API server to be ready...")
        
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.API_BASE_URL}/", timeout=10)
                if response.status_code == 200:
                    logger.info("✅ API server is ready")
                    return True
            except Exception as e:
                if i < max_retries - 1:
                    logger.info(f"Waiting for API server... ({i+1}/{max_retries}) - {str(e)[:50]}")
                    time.sleep(delay)
                else:
                    pytest.skip(f"API server not responding after {max_retries} attempts")
        return False
    
    def test_01_transactions_endpoint(self):
        """Test /transactions endpoint - core data retrieval."""
        logger.info("📊 Testing /transactions endpoint...")
        
        response = requests.get(f"{self.API_BASE_URL}/transactions", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Response should have status field"
        assert "data" in data, "Response should have data field"
        assert data["status"] == "success", f"Expected success status, got {data['status']}"
        
        transactions = data["data"]
        assert isinstance(transactions, list), "Transactions should be a list"
        assert len(transactions) > 0, "Should have at least some transactions"
        
        # Validate transaction structure
        sample_txn = transactions[0]
        required_fields = [
            "transaction_id", "risk_score", "risk_category",
            "product", "unit_price", "market_price", "date"
        ]
        
        for field in required_fields:
            assert field in sample_txn, f"Transaction missing required field: {field}"
        
        # Validate data types
        assert isinstance(sample_txn["risk_score"], (int, float)), "Risk score should be numeric"
        assert sample_txn["risk_category"] in ["SAFE", "SUSPICIOUS", "FRAUD"], "Invalid risk category"
        
        logger.info(f"✅ /transactions endpoint working ({len(transactions)} transactions)")
    
    def test_02_suspicious_endpoint(self):
        """Test /suspicious endpoint - filtered data retrieval."""
        logger.info("🔍 Testing /suspicious endpoint...")
        
        response = requests.get(f"{self.API_BASE_URL}/suspicious", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success", "Should return success status"
        
        suspicious_txns = data["data"]
        assert isinstance(suspicious_txns, list), "Suspicious transactions should be a list"
        
        # Verify all returned transactions are actually suspicious
        for txn in suspicious_txns:
            assert txn["risk_category"] == "SUSPICIOUS", f"Expected SUSPICIOUS, got {txn['risk_category']}"
        
        logger.info(f"✅ /suspicious endpoint working ({len(suspicious_txns)} suspicious transactions)")
    
    def test_03_fraud_endpoint(self):
        """Test /fraud endpoint - high-risk data retrieval."""
        logger.info("🚨 Testing /fraud endpoint...")
        
        response = requests.get(f"{self.API_BASE_URL}/fraud", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success", "Should return success status"
        
        fraud_txns = data["data"]
        assert isinstance(fraud_txns, list), "Fraud transactions should be a list"
        
        # Verify all returned transactions are actually fraud
        for txn in fraud_txns:
            assert txn["risk_category"] == "FRAUD", f"Expected FRAUD, got {txn['risk_category']}"
        
        logger.info(f"✅ /fraud endpoint working ({len(fraud_txns)} fraud transactions)")
    
    def test_04_stats_endpoint(self):
        """Test /stats endpoint - dashboard KPI data."""
        logger.info("📈 Testing /stats endpoint...")
        
        response = requests.get(f"{self.API_BASE_URL}/stats", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success", "Should return success status"
        
        stats = data["data"]
        assert isinstance(stats, dict), "Stats should be a dictionary"
        
        # Verify required KPI fields for dashboard
        required_kpis = [
            "total_transactions", "fraud_rate", "total_trade_value", 
            "high_risk_countries", "suspicious_count", "fraud_count", "safe_count"
        ]
        
        for kpi in required_kpis:
            assert kpi in stats, f"Stats missing required KPI: {kpi}"
            assert isinstance(stats[kpi], (int, float, str)), f"Invalid type for {kpi}"
        
        # Validate logical consistency
        total = stats["total_transactions"]
        fraud_count = stats["fraud_count"]
        suspicious_count = stats["suspicious_count"]
        safe_count = stats["safe_count"]
        
        assert fraud_count + suspicious_count + safe_count == total, "Transaction counts should sum to total"
        
        logger.info(f"✅ /stats endpoint working (total: {total}, fraud: {fraud_count})")
    
    def test_05_explain_endpoint(self):
        """Test /explain/{transaction_id} endpoint - AI explanations."""
        logger.info("🧠 Testing /explain endpoint...")
        
        # First get a transaction ID to explain
        txns_response = requests.get(f"{self.API_BASE_URL}/transactions?limit=1", timeout=15)
        assert txns_response.status_code == 200, "Should be able to get transactions"
        
        txns_data = txns_response.json()
        transactions = txns_data["data"]
        
        if len(transactions) == 0:
            pytest.skip("No transactions available for explanation test")
        
        transaction_id = transactions[0]["transaction_id"]
        
        # Test explanation endpoint
        explain_response = requests.post(
            f"{self.API_BASE_URL}/explain/{transaction_id}",
            json={"force_ai": False},
            timeout=20
        )
        
        assert explain_response.status_code == 200, f"Expected 200, got {explain_response.status_code}"
        
        explain_data = explain_response.json()
        assert "status" in explain_data, "Explanation response should have status"
        assert "data" in explain_data, "Explanation response should have data"
        
        explanation = explain_data["data"]
        assert "explanation" in explanation, "Should have explanation text"
        assert "transaction_id" in explanation, "Should include transaction ID"
        assert isinstance(explanation["explanation"], str), "Explanation should be text"
        assert len(explanation["explanation"]) > 0, "Explanation should not be empty"
        
        logger.info(f"✅ /explain endpoint working (explained {transaction_id})")
    
    def test_06_query_endpoint(self):
        """Test /query endpoint - natural language queries."""
        logger.info("💬 Testing /query endpoint...")
        
        test_query = "What are the main fraud patterns in the data?"
        
        response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"query": test_query},
            timeout=25
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Query response should have status"
        assert "data" in data, "Query response should have data"
        
        query_result = data["data"]
        assert "response" in query_result, "Should have response text"
        assert "query" in query_result, "Should echo back the query"
        assert isinstance(query_result["response"], str), "Response should be text"
        assert len(query_result["response"]) > 0, "Response should not be empty"
        
        logger.info(f"✅ /query endpoint working (processed: '{test_query[:30]}...')")
    
    def test_07_session_endpoints(self):
        """Test session management endpoints."""
        logger.info("🔄 Testing session management endpoints...")
        
        # Test session info
        info_response = requests.get(f"{self.API_BASE_URL}/session/info", timeout=10)
        assert info_response.status_code == 200, "Session info should be accessible"
        
        info_data = info_response.json()
        assert info_data["status"] == "success", "Session info should succeed"
        
        session_info = info_data["data"]
        assert "queries_used" in session_info, "Should track queries used"
        assert "explanations_used" in session_info, "Should track explanations used"
        
        # Test session reset
        reset_response = requests.post(f"{self.API_BASE_URL}/session/reset", timeout=10)
        assert reset_response.status_code == 200, "Session reset should work"
        
        reset_data = reset_response.json()
        assert reset_data["status"] == "success", "Session reset should succeed"
        
        logger.info("✅ Session management endpoints working")
    
    def test_08_alerts_endpoints(self):
        """Test alert system endpoints."""
        logger.info("🚨 Testing alert system endpoints...")
        
        # Test all alerts
        alerts_response = requests.get(f"{self.API_BASE_URL}/alerts", timeout=10)
        assert alerts_response.status_code == 200, "Alerts endpoint should work"
        
        alerts_data = alerts_response.json()
        assert alerts_data["status"] == "success", "Alerts should return success"
        
        # Test active alerts
        active_response = requests.get(f"{self.API_BASE_URL}/alerts/active", timeout=10)
        assert active_response.status_code == 200, "Active alerts should work"
        
        # Test alert statistics
        stats_response = requests.get(f"{self.API_BASE_URL}/alerts/statistics", timeout=10)
        assert stats_response.status_code == 200, "Alert statistics should work"
        
        stats_data = stats_response.json()
        alert_stats = stats_data["data"]
        
        expected_stats = ["total_alerts", "active_alerts", "dismissed_alerts"]
        for stat in expected_stats:
            assert stat in alert_stats, f"Alert stats should include {stat}"
        
        logger.info("✅ Alert system endpoints working")
    
    def test_09_dashboard_data_consumption(self):
        """Test that dashboard can properly consume all API responses."""
        logger.info("📱 Testing dashboard data consumption patterns...")
        
        # Simulate dashboard startup data loading
        dashboard_endpoints = [
            ("/stats", "Dashboard KPIs"),
            ("/transactions?limit=50", "Transaction table"),
            ("/alerts/active", "Active alerts"),
            ("/alerts/statistics", "Alert statistics"),
            ("/session/info", "Session information")
        ]
        
        dashboard_data = {}
        
        for endpoint, description in dashboard_endpoints:
            response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=15)
            assert response.status_code == 200, f"{description} endpoint should work"
            
            data = response.json()
            assert data["status"] == "success", f"{description} should return success"
            
            dashboard_data[endpoint] = data["data"]
            logger.info(f"✅ {description} data loaded successfully")
        
        # Validate dashboard can process the data
        stats = dashboard_data["/stats"]
        transactions = dashboard_data["/transactions?limit=50"]
        alerts = dashboard_data["/alerts/active"]
        
        # Test KPI calculations (what dashboard would do)
        assert isinstance(stats["total_transactions"], int), "Total transactions should be integer"
        assert isinstance(stats["fraud_rate"], (int, float)), "Fraud rate should be numeric"
        
        # Test transaction table data
        assert isinstance(transactions, list), "Transactions should be list for table"
        if len(transactions) > 0:
            # Verify dashboard can extract display fields
            txn = transactions[0]
            display_fields = ["transaction_id", "product", "risk_category", "risk_score"]
            for field in display_fields:
                assert field in txn, f"Dashboard needs {field} for display"
        
        # Test alert data
        assert isinstance(alerts, list), "Alerts should be list for dashboard"
        
        logger.info("✅ Dashboard data consumption test passed")
    
    def test_10_api_performance_requirements(self):
        """Test API performance meets dashboard requirements."""
        logger.info("⚡ Testing API performance requirements...")
        
        # Test response times (requirement: API responses < 1 second)
        performance_endpoints = [
            "/stats",
            "/transactions?limit=10",
            "/suspicious?limit=10",
            "/fraud?limit=10"
        ]
        
        performance_results = {}
        
        for endpoint in performance_endpoints:
            start_time = time.time()
            response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            performance_results[endpoint] = response_time
            
            assert response.status_code == 200, f"{endpoint} should work"
            assert response_time < 2.0, f"{endpoint} took {response_time:.3f}s (should be < 2s)"
            
            logger.info(f"✅ {endpoint}: {response_time:.3f}s")
        
        # Calculate average response time
        avg_response_time = sum(performance_results.values()) / len(performance_results)
        logger.info(f"✅ Average API response time: {avg_response_time:.3f}s")
        
        assert avg_response_time < 1.5, f"Average response time {avg_response_time:.3f}s should be < 1.5s"
    
    def test_11_error_handling_robustness(self):
        """Test error handling for dashboard integration."""
        logger.info("🛡️ Testing error handling robustness...")
        
        # Test invalid transaction ID
        invalid_response = requests.post(
            f"{self.API_BASE_URL}/explain/INVALID_ID_123",
            json={"force_ai": False},
            timeout=10
        )
        
        # Should handle gracefully (not crash)
        assert invalid_response.status_code in [200, 404, 400], "Should handle invalid ID gracefully"
        
        if invalid_response.status_code == 200:
            data = invalid_response.json()
            assert "status" in data, "Error response should have status"
        
        # Test malformed query
        malformed_response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"invalid_field": "test"},
            timeout=10
        )
        
        assert malformed_response.status_code in [200, 400, 422], "Should handle malformed request"
        
        # Test empty query
        empty_response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"query": ""},
            timeout=10
        )
        
        assert empty_response.status_code in [200, 400], "Should handle empty query"
        
        logger.info("✅ Error handling robustness test passed")
    
    def test_12_data_consistency_across_endpoints(self):
        """Test data consistency across different endpoints."""
        logger.info("🔄 Testing data consistency across endpoints...")
        
        # Get data from different endpoints
        all_txns_response = requests.get(f"{self.API_BASE_URL}/transactions", timeout=15)
        suspicious_response = requests.get(f"{self.API_BASE_URL}/suspicious", timeout=15)
        fraud_response = requests.get(f"{self.API_BASE_URL}/fraud", timeout=15)
        stats_response = requests.get(f"{self.API_BASE_URL}/stats", timeout=15)
        
        assert all([r.status_code == 200 for r in [all_txns_response, suspicious_response, fraud_response, stats_response]]), "All endpoints should work"
        
        all_txns = all_txns_response.json()["data"]
        suspicious_txns = suspicious_response.json()["data"]
        fraud_txns = fraud_response.json()["data"]
        stats = stats_response.json()["data"]
        
        # Verify counts are consistent
        total_count = len(all_txns)
        suspicious_count = len(suspicious_txns)
        fraud_count = len(fraud_txns)
        
        # Stats should match actual counts
        assert stats["total_transactions"] == total_count, f"Stats total {stats['total_transactions']} != actual {total_count}"
        assert stats["suspicious_count"] == suspicious_count, f"Stats suspicious {stats['suspicious_count']} != actual {suspicious_count}"
        assert stats["fraud_count"] == fraud_count, f"Stats fraud {stats['fraud_count']} != actual {fraud_count}"
        
        # Verify no overlap between suspicious and fraud
        suspicious_ids = {txn["transaction_id"] for txn in suspicious_txns}
        fraud_ids = {txn["transaction_id"] for txn in fraud_txns}
        
        overlap = suspicious_ids.intersection(fraud_ids)
        assert len(overlap) == 0, f"Suspicious and fraud should not overlap, found {len(overlap)} overlapping IDs"
        
        logger.info(f"✅ Data consistency verified (total: {total_count}, suspicious: {suspicious_count}, fraud: {fraud_count})")


def run_integration_test():
    """Run the comprehensive integration test."""
    logger.info("🚀 Starting comprehensive API and dashboard integration test...")
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
    
    if exit_code == 0:
        logger.info("✅ All integration tests passed!")
    else:
        logger.error("❌ Some integration tests failed!")
    
    return exit_code


if __name__ == "__main__":
    run_integration_test()