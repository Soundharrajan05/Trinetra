"""
Unit Tests for Helper Utilities Module - TRINETRA AI

This module contains comprehensive unit tests for the utils/helpers.py module,
testing data formatting, validation, logging, and performance tracking utilities.
"""

import pytest
import pandas as pd
import numpy as np
import logging
from datetime import datetime, date
from unittest.mock import patch, MagicMock
import tempfile
import os

# Import the module under test
from utils.helpers import (
    DataFormatter, ValidationHelpers, PerformanceTracker,
    setup_logging, log_system_startup, log_system_shutdown,
    TimedOperation, performance_tracker
)


class TestDataFormatter:
    """Test class for DataFormatter utility functions."""
    
    def test_format_currency_basic(self):
        """Test basic currency formatting."""
        assert DataFormatter.format_currency(1234.56) == "$1,234.56"
        assert DataFormatter.format_currency(1000000) == "$1,000,000.00"
        assert DataFormatter.format_currency(0) == "$0.00"
        assert DataFormatter.format_currency(0.99) == "$0.99"
    
    def test_format_currency_edge_cases(self):
        """Test currency formatting with edge cases."""
        assert DataFormatter.format_currency(None) == "$0.00"
        assert DataFormatter.format_currency("") == "$0.00"
        assert DataFormatter.format_currency("1234.56") == "$1,234.56"
        assert DataFormatter.format_currency(np.nan) == "$0.00"
        assert DataFormatter.format_currency(float('inf')) == "$0.00"
    
    def test_format_currency_custom_parameters(self):
        """Test currency formatting with custom parameters."""
        assert DataFormatter.format_currency(1234.567, precision=3) == "$1,234.567"
        assert DataFormatter.format_currency(1234.56, symbol="€") == "€1,234.56"
        assert DataFormatter.format_currency(1234.56, include_commas=False) == "$1234.56"
    
    def test_format_percentage_basic(self):
        """Test basic percentage formatting."""
        assert DataFormatter.format_percentage(0.1534) == "15.34%"
        assert DataFormatter.format_percentage(-0.05) == "-5.00%"
        assert DataFormatter.format_percentage(0) == "0.00%"
        assert DataFormatter.format_percentage(1) == "100.00%"
    
    def test_format_percentage_edge_cases(self):
        """Test percentage formatting with edge cases."""
        assert DataFormatter.format_percentage(None) == "0.00%"
        assert DataFormatter.format_percentage("") == "0.00%"
        assert DataFormatter.format_percentage("0.15") == "15.00%"
        assert DataFormatter.format_percentage(np.nan) == "0.00%"
        assert DataFormatter.format_percentage(float('inf')) == "0.00%"
    
    def test_format_percentage_custom_parameters(self):
        """Test percentage formatting with custom parameters."""
        assert DataFormatter.format_percentage(0.1534, precision=1) == "15.3%"
        assert DataFormatter.format_percentage(0.1534, include_sign=False) == "15.34"
    
    def test_format_decimal_basic(self):
        """Test basic decimal formatting."""
        assert DataFormatter.format_decimal(3.14159, precision=2) == "3.14"
        assert DataFormatter.format_decimal(1234.5678) == "1234.5678"
        assert DataFormatter.format_decimal(0) == "0.0000"
    
    def test_format_decimal_edge_cases(self):
        """Test decimal formatting with edge cases."""
        assert DataFormatter.format_decimal(None) == "0.0000"
        assert DataFormatter.format_decimal("") == "0.0000"
        assert DataFormatter.format_decimal("123.456") == "123.4560"
        assert DataFormatter.format_decimal(np.nan) == "N/A"
        assert DataFormatter.format_decimal(float('inf')) == "∞"
        assert DataFormatter.format_decimal(float('-inf')) == "-∞"
    
    def test_format_decimal_with_commas(self):
        """Test decimal formatting with comma separators."""
        result = DataFormatter.format_decimal(1234.5678, include_commas=True)
        assert result == "1,234.5678"
    
    def test_format_date_basic(self):
        """Test basic date formatting."""
        test_date = datetime(2024, 1, 15)
        assert DataFormatter.format_date(test_date) == "2024-01-15"
        
        test_date_obj = date(2024, 1, 15)
        assert DataFormatter.format_date(test_date_obj) == "2024-01-15"
    
    def test_format_date_string_input(self):
        """Test date formatting with string input."""
        assert DataFormatter.format_date("2024-01-15") == "2024-01-15"
        assert DataFormatter.format_date("01/15/2024") == "2024-01-15"
    
    def test_format_date_edge_cases(self):
        """Test date formatting with edge cases."""
        assert DataFormatter.format_date(None) == "N/A"
        assert DataFormatter.format_date("") == "N/A"
        assert DataFormatter.format_date("invalid_date") == "N/A"
    
    def test_format_date_custom_format(self):
        """Test date formatting with custom format."""
        test_date = datetime(2024, 1, 15)
        result = DataFormatter.format_date(test_date, "%B %d, %Y")
        assert result == "January 15, 2024"
    
    def test_format_risk_score_basic(self):
        """Test basic risk score formatting."""
        assert DataFormatter.format_risk_score(0.234) == "0.234"
        assert DataFormatter.format_risk_score(-0.123) == "-0.123"
        assert DataFormatter.format_risk_score(0) == "0.000"
    
    def test_format_risk_score_with_category(self):
        """Test risk score formatting with category."""
        result = DataFormatter.format_risk_score(0.5, include_category=True)
        assert "0.500" in result
        assert "FRAUD" in result
        
        result = DataFormatter.format_risk_score(-0.3, include_category=True)
        assert "SAFE" in result
    
    def test_format_risk_score_edge_cases(self):
        """Test risk score formatting with edge cases."""
        assert DataFormatter.format_risk_score(None) == "N/A"
        assert DataFormatter.format_risk_score("") == "N/A"
        assert DataFormatter.format_risk_score("0.234") == "0.234"
        assert DataFormatter.format_risk_score(np.nan) == "N/A"
        assert DataFormatter.format_risk_score(float('inf')) == "∞"
    
    def test_get_risk_category(self):
        """Test risk category determination."""
        assert DataFormatter.get_risk_category(-0.5) == "SAFE"
        assert DataFormatter.get_risk_category(-0.2) == "SAFE"
        assert DataFormatter.get_risk_category(0.0) == "SUSPICIOUS"
        assert DataFormatter.get_risk_category(0.1) == "SUSPICIOUS"
        assert DataFormatter.get_risk_category(0.3) == "FRAUD"
        assert DataFormatter.get_risk_category(1.0) == "FRAUD"
    
    def test_get_risk_category_edge_cases(self):
        """Test risk category with edge cases."""
        assert DataFormatter.get_risk_category(None) == "UNKNOWN"
        assert DataFormatter.get_risk_category("") == "UNKNOWN"
        assert DataFormatter.get_risk_category("0.1") == "SUSPICIOUS"
        assert DataFormatter.get_risk_category(np.nan) == "UNKNOWN"
        assert DataFormatter.get_risk_category(float('inf')) == "UNKNOWN"
    
    def test_format_transaction_for_display(self):
        """Test transaction formatting for display."""
        transaction = {
            'transaction_id': 'TXN001',
            'date': '2024-01-15',
            'product': 'Electronics',
            'quantity': 100,
            'unit_price': 10.50,
            'risk_score': 0.234
        }
        
        result = DataFormatter.format_transaction_for_display(transaction)
        
        assert isinstance(result, dict)
        assert result['transaction_id'] == 'TXN001'
        assert result['product'] == 'Electronics'
        assert '$' in result['unit_price']
        assert result['risk_category'] in ['SAFE', 'SUSPICIOUS', 'FRAUD']
    
    def test_format_transaction_for_api(self):
        """Test transaction formatting for API responses."""
        transaction = {
            'transaction_id': 'TXN001',
            'quantity': '100',  # String number
            'unit_price': 10.50,
            'risk_score': 0.234,
            'invalid_field': np.nan
        }
        
        result = DataFormatter.format_transaction_for_api(transaction)
        
        assert isinstance(result, dict)
        assert result['transaction_id'] == 'TXN001'
        assert isinstance(result['quantity'], float)
        assert isinstance(result['unit_price'], float)
        assert result['risk_category'] in ['SAFE', 'SUSPICIOUS', 'FRAUD']


