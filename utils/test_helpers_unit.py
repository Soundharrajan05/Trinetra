"""
Comprehensive Unit Tests for TRINETRA AI Helpers Module

This module contains unit tests for the utility functions in utils/helpers.py.
Tests cover data formatting, logging, performance tracking, and error handling utilities.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
import tempfile
import logging
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, date
from pathlib import Path

# Add the utils directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import (
    DataFormatter,
    PerformanceTracker,
    TimedOperation,
    setup_logging,
    log_system_startup,
    log_system_shutdown,
    log_error_with_context,
    log_configuration_info,
    performance_tracker,
    CURRENCY_SYMBOL,
    PERCENTAGE_PRECISION,
    DECIMAL_PRECISION,
    DATE_FORMAT,
    DATETIME_FORMAT,
    RISK_COLORS,
    PRIORITY_COLORS
)


class TestDataFormatter:
    """Test cases for the DataFormatter class."""
    
    def test_format_currency_basic(self):
        """Test basic currency formatting."""
        assert DataFormatter.format_currency(1234.56) == "$1,234.56"
        assert DataFormatter.format_currency(1000000) == "$1,000,000.00"
        assert DataFormatter.format_currency(0) == "$0.00"
        assert DataFormatter.format_currency(0.99) == "$0.99"
    
    def test_format_currency_custom_symbol(self):
        """Test currency formatting with custom symbol."""
        assert DataFormatter.format_currency(100, symbol="€") == "€100.00"
        assert DataFormatter.format_currency(1234.56, symbol="£") == "£1,234.56"
    
    def test_format_currency_custom_precision(self):
        """Test currency formatting with custom precision."""
        assert DataFormatter.format_currency(1234.567, precision=0) == "$1,235"
        assert DataFormatter.format_currency(1234.567, precision=3) == "$1,234.567"
    
    def test_format_currency_no_commas(self):
        """Test currency formatting without commas."""
        assert DataFormatter.format_currency(1234.56, include_commas=False) == "$1234.56"
    
    def test_format_currency_special_values(self):
        """Test currency formatting with special values."""
        assert DataFormatter.format_currency(None) == "$0.00"
        assert DataFormatter.format_currency("") == "$0.00"
        assert DataFormatter.format_currency(np.nan) == "$0.00"
        assert DataFormatter.format_currency(float('inf')) == "$0.00"
    
    def test_format_currency_string_input(self):
        """Test currency formatting with string input."""
        assert DataFormatter.format_currency("1234.56") == "$1,234.56"
        assert DataFormatter.format_currency("$1,234.56") == "$1,234.56"  # Remove existing symbols
        assert DataFormatter.format_currency("invalid") == "$0.00"
    
    def test_format_percentage_basic(self):
        """Test basic percentage formatting."""
        assert DataFormatter.format_percentage(0.1534) == "15.34%"
        assert DataFormatter.format_percentage(0.5) == "50.00%"
        assert DataFormatter.format_percentage(-0.05) == "-5.00%"
        assert DataFormatter.format_percentage(0) == "0.00%"
    
    def test_format_percentage_custom_precision(self):
        """Test percentage formatting with custom precision."""
        assert DataFormatter.format_percentage(0.1534, precision=1) == "15.3%"
        assert DataFormatter.format_percentage(0.1534, precision=3) == "15.340%"
    
    def test_format_percentage_no_sign(self):
        """Test percentage formatting without % sign."""
        assert DataFormatter.format_percentage(0.15, include_sign=False) == "15.00"
    
    def test_format_percentage_special_values(self):
        """Test percentage formatting with special values."""
        assert DataFormatter.format_percentage(None) == "0.00%"
        assert DataFormatter.format_percentage("") == "0.00%"
        assert DataFormatter.format_percentage(np.nan) == "0.00%"
        assert DataFormatter.format_percentage(float('inf')) == "0.00%"
    
    def test_format_decimal_basic(self):
        """Test basic decimal formatting."""
        assert DataFormatter.format_decimal(3.14159, precision=2) == "3.14"
        assert DataFormatter.format_decimal(1234.5678) == "1234.5678"
        assert DataFormatter.format_decimal(0) == "0.0000"
    
    def test_format_decimal_with_commas(self):
        """Test decimal formatting with commas."""
        assert DataFormatter.format_decimal(1234.5678, include_commas=True) == "1,234.5678"
    
    def test_format_decimal_special_values(self):
        """Test decimal formatting with special values."""
        assert DataFormatter.format_decimal(None) == "0.0000"
        assert DataFormatter.format_decimal("") == "0.0000"
        assert DataFormatter.format_decimal(np.nan) == "N/A"
        assert DataFormatter.format_decimal(float('inf')) == "∞"
        assert DataFormatter.format_decimal(float('-inf')) == "-∞"
    
    def test_format_date_basic(self):
        """Test basic date formatting."""
        test_date = datetime(2024, 1, 15)
        assert DataFormatter.format_date(test_date) == "2024-01-15"
        
        test_date_obj = date(2024, 1, 15)
        assert DataFormatter.format_date(test_date_obj) == "2024-01-15"
    
    def test_format_date_custom_format(self):
        """Test date formatting with custom format."""
        test_date = datetime(2024, 1, 15)
        assert DataFormatter.format_date(test_date, "%B %d, %Y") == "January 15, 2024"
        assert DataFormatter.format_date(test_date, "%m/%d/%Y") == "01/15/2024"
    
    def test_format_date_string_input(self):
        """Test date formatting with string input."""
        assert DataFormatter.format_date("2024-01-15") == "2024-01-15"
        assert DataFormatter.format_date("01/15/2024") == "2024-01-15"
        assert DataFormatter.format_date("invalid_date") == "N/A"
    
    def test_format_date_pandas_timestamp(self):
        """Test date formatting with pandas Timestamp."""
        test_timestamp = pd.Timestamp("2024-01-15")
        assert DataFormatter.format_date(test_timestamp) == "2024-01-15"
    
    def test_format_date_special_values(self):
        """Test date formatting with special values."""
        assert DataFormatter.format_date(None) == "N/A"
        assert DataFormatter.format_date("") == "N/A"
    
    def test_format_risk_score_basic(self):
        """Test basic risk score formatting."""
        assert DataFormatter.format_risk_score(0.234) == "0.234"
        assert DataFormatter.format_risk_score(-0.123) == "-0.123"
        assert DataFormatter.format_risk_score(0) == "0.000"
    
    def test_format_risk_score_with_category(self):
        """Test risk score formatting with category."""
        assert DataFormatter.format_risk_score(0.5, include_category=True) == "0.500 (FRAUD)"
        assert DataFormatter.format_risk_score(-0.3, include_category=True) == "-0.300 (SAFE)"
        assert DataFormatter.format_risk_score(0.1, include_category=True) == "0.100 (SUSPICIOUS)"
    
    def test_format_risk_score_custom_precision(self):
        """Test risk score formatting with custom precision."""
        assert DataFormatter.format_risk_score(0.234567, precision=2) == "0.23"
        assert DataFormatter.format_risk_score(0.234567, precision=5) == "0.23457"
    
    def test_format_risk_score_special_values(self):
        """Test risk score formatting with special values."""
        assert DataFormatter.format_risk_score(None) == "N/A"
        assert DataFormatter.format_risk_score("") == "N/A"
        assert DataFormatter.format_risk_score(np.nan) == "N/A"
        assert DataFormatter.format_risk_score(float('inf')) == "∞"
        assert DataFormatter.format_risk_score(float('-inf')) == "-∞"
    
    def test_get_risk_category(self):
        """Test risk category determination."""
        assert DataFormatter.get_risk_category(-0.3) == "SAFE"
        assert DataFormatter.get_risk_category(-0.2) == "SUSPICIOUS"
        assert DataFormatter.get_risk_category(0.1) == "SUSPICIOUS"
        assert DataFormatter.get_risk_category(0.2) == "FRAUD"
        assert DataFormatter.get_risk_category(0.5) == "FRAUD"
    
    def test_get_risk_category_boundary_conditions(self):
        """Test risk category at boundary values."""
        assert DataFormatter.get_risk_category(-0.2) == "SUSPICIOUS"  # Exactly at boundary
        assert DataFormatter.get_risk_category(0.2) == "FRAUD"        # Exactly at boundary
    
    def test_get_risk_category_special_values(self):
        """Test risk category with special values."""
        assert DataFormatter.get_risk_category(None) == "UNKNOWN"
        assert DataFormatter.get_risk_category("") == "UNKNOWN"
        assert DataFormatter.get_risk_category(np.nan) == "UNKNOWN"
        assert DataFormatter.get_risk_category(float('inf')) == "UNKNOWN"
        assert DataFormatter.get_risk_category("invalid") == "UNKNOWN"
    
    def test_format_transaction_for_display(self):
        """Test transaction formatting for display."""
        transaction = {
            'transaction_id': 'TXN001',
            'date': '2024-01-15',
            'product': 'Electronics',
            'commodity_category': 'Consumer',
            'quantity': 100,
            'unit_price': 25.50,
            'trade_value': 2550.0,
            'market_price': 24.00,
            'price_deviation': 0.0625,
            'risk_score': 0.15
        }
        
        formatted = DataFormatter.format_transaction_for_display(transaction)
        
        assert formatted['transaction_id'] == 'TXN001'
        assert formatted['product'] == 'Electronics'
        assert formatted['unit_price'] == '$25.50'
        assert formatted['trade_value'] == '$2,550.00'
        assert formatted['price_deviation'] == '6.25%'
        assert formatted['risk_score'] == '0.150'
        assert formatted['risk_category'] == 'SUSPICIOUS'
    
    def test_format_transaction_missing_fields(self):
        """Test transaction formatting with missing fields."""
        transaction = {
            'transaction_id': 'TXN001'
            # Missing other fields
        }
        
        formatted = DataFormatter.format_transaction_for_display(transaction)
        
        # Should handle missing fields gracefully
        assert formatted['transaction_id'] == 'TXN001'
        assert 'N/A' in formatted['date']
        assert formatted['unit_price'] == '$0.00'


class TestPerformanceTracker:
    """Test cases for the PerformanceTracker class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = PerformanceTracker()
    
    def test_performance_tracker_initialization(self):
        """Test PerformanceTracker initialization."""
        assert self.tracker.metrics['dataset_loads'] == 0
        assert self.tracker.metrics['model_trainings'] == 0
        assert self.tracker.metrics['api_calls'] == 0
        assert self.tracker.metrics['gemini_calls'] == 0
        assert self.tracker.metrics['alerts_triggered'] == 0
    
    def test_log_dataset_load(self):
        """Test dataset load logging."""
        self.tracker.log_dataset_load(2.5, 1000, "test.csv")
        
        assert self.tracker.metrics['dataset_loads'] == 1
        assert self.tracker.metrics['total_dataset_load_time'] == 2.5
    
    def test_log_model_training(self):
        """Test model training logging."""
        self.tracker.log_model_training(15.0, "IsolationForest", 6)
        
        assert self.tracker.metrics['model_trainings'] == 1
        assert self.tracker.metrics['total_model_training_time'] == 15.0
    
    def test_log_api_response(self):
        """Test API response logging."""
        self.tracker.log_api_response("/transactions", 0.5, 200)
        
        assert self.tracker.metrics['api_calls'] == 1
        assert self.tracker.metrics['total_api_response_time'] == 0.5
    
    def test_log_gemini_call_success(self):
        """Test successful Gemini call logging."""
        self.tracker.log_gemini_call(True, 3.0)
        
        assert self.tracker.metrics['gemini_calls'] == 1
        assert self.tracker.metrics['gemini_successes'] == 1
        assert self.tracker.metrics['gemini_failures'] == 0
        assert self.tracker.metrics['total_gemini_response_time'] == 3.0
    
    def test_log_gemini_call_failure(self):
        """Test failed Gemini call logging."""
        self.tracker.log_gemini_call(False, 2.0, "API error")
        
        assert self.tracker.metrics['gemini_calls'] == 1
        assert self.tracker.metrics['gemini_successes'] == 0
        assert self.tracker.metrics['gemini_failures'] == 1
        assert self.tracker.metrics['total_gemini_response_time'] == 2.0
    
    def test_log_alert_triggered(self):
        """Test alert trigger logging."""
        alert_details = {'severity': 'HIGH', 'type': 'PRICE_ANOMALY'}
        self.tracker.log_alert_triggered('PRICE_ANOMALY', 'TXN001', alert_details)
        
        assert self.tracker.metrics['alerts_triggered'] == 1
    
    def test_get_performance_summary(self):
        """Test performance summary generation."""
        # Log some metrics
        self.tracker.log_dataset_load(2.0, 1000, "test.csv")
        self.tracker.log_model_training(10.0, "IsolationForest", 6)
        self.tracker.log_api_response("/test", 0.5, 200)
        self.tracker.log_gemini_call(True, 3.0)
        self.tracker.log_gemini_call(False, 2.0, "Error")
        
        summary = self.tracker.get_performance_summary()
        
        assert summary['dataset_loads'] == 1
        assert summary['model_trainings'] == 1
        assert summary['api_calls'] == 1
        assert summary['gemini_calls'] == 2
        assert summary['gemini_success_rate'] == 50.0  # 1 success out of 2 calls
        assert summary['avg_dataset_load_time'] == 2.0
        assert summary['avg_model_training_time'] == 10.0
        assert summary['avg_api_response_time'] == 0.5
        assert summary['avg_gemini_response_time'] == 2.5  # (3.0 + 2.0) / 2
    
    def test_reset_metrics(self):
        """Test metrics reset."""
        # Log some metrics first
        self.tracker.log_dataset_load(2.0, 1000, "test.csv")
        self.tracker.log_api_response("/test", 0.5, 200)
        
        # Reset metrics
        self.tracker.reset_metrics()
        
        # All metrics should be zero
        assert self.tracker.metrics['dataset_loads'] == 0
        assert self.tracker.metrics['api_calls'] == 0
        assert self.tracker.metrics['total_dataset_load_time'] == 0.0
        assert self.tracker.metrics['total_api_response_time'] == 0.0


