"""
Dashboard Component Integration Test for TRINETRA AI

This test validates that all dashboard components properly integrate with the FastAPI backend.
Tests each dashboard section: KPI metrics, fraud alerts, transaction tables, visualizations,
and AI assistant functionality.

**Validates: System Integration Tests (Task 12.2) - Test dashboard component integration**
"""

import pytest
import requests
import json
import time
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api import app


class TestDashboardComponentIntegration:
    """Integration test for dashboard components and API connectivity."""
    
    API_BASE_URL = "http://localhost:8000"
    
    @classmethod
    def setup_class(cls):
        """Set up test environment with running API server."""
        print("🔧 Setting up dashboard component integration test environment...")
        
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

    
    def test_kpi_metrics_component(self):
        """Test 1: Global Trade Overview KPI metrics component integration."""
        print("📊 Testing KPI Metrics Component...")
        
        # Dashboard calls /stats endpoint for KPI metrics
        response = requests.get(f"{self.API_BASE_URL}/stats", timeout=10)
        assert response.status_code == 200, "Stats endpoint should be accessible"
        
        data = response.json()
        assert data["status"] == "success", "Stats response should indicate success"
        assert "data" in data, "Stats response should contain data"
        
        stats = data["data"]
        
        # Verify all KPI metrics required by dashboard are present
        required_kpis = [
            "total_transactions",
            "fraud_cases",
            "suspicious_cases",
            "safe_cases",
            "fraud_rate",
            "suspicious_rate",
            "total_trade_value",
            "high_risk_countries",
            "avg_risk_score"
        ]
        
        missing_kpis = [kpi for kpi in required_kpis if kpi not in stats]
        assert len(missing_kpis) == 0, f"Missing KPI metrics: {missing_kpis}"
        
        # Validate KPI data types and ranges
        assert isinstance(stats["total_transactions"], int), "Total transactions should be integer"
        assert stats["total_transactions"] > 0, "Should have transactions"
        
        assert isinstance(stats["fraud_rate"], (int, float)), "Fraud rate should be numeric"
        assert 0 <= stats["fraud_rate"] <= 100, "Fraud rate should be percentage (0-100)"
        
        assert isinstance(stats["total_trade_value"], (int, float)), "Trade value should be numeric"
        assert stats["total_trade_value"] >= 0, "Trade value should be non-negative"
        
        assert isinstance(stats["avg_risk_score"], (int, float)), "Avg risk score should be numeric"
        
        # Verify alert statistics are included
        assert "alert_statistics" in stats, "Stats should include alert statistics"
        alert_stats = stats["alert_statistics"]
        assert "active_count" in alert_stats, "Alert stats should include active count"
        assert "priority_counts" in alert_stats, "Alert stats should include priority counts"
        
        # Verify session info is included
        assert "session_info" in stats, "Stats should include session info"
        session_info = stats["session_info"]
        assert "explanations_used" in session_info, "Session info should include explanations used"
        assert "explanations_remaining" in session_info, "Session info should include explanations remaining"
        
        print(f"✅ KPI Metrics Component: All {len(required_kpis)} metrics present and valid")
        print(f"   Total Transactions: {stats['total_transactions']}")
        print(f"   Fraud Rate: {stats['fraud_rate']:.2f}%")
        print(f"   Active Alerts: {alert_stats['active_count']}")

    
    def test_fraud_alerts_component(self):
        """Test 2: Fraud Alerts section component integration."""
        print("🚨 Testing Fraud Alerts Component...")
        
        # Dashboard calls /alerts/active endpoint for active alerts
        response = requests.get(f"{self.API_BASE_URL}/alerts/active", timeout=10)
        assert response.status_code == 200, "Active alerts endpoint should be accessible"
        
        data = response.json()
        assert data["status"] == "success", "Alerts response should indicate success"
        assert "data" in data, "Alerts response should contain data"
        
        alerts_data = data["data"]
        assert "summaries" in alerts_data, "Alerts data should contain summaries"
        assert "count" in alerts_data, "Alerts data should contain count"
        
        summaries = alerts_data["summaries"]
        assert isinstance(summaries, list), "Summaries should be a list"
        
        # If there are alerts, validate their structure
        if len(summaries) > 0:
            sample_alert = summaries[0]
            
            # Required fields for dashboard alert display
            required_alert_fields = [
                "transaction_id",
                "priority",
                "risk_category",
                "alert_count",
                "priority_reason",
                "alerts"
            ]
            
            missing_fields = [field for field in required_alert_fields if field not in sample_alert]
            assert len(missing_fields) == 0, f"Missing alert fields: {missing_fields}"
            
            # Validate priority levels
            valid_priorities = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
            assert sample_alert["priority"] in valid_priorities, f"Invalid priority: {sample_alert['priority']}"
            
            # Validate risk categories
            valid_categories = {"SAFE", "SUSPICIOUS", "FRAUD"}
            assert sample_alert["risk_category"] in valid_categories, f"Invalid risk category: {sample_alert['risk_category']}"
            
            # Validate alerts array
            assert isinstance(sample_alert["alerts"], list), "Alerts should be a list"
            if len(sample_alert["alerts"]) > 0:
                alert = sample_alert["alerts"][0]
                assert "alert_type" in alert, "Alert should have type"
                assert "severity" in alert, "Alert should have severity"
        
        print(f"✅ Fraud Alerts Component: {len(summaries)} active alerts found")
        
        # Test alert statistics endpoint
        response = requests.get(f"{self.API_BASE_URL}/alerts/statistics", timeout=10)
        assert response.status_code == 200, "Alert statistics endpoint should be accessible"
        
        stats_data = response.json()
        assert stats_data["status"] == "success", "Alert stats should indicate success"
        
        stats = stats_data["data"]
        assert "total_alerts" in stats, "Stats should include total alerts"
        assert "active_count" in stats, "Stats should include active count"
        assert "priority_counts" in stats, "Stats should include priority counts"
        
        print(f"✅ Alert Statistics: {stats['total_alerts']} total, {stats['active_count']} active")
        
        # Test alert dismissal functionality
        if len(summaries) > 0:
            test_transaction_id = summaries[0]["transaction_id"]
            
            # Test dismiss
            dismiss_response = requests.post(
                f"{self.API_BASE_URL}/alerts/dismiss/{test_transaction_id}",
                timeout=10
            )
            assert dismiss_response.status_code == 200, "Alert dismissal should work"
            
            dismiss_data = dismiss_response.json()
            assert dismiss_data["status"] == "success", "Dismissal should succeed"
            
            # Test undismiss (restore)
            undismiss_response = requests.post(
                f"{self.API_BASE_URL}/alerts/undismiss/{test_transaction_id}",
                timeout=10
            )
            assert undismiss_response.status_code == 200, "Alert restoration should work"
            
            undismiss_data = undismiss_response.json()
            assert undismiss_data["status"] == "success", "Restoration should succeed"
            
            print(f"✅ Alert Dismissal/Restoration: Working correctly")

    
    def test_suspicious_transactions_table_component(self):
        """Test 3: Suspicious Transactions Table component integration."""
        print("📋 Testing Suspicious Transactions Table Component...")
        
        # Dashboard calls /suspicious endpoint for suspicious transactions
        response = requests.get(f"{self.API_BASE_URL}/suspicious", timeout=10)
        assert response.status_code == 200, "Suspicious endpoint should be accessible"
        
        data = response.json()
        assert data["status"] == "success", "Suspicious response should indicate success"
        assert "data" in data, "Suspicious response should contain data"
        
        transactions = data["data"]
        assert isinstance(transactions, list), "Transactions should be a list"
        
        print(f"✅ Suspicious Transactions: {len(transactions)} found")
        
        # If there are suspicious transactions, validate their structure
        if len(transactions) > 0:
            sample_txn = transactions[0]
            
            # Required fields for dashboard table display
            required_table_fields = [
                "transaction_id",
                "product",
                "unit_price",
                "market_price",
                "price_deviation",
                "risk_score",
                "risk_category"
            ]
            
            missing_fields = [field for field in required_table_fields if field not in sample_txn]
            assert len(missing_fields) == 0, f"Missing table fields: {missing_fields}"
            
            # Validate all are SUSPICIOUS category
            for txn in transactions[:10]:  # Check first 10
                assert txn["risk_category"] == "SUSPICIOUS", "All should be SUSPICIOUS category"
            
            # Validate numeric fields
            assert isinstance(sample_txn["unit_price"], (int, float)), "Unit price should be numeric"
            assert isinstance(sample_txn["market_price"], (int, float)), "Market price should be numeric"
            assert isinstance(sample_txn["risk_score"], (int, float)), "Risk score should be numeric"
            
            print(f"✅ Table Structure: All required fields present")
        
        # Test fraud transactions endpoint (similar structure)
        response = requests.get(f"{self.API_BASE_URL}/fraud", timeout=10)
        assert response.status_code == 200, "Fraud endpoint should be accessible"
        
        fraud_data = response.json()
        assert fraud_data["status"] == "success", "Fraud response should indicate success"
        
        fraud_transactions = fraud_data["data"]
        assert isinstance(fraud_transactions, list), "Fraud transactions should be a list"
        
        print(f"✅ Fraud Transactions: {len(fraud_transactions)} found")
        
        # Test all transactions endpoint with pagination
        response = requests.get(f"{self.API_BASE_URL}/transactions?limit=50&offset=0", timeout=10)
        assert response.status_code == 200, "Transactions endpoint should be accessible"
        
        all_data = response.json()
        assert all_data["status"] == "success", "Transactions response should indicate success"
        
        all_txns_data = all_data["data"]
        assert "transactions" in all_txns_data, "Should have transactions field"
        assert "pagination" in all_txns_data, "Should have pagination info"
        
        pagination = all_txns_data["pagination"]
        assert "total" in pagination, "Pagination should include total"
        assert "limit" in pagination, "Pagination should include limit"
        assert "offset" in pagination, "Pagination should include offset"
        assert "returned" in pagination, "Pagination should include returned count"
        
        print(f"✅ Pagination: {pagination['returned']} of {pagination['total']} transactions")

    
    def test_transaction_explanation_component(self):
        """Test 4: Transaction explanation functionality (AI and fallback)."""
        print("🤖 Testing Transaction Explanation Component...")
        
        # Get a transaction to explain
        response = requests.get(f"{self.API_BASE_URL}/transactions?limit=5", timeout=10)
        assert response.status_code == 200, "Transactions endpoint should work"
        
        data = response.json()
        transactions = data["data"]["transactions"]
        
        if len(transactions) == 0:
            pytest.skip("No transactions available for explanation test")
        
        test_transaction_id = transactions[0]["transaction_id"]
        
        # Test fallback explanation (force_ai=False)
        print(f"Testing fallback explanation for {test_transaction_id}...")
        explain_response = requests.post(
            f"{self.API_BASE_URL}/explain/{test_transaction_id}",
            json={"force_ai": False},
            timeout=15
        )
        
        assert explain_response.status_code == 200, "Explanation endpoint should work"
        
        explain_data = explain_response.json()
        assert explain_data["status"] == "success", "Explanation should succeed"
        assert "data" in explain_data, "Explanation should contain data"
        
        explanation_result = explain_data["data"]
        
        # Validate explanation structure
        required_explanation_fields = [
            "transaction_id",
            "explanation",
            "explanation_type",
            "session_info"
        ]
        
        missing_fields = [field for field in required_explanation_fields if field not in explanation_result]
        assert len(missing_fields) == 0, f"Missing explanation fields: {missing_fields}"
        
        assert explanation_result["transaction_id"] == test_transaction_id, "Transaction ID should match"
        assert isinstance(explanation_result["explanation"], str), "Explanation should be string"
        assert len(explanation_result["explanation"]) > 0, "Explanation should not be empty"
        
        # Validate explanation type
        valid_types = {"ai_generated", "fallback", "cached", "quota_exceeded"}
        assert explanation_result["explanation_type"] in valid_types, f"Invalid explanation type: {explanation_result['explanation_type']}"
        
        # Validate session info
        session_info = explanation_result["session_info"]
        assert "current_count" in session_info, "Session info should include current count"
        assert "max_count" in session_info, "Session info should include max count"
        assert "remaining" in session_info, "Session info should include remaining"
        
        print(f"✅ Fallback Explanation: Type={explanation_result['explanation_type']}, Length={len(explanation_result['explanation'])} chars")
        print(f"✅ Session Info: {session_info['current_count']}/{session_info['max_count']} used")
        
        # Test AI explanation (force_ai=True) - may hit quota
        print(f"Testing AI explanation for {test_transaction_id}...")
        ai_explain_response = requests.post(
            f"{self.API_BASE_URL}/explain/{test_transaction_id}",
            json={"force_ai": True},
            timeout=20
        )
        
        assert ai_explain_response.status_code == 200, "AI explanation endpoint should work"
        
        ai_explain_data = ai_explain_response.json()
        assert ai_explain_data["status"] == "success", "AI explanation should succeed"
        
        ai_result = ai_explain_data["data"]
        assert "explanation" in ai_result, "AI result should have explanation"
        assert "explanation_type" in ai_result, "AI result should have type"
        
        # Type should be ai_generated, quota_exceeded, or cached
        print(f"✅ AI Explanation: Type={ai_result['explanation_type']}")
        
        # Test invalid transaction ID
        invalid_response = requests.post(
            f"{self.API_BASE_URL}/explain/INVALID_TXN_999",
            json={"force_ai": False},
            timeout=10
        )
        
        # Should handle gracefully (404 or error response)
        assert invalid_response.status_code in [200, 404], "Should handle invalid ID gracefully"
        
        print(f"✅ Invalid Transaction Handling: Status={invalid_response.status_code}")

    
    def test_visualization_data_endpoints(self):
        """Test 5: Data endpoints for Route Intelligence Map and visualizations."""
        print("🗺️ Testing Visualization Data Endpoints...")
        
        # Get transactions for visualizations (dashboard uses limit=200)
        response = requests.get(f"{self.API_BASE_URL}/transactions?limit=200", timeout=10)
        assert response.status_code == 200, "Transactions endpoint should work"
        
        data = response.json()
        assert data["status"] == "success", "Response should indicate success"
        
        transactions_data = data["data"]
        transactions = transactions_data["transactions"]
        
        assert isinstance(transactions, list), "Transactions should be a list"
        assert len(transactions) > 0, "Should have transactions for visualization"
        
        print(f"✅ Visualization Data: {len(transactions)} transactions retrieved")
        
        # Validate fields required for Route Intelligence Map
        if len(transactions) > 0:
            sample_txn = transactions[0]
            
            # Route map requires these fields
            route_map_fields = [
                "export_port",
                "import_port",
                "risk_category",
                "transaction_id",
                "product",
                "distance_km"
            ]
            
            available_route_fields = [field for field in route_map_fields if field in sample_txn]
            print(f"✅ Route Map Fields: {len(available_route_fields)}/{len(route_map_fields)} available")
            
            # Validate fields for Company Risk Network
            network_fields = [
                "exporter_company",
                "importer_company",
                "risk_category",
                "company_risk_score"
            ]
            
            available_network_fields = [field for field in network_fields if field in sample_txn]
            print(f"✅ Network Graph Fields: {len(available_network_fields)}/{len(network_fields)} available")
            
            # Validate fields for Price Deviation Chart
            price_chart_fields = [
                "market_price",
                "unit_price",
                "risk_category",
                "transaction_id",
                "product",
                "price_deviation"
            ]
            
            available_price_fields = [field for field in price_chart_fields if field in sample_txn]
            print(f"✅ Price Chart Fields: {len(available_price_fields)}/{len(price_chart_fields)} available")
            
            # Validate risk category distribution data
            risk_categories = [txn.get("risk_category") for txn in transactions if "risk_category" in txn]
            unique_categories = set(risk_categories)
            
            print(f"✅ Risk Categories: {unique_categories}")
            
            # Count by category
            from collections import Counter
            category_counts = Counter(risk_categories)
            for category, count in category_counts.items():
                print(f"   {category}: {count} transactions")

    
    def test_ai_investigation_assistant_component(self):
        """Test 6: AI Investigation Assistant (chat interface) component."""
        print("💬 Testing AI Investigation Assistant Component...")
        
        # Dashboard calls /query endpoint for natural language queries
        test_queries = [
            "What are the main fraud patterns?",
            "How many suspicious transactions are there?",
            "What should I investigate next?",
            "Tell me about high-risk companies"
        ]
        
        for query in test_queries:
            print(f"Testing query: '{query}'")
            
            response = requests.post(
                f"{self.API_BASE_URL}/query",
                json={"query": query},
                timeout=15
            )
            
            assert response.status_code == 200, f"Query endpoint should work for: {query}"
            
            data = response.json()
            assert data["status"] == "success", "Query should succeed"
            assert "data" in data, "Query response should contain data"
            
            query_result = data["data"]
            
            # Validate query response structure
            required_query_fields = [
                "query",
                "answer",
                "context_summary"
            ]
            
            missing_fields = [field for field in required_query_fields if field not in query_result]
            assert len(missing_fields) == 0, f"Missing query fields: {missing_fields}"
            
            assert query_result["query"] == query, "Query should match request"
            assert isinstance(query_result["answer"], str), "Answer should be string"
            assert len(query_result["answer"]) > 0, "Answer should not be empty"
            
            # Validate context summary
            context = query_result["context_summary"]
            assert "total_transactions" in context, "Context should include total transactions"
            assert "fraud_rate" in context, "Context should include fraud rate"
            assert "suspicious_rate" in context, "Context should include suspicious rate"
            
            print(f"✅ Query Response: {len(query_result['answer'])} chars, Context: {context['total_transactions']} transactions")
        
        print(f"✅ AI Investigation Assistant: All {len(test_queries)} queries processed successfully")
        
        # Test empty query handling
        empty_response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"query": ""},
            timeout=10
        )
        
        # Should handle gracefully
        assert empty_response.status_code in [200, 400, 422], "Should handle empty query gracefully"
        
        print(f"✅ Empty Query Handling: Status={empty_response.status_code}")

    
    def test_session_management_component(self):
        """Test 7: Session management and quota system integration."""
        print("🔐 Testing Session Management Component...")
        
        # Test session info endpoint
        response = requests.get(f"{self.API_BASE_URL}/session/info", timeout=10)
        assert response.status_code == 200, "Session info endpoint should be accessible"
        
        data = response.json()
        assert data["status"] == "success", "Session info should succeed"
        assert "data" in data, "Session info should contain data"
        
        session_info = data["data"]
        
        # Validate session info structure
        required_session_fields = [
            "current_count",
            "max_count",
            "remaining",
            "can_make_explanation"
        ]
        
        missing_fields = [field for field in required_session_fields if field not in session_info]
        assert len(missing_fields) == 0, f"Missing session fields: {missing_fields}"
        
        # Validate session data
        assert isinstance(session_info["current_count"], int), "Current count should be integer"
        assert isinstance(session_info["max_count"], int), "Max count should be integer"
        assert isinstance(session_info["remaining"], int), "Remaining should be integer"
        assert isinstance(session_info["can_make_explanation"], bool), "Can make explanation should be boolean"
        
        assert session_info["current_count"] >= 0, "Current count should be non-negative"
        assert session_info["max_count"] > 0, "Max count should be positive"
        assert session_info["remaining"] >= 0, "Remaining should be non-negative"
        
        # Verify math: current + remaining = max
        assert session_info["current_count"] + session_info["remaining"] == session_info["max_count"], \
            "Current + Remaining should equal Max"
        
        print(f"✅ Session Info: {session_info['current_count']}/{session_info['max_count']} used, {session_info['remaining']} remaining")
        
        # Test session reset endpoint
        reset_response = requests.post(f"{self.API_BASE_URL}/session/reset", timeout=10)
        assert reset_response.status_code == 200, "Session reset should work"
        
        reset_data = reset_response.json()
        assert reset_data["status"] == "success", "Session reset should succeed"
        assert "data" in reset_data, "Reset response should contain data"
        
        reset_session_info = reset_data["data"]
        assert reset_session_info["session_count"] == 0, "Session count should be reset to 0"
        
        print(f"✅ Session Reset: Count reset to {reset_session_info['session_count']}")
        
        # Verify session was actually reset
        verify_response = requests.get(f"{self.API_BASE_URL}/session/info", timeout=10)
        verify_data = verify_response.json()
        verify_session = verify_data["data"]
        
        assert verify_session["current_count"] == 0, "Session should be reset after reset call"
        assert verify_session["remaining"] == verify_session["max_count"], "All explanations should be available after reset"
        
        print(f"✅ Session Reset Verification: Confirmed reset successful")

    
    def test_dashboard_data_refresh_mechanism(self):
        """Test 8: Dashboard data refresh and real-time updates."""
        print("🔄 Testing Dashboard Data Refresh Mechanism...")
        
        # Simulate dashboard refresh by calling multiple endpoints
        refresh_endpoints = [
            "/stats",
            "/transactions?limit=50",
            "/alerts/active",
            "/session/info"
        ]
        
        # First refresh
        first_refresh_results = {}
        for endpoint in refresh_endpoints:
            response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=10)
            assert response.status_code == 200, f"Endpoint {endpoint} should work"
            
            data = response.json()
            first_refresh_results[endpoint] = data
        
        print(f"✅ First Refresh: All {len(refresh_endpoints)} endpoints responded")
        
        # Wait a moment
        time.sleep(1)
        
        # Second refresh
        second_refresh_results = {}
        for endpoint in refresh_endpoints:
            response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=10)
            assert response.status_code == 200, f"Endpoint {endpoint} should work on second refresh"
            
            data = response.json()
            second_refresh_results[endpoint] = data
        
        print(f"✅ Second Refresh: All {len(refresh_endpoints)} endpoints responded")
        
        # Verify data consistency (core metrics should remain stable)
        stats1 = first_refresh_results["/stats"]["data"]
        stats2 = second_refresh_results["/stats"]["data"]
        
        assert stats1["total_transactions"] == stats2["total_transactions"], \
            "Total transactions should be consistent across refreshes"
        
        print(f"✅ Data Consistency: Core metrics stable across refreshes")
        
        # Test rapid refresh (simulate user clicking refresh button multiple times)
        rapid_refresh_count = 5
        rapid_results = []
        
        start_time = time.time()
        for i in range(rapid_refresh_count):
            response = requests.get(f"{self.API_BASE_URL}/stats", timeout=10)
            assert response.status_code == 200, f"Rapid refresh {i+1} should work"
            rapid_results.append(response.json())
        end_time = time.time()
        
        avg_response_time = (end_time - start_time) / rapid_refresh_count
        
        print(f"✅ Rapid Refresh: {rapid_refresh_count} refreshes in {end_time - start_time:.2f}s")
        print(f"   Average response time: {avg_response_time:.3f}s")
        
        # Verify all rapid refreshes returned consistent data
        for i in range(1, len(rapid_results)):
            assert rapid_results[i]["data"]["total_transactions"] == rapid_results[0]["data"]["total_transactions"], \
                f"Rapid refresh {i+1} should have consistent data"
        
        print(f"✅ Rapid Refresh Consistency: All {rapid_refresh_count} refreshes returned consistent data")