class TestValidationHelpers:
    """Test class for ValidationHelpers utility functions."""
    
    def test_validate_dataset_schema_success(self):
        """Test successful dataset schema validation."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02']),
            'product': ['A', 'B'],
            'commodity_category': ['C', 'D'],
            'quantity': [100, 200],
            'unit_price': [10.0, 20.0],
            'trade_value': [1000.0, 4000.0],
            'market_price': [9.0, 19.0]
        })
        
        result = ValidationHelpers.validate_dataset_schema(df, strict=False)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert result['row_count'] == 2
        assert result['column_count'] == 8
    
    def test_validate_dataset_schema_missing_columns(self):
        """Test dataset schema validation with missing columns."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'date': ['2024-01-01']
            # Missing other required columns
        })
        
        result = ValidationHelpers.validate_dataset_schema(df, strict=False)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert any("Missing required columns" in error for error in result['errors'])
    
    def test_validate_dataset_schema_empty_dataframe(self):
        """Test dataset schema validation with empty DataFrame."""
        df = pd.DataFrame()
        
        result = ValidationHelpers.validate_dataset_schema(df)
        
        assert result['valid'] is False
        assert any("empty" in error.lower() for error in result['errors'])
    
    def test_validate_transaction_data_success(self):
        """Test successful transaction data validation."""
        transaction = {
            'transaction_id': 'TXN001',
            'date': '2024-01-01',
            'product': 'Electronics',
            'commodity_category': 'Consumer',
            'quantity': 100,
            'unit_price': 10.50,
            'trade_value': 1050.0,
            'market_price': 10.0
        }
        
        result = ValidationHelpers.validate_transaction_data(transaction)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_transaction_data_missing_fields(self):
        """Test transaction validation with missing required fields."""
        transaction = {
            'transaction_id': 'TXN001'
            # Missing other required fields
        }
        
        result = ValidationHelpers.validate_transaction_data(transaction)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
    
    def test_validate_transaction_data_invalid_types(self):
        """Test transaction validation with invalid data types."""
        transaction = {
            'transaction_id': 'TXN001',
            'date': '2024-01-01',
            'product': 'Electronics',
            'commodity_category': 'Consumer',
            'quantity': 'invalid_number',  # Invalid numeric value
            'unit_price': 10.50,
            'trade_value': 1050.0,
            'market_price': 10.0
        }
        
        result = ValidationHelpers.validate_transaction_data(transaction)
        
        assert result['valid'] is False
        assert any("Invalid numeric value" in error for error in result['errors'])
    
    def test_validate_api_input_query_endpoint(self):
        """Test API input validation for query endpoint."""
        # Valid input
        valid_input = {'query': 'What is the fraud rate?'}
        result = ValidationHelpers.validate_api_input(valid_input, 'query')
        assert result['valid'] is True
        
        # Missing query
        invalid_input = {}
        result = ValidationHelpers.validate_api_input(invalid_input, 'query')
        assert result['valid'] is False
        
        # Empty query
        empty_input = {'query': ''}
        result = ValidationHelpers.validate_api_input(empty_input, 'query')
        assert result['valid'] is False
    
    def test_validate_api_input_explain_endpoint(self):
        """Test API input validation for explain endpoint."""
        # Valid input
        valid_input = {'transaction_id': 'TXN001', 'force_ai': True}
        result = ValidationHelpers.validate_api_input(valid_input, 'explain')
        assert result['valid'] is True
        
        # Missing transaction_id
        invalid_input = {'force_ai': True}
        result = ValidationHelpers.validate_api_input(invalid_input, 'explain')
        assert result['valid'] is False
    
    def test_validate_feature_data_success(self):
        """Test successful feature data validation."""
        df = pd.DataFrame({
            'price_anomaly_score': [0.1, 0.2, 0.3],
            'route_risk_score': [0, 1, 0],
            'company_network_risk': [0.2, 0.5, 0.8],
            'port_congestion_score': [1.0, 2.0, 1.5],
            'shipment_duration_risk': [0.05, 0.1, 0.08],
            'volume_spike_score': [10.0, 20.0, 15.0]
        })
        
        result = ValidationHelpers.validate_feature_data(df)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert result['feature_count'] == 6
    
    def test_validate_feature_data_missing_features(self):
        """Test feature data validation with missing features."""
        df = pd.DataFrame({
            'price_anomaly_score': [0.1, 0.2, 0.3]
            # Missing other required features
        })
        
        result = ValidationHelpers.validate_feature_data(df)
        
        assert result['valid'] is False
        assert any("Missing required features" in error for error in result['errors'])
    
    def test_validate_configuration_success(self):
        """Test successful configuration validation."""
        config = {
            'gemini_api_key': 'valid_api_key_12345',
            'risk_thresholds': {
                'safe_threshold': -0.2,
                'suspicious_threshold': 0.0,
                'fraud_threshold': 0.2
            },
            'alert_thresholds': {
                'price_deviation_threshold': 0.5,
                'company_risk_threshold': 0.8,
                'port_activity_threshold': 1.5
            }
        }
        
        result = ValidationHelpers.validate_configuration(config)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_configuration_missing_keys(self):
        """Test configuration validation with missing keys."""
        config = {
            'gemini_api_key': 'valid_api_key_12345'
            # Missing other required keys
        }
        
        result = ValidationHelpers.validate_configuration(config)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0