class TestTimedOperation:
    """Test cases for the TimedOperation context manager."""
    
    def test_timed_operation_success(self):
        """Test successful timed operation."""
        with patch('utils.helpers.logger') as mock_logger:
            with TimedOperation("Test operation", mock_logger) as timer:
                # Simulate some work
                pass
            
            # Should log start and completion
            assert mock_logger.info.call_count == 2
            start_call = mock_logger.info.call_args_list[0]
            end_call = mock_logger.info.call_args_list[1]
            
            assert "Starting: Test operation" in start_call[0][0]
            assert "Completed: Test operation" in end_call[0][0]
    
    def test_timed_operation_with_exception(self):
        """Test timed operation with exception."""
        with patch('utils.helpers.logger') as mock_logger:
            with pytest.raises(ValueError):
                with TimedOperation("Test operation", mock_logger):
                    raise ValueError("Test error")
            
            # Should log start and failure
            assert mock_logger.info.call_count == 1  # Start
            assert mock_logger.error.call_count == 1  # Failure
            
            error_call = mock_logger.error.call_args_list[0]
            assert "Failed: Test operation" in error_call[0][0]
            assert "ValueError: Test error" in error_call[0][0]
    
    def test_timed_operation_default_logger(self):
        """Test timed operation with default logger."""
        with TimedOperation("Test operation") as timer:
            # Should not raise any exceptions
            pass
        
        # Timer should have start and end times
        assert timer.start_time is not None
        assert timer.end_time is not None
        assert timer.end_time > timer.start_time

