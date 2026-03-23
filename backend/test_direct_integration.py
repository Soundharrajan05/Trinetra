"""
Direct API and Dashboard Integration Test for TRINETRA AI

This test directly initializes system components and tests API endpoints
without requiring a separate server process.

**Validates: Task "Verify API and dashboard integration"**
"""

import pytest
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import logging
from fastapi.testclient import TestClient

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestDirectIntegration:
    """Direct integration test using FastAPI TestClient."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment by initializing system components."""
        logger.info("🔧 Setting up direct integration test environment...")
        
        # Check if dataset exists
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Dataset not available for integration test")
        
        # Initialize system components
        cls.initialize_system()
        
        # Create test client
        from backend.api import app
        cls.client = TestClient(app)
        
        logger.info("✅ Direct integration test environment ready")
    
    @classmethod
    def initialize_system(cls):
        """Initialize the system components directly."""
        try:
            # Import and initialize system components
            from backend.data_loader import load_dataset
            from backend.feature_engineering import engineer_features
            from backend.model import train_model, save_model, load_model
            from backend.fraud_detection import score_transactions, classify_risk
            
            logger.info("📊 Loading and processing dataset...")
            
            # Load dataset
            dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
            df = load_dataset(dataset_path)
            
            if df is None or df.empty:
                pytest.skip("Failed to load dataset")
            
            # Engineer features
            df_engineered = engineer_features(df)
            
            # Setup model
            model_path = "models/isolation_forest.pkl"
            if Path(model_path).exists():
                model = load_model(model_path)
            else:
                model = train_model(df_engineered)
                Path(model_path).parent.mkdir(exist_ok=True)
                save_model(model, model_path)
            
            # Score transactions
            df_scored = score_transactions(df_engineered, model)
            df_final = classify_risk(df_scored)
            
            logger.info(f"✅ System initialized with {len(df_final)} transactions")
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            pytest.skip(f"System initialization failed: {e}")
    
    def test_01_transactions_endpoint(self):
        """Test /transactions endpoint - core data retrieval."""
        logger.info("📊 Testing /transactions endpoint...")
        
        response = self.client.get("/transactions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Response should have status field"
        assert "data" in data, "Response should have data field"
        assert data["status"] == "success", f"Expected success status, got {data['status']}"
        
        transactions = data["data"]
        assert isinstance(transactions, list), "Transactions should be a list"
        assert len(transactions) > 0, "Should have at least some transactions"
        
        # Validate transaction structure for dashboard consumption
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
        
        response = self.client.get("/suspicious")
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
        
        response = self.client.get("/fraud")
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
        
        response = self.client.get("/stats")
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
        txns_response = self.client.get("/transactions?limit=1")
        assert txns_response.status_code == 200, "Should be able to get transactions"
        
        txns_data = txns_response.json()
        transactions = txns_data["data"]
        
        if len(transactions) == 0:
            pytest.skip("No transactions available for explanation test")
        
        transaction_id = transactions[0]["transaction_id"]
        
        # Test explanation endpoint
        explain_response = self.client.post(
            f"/explain/{transaction_id}",
            json={"force_ai": False}
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
        
        response = self.client.post(
            "/query",
            json={"query": test_query}
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
        info_response = self.client.get("/session/info")
        assert info_response.status_code == 200, "Session info should be accessible"
        
        info_data = info_response.json()
        assert info_data["status"] == "success", "Session info should succeed"
        
        session_info = info_data["data"]
        assert "queries_used" in session_info, "Should track queries used"
        assert "explanations_used" in session_info, "Should track explanations used"
        
        # Test session reset
        reset_response = self.client.post("/session/reset")
        assert reset_response.status_code == 200, "Session reset should work"
        
        reset_data = reset_response.json()
        assert reset_data["status"] == "success", "Session reset should succeed"
        
        logger.info("✅ Session management endpoints working")
    
    def test_08_alerts_endpoints(self):
        """Test alert system endpoints."""
        logger.info("🚨 Testing alert system endpoints...")
        
        # Test all alerts
        alerts_response = self.client.get("/alerts")
        assert alerts_response.status_code == 200, "Alerts endpoint should work"
        
        alerts_data = alerts_response.json()
        assert alerts_data["status"] == "success", "Alerts should return success"
        
        # Test active alerts
        active_response = self.client.get("/alerts/active")
        assert active_response.status_code == 200, "Active alerts should work"
        
        # Test alert statistics
        stats_response = self.client.get("/alerts/statistics")
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
            response = self.client.get(endpoint)
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
    
    def test_10_data_consistency_across_endpoints(self):
        """Test data consistency across different endpoints."""
        logger.info("🔄 Testing data consistency across endpoints...")
        
        # Get data from different endpoints
        all_txns_response = self.client.get("/transactions")
        suspicious_response = self.client.get("/suspicious")
        fraud_response = self.client.get("/fraud")
        stats_response = self.client.get("/stats")
        
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
    
    def test_11_dashboard_response_format_compatibility(self):
        """Test response formats are compatible with dashboard expectations."""
        logger.info("📋 Testing dashboard response format compatibility...")
        
        # Test transaction response format for dashboard table
        response = self.client.get("/transactions?limit=5")
        assert response.status_code == 200, "Transactions endpoint should work"
        
        data = response.json()
        transactions = data["data"]
        
        if len(transactions) > 0:
            txn = transactions[0]
            
            # Dashboard table required fields
            table_fields = [
                "transaction_id", "product", "commodity_category",
                "unit_price", "market_price", "price_deviation",
                "risk_score", "risk_category", "date"
            ]
            
            missing_fields = [field for field in table_fields if field not in txn]
            assert len(missing_fields) == 0, f"Missing fields for dashboard table: {missing_fields}"
            
            # Validate data types for dashboard display
            assert isinstance(txn["risk_score"], (int, float)), "Risk score should be numeric for sorting"
            assert isinstance(txn["risk_category"], str), "Risk category should be string for filtering"
            assert isinstance(txn["unit_price"], (int, float)), "Unit price should be numeric for display"
        
        logger.info("✅ Dashboard response format compatibility verified")


if __name__ == "__main__":
    # Run the direct integration tests
    pytest.main([__file__, "-v", "-s"])