class TestPerformanceTracker:
    """Test class for PerformanceTracker functionality."""
    
    def test_performance_tracker_initialization(self):
        """Test performance tracker initialization."""
        tracker = PerformanceTracker()
        
        assert isinstance(tracker.metrics, dict)
        assert tracker.metrics['dataset_loads'] == 0
        assert tracker.metrics['model_trainings'] == 0
        assert tracker.metrics['api_calls'] == 0
    
    def test_log_dataset_load(self):
        """Test dataset load logging."""
        tracker = PerformanceTracker()
        
        tracker.log_dataset_load(2.5, 1000, "test_dataset.csv")
        
        assert tracker.metrics['dataset_loads'] == 1
        assert tracker.metrics['total_dataset_load_time'] == 2.5
    
    def test_log_model_training(self):
        """Test model training logging."""
        tracker = PerformanceTracker()
        
        tracker.log_model_training(30.0, "IsolationForest", 6)
        
        assert tracker.metrics['model_trainings'] == 1
        assert tracker.metrics['total_model_training_time'] == 30.0
    
    def test_log_api_response(self):
        """Test API response logging."""
        tracker = PerformanceTracker()
        
        tracker.log_api_response("/transactions", 0.5, 200)
        
        assert tracker.metrics['api_calls'] == 1
        assert tracker.metrics['total_api_response_time'] == 0.5
    
    def test_log_gemini_call_success(self):
        """Test successful Gemini call logging."""
        tracker = PerformanceTracker()
        
        tracker.log_gemini_call(True, 2.0)
        
        assert tracker.metrics['gemini_calls'] == 1
        assert tracker.metrics['gemini_successes'] == 1
        assert tracker.metrics['gemini_failures'] == 0
    
    def test_log_gemini_call_failure(self):
        """Test failed Gemini call logging."""
        tracker = PerformanceTracker()
        
        tracker.log_gemini_call(False, 1.5, "API error")
        
        assert tracker.metrics['gemini_calls'] == 1
        assert tracker.metrics['gemini_successes'] == 0
        assert tracker.metrics['gemini_failures'] == 1
    
    def test_get_performance_summary(self):
        """Test performance summary generation."""
        tracker = PerformanceTracker()
        
        # Log some metrics
        tracker.log_dataset_load(2.0, 1000, "test.csv")
        tracker.log_model_training(25.0, "IsolationForest", 6)
        tracker.log_gemini_call(True, 1.5)
        
        summary = tracker.get_performance_summary()
        
        assert isinstance(summary, dict)
        assert 'dataset_loads' in summary
        assert 'avg_dataset_load_time' in summary
        assert 'gemini_success_rate' in summary
        assert summary['dataset_loads'] == 1
        assert summary['avg_dataset_load_time'] == 2.0
    
    def test_reset_metrics(self):
        """Test metrics reset functionality."""
        tracker = PerformanceTracker()
        
        # Log some metrics
        tracker.log_dataset_load(2.0, 1000, "test.csv")
        tracker.log_model_training(25.0, "IsolationForest", 6)
        
        # Reset
        tracker.reset_metrics()
        
        assert tracker.metrics['dataset_loads'] == 0
        assert tracker.metrics['model_trainings'] == 0
        assert tracker.metrics['total_dataset_load_time'] == 0.0


