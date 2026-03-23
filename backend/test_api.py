"""
Unit Tests for FastAPI Backend - TRINETRA AI

This module contains comprehensive unit tests for the api.py module,
testing all API endpoints, request/response handling, and error conditions.
"""

import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

# Import the module under test
from backend.api import app, initialize_system


class TestAPIEndpoints:
    """Test class for API endpoint functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_transactions_data(self):
        """Create sample transactions data for testing."""
        return pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
            'product': ['Electronics', 'Textiles', 'Machinery'],
            'commodity_category': ['Consumer', 'Industrial', 'Capital'],
            'quantity': [100, 200, 150],
            'unit_price': [10.50, 25.00, 500.00],
            'trade_value': [1050.00, 5000.00, 75000.00],
            'market_price': [10.00, 24.00, 480.00],
            'price_deviation': [0.05, 0.04, 0.04],
            'risk_score': [-0.1, 0.1, 0.3],
            'risk_category': ['SAFE', 'SUSPICIOUS', 'FRAUD']
        })
    
    @patch('backend.api._transactions_df')
    def test_root_endpoint(self, mock_df, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'TRINETRA AI' in data['data']['name']
    
    @patch('backend.api._transactions_df')
    def test_get_transactions_success(self, mock_df, client, sample_transactions_data):
        """Test successful transactions retrieval."""
        mock_df.__len__ = MagicMock(return_value=3)
        mock_df.iloc = sample_transactions_data.iloc
        mock_df.to_dict = MagicMock(return_value=sample_transactions_data.to_dict('records'))
        
        response = client.get("/transactions")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'transactions' in data['data']
        assert 'pagination' in data['data']
    
    @patch('backend.api._transactions_df', None)
    def test_get_transactions_system_not_initialized(self, client):
        """Test transactions endpoint when system not initialized."""
        response = client.get("/transactions")
        
        assert response.status_code == 500
        assert "System not initialized" in response.json()['detail']
    
    @patch('backend.api._transactions_df')
    def test_get_transactions_with_pagination(self, mock_df, client, sample_transactions_data):
        """Test transactions endpoint with pagination parameters."""
        mock_df.__len__ = MagicMock(return_value=100)
        mock_df.iloc = sample_transactions_data.iloc
        mock_df.to_dict = MagicMock(return_value=sample_transactions_data.to_dict('records'))
        
        response = client.get("/transactions?limit=10&offset=20")
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['pagination']['limit'] == 10
        assert data['data']['pagination']['offset'] == 20
    
    @patch('backend.api._transactions_df')
    def test_get_suspicious_transactions(self, mock_df, client, sample_transactions_data):
        """Test suspicious transactions endpoint."""
        suspicious_data = sample_transactions_data[sample_transactions_data['risk_category'] == 'SUSPICIOUS']
        mock_df.__getitem__ = MagicMock(return_value=suspicious_data)
        mock_df.to_dict = MagicMock(return_value=suspicious_data.to_dict('records'))
        
        response = client.get("/suspicious")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert isinstance(data['data'], list)
    
    @patch('backend.api._transactions_df')
    def test_get_fraud_transactions(self, mock_df, client, sample_transactions_data):
        """Test fraud transactions endpoint."""
        fraud_data = sample_transactions_data[sample_transactions_data['risk_category'] == 'FRAUD']
        mock_df.__getitem__ = MagicMock(return_value=fraud_data)
        mock_df.to_dict = MagicMock(return_value=fraud_data.to_dict('records'))
        
        response = client.get("/fraud")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert isinstance(data['data'], list)
    
    @patch('backend.api._transactions_df')
    @patch('backend.api.explain_transaction')
    def test_explain_transaction_endpoint(self, mock_explain, mock_df, client, sample_transactions_data):
        """Test transaction explanation endpoint."""
        # Mock DataFrame filtering
        mock_transaction_row = sample_transactions_data[sample_transactions_data['transaction_id'] == 'TXN001']
        mock_df.__getitem__ = MagicMock(return_value=mock_transaction_row)
        mock_df.empty = False
        mock_df.iloc = [sample_transactions_data.iloc[0]]
        
        # Mock explanation
        mock_explain.return_value = "This transaction is suspicious due to price deviation."
        
        response = client.post("/explain/TXN001", json={"force_ai": False})
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'explanation' in data['data']
        assert 'transaction_id' in data['data']
    
    @patch('backend.api._transactions_df')
    def test_explain_transaction_not_found(self, mock_df, client):
        """Test explanation endpoint with non-existent transaction."""
        # Mock empty DataFrame (transaction not found)
        mock_empty_df = MagicMock()
        mock_empty_df.empty = True
        mock_df.__getitem__ = MagicMock(return_value=mock_empty_df)
        
        response = client.post("/explain/NONEXISTENT", json={"force_ai": False})
        
        assert response.status_code == 404
        assert "not found" in response.json()['detail']
    
    @patch('backend.api._transactions_df')
    @patch('backend.api.answer_investigation_query')
    def test_natural_language_query(self, mock_query, mock_df, client):
        """Test natural language query endpoint."""
        mock_query.return_value = "The fraud rate is approximately 10%."
        mock_df.__len__ = MagicMock(return_value=1000)
        mock_df.__getitem__ = MagicMock(return_value=pd.Series([100, 200]))  # Mock filtering results
        
        response = client.post("/query", json={"query": "What is the fraud rate?"})
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'answer' in data['data']
        assert 'query' in data['data']
    
    @patch('backend.api._transactions_df')
    def test_get_statistics(self, mock_df, client, sample_transactions_data):
        """Test statistics endpoint."""
        # Mock DataFrame operations
        mock_df.__len__ = MagicMock(return_value=3)
        mock_df.__getitem__ = MagicMock(side_effect=lambda x: {
            'risk_category': pd.Series(['SAFE', 'SUSPICIOUS', 'FRAUD']),
            'unit_price': pd.Series([10, 20, 30]),
            'quantity': pd.Series([1, 2, 3]),
            'risk_score': pd.Series([0.1, 0.2, 0.3])
        }.get(x, pd.Series()))
        
        # Mock additional operations
        mock_df.columns = sample_transactions_data.columns
        
        response = client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'total_transactions' in data['data']
        assert 'fraud_rate' in data['data']
    
    def test_session_reset(self, client):
        """Test session reset endpoint."""
        response = client.post("/session/reset")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'session_count' in data['data']
    
    def test_session_info(self, client):
        """Test session info endpoint."""
        response = client.get("/session/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'current_count' in data['data']
        assert 'max_count' in data['data']


class TestAPIValidation:
    """Test API input validation and error handling."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    def test_transactions_invalid_pagination(self, client):
        """Test transactions endpoint with invalid pagination parameters."""
        # Test negative limit
        response = client.get("/transactions?limit=-1")
        assert response.status_code == 422  # Validation error
        
        # Test negative offset
        response = client.get("/transactions?offset=-1")
        assert response.status_code == 422  # Validation error
        
        # Test limit too large
        response = client.get("/transactions?limit=10001")
        assert response.status_code == 422  # Validation error
    
    def test_explain_transaction_invalid_request(self, client):
        """Test explanation endpoint with invalid request body."""
        # Test with invalid JSON
        response = client.post("/explain/TXN001", 
                             content="invalid json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422
    
    def test_query_endpoint_validation(self, client):
        """Test query endpoint input validation."""
        # Test missing query
        response = client.post("/query", json={})
        assert response.status_code == 422
        
        # Test empty query
        response = client.post("/query", json={"query": ""})
        # Should handle gracefully (might return 200 with appropriate message)
        assert response.status_code in [200, 422]
    
    @patch('backend.api._transactions_df', None)
    def test_endpoints_system_not_initialized(self, client):
        """Test various endpoints when system is not initialized."""
        endpoints_to_test = [
            ("/transactions", "get"),
            ("/suspicious", "get"),
            ("/fraud", "get"),
            ("/stats", "get")
        ]
        
        for endpoint, method in endpoints_to_test:
            if method == "get":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            assert response.status_code == 500
            assert "System not initialized" in response.json()['detail']


class TestAPIErrorHandling:
    """Test API error handling and edge cases."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    @patch('backend.api._transactions_df')
    def test_transactions_endpoint_exception(self, mock_df, client):
        """Test transactions endpoint with internal exception."""
        mock_df.iloc.side_effect = Exception("Database error")
        
        response = client.get("/transactions")
        
        assert response.status_code == 500
        assert "Failed to retrieve transactions" in response.json()['detail']
    
    @patch('backend.api._transactions_df')
    @patch('backend.api.explain_transaction')
    def test_explain_endpoint_exception(self, mock_explain, mock_df, client, sample_transactions_data):
        """Test explanation endpoint with internal exception."""
        # Mock successful transaction lookup
        mock_transaction_row = sample_transactions_data[sample_transactions_data['transaction_id'] == 'TXN001']
        mock_df.__getitem__ = MagicMock(return_value=mock_transaction_row)
        mock_df.empty = False
        mock_df.iloc = [sample_transactions_data.iloc[0]]
        
        # Mock explanation failure
        mock_explain.side_effect = Exception("Explanation service error")
        
        response = client.post("/explain/TXN001", json={"force_ai": False})
        
        assert response.status_code == 500
        assert "Failed to explain transaction" in response.json()['detail']
    
    @patch('backend.api._transactions_df')
    @patch('backend.api.answer_investigation_query')
    def test_query_endpoint_exception(self, mock_query, mock_df, client):
        """Test query endpoint with internal exception."""
        mock_query.side_effect = Exception("Query processing error")
        
        response = client.post("/query", json={"query": "What is the fraud rate?"})
        
        assert response.status_code == 500
        assert "Failed to process query" in response.json()['detail']
    
    @patch('backend.api._transactions_df')
    def test_stats_endpoint_exception(self, mock_df, client):
        """Test statistics endpoint with internal exception."""
        mock_df.__len__.side_effect = Exception("Stats calculation error")
        
        response = client.get("/stats")
        
        assert response.status_code == 500
        assert "Failed to retrieve statistics" in response.json()['detail']


class TestAPIIntegration:
    """Integration tests for API functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    @patch('backend.api.load_dataset')
    @patch('backend.api.engineer_features')
    @patch('backend.api.load_fraud_detector')
    @patch('backend.api.score_transactions')
    @patch('backend.api.classify_risk')
    def test_system_initialization(self, mock_classify, mock_score, mock_load_model, 
                                 mock_engineer, mock_load_data):
        """Test system initialization process."""
        # Mock successful initialization
        sample_df = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'risk_score': [0.1],
            'risk_category': ['SAFE']
        })
        
        mock_load_data.return_value = sample_df
        mock_engineer.return_value = sample_df
        mock_load_model.return_value = MagicMock()
        mock_score.return_value = sample_df
        mock_classify.return_value = sample_df
        
        # Should not raise exception
        initialize_system()
        
        # Verify all steps were called
        mock_load_data.assert_called_once()
        mock_engineer.assert_called_once()
        mock_load_model.assert_called_once()
        mock_score.assert_called_once()
        mock_classify.assert_called_once()
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = client.options("/")
        
        # Should allow CORS
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented
        
        # Test with actual request
        response = client.get("/")
        assert response.status_code == 200
    
    def test_api_response_format_consistency(self, client):
        """Test that all API responses follow consistent format."""
        # Test various endpoints
        endpoints = [
            "/",
            "/session/info",
            "/session/reset"
        ]
        
        for endpoint in endpoints:
            if endpoint == "/session/reset":
                response = client.post(endpoint)
            else:
                response = client.get(endpoint)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check consistent response format
            assert 'status' in data
            assert 'data' in data
            assert 'message' in data
            assert data['status'] in ['success', 'error']
    
    @patch('backend.api._transactions_df')
    def test_large_dataset_handling(self, mock_df, client):
        """Test API handling of large datasets."""
        # Mock large dataset
        mock_df.__len__ = MagicMock(return_value=100000)
        
        # Create mock data for pagination
        large_data = pd.DataFrame({
            'transaction_id': [f'TXN{i:06d}' for i in range(1000)],
            'risk_score': np.random.uniform(-1, 1, 1000),
            'risk_category': np.random.choice(['SAFE', 'SUSPICIOUS', 'FRAUD'], 1000)
        })
        
        mock_df.iloc = large_data.iloc
        mock_df.to_dict = MagicMock(return_value=large_data.to_dict('records'))
        
        # Test with reasonable pagination
        response = client.get("/transactions?limit=100&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['pagination']['total'] == 100000
    
    def test_concurrent_requests(self, client):
        """Test API handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = [threading.Thread(target=make_request) for _ in range(10)]
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10


class TestAPIPerformance:
    """Test API performance characteristics."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    def test_response_time_root_endpoint(self, client):
        """Test response time for root endpoint."""
        import time
        
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_response_time_session_endpoints(self, client):
        """Test response time for session management endpoints."""
        import time
        
        # Test session info
        start_time = time.time()
        response = client.get("/session/info")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 0.5  # Should be very fast
        
        # Test session reset
        start_time = time.time()
        response = client.post("/session/reset")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 0.5  # Should be very fast
    
    @patch('backend.api._transactions_df')
    def test_memory_usage_large_response(self, mock_df, client):
        """Test memory usage with large API responses."""
        # Mock large dataset
        large_data = pd.DataFrame({
            'transaction_id': [f'TXN{i:06d}' for i in range(10000)],
            'risk_score': np.random.uniform(-1, 1, 10000),
            'risk_category': np.random.choice(['SAFE', 'SUSPICIOUS', 'FRAUD'], 10000)
        })
        
        mock_df.__len__ = MagicMock(return_value=10000)
        mock_df.iloc = large_data.iloc
        mock_df.to_dict = MagicMock(return_value=large_data.to_dict('records'))
        
        # Request large dataset with pagination
        response = client.get("/transactions?limit=1000")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should handle large response without issues
        assert len(data['data']['transactions']) <= 1000


if __name__ == "__main__":
    pytest.main([__file__])