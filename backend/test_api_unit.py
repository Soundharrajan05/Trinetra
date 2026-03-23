"""
Comprehensive Unit Tests for TRINETRA AI API Module

This module contains unit tests for the FastAPI backend functions in api.py.
Tests cover API endpoints, request/response handling, and error scenarios with mocking.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import patch, MagicMock, Mock
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the dependencies before importing the API module
with patch('api.load_dataset'), \
     patch('api.engineer_features'), \
     patch('api.load_fraud_detector'), \
     patch('api.score_transactions'), \
     patch('api.classify_risk'), \
     patch('api.get_alert_store'):
    
    from api import (
        app,
        initialize_system,
        _transactions_df,
        _fraud_detector,
        ExplanationRequest,
        QueryRequest,
        APIResponse,
        SessionInfo
    )

# Create test client
client = TestClient(app)


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mock transaction data
        self.mock_transactions = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'product': ['Electronics', 'Textiles', 'Machinery'],
            'risk_score': [0.1, 0.3, -0.1],
            'risk_category': ['SUSPICIOUS', 'FRAUD', 'SAFE'],
            'price_deviation': [0.2, 0.6, 0.1],
            'company_risk_score': [0.5, 0.9, 0.3]
        })
    
    @patch('api._transactions_df')
    def test_root_endpoint(self, mock_df):
        """Test root endpoint returns system information."""
        mock_df.return_value = self.mock_transactions
        
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'TRINETRA AI' in data['data']['name']
        assert data['data']['version'] == '1.0.0'
    
    @patch('api._transactions_df')
    def test_get_transactions_success(self, mock_df):
        """Test successful transaction retrieval."""
        # Mock the global variable
        with patch('api._transactions_df', self.mock_transactions):
            response = client.get("/transactions?limit=2&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'transactions' in data['data']
        assert 'pagination' in data['data']
        assert data['data']['pagination']['total'] == 3
        assert data['data']['pagination']['limit'] == 2
        assert len(data['data']['transactions']) <= 2
    
    @patch('api._transactions_df', None)
    def test_get_transactions_system_not_initialized(self):
        """Test transaction retrieval when system not initialized."""
        response = client.get("/transactions")
        
        assert response.status_code == 500
        assert "System not initialized" in response.json()['detail']
    
    def test_get_transactions_pagination(self):
        """Test transaction pagination parameters."""
        with patch('api._transactions_df', self.mock_transactions):
            # Test with different pagination parameters
            response = client.get("/transactions?limit=1&offset=1")
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['pagination']['limit'] == 1
        assert data['data']['pagination']['offset'] == 1
        assert len(data['data']['transactions']) == 1
    
    def test_get_transactions_invalid_pagination(self):
        """Test transaction retrieval with invalid pagination."""
        with patch('api._transactions_df', self.mock_transactions):
            # Test with invalid limit (too high)
            response = client.get("/transactions?limit=2000")
        
        assert response.status_code == 422  # Validation error
    
    @patch('api._transactions_df')
    def test_get_suspicious_transactions(self, mock_df):
        """Test retrieval of suspicious transactions."""
        with patch('api._transactions_df', self.mock_transactions):
            response = client.get("/suspicious")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        
        # Should only return SUSPICIOUS transactions
        transactions = data['data']
        for txn in transactions:
            assert txn['risk_category'] == 'SUSPICIOUS'
    
    @patch('api._transactions_df')
    def test_get_fraud_transactions(self, mock_df):
        """Test retrieval of fraud transactions."""
        with patch('api._transactions_df', self.mock_transactions):
            response = client.get("/fraud")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        
        # Should only return FRAUD transactions
        transactions = data['data']
        for txn in transactions:
            assert txn['risk_category'] == 'FRAUD'
    
    @patch('api.explain_transaction')
    def test_explain_transaction_endpoint_success(self, mock_explain):
        """Test successful transaction explanation."""
        mock_explain.return_value = "This transaction is suspicious due to price anomaly."
        
        with patch('api._transactions_df', self.mock_transactions):
            response = client.post(
                "/explain/TXN001",
                json={"force_ai": False}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'explanation' in data['data']
        assert 'explanation_type' in data['data']
        assert 'session_info' in data['data']
    
    def test_explain_transaction_not_found(self):
        """Test explanation for non-existent transaction."""
        with patch('api._transactions_df', self.mock_transactions):
            response = client.post(
                "/explain/NONEXISTENT",
                json={"force_ai": False}
            )
        
        assert response.status_code == 404
        assert "not found" in response.json()['detail']
    
    @patch('api.answer_investigation_query')
    def test_natural_language_query_success(self, mock_query):
        """Test successful natural language query processing."""
        mock_query.return_value = "Based on the data, there are 3 transactions with 1 fraud case."
        
        with patch('api._transactions_df', self.mock_transactions):
            response = client.post(
                "/query",
                json={"query": "How many fraud cases are there?"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'answer' in data['data']
        assert 'context_summary' in data['data']
    
    def test_natural_language_query_invalid_request(self):
        """Test query with invalid request format."""
        response = client.post("/query", json={})  # Missing query field
        
        assert response.status_code == 422  # Validation error
    
    def test_get_statistics_success(self):
        """Test successful statistics retrieval."""
        with patch('api._transactions_df', self.mock_transactions), \
             patch('api.get_alert_store') as mock_alert_store:
            
            # Mock alert store
            mock_store = Mock()
            mock_store.get_statistics.return_value = {'total_alerts': 5}
            mock_alert_store.return_value = mock_store
            
            response = client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'total_transactions' in data['data']
        assert 'fraud_cases' in data['data']
        assert 'fraud_rate' in data['data']
        assert 'session_info' in data['data']
    
    @patch('api.reset_session_count')
    @patch('api.clear_explanation_cache')
    def test_reset_session_success(self, mock_clear, mock_reset):
        """Test successful session reset."""
        response = client.post("/session/reset")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'session_count' in data['data']
        assert 'max_count' in data['data']
        
        # Verify functions were called
        mock_reset.assert_called_once()
        mock_clear.assert_called_once()
    
    @patch('api.get_session_count')
    @patch('api.can_make_explanation')
    def test_get_session_info_success(self, mock_can_make, mock_get_count):
        """Test successful session info retrieval."""
        mock_get_count.return_value = 3
        mock_can_make.return_value = True
        
        response = client.get("/session/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['data']['current_count'] == 3
        assert data['data']['can_make_explanation'] is True


class TestAPIModels:
    """Test cases for Pydantic models."""
    
    def test_explanation_request_model(self):
        """Test ExplanationRequest model validation."""
        # Test with valid data
        request = ExplanationRequest(force_ai=True)
        assert request.force_ai is True
        
        # Test with default value
        request_default = ExplanationRequest()
        assert request_default.force_ai is False
    
    def test_query_request_model(self):
        """Test QueryRequest model validation."""
        request = QueryRequest(query="Test query")
        assert request.query == "Test query"
    
    def test_api_response_model(self):
        """Test APIResponse model validation."""
        response = APIResponse(
            status="success",
            data={"key": "value"},
            message="Test message"
        )
        assert response.status == "success"
        assert response.data == {"key": "value"}
        assert response.message == "Test message"
    
    def test_session_info_model(self):
        """Test SessionInfo model validation."""
        info = SessionInfo(
            current_count=5,
            max_count=10,
            can_make_explanation=True
        )
        assert info.current_count == 5
        assert info.max_count == 10
        assert info.can_make_explanation is True

class TestAlertEndpoints:
    """Test cases for alert-related API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_alert_data = [
            {
                'transaction_id': 'TXN001',
                'alert_type': 'PRICE_ANOMALY',
                'severity': 'HIGH',
                'timestamp': '2024-01-01T12:00:00'
            }
        ]
    
    @patch('api.get_alert_store')
    def test_get_all_alerts_success(self, mock_get_store):
        """Test successful retrieval of all alerts."""
        # Mock alert store
        mock_store = Mock()
        mock_alert = Mock()
        mock_alert.to_dict.return_value = self.mock_alert_data[0]
        mock_store.get_all_alerts.return_value = [mock_alert]
        mock_get_store.return_value = mock_store
        
        response = client.get("/alerts")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'alerts' in data['data']
        assert 'count' in data['data']
        assert data['data']['count'] == 1
    
    @patch('api.get_alert_store')
    def test_get_alerts_by_transaction_success(self, mock_get_store):
        """Test successful retrieval of alerts by transaction."""
        mock_store = Mock()
        mock_alert = Mock()
        mock_alert.to_dict.return_value = self.mock_alert_data[0]
        mock_store.get_alerts_by_transaction.return_value = [mock_alert]
        mock_get_store.return_value = mock_store
        
        response = client.get("/alerts/transaction/TXN001")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['data']['transaction_id'] == 'TXN001'
        assert len(data['data']['alerts']) == 1
    
    @patch('api.get_alert_store')
    def test_get_alerts_by_transaction_not_found(self, mock_get_store):
        """Test retrieval of alerts for non-existent transaction."""
        mock_store = Mock()
        mock_store.get_alerts_by_transaction.return_value = []
        mock_get_store.return_value = mock_store
        
        response = client.get("/alerts/transaction/NONEXISTENT")
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['count'] == 0
        assert len(data['data']['alerts']) == 0
    
    @patch('api.get_alert_store')
    def test_get_alerts_by_priority_success(self, mock_get_store):
        """Test successful retrieval of alerts by priority."""
        mock_store = Mock()
        mock_summary = Mock()
        mock_summary.to_dict.return_value = {
            'transaction_id': 'TXN001',
            'priority': 'HIGH'
        }
        mock_store.get_alerts_by_priority.return_value = [mock_summary]
        mock_get_store.return_value = mock_store
        
        response = client.get("/alerts/priority/HIGH")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['data']['priority'] == 'HIGH'
        assert len(data['data']['summaries']) == 1
    
    def test_get_alerts_by_priority_invalid(self):
        """Test retrieval of alerts with invalid priority."""
        response = client.get("/alerts/priority/INVALID")
        
        assert response.status_code == 400
        assert "Invalid priority level" in response.json()['detail']
    
    @patch('api.get_alert_store')
    def test_get_alert_statistics_success(self, mock_get_store):
        """Test successful retrieval of alert statistics."""
        mock_store = Mock()
        mock_store.get_statistics.return_value = {
            'total_alerts': 10,
            'by_priority': {'HIGH': 3, 'MEDIUM': 5, 'LOW': 2}
        }
        mock_get_store.return_value = mock_store
        
        response = client.get("/alerts/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'total_alerts' in data['data']
    
    @patch('api.get_alert_store')
    def test_dismiss_alert_success(self, mock_get_store):
        """Test successful alert dismissal."""
        mock_store = Mock()
        mock_store.dismiss_alert_summary.return_value = True
        mock_get_store.return_value = mock_store
        
        response = client.post("/alerts/dismiss/TXN001?dismissed_by=analyst")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['data']['dismissed'] is True
        assert data['data']['dismissed_by'] == 'analyst'
    
    @patch('api.get_alert_store')
    def test_dismiss_alert_not_found(self, mock_get_store):
        """Test dismissal of non-existent alert."""
        mock_store = Mock()
        mock_store.dismiss_alert_summary.return_value = False
        mock_get_store.return_value = mock_store
        
        response = client.post("/alerts/dismiss/NONEXISTENT")
        
        assert response.status_code == 404
        assert "No alert found" in response.json()['detail']
    
    @patch('api.get_alert_store')
    def test_undismiss_alert_success(self, mock_get_store):
        """Test successful alert undismissal."""
        mock_store = Mock()
        mock_store.undismiss_alert_summary.return_value = True
        mock_get_store.return_value = mock_store
        
        response = client.post("/alerts/undismiss/TXN001")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['data']['dismissed'] is False


class TestInitializeSystem:
    """Test cases for system initialization."""
    
    @patch('api.load_dataset')
    @patch('api.validate_schema')
    @patch('api.engineer_features')
    @patch('api.load_fraud_detector')
    @patch('api.score_transactions')
    @patch('api.classify_risk')
    @patch('api.get_alert_store')
    def test_initialize_system_success(self, mock_alert_store, mock_classify, 
                                     mock_score, mock_load_detector, mock_engineer,
                                     mock_validate, mock_load):
        """Test successful system initialization."""
        # Mock all dependencies with complete transaction data
        mock_df = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'price_deviation': [0.1],
            'route_anomaly': [0],
            'company_risk_score': [0.3],
            'port_activity_index': [1.0]
        })
        mock_load.return_value = mock_df
        mock_validate.return_value = True
        mock_engineer.return_value = mock_df
        mock_detector = Mock()
        mock_load_detector.return_value = mock_detector
        mock_score.return_value = mock_df
        mock_classify.return_value = mock_df
        
        mock_store = Mock()
        mock_alert_store.return_value = mock_store
        
        # Should not raise any exceptions
        initialize_system()
        
        # Verify all functions were called
        mock_load.assert_called_once()
        mock_validate.assert_called_once()
        mock_engineer.assert_called_once()
        mock_load_detector.assert_called_once()
        mock_score.assert_called_once()
        mock_classify.assert_called_once()
    
    @patch('api.load_dataset')
    def test_initialize_system_load_failure(self, mock_load):
        """Test system initialization with dataset load failure."""
        mock_load.side_effect = Exception("Failed to load dataset")
        
        with pytest.raises(Exception, match="Failed to load dataset"):
            initialize_system()
    
    @patch('api.load_dataset')
    @patch('api.validate_schema')
    def test_initialize_system_validation_failure(self, mock_validate, mock_load):
        """Test system initialization with schema validation failure."""
        mock_load.return_value = pd.DataFrame()
        mock_validate.return_value = False
        
        with pytest.raises(Exception, match="Failed to load dataset"):
            initialize_system()


class TestErrorHandling:
    """Test cases for API error handling."""
    
    def test_api_error_response_format(self):
        """Test that API errors return proper format."""
        # Test with system not initialized
        with patch('api._transactions_df', None):
            response = client.get("/transactions")
        
        assert response.status_code == 500
        error_detail = response.json()
        assert 'detail' in error_detail
        assert isinstance(error_detail['detail'], str)
    
    def test_api_internal_error_handling(self):
        """Test handling of internal API errors."""
        # Test with system not initialized (should return 500)
        with patch('api._transactions_df', None):
            response = client.get("/transactions")
        
        assert response.status_code == 500
        assert "system not initialized" in response.json()['detail'].lower()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])