class TestLoggingUtilities:
    """Test class for logging utility functions."""
    
    def test_setup_logging(self):
        """Test logging setup."""
        logger = setup_logging(log_level="INFO")
        
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO
    
    @patch('utils.helpers.logger')
    def test_log_system_startup(self, mock_logger):
        """Test system startup logging."""
        log_system_startup()
        
        assert mock_logger.info.called
        # Check that startup messages were logged
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("TRINETRA AI" in call for call in log_calls)
    
    @patch('utils.helpers.logger')
    @patch('utils.helpers.performance_tracker')
    def test_log_system_shutdown(self, mock_tracker, mock_logger):
        """Test system shutdown logging."""
        log_system_shutdown()
        
        assert mock_logger.info.called
        assert mock_tracker.get_performance_summary.called
    
    def test_timed_operation_success(self):
        """Test timed operation context manager with success."""
        with patch('utils.helpers.logger') as mock_logger:
            with TimedOperation("test operation", mock_logger) as timer:
                # Simulate some work
                import time
                time.sleep(0.01)
            
            # Check that start and completion messages were logged
            assert mock_logger.info.call_count >= 2
    
    def test_timed_operation_with_exception(self):
        """Test timed operation context manager with exception."""
        with patch('utils.helpers.logger') as mock_logger:
            try:
                with TimedOperation("test operation", mock_logger) as timer:
                    raise ValueError("Test exception")
            except ValueError:
                pass
            
            # Check that error message was logged
            assert mock_logger.error.called