class TestLoggingUtilities:
    """Test cases for logging utility functions."""
    
    @patch('utils.helpers.logger')
    def test_setup_logging(self, mock_logger):
        """Test logging setup."""
        # Mock the logger to avoid file system issues
        logger = setup_logging(log_level="DEBUG", log_file="test.log")
        
        assert isinstance(logger, logging.Logger)
    
    @patch('utils.helpers.logger')
    def test_log_system_startup(self, mock_logger):
        """Test system startup logging."""
        log_system_startup()
        
        # Should log multiple startup messages
        assert mock_logger.info.call_count >= 3
        
        # Check for specific startup messages
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        startup_messages = [msg for msg in calls if "TRINETRA AI" in msg or "startup" in msg]
        assert len(startup_messages) >= 1
    
    @patch('utils.helpers.logger')
    @patch('utils.helpers.performance_tracker')
    def test_log_system_shutdown(self, mock_tracker, mock_logger):
        """Test system shutdown logging."""
        mock_tracker.get_performance_summary.return_value = {'test': 'summary'}
        
        log_system_shutdown()
        
        # Should log shutdown messages and get performance summary
        assert mock_logger.info.call_count >= 2
        mock_tracker.get_performance_summary.assert_called_once()
    
    @patch('utils.helpers.logger')
    def test_log_error_with_context(self, mock_logger):
        """Test error logging with context."""
        test_error = ValueError("Test error")
        context = "test function"
        additional_info = {"key": "value"}
        
        log_error_with_context(test_error, context, additional_info)
        
        # Should log error and additional info
        assert mock_logger.error.call_count >= 2
        
        error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
        assert any("ValueError: Test error" in msg for msg in error_calls)
        assert any("Additional context" in msg for msg in error_calls)
    
    @patch('utils.helpers.logger')
    def test_log_configuration_info(self, mock_logger):
        """Test configuration logging."""
        config = {
            'setting1': 'value1',
            'api_key': 'secret123',
            'password': 'secret456',
            'normal_setting': 'normal_value'
        }
        
        log_configuration_info(config)
        
        # Should log configuration with sensitive values redacted
        assert mock_logger.info.call_count >= 4
        
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        config_messages = [msg for msg in calls if ':' in msg]
        
        # Check that sensitive values are redacted
        sensitive_messages = [msg for msg in config_messages if '[REDACTED]' in msg]
        assert len(sensitive_messages) >= 2  # api_key and password
        
        # Check that normal values are not redacted
        normal_messages = [msg for msg in config_messages if 'normal_value' in msg]
        assert len(normal_messages) >= 1


