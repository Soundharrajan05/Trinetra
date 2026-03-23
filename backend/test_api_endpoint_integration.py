"""
API Endpoint Integration Tests for TRINETRA AI Fraud Detection System

This module tests the integration of API endpoints with the ML pipeline,
verifying data flow between components, error handling, and response formats.

**Validates: Requirements 12.2 - Integration Testing**
"""

import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import os
import sys
import tempfile
import joblib
from sklearn.ensemble import IsolationForest

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))

from api import app
from data_loader import load_dataset
from feature_engineering import engineer_features
from model import train_model
from fraud_detection import score_transactions, classify_risk


class TestAPIEndpointIntegration:
    """Test API endpoint integration with ML pipeline."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_dataset(self):
        """Create sample dataset for testing."""
        np.random.seed(42)
        data = {
            'transaction_id': [f'TXN{i:05d}' for i in range(100)],
            'date': pd.date_range('2024-01-01', periods=100),
            'fraud_label': np.random.choice(['SAFE', 'SUSPICIOUS', 'FRAUD'], 100),
            'product': np.random.choice(['Electronics', 'Textiles', 'Machinery'], 100),
            'commodity_category': np.random.choice(['Consumer', 'Industrial', 'Raw'], 100),
            'unit_price': np.random.uniform(10, 1000, 100),
            'market_price': np.random.uniform(10, 1000, 100),
            'price_deviation': np.random.uniform(-0.5, 0.5, 100),
            'route_anomaly': np.random.choice([0, 1], 100),
            'company_risk_score': np.random.uniform(0, 1, 100),
            'port_activity_index': np.random.uniform(0.5, 2.0, 100),
            'shipment_duration_days': np.random.uniform(1, 30, 100),
            'distance_km': np.random.uniform(100, 10000, 100),
            'cargo_volume': np.random.uniform(10, 1000, 100),
            'quantity': np.random.uniform(1, 100, 100),
            'shipping_route': [f'Route_{i%10}' for i in range(100)],
            'export_port': [f'Port_{i%5}' for i in range(100)],
            'import_port': [f'Port_{(i+1)%5}' for i in range(100)]
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def trained_model(self, sample_dataset):
        """Create and train a model for testing."""
        # Engineer features
        df_with_features = engineer_features(sample_dataset)
        
        # Train model
        model = train_model(df_with_features)
        return model
    
    @pytest.fixture
    def processed_dataset(self, sample_dataset, trained_model):
        """Create fully processed dataset with scores and classifications."""
        # Engineer features
        df_with_features = engineer_features(sample_dataset)
        
        # Score transactions
        df_scored = score_transactions(df_with_features, trained_model)
        
        # Classify risk
        df_classified = classify_risk(df_scored)
        
        return df_classified

    def test_api_ml_pipeline_integration(self, client, processed_dataset):
        """Test integration between API endpoints and ML pipeline."""
        
        # Mock the global dataframe in the API module
        with patch('api._transactions_df', processed_dataset):
            # Test /transactions endpoint returns ML-processed data
            response = client.get("/transactions")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert "data" in data
            
            # The data contains transactions and pagination
            response_data = data["data"]
            assert "transactions" in response_data
            assert "pagination" in response_data
            
            transactions = response_data["transactions"]
            assert len(transactions) > 0
            
            # Verify ML pipeline outputs are present
            first_transaction = transactions[0]
            assert "risk_score" in first_transaction
            assert "risk_category" in first_transaction
            assert first_transaction["risk_category"] in ["SAFE", "SUSPICIOUS", "FRAUD"]
            
            # Verify engineered features are present
            assert "price_anomaly_score" in first_transaction
            assert "route_risk_score" in first_transaction
            assert "company_network_risk" in first_transaction
            assert "port_congestion_score" in first_transaction
            assert "shipment_duration_risk" in first_transaction
            assert "volume_spike_score" in first_transaction

    def test_suspicious_transactions_filtering(self, client, processed_dataset):
        """Test that suspicious endpoint correctly filters ML results."""
        
        with patch('api._transactions_df', processed_dataset):
            response = client.get("/suspicious")
            assert response.status_code == 200
            
            data = response.json()
            transactions = data["data"]  # Direct list for suspicious endpoint
            
            # All returned transactions should be SUSPICIOUS
            for transaction in transactions:
                assert transaction["risk_category"] == "SUSPICIOUS"

    def test_fraud_transactions_filtering(self, client, processed_dataset):
        """Test that fraud endpoint correctly filters ML results."""
        
        with patch('api._transactions_df', processed_dataset):
            response = client.get("/fraud")
            assert response.status_code == 200
            
            data = response.json()
            transactions = data["data"]  # Direct list for fraud endpoint
            
            # All returned transactions should be FRAUD
            for transaction in transactions:
                assert transaction["risk_category"] == "FRAUD"

    def test_statistics_endpoint_ml_integration(self, client, processed_dataset):
        """Test that statistics endpoint correctly aggregates ML results."""
        
        with patch('api._transactions_df', processed_dataset):
            response = client.get("/stats")
            assert response.status_code == 200
            
            data = response.json()["data"]
            
            # Verify ML-derived statistics
            assert "total_transactions" in data
            assert "fraud_rate" in data
            assert "suspicious_rate" in data
            assert "safe_rate" in data
            
            # Verify rates sum to approximately 100%
            total_rate = data["fraud_rate"] + data["suspicious_rate"] + data["safe_rate"]
            assert abs(total_rate - 100.0) < 0.1

    def test_explain_endpoint_integration(self, client, processed_dataset):
        """Test explanation endpoint integration with ML results."""
        
        with patch('api._transactions_df', processed_dataset):
            # Get a transaction ID from the dataset
            transaction_id = processed_dataset.iloc[0]['transaction_id']
            
            # Mock the AI explainer
            with patch('api.explain_transaction') as mock_explain:
                mock_explain.return_value = "This transaction is suspicious due to price anomaly."
                
                response = client.post(f"/explain/{transaction_id}")
                assert response.status_code == 200
                
                data = response.json()
                assert data["status"] == "success"
                assert "explanation" in data["data"]
                
                # Verify the explainer was called with ML-processed data
                mock_explain.assert_called_once()
                call_args = mock_explain.call_args[0][0]
                
                # Verify the transaction data includes ML outputs
                assert "risk_score" in call_args
                assert "risk_category" in call_args

    def test_data_flow_consistency(self, client, processed_dataset):
        """Test data consistency across different endpoints."""
        
        with patch('api._transactions_df', processed_dataset):
            # Get all transactions
            all_response = client.get("/transactions")
            all_transactions = all_response.json()["data"]["transactions"]  # Nested structure
            
            # Get suspicious transactions
            suspicious_response = client.get("/suspicious")
            suspicious_transactions = suspicious_response.json()["data"]  # Direct list
            
            # Get fraud transactions
            fraud_response = client.get("/fraud")
            fraud_transactions = fraud_response.json()["data"]  # Direct list
            
            # Verify data consistency
            all_ids = {t["transaction_id"] for t in all_transactions}
            suspicious_ids = {t["transaction_id"] for t in suspicious_transactions}
            fraud_ids = {t["transaction_id"] for t in fraud_transactions}
            
            # Suspicious and fraud IDs should be subsets of all IDs
            assert suspicious_ids.issubset(all_ids)
            assert fraud_ids.issubset(all_ids)
            
            # No overlap between suspicious and fraud
            assert suspicious_ids.isdisjoint(fraud_ids)

    def test_error_handling_with_corrupted_ml_data(self, client):
        """Test API error handling when ML pipeline data is corrupted."""
        
        # Create corrupted dataset (missing required columns)
        corrupted_data = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'incomplete_data': ['test']
        })
        
        with patch('api._transactions_df', corrupted_data):
            response = client.get("/transactions")
            # Should handle gracefully and return appropriate error
            assert response.status_code in [200, 500]  # Depending on error handling strategy

    def test_ml_model_integration_with_real_data(self, client):
        """Test ML model integration with actual dataset if available."""
        
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        
        if os.path.exists(dataset_path):
            # Load real dataset
            df = load_dataset(dataset_path)
            
            # Process through ML pipeline
            df_features = engineer_features(df)
            
            # Create temporary model for testing
            with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp_file:
                model = train_model(df_features)
                joblib.dump(model, tmp_file.name)
                
                try:
                    # Score and classify
                    df_scored = score_transactions(df_features, model)
                    df_classified = classify_risk(df_scored)
                    
                    with patch('api._transactions_df', df_classified):
                        # Test endpoints with real data
                        response = client.get("/transactions?limit=10")
                        assert response.status_code == 200
                        
                        data = response.json()
                        assert len(data["data"]) <= 10
                        
                        # Verify real data has expected structure
                        if data["data"]:
                            transaction = data["data"][0]
                            assert "risk_score" in transaction
                            assert "risk_category" in transaction
                            
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(tmp_file.name)
                    except:
                        pass  # Ignore cleanup errors
        else:
            pytest.skip("Real dataset not available for integration test")

    def test_concurrent_requests_ml_pipeline(self, client, processed_dataset):
        """Test concurrent API requests with ML pipeline integration."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request(endpoint):
            try:
                response = client.get(endpoint)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        with patch('api._transactions_df', processed_dataset):
            # Create multiple threads making concurrent requests
            threads = []
            endpoints = ["/transactions", "/suspicious", "/fraud", "/stats"]
            
            for _ in range(5):  # Reduced to 5 concurrent requests for stability
                for endpoint in endpoints:
                    thread = threading.Thread(target=make_request, args=(endpoint,))
                    threads.append(thread)
            
            # Start all threads
            start_time = time.time()
            for thread in threads:
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            
            # Verify results
            assert len(errors) == 0, f"Errors occurred: {errors}"
            assert all(status == 200 for status in results)
            
            # Performance check - should complete within reasonable time
            assert end_time - start_time < 10.0  # 10 seconds max

    def test_json_schema_compliance(self, client, processed_dataset):
        """Test that API responses comply with expected JSON schemas."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test transactions endpoint schema
            response = client.get("/transactions?limit=1")
            data = response.json()
            
            # Verify top-level structure
            assert "status" in data
            assert "data" in data
            assert isinstance(data["data"], dict)
            
            # Verify nested structure
            response_data = data["data"]
            assert "transactions" in response_data
            assert "pagination" in response_data
            
            transactions = response_data["transactions"]
            if transactions:
                transaction = transactions[0]
                
                # Verify required fields from ML pipeline
                required_fields = [
                    "transaction_id", "risk_score", "risk_category",
                    "price_anomaly_score", "route_risk_score",
                    "company_network_risk", "port_congestion_score",
                    "shipment_duration_risk", "volume_spike_score"
                ]
                
                for field in required_fields:
                    assert field in transaction, f"Missing field: {field}"
                
                # Verify data types
                assert isinstance(transaction["risk_score"], (int, float))
                assert isinstance(transaction["risk_category"], str)
                assert transaction["risk_category"] in ["SAFE", "SUSPICIOUS", "FRAUD"]

    def test_alert_system_integration(self, client, processed_dataset):
        """Test alert system integration with ML pipeline results."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test alerts endpoint
            response = client.get("/alerts")
            assert response.status_code == 200
            
            data = response.json()
            assert "data" in data
            
            # Verify alerts are based on ML results
            alerts_data = data["data"]
            if "alerts" in alerts_data and alerts_data["alerts"]:
                alert = alerts_data["alerts"][0]
                assert "transaction_id" in alert
                assert "alert_type" in alert
                assert "priority" in alert

    def test_session_management_endpoints(self, client, processed_dataset):
        """Test session management endpoints for quota tracking."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test session info endpoint
            response = client.get("/session/info")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert "data" in data
            
            session_info = data["data"]
            assert "current_count" in session_info
            assert "max_count" in session_info
            assert "remaining" in session_info
            assert "can_make_explanation" in session_info
            
            # Verify data types
            assert isinstance(session_info["current_count"], int)
            assert isinstance(session_info["max_count"], int)
            assert isinstance(session_info["remaining"], int)
            assert isinstance(session_info["can_make_explanation"], bool)
            
            # Test session reset endpoint
            reset_response = client.post("/session/reset")
            assert reset_response.status_code == 200
            
            reset_data = reset_response.json()
            assert reset_data["status"] == "success"
            assert "data" in reset_data
            
            # Verify session was reset
            reset_session_info = reset_data["data"]
            assert reset_session_info["session_count"] == 0

    def test_quota_management_system(self, client, processed_dataset):
        """Test quota management for AI explanations."""
        
        with patch('api._transactions_df', processed_dataset):
            transaction_id = processed_dataset.iloc[0]['transaction_id']
            
            # Mock the AI explainer to track calls
            with patch('api.explain_transaction') as mock_explain:
                mock_explain.return_value = "AI explanation"
                
                # Test explanation with force_ai flag
                response = client.post(
                    f"/explain/{transaction_id}",
                    json={"force_ai": True}
                )
                assert response.status_code == 200
                
                data = response.json()
                assert "data" in data
                assert "explanation_type" in data["data"]
                assert "session_info" in data["data"]
                
                session_info = data["data"]["session_info"]
                assert "current_count" in session_info
                assert "max_count" in session_info
                assert "remaining" in session_info

    def test_cors_configuration(self, client):
        """Test CORS middleware configuration."""
        
        # Test preflight request
        response = client.options(
            "/transactions",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # CORS should allow the request
        assert response.status_code in [200, 204]
        
        # Test actual request with CORS headers
        response = client.get(
            "/transactions",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Should have CORS headers in response
        assert "access-control-allow-origin" in response.headers or \
               "Access-Control-Allow-Origin" in response.headers

    def test_error_handling_middleware(self, client):
        """Test error handling middleware for various error conditions."""
        
        # Test with non-existent transaction ID
        response = client.post("/explain/INVALID_ID")
        assert response.status_code in [404, 500]
        
        data = response.json()
        assert "detail" in data or "message" in data
        
        # Test with invalid query
        response = client.post("/query", json={"query": ""})
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]

    def test_pagination_functionality(self, client, processed_dataset):
        """Test pagination parameters for transactions endpoint."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test with limit parameter
            response = client.get("/transactions?limit=5")
            assert response.status_code == 200
            
            data = response.json()["data"]
            assert "pagination" in data
            assert data["pagination"]["limit"] == 5
            assert len(data["transactions"]) <= 5
            
            # Test with offset parameter
            response = client.get("/transactions?limit=10&offset=10")
            assert response.status_code == 200
            
            data = response.json()["data"]
            assert data["pagination"]["offset"] == 10
            assert data["pagination"]["limit"] == 10
            
            # Test with invalid pagination parameters
            response = client.get("/transactions?limit=-1")
            assert response.status_code in [200, 422]  # Should validate or use default

    def test_query_endpoint_integration(self, client, processed_dataset):
        """Test natural language query endpoint integration."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test valid query
            response = client.post(
                "/query",
                json={"query": "What is the fraud rate?"}
            )
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert "data" in data
            
            query_data = data["data"]
            assert "query" in query_data
            assert "answer" in query_data
            assert "context_summary" in query_data
            
            # Verify context summary has expected fields
            context = query_data["context_summary"]
            assert "total_transactions" in context
            assert "fraud_rate" in context
            assert "suspicious_rate" in context

    def test_alert_endpoints_comprehensive(self, client, processed_dataset):
        """Test all alert-related endpoints comprehensively."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test get all alerts
            response = client.get("/alerts")
            assert response.status_code == 200
            
            # Test get alerts by transaction
            transaction_id = processed_dataset.iloc[0]['transaction_id']
            response = client.get(f"/alerts/transaction/{transaction_id}")
            assert response.status_code == 200
            
            # Test get alerts by priority
            for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                response = client.get(f"/alerts/priority/{priority}")
                assert response.status_code == 200
                
                data = response.json()
                assert data["status"] == "success"
            
            # Test invalid priority
            response = client.get("/alerts/priority/INVALID")
            assert response.status_code == 400
            
            # Test alert statistics
            response = client.get("/alerts/statistics")
            assert response.status_code == 200
            
            data = response.json()
            assert "data" in data
            
            # Test alert summaries
            response = client.get("/alerts/summaries")
            assert response.status_code == 200
            
            # Test alert summaries with min_priority filter
            response = client.get("/alerts/summaries?min_priority=HIGH")
            assert response.status_code == 200

    def test_alert_dismissal_workflow(self, client, processed_dataset):
        """Test alert dismissal and undismissal workflow."""
        
        with patch('api._transactions_df', processed_dataset):
            transaction_id = processed_dataset.iloc[0]['transaction_id']
            
            # Test dismiss alert
            response = client.post(
                f"/alerts/dismiss/{transaction_id}",
                params={"dismissed_by": "test_analyst"}
            )
            # May return 200 if alert exists, 404 if not
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                data = response.json()
                assert data["status"] == "success"
                assert data["data"]["dismissed"] == True
                
                # Test undismiss alert
                response = client.post(f"/alerts/undismiss/{transaction_id}")
                assert response.status_code == 200
                
                data = response.json()
                assert data["status"] == "success"
                assert data["data"]["dismissed"] == False

    def test_active_and_dismissed_alerts(self, client, processed_dataset):
        """Test endpoints for active and dismissed alerts."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test get active alerts
            response = client.get("/alerts/active")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert "data" in data
            assert "summaries" in data["data"]
            assert "count" in data["data"]
            
            # Test get dismissed alerts
            response = client.get("/alerts/dismissed")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert "data" in data
            assert "summaries" in data["data"]
            assert "count" in data["data"]

    def test_root_endpoint(self, client):
        """Test root endpoint returns system information."""
        
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        
        system_info = data["data"]
        assert "name" in system_info
        assert "version" in system_info
        assert "description" in system_info
        assert "TRINETRA AI" in system_info["name"]

    def test_response_format_consistency(self, client, processed_dataset):
        """Test that all endpoints return consistent response format."""
        
        with patch('api._transactions_df', processed_dataset):
            endpoints = [
                ("/", "GET"),
                ("/transactions", "GET"),
                ("/suspicious", "GET"),
                ("/fraud", "GET"),
                ("/stats", "GET"),
                ("/session/info", "GET"),
                ("/alerts", "GET"),
                ("/alerts/statistics", "GET"),
                ("/alerts/summaries", "GET"),
                ("/alerts/active", "GET"),
                ("/alerts/dismissed", "GET")
            ]
            
            for endpoint, method in endpoints:
                if method == "GET":
                    response = client.get(endpoint)
                    assert response.status_code == 200
                    
                    data = response.json()
                    # All responses should have status field
                    assert "status" in data
                    assert data["status"] == "success"
                    # All responses should have data field
                    assert "data" in data

    def test_backend_service_integration(self, client, processed_dataset, trained_model):
        """Test integration with backend services (data loader, fraud detection, AI explainer)."""
        
        with patch('api._transactions_df', processed_dataset):
            with patch('api._fraud_detector', trained_model):
                # Test that endpoints use the fraud detector
                response = client.get("/transactions?limit=1")
                assert response.status_code == 200
                
                data = response.json()["data"]["transactions"]
                if data:
                    transaction = data[0]
                    # Verify fraud detection outputs
                    assert "risk_score" in transaction
                    assert "risk_category" in transaction
                    assert isinstance(transaction["risk_score"], (int, float))
                    
                # Test AI explainer integration
                transaction_id = processed_dataset.iloc[0]['transaction_id']
                
                with patch('api.explain_transaction') as mock_explain:
                    mock_explain.return_value = "Test explanation"
                    
                    response = client.post(f"/explain/{transaction_id}")
                    assert response.status_code == 200
                    
                    # Verify explainer was called
                    mock_explain.assert_called_once()

    def test_caching_system(self, client, processed_dataset):
        """Test caching system for explanations."""
        
        with patch('api._transactions_df', processed_dataset):
            transaction_id = processed_dataset.iloc[0]['transaction_id']
            
            with patch('api.explain_transaction') as mock_explain:
                mock_explain.return_value = "Cached explanation"
                
                # First request
                response1 = client.post(f"/explain/{transaction_id}")
                assert response1.status_code == 200
                
                # Second request (should use cache)
                response2 = client.post(f"/explain/{transaction_id}")
                assert response2.status_code == 200
                
                # Both should return same explanation
                assert response1.json()["data"]["explanation"] == \
                       response2.json()["data"]["explanation"]

    def test_api_response_time_requirements(self, client, processed_dataset):
        """Test that API responses meet performance requirements (<1 second)."""
        import time
        
        with patch('api._transactions_df', processed_dataset):
            endpoints = [
                "/transactions?limit=10",
                "/suspicious",
                "/fraud",
                "/stats",
                "/session/info"
            ]
            
            for endpoint in endpoints:
                start_time = time.time()
                response = client.get(endpoint)
                elapsed_time = time.time() - start_time
                
                assert response.status_code == 200
                # NFR-1: API responses within 1 second
                assert elapsed_time < 1.0, f"Endpoint {endpoint} took {elapsed_time:.3f}s (>1s)"

    def test_api_error_responses_format(self, client):
        """Test that error responses follow consistent format."""
        
        # Test 404 error
        response = client.post("/explain/NONEXISTENT_ID")
        assert response.status_code in [404, 500]
        
        error_data = response.json()
        # Should have either 'detail' (FastAPI default) or 'message' field
        assert "detail" in error_data or "message" in error_data
        
        # Test invalid priority parameter
        response = client.get("/alerts/priority/INVALID_PRIORITY")
        assert response.status_code == 400
        
        error_data = response.json()
        assert "detail" in error_data or "message" in error_data

    def test_api_data_validation(self, client, processed_dataset):
        """Test API input validation with invalid data."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test invalid pagination parameters
            response = client.get("/transactions?limit=0")
            # Should either reject or use default
            assert response.status_code in [200, 422]
            
            # Test invalid query format
            response = client.post("/query", json={})
            # Should reject missing required field
            assert response.status_code in [400, 422]
            
            # Test empty query string
            response = client.post("/query", json={"query": ""})
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]

    def test_api_session_state_management(self, client, processed_dataset):
        """Test session state management across multiple requests."""
        
        with patch('api._transactions_df', processed_dataset):
            # Get initial session info
            response = client.get("/session/info")
            assert response.status_code == 200
            initial_count = response.json()["data"]["current_count"]
            
            # Reset session
            response = client.post("/session/reset")
            assert response.status_code == 200
            
            # Verify session was reset
            response = client.get("/session/info")
            assert response.status_code == 200
            reset_count = response.json()["data"]["current_count"]
            assert reset_count == 0

    def test_api_cache_endpoints(self, client, processed_dataset):
        """Test cache management endpoints."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test cache clear endpoint
            response = client.post("/cache/clear")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"

    def test_api_performance_monitoring(self, client, processed_dataset):
        """Test performance monitoring endpoints."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test get performance stats
            response = client.get("/performance/stats")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert "data" in data
            
            perf_data = data["data"]
            assert "performance" in perf_data
            assert "cache" in perf_data
            
            # Test reset performance stats
            response = client.post("/performance/reset")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"

    def test_api_integration_with_all_services(self, client, processed_dataset, trained_model):
        """Test complete integration of API with all backend services."""
        
        with patch('api._transactions_df', processed_dataset):
            with patch('api._fraud_detector', trained_model):
                # Test data loader integration
                response = client.get("/transactions?limit=1")
                assert response.status_code == 200
                
                # Test feature engineering integration
                data = response.json()["data"]["transactions"]
                if data:
                    transaction = data[0]
                    # Verify engineered features are present
                    assert "price_anomaly_score" in transaction
                    assert "route_risk_score" in transaction
                    assert "company_network_risk" in transaction
                
                # Test fraud detection integration
                response = client.get("/fraud")
                assert response.status_code == 200
                fraud_data = response.json()["data"]
                for transaction in fraud_data:
                    assert transaction["risk_category"] == "FRAUD"
                
                # Test alert system integration
                response = client.get("/alerts/statistics")
                assert response.status_code == 200
                
                # Test AI explainer integration (mocked)
                transaction_id = processed_dataset.iloc[0]['transaction_id']
                with patch('api.explain_transaction') as mock_explain:
                    mock_explain.return_value = "Integration test explanation"
                    
                    response = client.post(f"/explain/{transaction_id}")
                    assert response.status_code == 200
                    assert mock_explain.called

    def test_api_concurrent_write_operations(self, client, processed_dataset):
        """Test concurrent write operations (session reset, cache clear, alert dismissal)."""
        import threading
        
        results = []
        errors = []
        
        def reset_session():
            try:
                response = client.post("/session/reset")
                results.append(("reset", response.status_code))
            except Exception as e:
                errors.append(("reset", str(e)))
        
        def clear_cache():
            try:
                response = client.post("/cache/clear")
                results.append(("cache", response.status_code))
            except Exception as e:
                errors.append(("cache", str(e)))
        
        with patch('api._transactions_df', processed_dataset):
            threads = []
            
            # Create multiple threads for concurrent operations
            for _ in range(3):
                threads.append(threading.Thread(target=reset_session))
                threads.append(threading.Thread(target=clear_cache))
            
            # Start all threads
            for thread in threads:
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            # Verify no errors occurred
            assert len(errors) == 0, f"Errors occurred: {errors}"
            
            # Verify all operations succeeded
            for operation, status_code in results:
                assert status_code == 200, f"{operation} failed with status {status_code}"

    def test_api_data_consistency_after_operations(self, client, processed_dataset):
        """Test data consistency after various API operations."""
        
        with patch('api._transactions_df', processed_dataset):
            # Get initial stats
            response1 = client.get("/stats")
            stats1 = response1.json()["data"]
            
            # Perform various operations
            client.get("/transactions?limit=50")
            client.get("/suspicious")
            client.get("/fraud")
            client.post("/session/reset")
            
            # Get stats again
            response2 = client.get("/stats")
            stats2 = response2.json()["data"]
            
            # Core statistics should remain consistent
            assert stats1["total_transactions"] == stats2["total_transactions"]
            assert stats1["fraud_cases"] == stats2["fraud_cases"]
            assert stats1["suspicious_cases"] == stats2["suspicious_cases"]

    def test_api_endpoint_accessibility(self, client):
        """Test that all documented API endpoints are accessible."""
        
        # Test all GET endpoints that don't require data
        get_endpoints = [
            "/",
            "/session/info",
        ]
        
        for endpoint in get_endpoints:
            response = client.get(endpoint)
            # Should not return 404
            assert response.status_code != 404, f"Endpoint {endpoint} not found"

    def test_api_json_content_type(self, client, processed_dataset):
        """Test that all API responses have correct JSON content type."""
        
        with patch('api._transactions_df', processed_dataset):
            endpoints = [
                "/",
                "/transactions",
                "/suspicious",
                "/fraud",
                "/stats",
                "/session/info"
            ]
            
            for endpoint in endpoints:
                response = client.get(endpoint)
                assert response.status_code == 200
                
                # Verify content type is JSON
                content_type = response.headers.get("content-type", "")
                assert "application/json" in content_type.lower()

    def test_api_integration_with_empty_dataset(self, client):
        """Test API behavior with empty dataset."""
        
        empty_df = pd.DataFrame()
        
        with patch('api._transactions_df', empty_df):
            # Should handle empty dataset gracefully
            response = client.get("/transactions")
            # May return empty list or error depending on implementation
            assert response.status_code in [200, 500]
            
            if response.status_code == 200:
                data = response.json()
                # Should return empty or handle gracefully
                assert "data" in data

    def test_api_large_dataset_handling(self, client, sample_dataset):
        """Test API handling of large dataset with pagination."""
        
        # Create a larger dataset
        large_dataset = pd.concat([sample_dataset] * 10, ignore_index=True)
        large_dataset['transaction_id'] = [f'TXN{i:05d}' for i in range(len(large_dataset))]
        
        # Add required ML columns
        large_dataset['risk_score'] = np.random.uniform(-1, 1, len(large_dataset))
        large_dataset['risk_category'] = np.random.choice(['SAFE', 'SUSPICIOUS', 'FRAUD'], len(large_dataset))
        
        with patch('api._transactions_df', large_dataset):
            # Test pagination with large dataset
            response = client.get("/transactions?limit=100&offset=0")
            assert response.status_code == 200
            
            data = response.json()["data"]
            assert "pagination" in data
            assert data["pagination"]["total"] == len(large_dataset)
            assert len(data["transactions"]) <= 100

    def test_api_special_characters_handling(self, client, processed_dataset):
        """Test API handling of special characters in inputs."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test query with special characters
            special_queries = [
                "What's the fraud rate?",
                "Show me transactions > $1000",
                "Find transactions with 'suspicious' patterns",
                "Transactions from 2024-01-01"
            ]
            
            for query in special_queries:
                response = client.post("/query", json={"query": query})
                # Should handle gracefully without crashing
                assert response.status_code in [200, 400, 422, 500]

    def test_api_boundary_conditions(self, client, processed_dataset):
        """Test API with boundary condition values."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test maximum pagination limit
            response = client.get("/transactions?limit=1000")
            assert response.status_code == 200
            
            # Test zero offset
            response = client.get("/transactions?offset=0")
            assert response.status_code == 200
            
            # Test large offset (beyond dataset size)
            response = client.get("/transactions?offset=999999")
            assert response.status_code == 200
            data = response.json()["data"]
            # Should return empty list or handle gracefully
            assert "transactions" in data

    def test_api_response_schema_validation(self, client, processed_dataset):
        """Test comprehensive response schema validation for all endpoints."""
        
        with patch('api._transactions_df', processed_dataset):
            # Test transactions endpoint schema
            response = client.get("/transactions?limit=1")
            assert response.status_code == 200
            data = response.json()
            
            # Validate APIResponse schema
            assert "status" in data
            assert data["status"] == "success"
            assert "data" in data
            assert "message" in data
            
            # Validate nested structure
            response_data = data["data"]
            assert "transactions" in response_data
            assert "pagination" in response_data
            
            pagination = response_data["pagination"]
            assert "total" in pagination
            assert "limit" in pagination
            assert "offset" in pagination
            assert "returned" in pagination
            
            # Test stats endpoint schema
            response = client.get("/stats")
            assert response.status_code == 200
            stats = response.json()["data"]
            
            required_stats_fields = [
                "total_transactions",
                "fraud_cases",
                "suspicious_cases",
                "safe_cases",
                "fraud_rate",
                "suspicious_rate",
                "avg_risk_score"
            ]
            
            for field in required_stats_fields:
                assert field in stats, f"Missing required stats field: {field}"


if __name__ == "__main__":
    # Run tests and exit cleanly
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    sys.exit(exit_code)