class TestHelpersIntegration:
    """Integration tests for helper utilities."""
    
    def test_complete_transaction_formatting_workflow(self):
        """Test complete transaction formatting workflow."""
        # Raw transaction data
        raw_transaction = {
            'transaction_id': 'TXN001',
            'date': '2024-01-15',
            'product': 'Electronics',
            'quantity': '100',  # String number
            'unit_price': 10.50,
            'market_price': 10.00,
            'price_deviation': 0.05,
            'risk_score': 0.234
        }
        
        # Format for display
        display_format = DataFormatter.format_transaction_for_display(raw_transaction)
        assert '$' in display_format['unit_price']
        assert display_format['risk_category'] in ['SAFE', 'SUSPICIOUS', 'FRAUD']
        
        # Format for API
        api_format = DataFormatter.format_transaction_for_api(raw_transaction)
        assert isinstance(api_format['quantity'], float)
        assert isinstance(api_format['unit_price'], float)
        
        # Validate transaction
        validation_result = ValidationHelpers.validate_transaction_data(raw_transaction)
        assert validation_result['valid'] is True
    
    def test_performance_tracking_workflow(self):
        """Test complete performance tracking workflow."""
        tracker = PerformanceTracker()
        
        # Simulate system operations
        tracker.log_dataset_load(2.5, 1000, "dataset.csv")
        tracker.log_model_training(30.0, "IsolationForest", 6)
        tracker.log_api_response("/transactions", 0.5, 200)
        tracker.log_gemini_call(True, 2.0)
        tracker.log_gemini_call(False, 1.5, "Error")
        
        # Get summary
        summary = tracker.get_performance_summary()
        
        assert summary['dataset_loads'] == 1
        assert summary['model_trainings'] == 1
        assert summary['api_calls'] == 1
        assert summary['gemini_calls'] == 2
        assert summary['gemini_success_rate'] == 50.0  # 1 success out of 2 calls
    
    def test_validation_workflow_with_errors(self):
        """Test validation workflow with various error conditions."""
        # Test dataset with multiple issues
        problematic_df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN001'],  # Duplicate IDs
            'quantity': ['invalid', 100],  # Invalid numeric
            'unit_price': [10.0, np.nan]  # Missing value
        })
        
        result = ValidationHelpers.validate_dataset_schema(problematic_df, strict=False)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0 or len(result['warnings']) > 0
        
        # Test transaction with issues
        problematic_transaction = {
            'transaction_id': '',  # Empty ID
            'quantity': 'invalid',  # Invalid number
            'unit_price': -10.0  # Negative price (might be valid in some contexts)
        }
        
        result = ValidationHelpers.validate_transaction_data(problematic_transaction)
        assert result['valid'] is False
        assert len(result['errors']) > 0


if __name__ == "__main__":
    pytest.main([__file__])