class TestConstants:
    """Test cases for module constants."""
    
    def test_currency_symbol(self):
        """Test currency symbol constant."""
        assert CURRENCY_SYMBOL == "$"
    
    def test_precision_constants(self):
        """Test precision constants."""
        assert isinstance(PERCENTAGE_PRECISION, int)
        assert isinstance(DECIMAL_PRECISION, int)
        assert PERCENTAGE_PRECISION >= 0
        assert DECIMAL_PRECISION >= 0
    
    def test_date_format_constants(self):
        """Test date format constants."""
        assert isinstance(DATE_FORMAT, str)
        assert isinstance(DATETIME_FORMAT, str)
        assert "%" in DATE_FORMAT
        assert "%" in DATETIME_FORMAT
    
    def test_color_constants(self):
        """Test color constants."""
        assert isinstance(RISK_COLORS, dict)
        assert isinstance(PRIORITY_COLORS, dict)
        
        # Check that expected risk categories are present
        expected_risk_categories = {"SAFE", "SUSPICIOUS", "FRAUD"}
        assert set(RISK_COLORS.keys()) == expected_risk_categories
        
        # Check that expected priority levels are present
        expected_priorities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        assert set(PRIORITY_COLORS.keys()) == expected_priorities
        
        # Check that all colors are hex color codes
        for color in RISK_COLORS.values():
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB format
        
        for color in PRIORITY_COLORS.values():
            assert color.startswith("#")
            assert len(color) in [7, 9]  # #RRGGBB or #RRGGBBAA format


class TestGlobalPerformanceTracker:
    """Test cases for the global performance tracker instance."""
    
    def test_global_performance_tracker_exists(self):
        """Test that global performance tracker exists."""
        assert performance_tracker is not None
        assert isinstance(performance_tracker, PerformanceTracker)
    
    def test_global_performance_tracker_functionality(self):
        """Test that global performance tracker works."""
        initial_count = performance_tracker.metrics['dataset_loads']
        
        performance_tracker.log_dataset_load(1.0, 100, "test.csv")
        
        assert performance_tracker.metrics['dataset_loads'] == initial_count + 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])