"""
Helper Module for TRINETRA AI - Trade Fraud Intelligence System

This module provides comprehensive data formatting utilities used across the system
for dashboard display, API responses, Gemini API prompts, and data presentation.

Author: TRINETRA AI Team
Date: 2024
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
import logging
import json
import re

# Import additional modules for logging configuration
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Custom Error Classes for TRINETRA AI System
# These error classes provide specific error handling for different system components

class DataLoaderError(Exception):
    """Custom exception for data loader errors."""
    pass

class SchemaValidationError(DataLoaderError):
    """Exception raised when schema validation fails."""
    pass

class DataQualityError(DataLoaderError):
    """Exception raised when data quality checks fail."""
    pass

class GeminiInitializationError(Exception):
    """Custom exception for Gemini API initialization failures"""
    pass

class GeminiAPIError(Exception):
    """Custom exception for Gemini API call failures"""
    pass

class GeminiRateLimitError(GeminiAPIError):
    """Custom exception for Gemini API rate limit errors"""
    pass

class GeminiTimeoutError(GeminiAPIError):
    """Custom exception for Gemini API timeout errors"""
    pass

class GeminiQuotaExceededError(GeminiAPIError):
    """Custom exception for Gemini API quota exceeded errors"""
    pass

class ModelTrainingError(Exception):
    """Custom exception for ML model training failures"""
    pass

class ModelPredictionError(Exception):
    """Custom exception for ML model prediction failures"""
    pass

class FeatureEngineeringError(Exception):
    """Custom exception for feature engineering failures"""
    pass

class AlertSystemError(Exception):
    """Custom exception for alert system failures"""
    pass

# Configure comprehensive logging for TRINETRA AI system
def setup_logging(log_level: str = "INFO", 
                 log_file: str = "trinetra.log",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5) -> logging.Logger:
    """
    Set up comprehensive logging configuration for TRINETRA AI system.
    
    This function configures logging to both file and console with proper formatting,
    rotation, and level management. It tracks key system metrics and operations.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file name (default: trinetra.log)
        max_file_size: Maximum log file size before rotation (default: 10MB)
        backup_count: Number of backup log files to keep (default: 5)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Full path to log file
    log_file_path = log_dir / log_file
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create formatter with timestamp, module name, log level, and message
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create specific logger for this module
    logger = logging.getLogger(__name__)
    
    # Log the logging configuration
    logger.info(f"Logging configured - Level: {log_level}, File: {log_file_path}")
    logger.info(f"Log rotation: {max_file_size // (1024*1024)}MB max size, {backup_count} backups")
    
    return logger

# Initialize logging system
logger = setup_logging()

# Performance tracking utilities
class PerformanceTracker:
    """
    Utility class for tracking and logging performance metrics.
    
    This class provides methods to track key system metrics like:
    - Dataset load time
    - Model training time  
    - API response times
    - Gemini API call success/failure
    - Alert trigger counts
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PerformanceTracker")
        self.metrics = {
            'dataset_loads': 0,
            'model_trainings': 0,
            'api_calls': 0,
            'gemini_calls': 0,
            'gemini_successes': 0,
            'gemini_failures': 0,
            'alerts_triggered': 0,
            'total_dataset_load_time': 0.0,
            'total_model_training_time': 0.0,
            'total_api_response_time': 0.0,
            'total_gemini_response_time': 0.0
        }
    
    def log_dataset_load(self, load_time: float, dataset_size: int, file_path: str):
        """
        Log dataset loading performance metrics.
        
        Args:
            load_time: Time taken to load dataset (seconds)
            dataset_size: Number of rows loaded
            file_path: Path to dataset file
        """
        self.metrics['dataset_loads'] += 1
        self.metrics['total_dataset_load_time'] += load_time
        
        avg_load_time = self.metrics['total_dataset_load_time'] / self.metrics['dataset_loads']
        
        self.logger.info(f"Dataset loaded: {file_path}")
        self.logger.info(f"Load time: {load_time:.2f}s, Rows: {dataset_size:,}")
        self.logger.info(f"Average load time: {avg_load_time:.2f}s")
        
        if load_time > 10.0:  # Warn if loading takes more than 10 seconds
            self.logger.warning(f"Slow dataset load detected: {load_time:.2f}s")
    
    def log_model_training(self, training_time: float, model_type: str, feature_count: int):
        """
        Log model training performance metrics.
        
        Args:
            training_time: Time taken to train model (seconds)
            model_type: Type of model trained (e.g., IsolationForest)
            feature_count: Number of features used for training
        """
        self.metrics['model_trainings'] += 1
        self.metrics['total_model_training_time'] += training_time
        
        avg_training_time = self.metrics['total_model_training_time'] / self.metrics['model_trainings']
        
        self.logger.info(f"Model trained: {model_type}")
        self.logger.info(f"Training time: {training_time:.2f}s, Features: {feature_count}")
        self.logger.info(f"Average training time: {avg_training_time:.2f}s")
        
        if training_time > 30.0:  # Warn if training takes more than 30 seconds
            self.logger.warning(f"Slow model training detected: {training_time:.2f}s")
    
    def log_api_response(self, endpoint: str, response_time: float, status_code: int):
        """
        Log API response performance metrics.
        
        Args:
            endpoint: API endpoint called
            response_time: Time taken for API response (seconds)
            status_code: HTTP status code returned
        """
        self.metrics['api_calls'] += 1
        self.metrics['total_api_response_time'] += response_time
        
        avg_response_time = self.metrics['total_api_response_time'] / self.metrics['api_calls']
        
        self.logger.info(f"API call: {endpoint} - {status_code} - {response_time:.3f}s")
        self.logger.info(f"Average API response time: {avg_response_time:.3f}s")
        
        if response_time > 1.0:  # Warn if API response takes more than 1 second
            self.logger.warning(f"Slow API response detected: {endpoint} - {response_time:.3f}s")
        
        if status_code >= 400:  # Log errors
            self.logger.error(f"API error: {endpoint} - Status {status_code}")
    
    def log_gemini_call(self, success: bool, response_time: float, error_message: str = None):
        """
        Log Gemini API call performance and success/failure metrics.
        
        Args:
            success: Whether the Gemini API call was successful
            response_time: Time taken for Gemini API response (seconds)
            error_message: Error message if call failed
        """
        self.metrics['gemini_calls'] += 1
        self.metrics['total_gemini_response_time'] += response_time
        
        if success:
            self.metrics['gemini_successes'] += 1
            self.logger.info(f"Gemini API success - Response time: {response_time:.3f}s")
        else:
            self.metrics['gemini_failures'] += 1
            self.logger.error(f"Gemini API failure - Response time: {response_time:.3f}s")
            if error_message:
                self.logger.error(f"Gemini error details: {error_message}")
        
        # Calculate success rate
        success_rate = (self.metrics['gemini_successes'] / self.metrics['gemini_calls']) * 100
        avg_response_time = self.metrics['total_gemini_response_time'] / self.metrics['gemini_calls']
        
        self.logger.info(f"Gemini API stats - Success rate: {success_rate:.1f}%, Avg response: {avg_response_time:.3f}s")
        
        if response_time > 10.0:  # Warn if Gemini response takes more than 10 seconds
            self.logger.warning(f"Slow Gemini API response detected: {response_time:.3f}s")
        
        if success_rate < 80.0 and self.metrics['gemini_calls'] >= 5:  # Warn if success rate drops below 80%
            self.logger.warning(f"Low Gemini API success rate: {success_rate:.1f}%")
    
    def log_alert_triggered(self, alert_type: str, transaction_id: str, alert_details: dict):
        """
        Log alert trigger events and counts.
        
        Args:
            alert_type: Type of alert triggered (PRICE_ANOMALY, ROUTE_ANOMALY, etc.)
            transaction_id: ID of transaction that triggered alert
            alert_details: Additional alert details
        """
        self.metrics['alerts_triggered'] += 1
        
        self.logger.info(f"Alert triggered: {alert_type} for transaction {transaction_id}")
        self.logger.info(f"Alert details: {alert_details}")
        self.logger.info(f"Total alerts triggered: {self.metrics['alerts_triggered']}")
        
        # Log alert frequency
        if self.metrics['alerts_triggered'] % 10 == 0:  # Every 10 alerts
            self.logger.info(f"Alert milestone: {self.metrics['alerts_triggered']} total alerts triggered")
    
    def get_performance_summary(self) -> dict:
        """
        Get comprehensive performance summary.
        
        Returns:
            dict: Performance metrics summary
        """
        summary = {
            'dataset_loads': self.metrics['dataset_loads'],
            'model_trainings': self.metrics['model_trainings'],
            'api_calls': self.metrics['api_calls'],
            'gemini_calls': self.metrics['gemini_calls'],
            'gemini_success_rate': (self.metrics['gemini_successes'] / max(1, self.metrics['gemini_calls'])) * 100,
            'alerts_triggered': self.metrics['alerts_triggered'],
            'avg_dataset_load_time': self.metrics['total_dataset_load_time'] / max(1, self.metrics['dataset_loads']),
            'avg_model_training_time': self.metrics['total_model_training_time'] / max(1, self.metrics['model_trainings']),
            'avg_api_response_time': self.metrics['total_api_response_time'] / max(1, self.metrics['api_calls']),
            'avg_gemini_response_time': self.metrics['total_gemini_response_time'] / max(1, self.metrics['gemini_calls'])
        }
        
        self.logger.info("Performance Summary:")
        for key, value in summary.items():
            if 'time' in key:
                self.logger.info(f"  {key}: {value:.3f}s")
            elif 'rate' in key:
                self.logger.info(f"  {key}: {value:.1f}%")
            else:
                self.logger.info(f"  {key}: {value}")
        
        return summary
    
    def reset_metrics(self):
        """Reset all performance metrics."""
        self.metrics = {key: 0 if isinstance(value, int) else 0.0 for key, value in self.metrics.items()}
        self.logger.info("Performance metrics reset")

# Global performance tracker instance
performance_tracker = PerformanceTracker()

# Logging utility functions
def log_system_startup():
    """Log system startup information."""
    logger.info("=" * 60)
    logger.info("TRINETRA AI - Trade Fraud Intelligence System")
    logger.info("=" * 60)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Log file location: {Path('logs/trinetra.log').absolute()}")
    logger.info("System startup initiated")

def log_system_shutdown():
    """Log system shutdown information."""
    logger.info("System shutdown initiated")
    performance_tracker.get_performance_summary()
    logger.info("TRINETRA AI system shutdown complete")
    logger.info("=" * 60)

def log_error_with_context(error: Exception, context: str, additional_info: dict = None):
    """
    Log errors with comprehensive context information.
    
    Args:
        error: Exception that occurred
        context: Context where error occurred
        additional_info: Additional information to log
    """
    logger.error(f"Error in {context}: {type(error).__name__}: {str(error)}")
    
    if additional_info:
        logger.error(f"Additional context: {additional_info}")
    
    # Log stack trace for debugging
    import traceback
    logger.debug(f"Stack trace:\n{traceback.format_exc()}")

def log_configuration_info(config: dict):
    """
    Log system configuration information.
    
    Args:
        config: Configuration dictionary to log
    """
    logger.info("System Configuration:")
    for key, value in config.items():
        # Don't log sensitive information like API keys
        if 'key' in key.lower() or 'password' in key.lower() or 'secret' in key.lower():
            logger.info(f"  {key}: [REDACTED]")
        else:
            logger.info(f"  {key}: {value}")

# Context manager for timing operations
class TimedOperation:
    """
    Context manager for timing operations and logging performance.
    
    Usage:
        with TimedOperation("Loading dataset", logger) as timer:
            # Your operation here
            pass
        # Automatically logs the operation time
    """
    
    def __init__(self, operation_name: str, logger_instance: logging.Logger = None):
        self.operation_name = operation_name
        self.logger = logger_instance or logger
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if exc_type is None:
            self.logger.info(f"Completed: {self.operation_name} in {duration:.3f}s")
        else:
            self.logger.error(f"Failed: {self.operation_name} after {duration:.3f}s - {exc_type.__name__}: {exc_val}")
        
        return False  # Don't suppress exceptions

# Import time for TimedOperation
import time

# Constants for formatting
CURRENCY_SYMBOL = "$"
PERCENTAGE_PRECISION = 2
DECIMAL_PRECISION = 4
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Risk category colors for dashboard
RISK_COLORS = {
    "SAFE": "#28a745",      # Green
    "SUSPICIOUS": "#ffc107", # Yellow
    "FRAUD": "#dc3545"       # Red
}

# Priority colors for alerts
PRIORITY_COLORS = {
    "LOW": "#6c757d",       # Gray
    "MEDIUM": "#fd7e14",    # Orange
    "HIGH": "#dc3545",      # Red
    "CRITICAL": "#721c24"   # Dark Red
}


class DataFormatter:
    """
    Comprehensive data formatting utilities for TRINETRA AI system.
    
    This class provides methods for formatting various types of data including:
    - Currency and numeric values
    - Dates and timestamps
    - Risk scores and categories
    - Transaction data for display
    - API response formatting
    - Gemini prompt formatting
    """
    
    @staticmethod
    def format_currency(value: Union[float, int, str], 
                       symbol: str = CURRENCY_SYMBOL,
                       precision: int = 2,
                       include_commas: bool = True) -> str:
        """
        Format numeric values as currency with proper formatting.
        
        Args:
            value: Numeric value to format
            symbol: Currency symbol (default: $)
            precision: Decimal places (default: 2)
            include_commas: Whether to include thousand separators
            
        Returns:
            str: Formatted currency string
            
        Examples:
            >>> DataFormatter.format_currency(1234.56)
            '$1,234.56'
            >>> DataFormatter.format_currency(1000000, precision=0)
            '$1,000,000'
        """
        try:
            # Handle None or empty values
            if value is None or value == "":
                return f"{symbol}0.00"
            
            # Convert to float
            if isinstance(value, str):
                # Remove any existing currency symbols and commas
                clean_value = re.sub(r'[^\d.-]', '', value)
                if not clean_value:
                    return f"{symbol}0.00"
                value = float(clean_value)
            else:
                value = float(value)
            
            # Handle special cases
            if np.isnan(value) or np.isinf(value):
                return f"{symbol}0.00"
            
            # Format with precision
            if include_commas:
                formatted = f"{value:,.{precision}f}"
            else:
                formatted = f"{value:.{precision}f}"
            
            return f"{symbol}{formatted}"
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error formatting currency value {value}: {e}")
            return f"{symbol}0.00"
    
    @staticmethod
    def format_percentage(value: Union[float, int, str],
                         precision: int = PERCENTAGE_PRECISION,
                         include_sign: bool = True) -> str:
        """
        Format numeric values as percentages.
        
        Args:
            value: Numeric value to format (0.15 = 15%)
            precision: Decimal places (default: 2)
            include_sign: Whether to include % sign
            
        Returns:
            str: Formatted percentage string
            
        Examples:
            >>> DataFormatter.format_percentage(0.1534)
            '15.34%'
            >>> DataFormatter.format_percentage(-0.05, precision=1)
            '-5.0%'
        """
        try:
            # Handle None or empty values
            if value is None or value == "":
                return "0.00%" if include_sign else "0.00"
            
            # Convert to float
            if isinstance(value, str):
                clean_value = re.sub(r'[^\d.-]', '', value)
                if not clean_value:
                    return "0.00%" if include_sign else "0.00"
                value = float(clean_value)
            else:
                value = float(value)
            
            # Handle special cases
            if np.isnan(value) or np.isinf(value):
                return "0.00%" if include_sign else "0.00"
            
            # Convert to percentage (multiply by 100)
            percentage = value * 100
            formatted = f"{percentage:.{precision}f}"
            
            return f"{formatted}%" if include_sign else formatted
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error formatting percentage value {value}: {e}")
            return "0.00%" if include_sign else "0.00"
    
    @staticmethod
    def format_decimal(value: Union[float, int, str],
                      precision: int = DECIMAL_PRECISION,
                      include_commas: bool = False) -> str:
        """
        Format numeric values with specified decimal precision.
        
        Args:
            value: Numeric value to format
            precision: Decimal places (default: 4)
            include_commas: Whether to include thousand separators
            
        Returns:
            str: Formatted decimal string
            
        Examples:
            >>> DataFormatter.format_decimal(3.14159, precision=2)
            '3.14'
            >>> DataFormatter.format_decimal(1234.5678, include_commas=True)
            '1,234.5678'
        """
        try:
            # Handle None or empty values
            if value is None or value == "":
                return "0.0000"
            
            # Convert to float
            if isinstance(value, str):
                clean_value = re.sub(r'[^\d.-]', '', value)
                if not clean_value:
                    return "0.0000"
                value = float(clean_value)
            else:
                value = float(value)
            
            # Handle special cases
            if np.isnan(value):
                return "N/A"
            if np.isinf(value):
                return "∞" if value > 0 else "-∞"
            
            # Format with precision
            if include_commas:
                return f"{value:,.{precision}f}"
            else:
                return f"{value:.{precision}f}"
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error formatting decimal value {value}: {e}")
            return "0.0000"
    
    @staticmethod
    def format_date(value: Union[datetime, date, str, pd.Timestamp],
                   format_string: str = DATE_FORMAT) -> str:
        """
        Format date values consistently.
        
        Args:
            value: Date value to format
            format_string: Date format string (default: %Y-%m-%d)
            
        Returns:
            str: Formatted date string
            
        Examples:
            >>> DataFormatter.format_date(datetime(2024, 1, 15))
            '2024-01-15'
            >>> DataFormatter.format_date('2024-01-15', '%B %d, %Y')
            'January 15, 2024'
        """
        try:
            # Handle None or empty values
            if value is None or value == "":
                return "N/A"
            
            # Convert to datetime if string
            if isinstance(value, str):
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        value = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # If no format worked, try pandas
                    value = pd.to_datetime(value)
            
            # Convert pandas Timestamp to datetime
            if isinstance(value, pd.Timestamp):
                value = value.to_pydatetime()
            
            # Convert date to datetime
            if isinstance(value, date) and not isinstance(value, datetime):
                value = datetime.combine(value, datetime.min.time())
            
            return value.strftime(format_string)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error formatting date value {value}: {e}")
            return "N/A"
    
    @staticmethod
    def format_risk_score(score: Union[float, int, str],
                         precision: int = 3,
                         include_category: bool = False) -> str:
        """
        Format risk scores with appropriate precision and optional category.
        
        Args:
            score: Risk score value
            precision: Decimal places (default: 3)
            include_category: Whether to include risk category
            
        Returns:
            str: Formatted risk score string
            
        Examples:
            >>> DataFormatter.format_risk_score(0.234)
            '0.234'
            >>> DataFormatter.format_risk_score(0.5, include_category=True)
            '0.500 (FRAUD)'
        """
        try:
            # Handle None or empty values
            if score is None or score == "":
                return "N/A"
            
            # Convert to float
            if isinstance(score, str):
                clean_value = re.sub(r'[^\d.-]', '', score)
                if not clean_value:
                    return "N/A"
                score = float(clean_value)
            else:
                score = float(score)
            
            # Handle special cases
            if np.isnan(score):
                return "N/A"
            if np.isinf(score):
                return "∞" if score > 0 else "-∞"
            
            # Format score
            formatted_score = f"{score:.{precision}f}"
            
            if include_category:
                category = DataFormatter.get_risk_category(score)
                return f"{formatted_score} ({category})"
            
            return formatted_score
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error formatting risk score {score}: {e}")
            return "N/A"
    
    @staticmethod
    def get_risk_category(score: Union[float, int, str]) -> str:
        """
        Get risk category from score using TRINETRA AI thresholds.
        
        Args:
            score: Risk score value
            
        Returns:
            str: Risk category (SAFE, SUSPICIOUS, FRAUD)
        """
        try:
            if score is None or score == "":
                return "UNKNOWN"
            
            # Convert to float
            if isinstance(score, str):
                clean_value = re.sub(r'[^\d.-]', '', score)
                if not clean_value:
                    return "UNKNOWN"
                score = float(clean_value)
            else:
                score = float(score)
            
            # Handle special cases
            if np.isnan(score) or np.isinf(score):
                return "UNKNOWN"
            
            # Apply TRINETRA AI risk thresholds
            if score < -0.2:
                return "SAFE"
            elif score < 0.2:
                return "SUSPICIOUS"
            else:
                return "FRAUD"
                
        except (ValueError, TypeError):
            return "UNKNOWN"
    
    @staticmethod
    def format_transaction_for_display(transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format transaction data for dashboard display.
        
        Args:
            transaction: Raw transaction dictionary
            
        Returns:
            Dict: Formatted transaction data
        """
        try:
            formatted = {}
            
            # Basic transaction info
            formatted['transaction_id'] = str(transaction.get('transaction_id', 'N/A'))
            formatted['date'] = DataFormatter.format_date(transaction.get('date'))
            formatted['product'] = str(transaction.get('product', 'N/A'))
            formatted['commodity_category'] = str(transaction.get('commodity_category', 'N/A'))
            
            # Financial data
            formatted['quantity'] = DataFormatter.format_decimal(
                transaction.get('quantity', 0), precision=0, include_commas=True
            )
            formatted['unit_price'] = DataFormatter.format_currency(
                transaction.get('unit_price', 0)
            )
            formatted['trade_value'] = DataFormatter.format_currency(
                transaction.get('trade_value', 0)
            )
            formatted['market_price'] = DataFormatter.format_currency(
                transaction.get('market_price', 0)
            )
            
            # Risk indicators
            formatted['price_deviation'] = DataFormatter.format_percentage(
                transaction.get('price_deviation', 0)
            )
            formatted['risk_score'] = DataFormatter.format_risk_score(
                transaction.get('risk_score', 0)
            )
            formatted['risk_category'] = DataFormatter.get_risk_category(
                transaction.get('risk_score', 0)
            )
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting transaction for display: {e}")
            return transaction  # Return original if formatting fails
    
    @staticmethod
    def format_transaction_for_api(transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format transaction data for API responses with consistent data types.
        
        Args:
            transaction: Raw transaction dictionary
            
        Returns:
            Dict: API-formatted transaction data
        """
        try:
            formatted = {}
            
            # Basic transaction info - keep as strings/original types for API
            formatted['transaction_id'] = str(transaction.get('transaction_id', ''))
            formatted['date'] = transaction.get('date', '')
            formatted['product'] = str(transaction.get('product', ''))
            formatted['commodity_category'] = str(transaction.get('commodity_category', ''))
            
            # Numeric fields - ensure proper types
            numeric_fields = [
                'quantity', 'unit_price', 'trade_value', 'market_price', 
                'price_deviation', 'risk_score', 'distance_km', 
                'company_risk_score', 'route_anomaly', 'port_activity_index'
            ]
            
            for field in numeric_fields:
                value = transaction.get(field)
                if value is not None and not (isinstance(value, float) and np.isnan(value)):
                    try:
                        formatted[field] = float(value)
                    except (ValueError, TypeError):
                        formatted[field] = 0.0
                else:
                    formatted[field] = 0.0
            
            # String fields
            string_fields = [
                'exporter_company', 'exporter_country', 'importer_company', 
                'importer_country', 'shipping_route', 'export_port', 'import_port'
            ]
            
            for field in string_fields:
                formatted[field] = str(transaction.get(field, ''))
            
            # Risk category
            formatted['risk_category'] = DataFormatter.get_risk_category(
                transaction.get('risk_score', 0)
            )
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting transaction for API: {e}")
            return transaction  # Return original if formatting fails
    
    @staticmethod
    def format_transaction_for_gemini(transaction: Dict[str, Any]) -> str:
        """
        Format transaction data for Gemini API prompts with human-readable formatting.
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            str: Formatted transaction string for AI prompts
        """
        try:
            # Format key transaction details for AI analysis
            formatted_parts = []
            
            # Basic info
            formatted_parts.append(f"Transaction ID: {transaction.get('transaction_id', 'N/A')}")
            formatted_parts.append(f"Date: {DataFormatter.format_date(transaction.get('date'))}")
            formatted_parts.append(f"Product: {transaction.get('product', 'N/A')}")
            
            # Financial details
            formatted_parts.append(f"Unit Price: {DataFormatter.format_currency(transaction.get('unit_price', 0))}")
            formatted_parts.append(f"Market Price: {DataFormatter.format_currency(transaction.get('market_price', 0))}")
            formatted_parts.append(f"Price Deviation: {DataFormatter.format_percentage(transaction.get('price_deviation', 0))}")
            
            # Risk indicators
            formatted_parts.append(f"Risk Score: {DataFormatter.format_risk_score(transaction.get('risk_score', 0))}")
            formatted_parts.append(f"Risk Category: {DataFormatter.get_risk_category(transaction.get('risk_score', 0))}")
            formatted_parts.append(f"Company Risk Score: {DataFormatter.format_risk_score(transaction.get('company_risk_score', 0))}")
            formatted_parts.append(f"Route Anomaly: {'Yes' if transaction.get('route_anomaly', 0) == 1 else 'No'}")
            
            return "\n".join(formatted_parts)
            
        except Exception as e:
            logger.error(f"Error formatting transaction for Gemini: {e}")
            return f"Transaction ID: {transaction.get('transaction_id', 'N/A')} (formatting error)"
    
    @staticmethod
    def format_alert_message(alert_type: str, transaction: Dict[str, Any]) -> str:
        """
        Format alert messages for display in the dashboard.
        
        Args:
            alert_type: Type of alert (PRICE_ANOMALY, ROUTE_ANOMALY, etc.)
            transaction: Transaction that triggered the alert
            
        Returns:
            str: Formatted alert message
        """
        try:
            transaction_id = transaction.get('transaction_id', 'N/A')
            product = transaction.get('product', 'Unknown Product')
            
            alert_messages = {
                'PRICE_ANOMALY': f"🚨 Price Alert: {product} (ID: {transaction_id}) shows {DataFormatter.format_percentage(transaction.get('price_deviation', 0))} price deviation",
                'ROUTE_ANOMALY': f"🛣️ Route Alert: {product} (ID: {transaction_id}) using unusual shipping route",
                'HIGH_RISK_COMPANY': f"🏢 Company Alert: {product} (ID: {transaction_id}) involves high-risk company",
                'PORT_CONGESTION': f"🚢 Port Alert: {product} (ID: {transaction_id}) at congested port",
                'FRAUD_DETECTED': f"⚠️ Fraud Alert: {product} (ID: {transaction_id}) classified as FRAUD"
            }
            
            return alert_messages.get(alert_type, f"Alert: {product} (ID: {transaction_id}) requires attention")
            
        except Exception as e:
            logger.error(f"Error formatting alert message: {e}")
            return f"Alert for transaction {transaction.get('transaction_id', 'N/A')}"
    
    @staticmethod
    def format_statistics_for_dashboard(stats: Dict[str, Any]) -> Dict[str, str]:
        """
        Format statistics for dashboard KPI display.
        
        Args:
            stats: Raw statistics dictionary
            
        Returns:
            Dict: Formatted statistics for display
        """
        try:
            formatted_stats = {}
            
            # Total transactions
            total_transactions = stats.get('total_transactions', 0)
            formatted_stats['total_transactions'] = f"{total_transactions:,}"
            
            # Fraud rate
            fraud_rate = stats.get('fraud_rate', 0)
            formatted_stats['fraud_rate'] = DataFormatter.format_percentage(fraud_rate / 100 if fraud_rate > 1 else fraud_rate)
            
            # Total trade value
            trade_value = stats.get('total_trade_value', 0)
            formatted_stats['total_trade_value'] = DataFormatter.format_currency(trade_value, precision=0)
            
            return formatted_stats
            
        except Exception as e:
            logger.error(f"Error formatting statistics for dashboard: {e}")
            return stats  # Return original if formatting fails


class ValidationHelpers:
    """
    Comprehensive validation helper functions for TRINETRA AI system.
    
    This class provides validation utilities for:
    - Data schema validation (supporting data_loader.py)
    - API input validation (supporting api.py)
    - Transaction data validation
    - Feature validation for ML pipeline
    - Configuration validation
    """
    
    # Define validation constants
    REQUIRED_TRANSACTION_FIELDS = [
        'transaction_id', 'date', 'product', 'commodity_category',
        'quantity', 'unit_price', 'trade_value', 'market_price'
    ]
    
    REQUIRED_DATASET_COLUMNS = [
        'transaction_id', 'date', 'product', 'commodity_category',
        'quantity', 'unit_price', 'trade_value', 'market_price',
        'exporter_company', 'exporter_country', 'importer_company', 'importer_country',
        'shipping_route', 'export_port', 'import_port', 'distance_km',
        'price_deviation', 'company_risk_score', 'route_anomaly', 'fraud_label'
    ]
    
    NUMERIC_FIELD_RANGES = {
        'quantity': (0, float('inf')),
        'unit_price': (0, float('inf')),
        'trade_value': (0, float('inf')),
        'market_price': (0, float('inf')),
        'distance_km': (0, float('inf')),
        'price_deviation': (-1, 1),
        'company_risk_score': (0, 1),
        'route_anomaly': (0, 1),
        'fraud_label': (0, 2),
        'risk_score': (-1, 1),
        'port_activity_index': (0, float('inf')),
        'shipment_duration_days': (0, float('inf')),
        'cargo_volume': (0, float('inf'))
    }
    
    FEATURE_FIELD_RANGES = {
        'price_anomaly_score': (0, 1),
        'route_risk_score': (0, 1),
        'company_network_risk': (0, 1),
        'port_congestion_score': (0, float('inf')),
        'shipment_duration_risk': (0, float('inf')),
        'volume_spike_score': (0, float('inf'))
    }
    
    @staticmethod
    def validate_dataset_schema(df: pd.DataFrame, strict: bool = False) -> Dict[str, Any]:
        """
        Comprehensive dataset schema validation for data_loader.py support.
        
        Args:
            df: DataFrame to validate
            strict: If True, require all columns; if False, only check critical ones
            
        Returns:
            Dict: Validation results with 'valid', 'errors', 'warnings', and 'summary'
        """
        errors = []
        warnings = []
        
        try:
            if df is None or df.empty:
                errors.append("DataFrame is None or empty")
                return {
                    'valid': False,
                    'errors': errors,
                    'warnings': warnings,
                    'summary': 'Dataset validation failed: empty dataset'
                }
            
            # Check required columns
            required_cols = ValidationHelpers.REQUIRED_DATASET_COLUMNS if strict else ValidationHelpers.REQUIRED_TRANSACTION_FIELDS
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                errors.append(f"Missing required columns: {missing_cols}")
            
            # Check for duplicate columns
            duplicate_cols = df.columns[df.columns.duplicated()].tolist()
            if duplicate_cols:
                warnings.append(f"Duplicate columns found: {duplicate_cols}")
            
            # Validate data types and ranges
            for col in df.columns:
                if col in ValidationHelpers.NUMERIC_FIELD_RANGES:
                    min_val, max_val = ValidationHelpers.NUMERIC_FIELD_RANGES[col]
                    
                    # Check if column is numeric
                    if not pd.api.types.is_numeric_dtype(df[col]):
                        warnings.append(f"Column '{col}' should be numeric but has type {df[col].dtype}")
                        continue
                    
                    # Check value ranges (excluding NaN values)
                    valid_values = df[col].dropna()
                    if len(valid_values) > 0:
                        out_of_range = ((valid_values < min_val) | (valid_values > max_val)).sum()
                        if out_of_range > 0:
                            warnings.append(f"Column '{col}' has {out_of_range} values outside range [{min_val}, {max_val}]")
            
            # Check transaction_id uniqueness
            if 'transaction_id' in df.columns:
                duplicate_ids = df['transaction_id'].duplicated().sum()
                if duplicate_ids > 0:
                    warnings.append(f"Found {duplicate_ids} duplicate transaction IDs")
            
            # Check date column
            if 'date' in df.columns:
                if not pd.api.types.is_datetime64_any_dtype(df['date']):
                    warnings.append("Date column is not in datetime format")
            
            # Data quality checks
            total_rows = len(df)
            null_counts = df.isnull().sum()
            high_null_cols = null_counts[null_counts > total_rows * 0.5].index.tolist()
            
            if high_null_cols:
                warnings.append(f"Columns with >50% null values: {high_null_cols}")
            
            # Summary
            is_valid = len(errors) == 0
            summary = f"Schema validation {'passed' if is_valid else 'failed'}: {len(df.columns)} columns, {total_rows} rows"
            
            return {
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings,
                'summary': summary,
                'column_count': len(df.columns),
                'row_count': total_rows,
                'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            }
            
        except Exception as e:
            errors.append(f"Schema validation error: {str(e)}")
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings,
                'summary': f'Schema validation failed with exception: {str(e)}'
            }
    
    @staticmethod
    def validate_transaction_data(transaction: Dict[str, Any], include_features: bool = False) -> Dict[str, Any]:
        """
        Validate individual transaction data with comprehensive checks.
        
        Args:
            transaction: Transaction dictionary to validate
            include_features: Whether to validate engineered features
            
        Returns:
            Dict: Validation results with 'valid', 'errors', 'warnings', and 'details'
        """
        errors = []
        warnings = []
        
        try:
            if not isinstance(transaction, dict):
                errors.append("Transaction must be a dictionary")
                return {'valid': False, 'errors': errors, 'warnings': warnings}
            
            # Check required fields
            required_fields = ValidationHelpers.REQUIRED_TRANSACTION_FIELDS
            for field in required_fields:
                if field not in transaction:
                    errors.append(f"Missing required field: {field}")
                elif transaction[field] is None or transaction[field] == "":
                    errors.append(f"Required field '{field}' is empty")
            
            # Validate numeric fields
            numeric_ranges = ValidationHelpers.NUMERIC_FIELD_RANGES.copy()
            if include_features:
                numeric_ranges.update(ValidationHelpers.FEATURE_FIELD_RANGES)
            
            for field, (min_val, max_val) in numeric_ranges.items():
                if field in transaction and transaction[field] is not None:
                    try:
                        value = float(transaction[field])
                        if np.isnan(value):
                            warnings.append(f"Field '{field}' has NaN value")
                        elif np.isinf(value):
                            warnings.append(f"Field '{field}' has infinite value")
                        elif not (min_val <= value <= max_val):
                            warnings.append(f"Field '{field}' value {value} outside expected range [{min_val}, {max_val}]")
                    except (ValueError, TypeError):
                        errors.append(f"Invalid numeric value for '{field}': {transaction[field]}")
            
            # Validate transaction_id format
            if 'transaction_id' in transaction:
                tx_id = str(transaction['transaction_id'])
                if not tx_id or len(tx_id.strip()) == 0:
                    errors.append("Transaction ID cannot be empty")
                elif len(tx_id) > 50:
                    warnings.append(f"Transaction ID is unusually long: {len(tx_id)} characters")
            
            # Validate date format
            if 'date' in transaction and transaction['date']:
                try:
                    if isinstance(transaction['date'], str):
                        pd.to_datetime(transaction['date'])
                except (ValueError, TypeError):
                    errors.append(f"Invalid date format: {transaction['date']}")
            
            # Business logic validations
            if 'unit_price' in transaction and 'market_price' in transaction:
                try:
                    unit_price = float(transaction['unit_price'])
                    market_price = float(transaction['market_price'])
                    
                    if unit_price > 0 and market_price > 0:
                        price_ratio = unit_price / market_price
                        if price_ratio > 10 or price_ratio < 0.1:
                            warnings.append(f"Extreme price ratio detected: {price_ratio:.2f}")
                except (ValueError, TypeError, ZeroDivisionError):
                    pass  # Already handled in numeric validation
            
            # Validate string fields
            string_fields = ['product', 'commodity_category', 'exporter_company', 'importer_company']
            for field in string_fields:
                if field in transaction and transaction[field]:
                    value = str(transaction[field])
                    if len(value) > 200:
                        warnings.append(f"Field '{field}' is unusually long: {len(value)} characters")
            
            is_valid = len(errors) == 0
            
            return {
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings,
                'details': {
                    'fields_checked': len(transaction),
                    'required_fields_present': len([f for f in required_fields if f in transaction]),
                    'numeric_fields_valid': len([f for f in numeric_ranges.keys() if f in transaction and ValidationHelpers._is_valid_numeric(transaction.get(f))])
                }
            }
            
        except Exception as e:
            errors.append(f"Transaction validation error: {str(e)}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def validate_api_input(input_data: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
        """
        Validate API input data for different endpoints.
        
        Args:
            input_data: Input data to validate
            endpoint: API endpoint name for context-specific validation
            
        Returns:
            Dict: Validation results with 'valid', 'errors', 'warnings'
        """
        errors = []
        warnings = []
        
        try:
            if endpoint == "query":
                # Validate natural language query
                if 'query' not in input_data:
                    errors.append("Missing 'query' field")
                else:
                    query = input_data['query']
                    if not isinstance(query, str):
                        errors.append("Query must be a string")
                    elif len(query.strip()) == 0:
                        errors.append("Query cannot be empty")
                    elif len(query) > 1000:
                        warnings.append(f"Query is very long: {len(query)} characters")
                    
                    # Check for potentially dangerous content
                    sanitized_query = ValidationHelpers.sanitize_string_input(query)
                    if sanitized_query != query:
                        warnings.append("Query contains potentially unsafe characters")
            
            elif endpoint == "explain":
                # Validate explanation request
                if 'transaction_id' not in input_data:
                    errors.append("Missing 'transaction_id' field")
                else:
                    tx_id = input_data['transaction_id']
                    if not isinstance(tx_id, str) or len(tx_id.strip()) == 0:
                        errors.append("Transaction ID must be a non-empty string")
                
                # Validate optional force_ai parameter
                if 'force_ai' in input_data:
                    if not isinstance(input_data['force_ai'], bool):
                        warnings.append("force_ai should be a boolean value")
            
            elif endpoint == "transactions":
                # Validate transaction filtering parameters
                if 'limit' in input_data:
                    try:
                        limit = int(input_data['limit'])
                        if limit <= 0:
                            errors.append("Limit must be positive")
                        elif limit > 10000:
                            warnings.append(f"Large limit requested: {limit}")
                    except (ValueError, TypeError):
                        errors.append("Limit must be an integer")
                
                if 'offset' in input_data:
                    try:
                        offset = int(input_data['offset'])
                        if offset < 0:
                            errors.append("Offset cannot be negative")
                    except (ValueError, TypeError):
                        errors.append("Offset must be an integer")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            errors.append(f"API input validation error: {str(e)}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def validate_feature_data(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate engineered features for ML pipeline.
        
        Args:
            df: DataFrame with engineered features
            
        Returns:
            Dict: Validation results for feature data
        """
        errors = []
        warnings = []
        
        try:
            if df is None or df.empty:
                errors.append("Feature DataFrame is None or empty")
                return {'valid': False, 'errors': errors, 'warnings': warnings}
            
            # Check for required feature columns
            required_features = list(ValidationHelpers.FEATURE_FIELD_RANGES.keys())
            missing_features = [f for f in required_features if f not in df.columns]
            
            if missing_features:
                errors.append(f"Missing required features: {missing_features}")
            
            # Validate feature ranges and distributions
            for feature, (min_val, max_val) in ValidationHelpers.FEATURE_FIELD_RANGES.items():
                if feature in df.columns:
                    feature_data = df[feature].dropna()
                    
                    if len(feature_data) == 0:
                        warnings.append(f"Feature '{feature}' has no valid values")
                        continue
                    
                    # Check ranges
                    out_of_range = ((feature_data < min_val) | (feature_data > max_val)).sum()
                    if out_of_range > 0:
                        warnings.append(f"Feature '{feature}' has {out_of_range} values outside range [{min_val}, {max_val}]")
                    
                    # Check for constant values
                    if feature_data.nunique() == 1:
                        warnings.append(f"Feature '{feature}' has constant value: {feature_data.iloc[0]}")
                    
                    # Check for extreme values
                    if np.isinf(feature_data).any():
                        inf_count = np.isinf(feature_data).sum()
                        warnings.append(f"Feature '{feature}' has {inf_count} infinite values")
            
            # Check feature correlations (basic check)
            numeric_features = [f for f in required_features if f in df.columns]
            if len(numeric_features) > 1:
                try:
                    corr_matrix = df[numeric_features].corr()
                    high_corr_pairs = []
                    
                    for i in range(len(numeric_features)):
                        for j in range(i+1, len(numeric_features)):
                            corr_val = corr_matrix.iloc[i, j]
                            if abs(corr_val) > 0.95:  # Very high correlation
                                high_corr_pairs.append((numeric_features[i], numeric_features[j], corr_val))
                    
                    if high_corr_pairs:
                        warnings.append(f"High feature correlations detected: {high_corr_pairs}")
                        
                except Exception as e:
                    warnings.append(f"Could not compute feature correlations: {str(e)}")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'feature_count': len([f for f in required_features if f in df.columns]),
                'total_features_expected': len(required_features)
            }
            
        except Exception as e:
            errors.append(f"Feature validation error: {str(e)}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def validate_configuration(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate system configuration parameters.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Validation results for configuration
        """
        errors = []
        warnings = []
        
        try:
            # Required configuration keys
            required_keys = ['gemini_api_key', 'risk_thresholds', 'alert_thresholds']
            
            for key in required_keys:
                if key not in config:
                    errors.append(f"Missing required configuration key: {key}")
            
            # Validate Gemini API key
            if 'gemini_api_key' in config:
                api_key = config['gemini_api_key']
                if not isinstance(api_key, str) or len(api_key.strip()) == 0:
                    errors.append("Gemini API key must be a non-empty string")
                elif len(api_key) < 20:  # Basic length check
                    warnings.append("Gemini API key seems too short")
            
            # Validate risk thresholds
            if 'risk_thresholds' in config:
                thresholds = config['risk_thresholds']
                if not isinstance(thresholds, dict):
                    errors.append("Risk thresholds must be a dictionary")
                else:
                    required_thresholds = ['safe_threshold', 'suspicious_threshold', 'fraud_threshold']
                    for threshold in required_thresholds:
                        if threshold not in thresholds:
                            errors.append(f"Missing risk threshold: {threshold}")
                        else:
                            try:
                                value = float(thresholds[threshold])
                                if not (-1 <= value <= 1):
                                    warnings.append(f"Risk threshold '{threshold}' outside expected range [-1, 1]: {value}")
                            except (ValueError, TypeError):
                                errors.append(f"Risk threshold '{threshold}' must be numeric: {thresholds[threshold]}")
            
            # Validate alert thresholds
            if 'alert_thresholds' in config:
                thresholds = config['alert_thresholds']
                if not isinstance(thresholds, dict):
                    errors.append("Alert thresholds must be a dictionary")
                else:
                    expected_alerts = ['price_deviation_threshold', 'company_risk_threshold', 'port_activity_threshold']
                    for alert in expected_alerts:
                        if alert in thresholds:
                            try:
                                value = float(thresholds[alert])
                                if value < 0:
                                    warnings.append(f"Alert threshold '{alert}' is negative: {value}")
                            except (ValueError, TypeError):
                                errors.append(f"Alert threshold '{alert}' must be numeric: {thresholds[alert]}")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            errors.append(f"Configuration validation error: {str(e)}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def sanitize_string_input(input_string: str, max_length: int = 1000, 
                            remove_html: bool = True, remove_sql: bool = True) -> str:
        """
        Comprehensive string sanitization for security and consistency.
        
        Args:
            input_string: String to sanitize
            max_length: Maximum allowed length
            remove_html: Whether to remove HTML-like tags
            remove_sql: Whether to remove potential SQL injection patterns
            
        Returns:
            str: Sanitized string
        """
        if not isinstance(input_string, str):
            input_string = str(input_string)
        
        # Remove potentially dangerous characters
        if remove_html:
            # Remove HTML tags and entities
            input_string = re.sub(r'<[^>]+>', '', input_string)
            input_string = re.sub(r'&[a-zA-Z0-9#]+;', '', input_string)
        
        if remove_sql:
            # Remove potential SQL injection patterns
            sql_patterns = [
                r'\b(DROP|DELETE|INSERT|UPDATE|SELECT|UNION|ALTER|CREATE)\b',
                r'[;\'"\\]',
                r'--',
                r'/\*.*?\*/'
            ]
            for pattern in sql_patterns:
                input_string = re.sub(pattern, '', input_string, flags=re.IGNORECASE)
        
        # Remove other potentially dangerous characters
        input_string = re.sub(r'[<>"\']', '', input_string)
        
        # Limit length
        if len(input_string) > max_length:
            input_string = input_string[:max_length] + "..."
        
        # Strip whitespace and normalize
        input_string = input_string.strip()
        input_string = re.sub(r'\s+', ' ', input_string)  # Normalize whitespace
        
        return input_string
    
    @staticmethod
    def validate_ml_model_input(features: np.ndarray) -> Dict[str, Any]:
        """
        Validate input data for ML model prediction.
        
        Args:
            features: Feature array for model input
            
        Returns:
            Dict: Validation results for ML input
        """
        errors = []
        warnings = []
        
        try:
            if features is None:
                errors.append("Features array is None")
                return {'valid': False, 'errors': errors, 'warnings': warnings}
            
            if not isinstance(features, np.ndarray):
                try:
                    features = np.array(features)
                except Exception as e:
                    errors.append(f"Cannot convert features to numpy array: {str(e)}")
                    return {'valid': False, 'errors': errors, 'warnings': warnings}
            
            # Check array shape
            if features.ndim != 2:
                errors.append(f"Features must be 2D array, got {features.ndim}D")
            
            if features.shape[1] != 6:  # Expected 6 features for TRINETRA AI
                warnings.append(f"Expected 6 features, got {features.shape[1]}")
            
            # Check for invalid values
            if np.isnan(features).any():
                nan_count = np.isnan(features).sum()
                warnings.append(f"Features contain {nan_count} NaN values")
            
            if np.isinf(features).any():
                inf_count = np.isinf(features).sum()
                warnings.append(f"Features contain {inf_count} infinite values")
            
            # Check feature ranges (basic sanity check)
            for i in range(features.shape[1]):
                feature_col = features[:, i]
                if len(feature_col) > 0:
                    min_val, max_val = np.nanmin(feature_col), np.nanmax(feature_col)
                    if max_val - min_val == 0:
                        warnings.append(f"Feature {i} has constant value: {min_val}")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'shape': features.shape,
                'nan_count': np.isnan(features).sum(),
                'inf_count': np.isinf(features).sum()
            }
            
        except Exception as e:
            errors.append(f"ML model input validation error: {str(e)}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def validate_model_predictions(predictions: np.ndarray, expected_shape: tuple = None) -> Dict[str, Any]:
        """
        Validate ML model prediction results.
        
        Args:
            predictions: Model prediction array
            expected_shape: Expected shape of predictions
            
        Returns:
            Dict: Validation results for model predictions
        """
        errors = []
        warnings = []
        
        try:
            if predictions is None:
                errors.append("Predictions array is None")
                return {'valid': False, 'errors': errors, 'warnings': warnings}
            
            if not isinstance(predictions, (np.ndarray, list)):
                try:
                    predictions = np.array(predictions)
                except Exception as e:
                    errors.append(f"Cannot convert predictions to array: {str(e)}")
                    return {'valid': False, 'errors': errors, 'warnings': warnings}
            
            predictions = np.array(predictions)
            
            # Check expected shape
            if expected_shape and predictions.shape != expected_shape:
                errors.append(f"Prediction shape mismatch: expected {expected_shape}, got {predictions.shape}")
            
            # Check for invalid values
            if np.isnan(predictions).any():
                nan_count = np.isnan(predictions).sum()
                warnings.append(f"Predictions contain {nan_count} NaN values")
            
            if np.isinf(predictions).any():
                inf_count = np.isinf(predictions).sum()
                warnings.append(f"Predictions contain {inf_count} infinite values")
            
            # Check prediction range (for risk scores, typically -1 to 1)
            if len(predictions) > 0:
                min_pred, max_pred = np.nanmin(predictions), np.nanmax(predictions)
                if min_pred < -10 or max_pred > 10:
                    warnings.append(f"Predictions have extreme values: min={min_pred:.4f}, max={max_pred:.4f}")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'shape': predictions.shape,
                'nan_count': np.isnan(predictions).sum(),
                'inf_count': np.isinf(predictions).sum(),
                'min_value': np.nanmin(predictions) if len(predictions) > 0 else None,
                'max_value': np.nanmax(predictions) if len(predictions) > 0 else None
            }
            
        except Exception as e:
            errors.append(f"Model prediction validation error: {str(e)}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def _is_valid_numeric(value: Any) -> bool:
        """
        Helper method to check if a value is valid numeric.
        
        Args:
            value: Value to check
            
        Returns:
            bool: True if value is valid numeric
        """
        try:
            if value is None:
                return False
            float_val = float(value)
            return not (np.isnan(float_val) or np.isinf(float_val))
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def get_validation_summary(validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary from multiple validation results.
        
        Args:
            validation_results: List of validation result dictionaries
            
        Returns:
            Dict: Summary of all validation results
        """
        total_validations = len(validation_results)
        passed_validations = sum(1 for result in validation_results if result.get('valid', False))
        
        all_errors = []
        all_warnings = []
        
        for result in validation_results:
            all_errors.extend(result.get('errors', []))
            all_warnings.extend(result.get('warnings', []))
        
        return {
            'total_validations': total_validations,
            'passed_validations': passed_validations,
            'failed_validations': total_validations - passed_validations,
            'success_rate': (passed_validations / max(1, total_validations)) * 100,
            'total_errors': len(all_errors),
            'total_warnings': len(all_warnings),
            'errors': all_errors,
            'warnings': all_warnings,
            'overall_valid': len(all_errors) == 0
        }

class ConfigurationHelpers:
    """
    Configuration management utilities for TRINETRA AI system.
    
    This class provides comprehensive configuration management including:
    - Environment variable management for API keys
    - Configuration for ML model parameters
    - API endpoint configurations
    - Dashboard settings and themes
    - File path configurations
    - Database/data source configurations
    """
    
    @staticmethod
    def load_environment_config() -> Dict[str, Any]:
        """
        Load configuration from environment variables with defaults.
        
        Returns:
            Dict: Complete configuration loaded from environment variables
        """
        try:
            config = {
                # AI/ML Configuration
                'gemini_api_key': os.getenv('GEMINI_API_KEY', ''),
                'gemini_model': os.getenv('GEMINI_MODEL', 'models/gemini-2.5-flash'),
                'gemini_timeout': int(os.getenv('GEMINI_TIMEOUT', '10')),
                'gemini_max_retries': int(os.getenv('GEMINI_MAX_RETRIES', '3')),
                
                # API Configuration
                'api_host': os.getenv('API_HOST', 'localhost'),
                'api_port': int(os.getenv('API_PORT', '8000')),
                'api_debug': os.getenv('API_DEBUG', 'false').lower() == 'true',
                'api_reload': os.getenv('API_RELOAD', 'true').lower() == 'true',
                
                # Dashboard Configuration
                'dashboard_host': os.getenv('DASHBOARD_HOST', 'localhost'),
                'dashboard_port': int(os.getenv('DASHBOARD_PORT', '8501')),
                'dashboard_theme': os.getenv('STREAMLIT_THEME', 'dark'),
                'dashboard_refresh_interval': int(os.getenv('DASHBOARD_REFRESH_INTERVAL', '30')),
                
                # Data Configuration
                'dataset_path': os.getenv('DATASET_PATH', 'data/trinetra_trade_fraud_dataset_1000_rows_complex.csv'),
                'model_path': os.getenv('MODEL_PATH', 'models/isolation_forest.pkl'),
                
                # ML Model Configuration
                'isolation_forest_n_estimators': int(os.getenv('ISOLATION_FOREST_N_ESTIMATORS', '100')),
                'isolation_forest_contamination': float(os.getenv('ISOLATION_FOREST_CONTAMINATION', '0.1')),
                'isolation_forest_random_state': int(os.getenv('ISOLATION_FOREST_RANDOM_STATE', '42')),
                
                # Risk Thresholds
                'risk_threshold_safe': float(os.getenv('RISK_THRESHOLD_SAFE', '-0.2')),
                'risk_threshold_fraud': float(os.getenv('RISK_THRESHOLD_FRAUD', '0.2')),
                
                # Alert Thresholds
                'alert_price_deviation_threshold': float(os.getenv('ALERT_PRICE_DEVIATION_THRESHOLD', '0.5')),
                'alert_company_risk_threshold': float(os.getenv('ALERT_COMPANY_RISK_THRESHOLD', '0.8')),
                'alert_port_activity_threshold': float(os.getenv('ALERT_PORT_ACTIVITY_THRESHOLD', '1.5')),
                
                # Logging Configuration
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'log_file': os.getenv('LOG_FILE', 'trinetra.log'),
                
                # CORS Configuration
                'cors_origins': os.getenv('CORS_ORIGINS', '*').split(','),
                'cors_methods': os.getenv('CORS_METHODS', '*').split(','),
                'cors_headers': os.getenv('CORS_HEADERS', '*').split(','),
                
                # Development Settings
                'environment': os.getenv('ENVIRONMENT', 'development'),
                'debug': os.getenv('DEBUG', 'false').lower() == 'true',
                'enable_ai_explanations': os.getenv('ENABLE_AI_EXPLANATIONS', 'true').lower() == 'true',
                'enable_alerts': os.getenv('ENABLE_ALERTS', 'true').lower() == 'true',
                'enable_caching': os.getenv('ENABLE_CACHING', 'true').lower() == 'true',
            }
            
            logger.info("Environment configuration loaded successfully")
            return config
            
        except Exception as e:
            logger.error(f"Error loading environment configuration: {e}")
            return ConfigurationHelpers.get_default_config()
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """
        Get default configuration values as fallback.
        
        Returns:
            Dict: Default configuration values
        """
        return {
            # AI/ML Configuration
            'gemini_api_key': '',
            'gemini_model': 'models/gemini-2.5-flash',
            'gemini_timeout': 10,
            'gemini_max_retries': 3,
            
            # API Configuration
            'api_host': 'localhost',
            'api_port': 8000,
            'api_debug': False,
            'api_reload': True,
            
            # Dashboard Configuration
            'dashboard_host': 'localhost',
            'dashboard_port': 8501,
            'dashboard_theme': 'dark',
            'dashboard_refresh_interval': 30,
            
            # Data Configuration
            'dataset_path': 'data/trinetra_trade_fraud_dataset_1000_rows_complex.csv',
            'model_path': 'models/isolation_forest.pkl',
            
            # ML Model Configuration
            'isolation_forest_n_estimators': 100,
            'isolation_forest_contamination': 0.1,
            'isolation_forest_random_state': 42,
            
            # Risk Thresholds
            'risk_threshold_safe': -0.2,
            'risk_threshold_fraud': 0.2,
            
            # Alert Thresholds
            'alert_price_deviation_threshold': 0.5,
            'alert_company_risk_threshold': 0.8,
            'alert_port_activity_threshold': 1.5,
            
            # Logging Configuration
            'log_level': 'INFO',
            'log_file': 'trinetra.log',
            
            # CORS Configuration
            'cors_origins': ['*'],
            'cors_methods': ['*'],
            'cors_headers': ['*'],
            
            # Development Settings
            'environment': 'development',
            'debug': False,
            'enable_ai_explanations': True,
            'enable_alerts': True,
            'enable_caching': True,
        }
    
    @staticmethod
    def get_api_config() -> Dict[str, Any]:
        """
        Get API-specific configuration settings.
        
        Returns:
            Dict: API configuration settings
        """
        config = ConfigurationHelpers.load_environment_config()
        return {
            'host': config['api_host'],
            'port': config['api_port'],
            'debug': config['api_debug'],
            'reload': config['api_reload'],
            'cors_origins': config['cors_origins'],
            'cors_methods': config['cors_methods'],
            'cors_headers': config['cors_headers'],
        }
    
    @staticmethod
    def get_gemini_config() -> Dict[str, Any]:
        """
        Get Gemini API configuration with secure handling of API key.
        
        Returns:
            Dict: Gemini API configuration
        """
        config = ConfigurationHelpers.load_environment_config()
        
        # Validate API key
        api_key = config['gemini_api_key']
        if not api_key or len(api_key.strip()) == 0:
            logger.warning("Gemini API key not configured - AI explanations will be disabled")
        elif len(api_key) < 20:
            logger.warning("Gemini API key appears to be invalid (too short)")
        
        return {
            'api_key': api_key,
            'model': config['gemini_model'],
            'timeout': config['gemini_timeout'],
            'max_retries': config['gemini_max_retries'],
            'enabled': bool(api_key and len(api_key.strip()) > 0)
        }
    
    @staticmethod
    def get_ml_model_config() -> Dict[str, Any]:
        """
        Get machine learning model configuration parameters.
        
        Returns:
            Dict: ML model configuration
        """
        config = ConfigurationHelpers.load_environment_config()
        return {
            'isolation_forest': {
                'n_estimators': config['isolation_forest_n_estimators'],
                'contamination': config['isolation_forest_contamination'],
                'random_state': config['isolation_forest_random_state'],
                'n_jobs': -1  # Use all available cores
            },
            'model_path': config['model_path'],
            'feature_count': 6,  # Expected number of features for TRINETRA AI
            'feature_names': [
                'price_anomaly_score',
                'route_risk_score', 
                'company_network_risk',
                'port_congestion_score',
                'shipment_duration_risk',
                'volume_spike_score'
            ]
        }
    
    @staticmethod
    def get_file_paths() -> Dict[str, str]:
        """
        Get all file path configurations with validation.
        
        Returns:
            Dict: File path configurations
        """
        config = ConfigurationHelpers.load_environment_config()
        
        paths = {
            'dataset': config['dataset_path'],
            'model': config['model_path'],
            'log_file': config['log_file'],
            'data_dir': 'data',
            'models_dir': 'models',
            'logs_dir': 'logs',
            'utils_dir': 'utils',
            'backend_dir': 'backend',
            'frontend_dir': 'frontend'
        }
        
        # Validate critical paths
        critical_paths = ['dataset', 'data_dir', 'backend_dir', 'utils_dir']
        for path_key in critical_paths:
            if path_key in paths and not os.path.exists(paths[path_key]):
                logger.warning(f"Critical path does not exist: {paths[path_key]}")
        
        return paths
    
    @staticmethod
    def get_dashboard_config() -> Dict[str, Any]:
        """
        Get dashboard and UI configuration settings.
        
        Returns:
            Dict: Dashboard configuration
        """
        config = ConfigurationHelpers.load_environment_config()
        return {
            'host': config['dashboard_host'],
            'port': config['dashboard_port'],
            'theme': config['dashboard_theme'],
            'refresh_interval': config['dashboard_refresh_interval'],
            'page_title': 'TRINETRA AI - Trade Fraud Intelligence',
            'page_icon': '🔍',
            'layout': 'wide',
            'sidebar_state': 'expanded',
            'display_settings': ConfigurationHelpers.get_display_settings()
        }
    
    @staticmethod
    def get_risk_thresholds() -> Dict[str, float]:
        """
        Get risk classification thresholds from environment or defaults.
        
        Returns:
            Dict: Risk thresholds for classification
        """
        config = ConfigurationHelpers.load_environment_config()
        return {
            'safe_threshold': config['risk_threshold_safe'],
            'suspicious_threshold': config['risk_threshold_fraud'],  # Suspicious is between safe and fraud
            'fraud_threshold': config['risk_threshold_fraud']
        }
    
    @staticmethod
    def get_alert_thresholds() -> Dict[str, float]:
        """
        Get alert trigger thresholds from environment or defaults.
        
        Returns:
            Dict: Alert thresholds for different indicators
        """
        config = ConfigurationHelpers.load_environment_config()
        return {
            'price_deviation_threshold': config['alert_price_deviation_threshold'],
            'company_risk_threshold': config['alert_company_risk_threshold'],
            'port_activity_threshold': config['alert_port_activity_threshold'],
            'route_anomaly_threshold': 1.0  # Route anomaly is binary (0 or 1)
        }
    
    @staticmethod
    def get_display_settings() -> Dict[str, Any]:
        """
        Get display formatting settings.
        
        Returns:
            Dict: Display configuration settings
        """
        return {
            'currency_symbol': CURRENCY_SYMBOL,
            'percentage_precision': PERCENTAGE_PRECISION,
            'decimal_precision': DECIMAL_PRECISION,
            'date_format': DATE_FORMAT,
            'datetime_format': DATETIME_FORMAT,
            'risk_colors': RISK_COLORS,
            'priority_colors': PRIORITY_COLORS
        }
    
    @staticmethod
    def get_logging_config() -> Dict[str, Any]:
        """
        Get logging configuration settings.
        
        Returns:
            Dict: Logging configuration
        """
        config = ConfigurationHelpers.load_environment_config()
        return {
            'level': config['log_level'],
            'file': config['log_file'],
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'date_format': '%Y-%m-%d %H:%M:%S'
        }
    
    @staticmethod
    def validate_configuration(config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate system configuration with comprehensive checks.
        
        Args:
            config: Optional configuration to validate. If None, loads from environment.
            
        Returns:
            Dict: Validation results
        """
        if config is None:
            config = ConfigurationHelpers.load_environment_config()
        
        errors = []
        warnings = []
        
        try:
            # Validate Gemini API configuration
            gemini_config = ConfigurationHelpers.get_gemini_config()
            if not gemini_config['enabled']:
                warnings.append("Gemini API key not configured - AI features will be limited")
            
            # Validate file paths
            file_paths = ConfigurationHelpers.get_file_paths()
            if not os.path.exists(file_paths['dataset']):
                errors.append(f"Dataset file not found: {file_paths['dataset']}")
            
            # Validate ML model configuration
            ml_config = ConfigurationHelpers.get_ml_model_config()
            if ml_config['isolation_forest']['contamination'] <= 0 or ml_config['isolation_forest']['contamination'] >= 1:
                errors.append("IsolationForest contamination must be between 0 and 1")
            
            # Validate risk thresholds
            risk_thresholds = ConfigurationHelpers.get_risk_thresholds()
            if risk_thresholds['safe_threshold'] >= risk_thresholds['fraud_threshold']:
                errors.append("Safe threshold must be less than fraud threshold")
            
            # Validate alert thresholds
            alert_thresholds = ConfigurationHelpers.get_alert_thresholds()
            for threshold_name, threshold_value in alert_thresholds.items():
                if threshold_value < 0:
                    warnings.append(f"Alert threshold '{threshold_name}' is negative: {threshold_value}")
            
            # Validate API configuration
            api_config = ConfigurationHelpers.get_api_config()
            if api_config['port'] < 1024 or api_config['port'] > 65535:
                warnings.append(f"API port {api_config['port']} may require special permissions or is invalid")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'config_sections': {
                    'gemini': gemini_config,
                    'api': api_config,
                    'ml_model': ml_config,
                    'file_paths': file_paths,
                    'risk_thresholds': risk_thresholds,
                    'alert_thresholds': alert_thresholds
                }
            }
            
        except Exception as e:
            errors.append(f"Configuration validation error: {str(e)}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def create_config_summary() -> str:
        """
        Create a human-readable configuration summary.
        
        Returns:
            str: Formatted configuration summary
        """
        try:
            config = ConfigurationHelpers.load_environment_config()
            validation = ConfigurationHelpers.validate_configuration(config)
            
            summary_lines = [
                "=" * 60,
                "TRINETRA AI - System Configuration Summary",
                "=" * 60,
                "",
                f"Environment: {config['environment']}",
                f"Debug Mode: {config['debug']}",
                "",
                "API Configuration:",
                f"  Host: {config['api_host']}:{config['api_port']}",
                f"  Debug: {config['api_debug']}",
                "",
                "Dashboard Configuration:",
                f"  Host: {config['dashboard_host']}:{config['dashboard_port']}",
                f"  Theme: {config['dashboard_theme']}",
                "",
                "AI Configuration:",
                f"  Gemini API: {'Enabled' if config['gemini_api_key'] else 'Disabled'}",
                f"  Model: {config['gemini_model']}",
                f"  Timeout: {config['gemini_timeout']}s",
                "",
                "ML Model Configuration:",
                f"  Estimators: {config['isolation_forest_n_estimators']}",
                f"  Contamination: {config['isolation_forest_contamination']}",
                f"  Random State: {config['isolation_forest_random_state']}",
                "",
                "Risk Thresholds:",
                f"  Safe: < {config['risk_threshold_safe']}",
                f"  Fraud: >= {config['risk_threshold_fraud']}",
                "",
                "Alert Thresholds:",
                f"  Price Deviation: {config['alert_price_deviation_threshold']}",
                f"  Company Risk: {config['alert_company_risk_threshold']}",
                f"  Port Activity: {config['alert_port_activity_threshold']}",
                "",
                "File Paths:",
                f"  Dataset: {config['dataset_path']}",
                f"  Model: {config['model_path']}",
                f"  Log File: {config['log_file']}",
                "",
                f"Configuration Status: {'VALID' if validation['valid'] else 'INVALID'}",
            ]
            
            if validation['errors']:
                summary_lines.extend([
                    "",
                    "Configuration Errors:",
                    *[f"  - {error}" for error in validation['errors']]
                ])
            
            if validation['warnings']:
                summary_lines.extend([
                    "",
                    "Configuration Warnings:",
                    *[f"  - {warning}" for warning in validation['warnings']]
                ])
            
            summary_lines.append("=" * 60)
            
            return "\n".join(summary_lines)
            
        except Exception as e:
            return f"Error creating configuration summary: {str(e)}"
    
    @staticmethod
    def save_config_to_file(config: Dict[str, Any], file_path: str = "config_backup.json") -> bool:
        """
        Save configuration to a JSON file for backup or debugging.
        
        Args:
            config: Configuration dictionary to save
            file_path: Path to save the configuration file
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Create a safe copy without sensitive data
            safe_config = config.copy()
            if 'gemini_api_key' in safe_config:
                safe_config['gemini_api_key'] = '[REDACTED]'
            
            with open(file_path, 'w') as f:
                json.dump(safe_config, f, indent=2, default=str)
            
            logger.info(f"Configuration saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration to file: {e}")
            return False

# Additional configuration utility functions
def load_config_from_file(file_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        file_path: Path to configuration file
        
    Returns:
        Dict: Configuration loaded from file
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Configuration file not found: {file_path}")
            return {}
        
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        logger.info(f"Configuration loaded from {file_path}")
        return config
        
    except Exception as e:
        logger.error(f"Error loading configuration from file: {e}")
        return {}


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries with later configs taking precedence.
    
    Args:
        *configs: Configuration dictionaries to merge
        
    Returns:
        Dict: Merged configuration
    """
    merged = {}
    
    for config in configs:
        if isinstance(config, dict):
            merged.update(config)
    
    return merged


def get_environment_info() -> Dict[str, Any]:
    """
    Get information about the current environment and system.
    
    Returns:
        Dict: Environment information
    """
    try:
        import platform
        import psutil
        
        return {
            'python_version': platform.python_version(),
            'platform': platform.platform(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
            'cpu_count': psutil.cpu_count(),
            'working_directory': os.getcwd(),
            'environment_variables': {
                key: value for key, value in os.environ.items() 
                if key.startswith(('TRINETRA_', 'GEMINI_', 'API_', 'LOG_', 'DATASET_', 'MODEL_'))
            }
        }
        
    except ImportError:
        # Fallback if psutil is not available
        return {
            'python_version': platform.python_version(),
            'platform': platform.platform(),
            'working_directory': os.getcwd(),
            'environment_variables': {
                key: value for key, value in os.environ.items() 
                if key.startswith(('TRINETRA_', 'GEMINI_', 'API_', 'LOG_', 'DATASET_', 'MODEL_'))
            }
        }
    except Exception as e:
        logger.error(f"Error getting environment info: {e}")
        return {'error': str(e)}


def validate_environment_setup() -> Dict[str, Any]:
    """
    Validate that the environment is properly set up for TRINETRA AI.
    
    Returns:
        Dict: Environment validation results
    """
    errors = []
    warnings = []
    
    try:
        # Check Python version
        import sys
        python_version = sys.version_info
        if python_version < (3, 8):
            errors.append(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        
        # Check required packages
        required_packages = [
            'pandas', 'numpy', 'scikit-learn', 'fastapi', 'streamlit', 
            'plotly', 'uvicorn', 'google-generativeai', 'pydantic'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            errors.append(f"Missing required packages: {missing_packages}")
        
        # Check environment variables
        config = ConfigurationHelpers.load_environment_config()
        if not config['gemini_api_key']:
            warnings.append("GEMINI_API_KEY not set - AI features will be disabled")
        
        # Check file system
        required_dirs = ['data', 'models', 'logs', 'utils', 'backend']
        missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
        if missing_dirs:
            warnings.append(f"Missing directories: {missing_dirs}")
        
        # Check dataset file
        if not os.path.exists(config['dataset_path']):
            errors.append(f"Dataset file not found: {config['dataset_path']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'python_version': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
            'packages_checked': len(required_packages),
            'missing_packages': missing_packages,
            'environment_ready': len(errors) == 0
        }
        
    except Exception as e:
        errors.append(f"Environment validation error: {str(e)}")
        return {'valid': False, 'errors': errors, 'warnings': warnings}


def create_environment_report() -> str:
    """
    Create a comprehensive environment and configuration report.
    
    Returns:
        str: Formatted environment report
    """
    try:
        env_info = get_environment_info()
        env_validation = validate_environment_setup()
        config_validation = ConfigurationHelpers.validate_configuration()
        
        report_lines = [
            "=" * 80,
            "TRINETRA AI - Environment & Configuration Report",
            "=" * 80,
            "",
            "System Information:",
            f"  Python Version: {env_info.get('python_version', 'Unknown')}",
            f"  Platform: {env_info.get('platform', 'Unknown')}",
            f"  Architecture: {env_info.get('architecture', 'Unknown')}",
            f"  Working Directory: {env_info.get('working_directory', 'Unknown')}",
            "",
            f"Environment Status: {'READY' if env_validation['environment_ready'] else 'NOT READY'}",
            f"Configuration Status: {'VALID' if config_validation['valid'] else 'INVALID'}",
            "",
        ]
        
        # Add memory info if available
        if 'memory_total_gb' in env_info:
            report_lines.extend([
                "Hardware Information:",
                f"  CPU Cores: {env_info.get('cpu_count', 'Unknown')}",
                f"  Total Memory: {env_info.get('memory_total_gb', 'Unknown')} GB",
                f"  Available Memory: {env_info.get('memory_available_gb', 'Unknown')} GB",
                "",
            ])
        
        # Add environment validation results
        if env_validation['errors']:
            report_lines.extend([
                "Environment Errors:",
                *[f"  - {error}" for error in env_validation['errors']],
                ""
            ])
        
        if env_validation['warnings']:
            report_lines.extend([
                "Environment Warnings:",
                *[f"  - {warning}" for warning in env_validation['warnings']],
                ""
            ])
        
        # Add configuration validation results
        if config_validation['errors']:
            report_lines.extend([
                "Configuration Errors:",
                *[f"  - {error}" for error in config_validation['errors']],
                ""
            ])
        
        if config_validation['warnings']:
            report_lines.extend([
                "Configuration Warnings:",
                *[f"  - {warning}" for warning in config_validation['warnings']],
                ""
            ])
        
        # Add environment variables (non-sensitive)
        env_vars = env_info.get('environment_variables', {})
        if env_vars:
            report_lines.extend([
                "Environment Variables:",
                *[f"  {key}: {'[SET]' if value else '[NOT SET]'}" for key, value in env_vars.items()],
                ""
            ])
        
        report_lines.extend([
            "Configuration Summary:",
            ConfigurationHelpers.create_config_summary(),
            "",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
        
    except Exception as e:
        return f"Error creating environment report: {str(e)}"


def setup_configuration_logging():
    """
    Set up logging specifically for configuration management.
    """
    config_logger = logging.getLogger('trinetra.configuration')
    config_logger.info("Configuration management utilities initialized")
    
    # Log current configuration status
    try:
        validation = ConfigurationHelpers.validate_configuration()
        if validation['valid']:
            config_logger.info("System configuration is valid")
        else:
            config_logger.warning(f"System configuration has issues: {validation['errors']}")
    except Exception as e:
        config_logger.error(f"Error validating configuration: {e}")


# Initialize configuration logging
setup_configuration_logging()

# Additional configuration management utilities for TRINETRA AI system

def get_system_config() -> Dict[str, Any]:
    """
    Get complete system configuration for TRINETRA AI.
    
    This function consolidates all configuration aspects into a single
    comprehensive configuration dictionary for easy access across the system.
    
    Returns:
        Dict: Complete system configuration
    """
    try:
        config = {
            # Core system configuration
            'system': {
                'name': 'TRINETRA AI',
                'version': '1.0.0',
                'description': 'Trade Fraud Intelligence System',
                'environment': os.getenv('ENVIRONMENT', 'development')
            },
            
            # Load all configuration sections
            'api': ConfigurationHelpers.get_api_config(),
            'gemini': ConfigurationHelpers.get_gemini_config(),
            'ml_model': ConfigurationHelpers.get_ml_model_config(),
            'dashboard': ConfigurationHelpers.get_dashboard_config(),
            'file_paths': ConfigurationHelpers.get_file_paths(),
            'risk_thresholds': ConfigurationHelpers.get_risk_thresholds(),
            'alert_thresholds': ConfigurationHelpers.get_alert_thresholds(),
            'logging': ConfigurationHelpers.get_logging_config(),
            'display': ConfigurationHelpers.get_display_settings(),
            
            # Runtime configuration
            'runtime': {
                'startup_time': datetime.now().isoformat(),
                'python_version': sys.version,
                'working_directory': os.getcwd(),
                'process_id': os.getpid()
            }
        }
        
        logger.info("Complete system configuration loaded successfully")
        return config
        
    except Exception as e:
        logger.error(f"Error loading complete system configuration: {e}")
        return ConfigurationHelpers.get_default_config()


def initialize_system_configuration() -> Dict[str, Any]:
    """
    Initialize and validate complete system configuration.
    
    This function performs comprehensive system configuration initialization,
    validation, and setup. It should be called during system startup.
    
    Returns:
        Dict: Initialization results with configuration and validation status
    """
    try:
        logger.info("Initializing TRINETRA AI system configuration...")
        
        # Load complete configuration
        config = get_system_config()
        
        # Validate configuration
        validation = ConfigurationHelpers.validate_configuration()
        
        # Create necessary directories
        directories_to_create = [
            config['file_paths']['data_dir'],
            config['file_paths']['models_dir'],
            config['file_paths']['logs_dir']
        ]
        
        for directory in directories_to_create:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Ensured directory exists: {directory}")
            except Exception as e:
                logger.warning(f"Could not create directory {directory}: {e}")
        
        # Log configuration summary
        if validation['valid']:
            logger.info("System configuration validation: PASSED")
        else:
            logger.warning(f"System configuration validation: FAILED - {validation['errors']}")
        
        # Log key configuration settings (without sensitive data)
        logger.info(f"API Host: {config['api']['host']}:{config['api']['port']}")
        logger.info(f"Dashboard Host: {config['dashboard']['host']}:{config['dashboard']['port']}")
        logger.info(f"Gemini API: {'Enabled' if config['gemini']['enabled'] else 'Disabled'}")
        logger.info(f"Environment: {config['system']['environment']}")
        
        return {
            'success': True,
            'config': config,
            'validation': validation,
            'directories_created': directories_to_create,
            'initialization_time': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"System configuration initialization failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'config': ConfigurationHelpers.get_default_config(),
            'validation': {'valid': False, 'errors': [str(e)], 'warnings': []}
        }


def update_runtime_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update runtime configuration settings.
    
    This function allows for dynamic updates to certain configuration
    settings during runtime without requiring a system restart.
    
    Args:
        updates: Dictionary of configuration updates
        
    Returns:
        Dict: Update results with success status and applied changes
    """
    try:
        logger.info(f"Updating runtime configuration: {list(updates.keys())}")
        
        # Define which settings can be updated at runtime
        updatable_settings = {
            'log_level', 'dashboard_refresh_interval', 'gemini_timeout',
            'gemini_max_retries', 'enable_ai_explanations', 'enable_alerts',
            'enable_caching', 'alert_price_deviation_threshold',
            'alert_company_risk_threshold', 'alert_port_activity_threshold'
        }
        
        applied_updates = {}
        skipped_updates = {}
        
        for key, value in updates.items():
            if key in updatable_settings:
                # Update environment variable
                os.environ[key.upper()] = str(value)
                applied_updates[key] = value
                logger.info(f"Updated runtime config: {key} = {value}")
            else:
                skipped_updates[key] = f"Setting '{key}' cannot be updated at runtime"
                logger.warning(f"Skipped runtime config update: {key} (not updatable)")
        
        return {
            'success': True,
            'applied_updates': applied_updates,
            'skipped_updates': skipped_updates,
            'update_time': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating runtime configuration: {e}")
        return {
            'success': False,
            'error': str(e),
            'applied_updates': {},
            'skipped_updates': updates
        }


# Configuration caching mechanism for improved performance
class ConfigurationCache:
    """
    Configuration caching mechanism to improve performance by avoiding
    repeated environment variable lookups and configuration validation.
    """
    
    def __init__(self):
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 300  # 5 minutes TTL
        self.logger = logging.getLogger(f"{__name__}.ConfigurationCache")
    
    def get_cached_config(self, config_type: str) -> Optional[Dict[str, Any]]:
        """
        Get cached configuration if still valid.
        
        Args:
            config_type: Type of configuration to retrieve
            
        Returns:
            Dict or None: Cached configuration if valid, None if expired/missing
        """
        if config_type not in self._cache:
            return None
        
        # Check if cache is still valid
        cache_time = self._cache_timestamps.get(config_type, 0)
        current_time = time.time()
        
        if current_time - cache_time > self._cache_ttl:
            # Cache expired, remove it
            self._cache.pop(config_type, None)
            self._cache_timestamps.pop(config_type, None)
            return None
        
        return self._cache[config_type]
    
    def set_cached_config(self, config_type: str, config: Dict[str, Any]):
        """
        Cache configuration with timestamp.
        
        Args:
            config_type: Type of configuration to cache
            config: Configuration dictionary to cache
        """
        self._cache[config_type] = config.copy()
        self._cache_timestamps[config_type] = time.time()
        self.logger.debug(f"Cached configuration: {config_type}")
    
    def clear_cache(self, config_type: str = None):
        """
        Clear cached configuration.
        
        Args:
            config_type: Specific config type to clear, or None to clear all
        """
        if config_type:
            self._cache.pop(config_type, None)
            self._cache_timestamps.pop(config_type, None)
            self.logger.info(f"Cleared cache for: {config_type}")
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
            self.logger.info("Cleared all configuration cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict: Cache statistics
        """
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        for config_type, cache_time in self._cache_timestamps.items():
            if current_time - cache_time <= self._cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_ttl_seconds': self._cache_ttl,
            'cached_types': list(self._cache.keys())
        }


# Global configuration cache instance
_config_cache = ConfigurationCache()


def get_cached_system_config() -> Dict[str, Any]:
    """
    Get system configuration with caching for improved performance.
    
    Returns:
        Dict: Complete system configuration (cached if available)
    """
    # Try to get from cache first
    cached_config = _config_cache.get_cached_config('system')
    if cached_config:
        logger.debug("Using cached system configuration")
        return cached_config
    
    # Load fresh configuration
    config = get_system_config()
    
    # Cache the configuration
    _config_cache.set_cached_config('system', config)
    
    return config


def refresh_configuration_cache():
    """
    Refresh all cached configurations by clearing cache and reloading.
    """
    logger.info("Refreshing configuration cache...")
    _config_cache.clear_cache()
    
    # Pre-load commonly used configurations
    get_cached_system_config()
    
    logger.info("Configuration cache refreshed successfully")


def get_configuration_cache_stats() -> Dict[str, Any]:
    """
    Get configuration cache statistics.
    
    Returns:
        Dict: Cache statistics and performance metrics
    """
    return _config_cache.get_cache_stats()


# Configuration management completion marker
logger.info("Configuration management utilities fully initialized and ready")
logger.info("Available configuration functions: environment loading, validation, caching, and runtime updates")


def format_large_number(number: Union[int, float], precision: int = 1) -> str:
    """
    Format large numbers with appropriate suffixes (K, M, B).
    
    Args:
        number: Number to format
        precision: Decimal precision for formatted number
        
    Returns:
        str: Formatted number with suffix
        
    Examples:
        >>> format_large_number(1500)
        '1.5K'
        >>> format_large_number(2500000)
        '2.5M'
    """
    try:
        if number is None:
            return "0"
        
        number = float(number)
        
        if abs(number) >= 1_000_000_000:
            return f"{number / 1_000_000_000:.{precision}f}B"
        elif abs(number) >= 1_000_000:
            return f"{number / 1_000_000:.{precision}f}M"
        elif abs(number) >= 1_000:
            return f"{number / 1_000:.{precision}f}K"
        else:
            return f"{number:.{precision}f}"
            
    except (ValueError, TypeError):
        return "0"


def get_configuration_health_check() -> Dict[str, Any]:
    """
    Perform comprehensive health check of system configuration.
    
    This function validates all aspects of the TRINETRA AI configuration
    and provides a detailed health report for monitoring and diagnostics.
    
    Returns:
        Dict: Configuration health check results
    """
    try:
        logger.info("Performing configuration health check...")
        
        health_results = {
            'overall_status': 'HEALTHY',
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # 1. Environment validation
        env_validation = validate_environment_setup()
        health_results['checks']['environment'] = {
            'status': 'PASS' if env_validation['valid'] else 'FAIL',
            'details': env_validation
        }
        if not env_validation['valid']:
            health_results['errors'].extend(env_validation['errors'])
            health_results['overall_status'] = 'UNHEALTHY'
        if env_validation['warnings']:
            health_results['warnings'].extend(env_validation['warnings'])
        
        # 2. Configuration validation
        config_validation = ConfigurationHelpers.validate_configuration()
        health_results['checks']['configuration'] = {
            'status': 'PASS' if config_validation['valid'] else 'FAIL',
            'details': config_validation
        }
        if not config_validation['valid']:
            health_results['errors'].extend(config_validation['errors'])
            health_results['overall_status'] = 'UNHEALTHY'
        if config_validation['warnings']:
            health_results['warnings'].extend(config_validation['warnings'])
        
        # 3. File system checks
        file_paths = ConfigurationHelpers.get_file_paths()
        file_check = {
            'status': 'PASS',
            'missing_files': [],
            'missing_directories': [],
            'permission_issues': []
        }
        
        # Check critical files
        critical_files = [file_paths['dataset']]
        for file_path in critical_files:
            if not os.path.exists(file_path):
                file_check['missing_files'].append(file_path)
                file_check['status'] = 'FAIL'
        
        # Check directories
        critical_dirs = [file_paths['data_dir'], file_paths['models_dir'], file_paths['logs_dir']]
        for dir_path in critical_dirs:
            if not os.path.exists(dir_path):
                file_check['missing_directories'].append(dir_path)
                file_check['status'] = 'WARN'
            elif not os.access(dir_path, os.W_OK):
                file_check['permission_issues'].append(f"No write access: {dir_path}")
                file_check['status'] = 'WARN'
        
        health_results['checks']['file_system'] = file_check
        if file_check['status'] == 'FAIL':
            health_results['overall_status'] = 'UNHEALTHY'
            health_results['errors'].extend([f"Missing file: {f}" for f in file_check['missing_files']])
        elif file_check['status'] == 'WARN':
            if health_results['overall_status'] == 'HEALTHY':
                health_results['overall_status'] = 'DEGRADED'
            health_results['warnings'].extend([f"Missing directory: {d}" for d in file_check['missing_directories']])
            health_results['warnings'].extend(file_check['permission_issues'])
        
        # 4. API connectivity checks
        gemini_config = ConfigurationHelpers.get_gemini_config()
        api_check = {
            'status': 'PASS',
            'gemini_configured': gemini_config['enabled'],
            'api_key_valid': bool(gemini_config['api_key'] and len(gemini_config['api_key']) > 20)
        }
        
        if not gemini_config['enabled']:
            api_check['status'] = 'WARN'
            health_results['warnings'].append("Gemini API not configured - AI features will be limited")
            if health_results['overall_status'] == 'HEALTHY':
                health_results['overall_status'] = 'DEGRADED'
        
        health_results['checks']['api_connectivity'] = api_check
        
        # 5. ML model configuration checks
        ml_config = ConfigurationHelpers.get_ml_model_config()
        model_check = {
            'status': 'PASS',
            'model_file_exists': os.path.exists(ml_config['model_path']),
            'feature_count': ml_config['feature_count'],
            'expected_features': len(ml_config['feature_names'])
        }
        
        if not model_check['model_file_exists']:
            model_check['status'] = 'WARN'
            health_results['warnings'].append(f"ML model file not found: {ml_config['model_path']} (will be trained on startup)")
            if health_results['overall_status'] == 'HEALTHY':
                health_results['overall_status'] = 'DEGRADED'
        
        health_results['checks']['ml_model'] = model_check
        
        # 6. Generate recommendations
        if health_results['warnings']:
            health_results['recommendations'].append("Review and address configuration warnings")
        if not gemini_config['enabled']:
            health_results['recommendations'].append("Configure GEMINI_API_KEY environment variable to enable AI features")
        if file_check['missing_directories']:
            health_results['recommendations'].append("Run system initialization to create missing directories")
        if not model_check['model_file_exists']:
            health_results['recommendations'].append("Train ML model by running the complete system startup process")
        
        # 7. Calculate health score
        total_checks = len(health_results['checks'])
        passed_checks = sum(1 for check in health_results['checks'].values() if check['status'] == 'PASS')
        health_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        health_results['health_score'] = round(health_score, 1)
        health_results['checks_summary'] = {
            'total': total_checks,
            'passed': passed_checks,
            'failed': sum(1 for check in health_results['checks'].values() if check['status'] == 'FAIL'),
            'warnings': sum(1 for check in health_results['checks'].values() if check['status'] == 'WARN')
        }
        
        logger.info(f"Configuration health check completed - Status: {health_results['overall_status']}, Score: {health_score}%")
        
        return health_results
        
    except Exception as e:
        logger.error(f"Configuration health check failed: {e}")
        return {
            'overall_status': 'ERROR',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'health_score': 0,
            'checks': {},
            'warnings': [],
            'errors': [f"Health check failed: {str(e)}"],
            'recommendations': ['Contact system administrator']
        }


def format_large_number(number: Union[int, float], precision: int = 1) -> str:
    """
    Format large numbers with appropriate suffixes (K, M, B).
    
    Args:
        number: Number to format
        precision: Decimal precision for formatted number
        
    Returns:
        str: Formatted number with suffix
        
    Examples:
        >>> format_large_number(1500)
        '1.5K'
        >>> format_large_number(2500000)
        '2.5M'
    """
    try:
        if number is None:
            return "0"
        
        number = float(number)
        
        if abs(number) >= 1_000_000_000:
            return f"{number / 1_000_000_000:.{precision}f}B"
        elif abs(number) >= 1_000_000:
            return f"{number / 1_000_000:.{precision}f}M"
        elif abs(number) >= 1_000:
            return f"{number / 1_000:.{precision}f}K"
        else:
            return f"{number:.{precision}f}"
            
    except (ValueError, TypeError):
        return "0"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncated
        
    Returns:
        str: Truncated text
    """
    if not isinstance(text, str):
        text = str(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: float = 0.0) -> float:
    """
    Safely divide two numbers, handling division by zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value when division by zero
        
    Returns:
        float: Division result or default value
    """
    try:
        if denominator == 0 or np.isnan(denominator) or np.isinf(denominator):
            return default
        
        result = float(numerator) / float(denominator)
        
        if np.isnan(result) or np.isinf(result):
            return default
        
        return result
        
    except (ValueError, TypeError, ZeroDivisionError):
        return default


def get_color_for_risk_category(category: str) -> str:
    """
    Get color code for risk category.
    
    Args:
        category: Risk category (SAFE, SUSPICIOUS, FRAUD)
        
    Returns:
        str: Hex color code
    """
    return RISK_COLORS.get(category.upper(), "#6c757d")  # Default to gray


def get_priority_color(priority: str) -> str:
    """
    Get color code for alert priority.
    
    Args:
        priority: Priority level (LOW, MEDIUM, HIGH, CRITICAL)
        
    Returns:
        str: Hex color code
    """
    return PRIORITY_COLORS.get(priority.upper(), "#6c757d")  # Default to gray


# Additional validation utility functions
def validate_file_path(file_path: str, must_exist: bool = True, extensions: List[str] = None) -> Dict[str, Any]:
    """
    Validate file path for data loading operations.
    
    Args:
        file_path: Path to validate
        must_exist: Whether file must exist
        extensions: Allowed file extensions (e.g., ['.csv', '.json'])
        
    Returns:
        Dict: Validation results
    """
    errors = []
    warnings = []
    
    try:
        if not isinstance(file_path, str) or not file_path.strip():
            errors.append("File path must be a non-empty string")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        file_path = file_path.strip()
        
        # Check if path exists
        if must_exist and not os.path.exists(file_path):
            errors.append(f"File does not exist: {file_path}")
        
        # Check file extension
        if extensions:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in [ext.lower() for ext in extensions]:
                errors.append(f"Invalid file extension '{file_ext}'. Allowed: {extensions}")
        
        # Check if it's a file (not directory)
        if os.path.exists(file_path) and os.path.isdir(file_path):
            errors.append(f"Path is a directory, not a file: {file_path}")
        
        # Check file permissions
        if os.path.exists(file_path):
            if not os.access(file_path, os.R_OK):
                errors.append(f"File is not readable: {file_path}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'absolute_path': os.path.abspath(file_path),
            'exists': os.path.exists(file_path)
        }
        
    except Exception as e:
        errors.append(f"File path validation error: {str(e)}")
        return {'valid': False, 'errors': errors, 'warnings': warnings}


def validate_dataframe_for_ml(df: pd.DataFrame, required_features: List[str] = None) -> Dict[str, Any]:
    """
    Validate DataFrame for ML model training/prediction.
    
    Args:
        df: DataFrame to validate
        required_features: List of required feature columns
        
    Returns:
        Dict: Validation results
    """
    errors = []
    warnings = []
    
    try:
        if df is None or df.empty:
            errors.append("DataFrame is None or empty")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check required features
        if required_features:
            missing_features = [f for f in required_features if f not in df.columns]
            if missing_features:
                errors.append(f"Missing required features: {missing_features}")
        
        # Check for infinite values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            inf_count = np.isinf(df[col]).sum()
            if inf_count > 0:
                warnings.append(f"Column '{col}' has {inf_count} infinite values")
        
        # Check for high null percentage
        null_percentages = (df.isnull().sum() / len(df)) * 100
        high_null_cols = null_percentages[null_percentages > 50].index.tolist()
        if high_null_cols:
            warnings.append(f"Columns with >50% null values: {high_null_cols}")
        
        # Check for constant columns
        constant_cols = []
        for col in numeric_cols:
            if df[col].nunique() <= 1:
                constant_cols.append(col)
        if constant_cols:
            warnings.append(f"Constant value columns detected: {constant_cols}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'shape': df.shape,
            'numeric_columns': len(numeric_cols),
            'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        }
        
    except Exception as e:
        errors.append(f"DataFrame ML validation error: {str(e)}")
        return {'valid': False, 'errors': errors, 'warnings': warnings}


def create_validation_report(validation_results: Dict[str, Any], title: str = "Validation Report") -> str:
    """
    Create a formatted validation report.
    
    Args:
        validation_results: Validation results dictionary
        title: Report title
        
    Returns:
        str: Formatted validation report
    """
    try:
        report_lines = [
            "=" * 60,
            f"{title}",
            "=" * 60,
            f"Status: {'PASSED' if validation_results.get('valid', False) else 'FAILED'}",
            ""
        ]
        
        # Add summary information
        if 'summary' in validation_results:
            report_lines.extend([
                "Summary:",
                f"  {validation_results['summary']}",
                ""
            ])
        
        # Add errors
        errors = validation_results.get('errors', [])
        if errors:
            report_lines.extend([
                f"Errors ({len(errors)}):",
                *[f"  - {error}" for error in errors],
                ""
            ])
        
        # Add warnings
        warnings = validation_results.get('warnings', [])
        if warnings:
            report_lines.extend([
                f"Warnings ({len(warnings)}):",
                *[f"  - {warning}" for warning in warnings],
                ""
            ])
        
        # Add additional details
        details = validation_results.get('details', {})
        if details:
            report_lines.extend([
                "Details:",
                *[f"  {key}: {value}" for key, value in details.items()],
                ""
            ])
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
        
    except Exception as e:
        return f"Error generating validation report: {str(e)}"


def validate_risk_score_range(risk_score: Union[float, int, str]) -> Dict[str, Any]:
    """
    Validate that risk scores are within expected range for TRINETRA AI system.
    
    Args:
        risk_score: Risk score value to validate
        
    Returns:
        Dict: Validation results with 'valid', 'errors', 'warnings', 'normalized_score'
    """
    errors = []
    warnings = []
    normalized_score = None
    
    try:
        # Convert to float
        if isinstance(risk_score, str):
            clean_value = re.sub(r'[^\d.-]', '', risk_score)
            if not clean_value:
                errors.append("Risk score cannot be empty or non-numeric")
                return {'valid': False, 'errors': errors, 'warnings': warnings, 'normalized_score': None}
            score = float(clean_value)
        else:
            score = float(risk_score)
        
        # Handle special cases
        if np.isnan(score):
            errors.append("Risk score cannot be NaN")
            return {'valid': False, 'errors': errors, 'warnings': warnings, 'normalized_score': None}
        
        if np.isinf(score):
            errors.append("Risk score cannot be infinite")
            return {'valid': False, 'errors': errors, 'warnings': warnings, 'normalized_score': None}
        
        # Validate range (TRINETRA AI uses -1 to 1 range typically)
        if score < -1.0:
            warnings.append(f"Risk score {score} is below expected minimum (-1.0)")
        elif score > 1.0:
            warnings.append(f"Risk score {score} is above expected maximum (1.0)")
        
        # Normalize score to [-1, 1] range if needed
        if score < -1.0:
            normalized_score = -1.0
            warnings.append(f"Risk score clamped to minimum value: {normalized_score}")
        elif score > 1.0:
            normalized_score = 1.0
            warnings.append(f"Risk score clamped to maximum value: {normalized_score}")
        else:
            normalized_score = score
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'normalized_score': normalized_score,
            'original_score': score,
            'risk_category': DataFormatter.get_risk_category(normalized_score)
        }
        
    except (ValueError, TypeError) as e:
        errors.append(f"Invalid risk score format: {str(e)}")
        return {'valid': False, 'errors': errors, 'warnings': warnings, 'normalized_score': None}


def validate_alert_thresholds(thresholds: Dict[str, float]) -> Dict[str, Any]:
    """
    Validate alert threshold configuration for TRINETRA AI system.
    
    Args:
        thresholds: Dictionary of alert thresholds
        
    Returns:
        Dict: Validation results for alert thresholds
    """
    errors = []
    warnings = []
    
    try:
        if not isinstance(thresholds, dict):
            errors.append("Alert thresholds must be a dictionary")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Expected threshold keys and their valid ranges
        expected_thresholds = {
            'price_deviation_threshold': (0.0, 1.0),
            'company_risk_threshold': (0.0, 1.0),
            'port_activity_threshold': (0.0, 10.0),
            'route_anomaly_threshold': (0.0, 1.0)
        }
        
        # Check for required thresholds
        missing_thresholds = [key for key in expected_thresholds.keys() if key not in thresholds]
        if missing_thresholds:
            errors.append(f"Missing required alert thresholds: {missing_thresholds}")
        
        # Validate each threshold
        for threshold_name, (min_val, max_val) in expected_thresholds.items():
            if threshold_name in thresholds:
                try:
                    value = float(thresholds[threshold_name])
                    
                    if np.isnan(value) or np.isinf(value):
                        errors.append(f"Alert threshold '{threshold_name}' has invalid value: {value}")
                    elif value < min_val or value > max_val:
                        warnings.append(f"Alert threshold '{threshold_name}' value {value} outside recommended range [{min_val}, {max_val}]")
                    
                except (ValueError, TypeError):
                    errors.append(f"Alert threshold '{threshold_name}' must be numeric: {thresholds[threshold_name]}")
        
        # Check for unknown thresholds
        unknown_thresholds = [key for key in thresholds.keys() if key not in expected_thresholds]
        if unknown_thresholds:
            warnings.append(f"Unknown alert thresholds (will be ignored): {unknown_thresholds}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'threshold_count': len([k for k in expected_thresholds.keys() if k in thresholds]),
            'expected_count': len(expected_thresholds)
        }
        
    except Exception as e:
        errors.append(f"Alert threshold validation error: {str(e)}")
        return {'valid': False, 'errors': errors, 'warnings': warnings}


def validate_gemini_api_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate Gemini API response structure and content.
    
    Args:
        response: Gemini API response dictionary
        
    Returns:
        Dict: Validation results for API response
    """
    errors = []
    warnings = []
    
    try:
        if not isinstance(response, dict):
            errors.append("Gemini API response must be a dictionary")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check for required fields in successful response
        if 'text' in response:
            text_content = response['text']
            if not isinstance(text_content, str):
                errors.append("Response text must be a string")
            elif len(text_content.strip()) == 0:
                warnings.append("Response text is empty")
            elif len(text_content) > 10000:
                warnings.append(f"Response text is very long: {len(text_content)} characters")
        
        # Check for error indicators
        if 'error' in response:
            error_info = response['error']
            if isinstance(error_info, dict):
                if 'message' in error_info:
                    warnings.append(f"API error message: {error_info['message']}")
                if 'code' in error_info:
                    warnings.append(f"API error code: {error_info['code']}")
            else:
                warnings.append(f"API error: {error_info}")
        
        # Check response metadata
        if 'usage' in response:
            usage = response['usage']
            if isinstance(usage, dict):
                if 'prompt_tokens' in usage and usage['prompt_tokens'] > 8000:
                    warnings.append(f"High prompt token usage: {usage['prompt_tokens']}")
                if 'completion_tokens' in usage and usage['completion_tokens'] > 2000:
                    warnings.append(f"High completion token usage: {usage['completion_tokens']}")
        
        # Validate content quality (basic checks)
        if 'text' in response and response['text']:
            text = response['text'].lower()
            
            # Check for common error patterns
            error_patterns = [
                'i cannot', 'i am unable', 'i don\'t have access',
                'error occurred', 'something went wrong', 'try again'
            ]
            
            for pattern in error_patterns:
                if pattern in text:
                    warnings.append(f"Response may contain error indication: '{pattern}'")
                    break
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'has_text': 'text' in response and bool(response['text']),
            'has_error': 'error' in response,
            'text_length': len(response.get('text', ''))
        }
        
    except Exception as e:
        errors.append(f"Gemini API response validation error: {str(e)}")
        return {'valid': False, 'errors': errors, 'warnings': warnings}


def validate_dashboard_data(dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate data structure for dashboard display.
    
    Args:
        dashboard_data: Data dictionary for dashboard
        
    Returns:
        Dict: Validation results for dashboard data
    """
    errors = []
    warnings = []
    
    try:
        if not isinstance(dashboard_data, dict):
            errors.append("Dashboard data must be a dictionary")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Expected dashboard data sections
        expected_sections = [
            'transactions', 'statistics', 'alerts', 'suspicious_transactions'
        ]
        
        missing_sections = [section for section in expected_sections if section not in dashboard_data]
        if missing_sections:
            warnings.append(f"Missing dashboard sections: {missing_sections}")
        
        # Validate transactions data
        if 'transactions' in dashboard_data:
            transactions = dashboard_data['transactions']
            if not isinstance(transactions, list):
                errors.append("Transactions must be a list")
            elif len(transactions) == 0:
                warnings.append("No transactions data available")
            else:
                # Validate first few transactions
                for i, transaction in enumerate(transactions[:5]):
                    if not isinstance(transaction, dict):
                        errors.append(f"Transaction {i} must be a dictionary")
                        continue
                    
                    required_fields = ['transaction_id', 'risk_score', 'risk_category']
                    missing_fields = [field for field in required_fields if field not in transaction]
                    if missing_fields:
                        errors.append(f"Transaction {i} missing fields: {missing_fields}")
        
        # Validate statistics data
        if 'statistics' in dashboard_data:
            stats = dashboard_data['statistics']
            if not isinstance(stats, dict):
                errors.append("Statistics must be a dictionary")
            else:
                expected_stats = ['total_transactions', 'fraud_rate', 'total_trade_value']
                missing_stats = [stat for stat in expected_stats if stat not in stats]
                if missing_stats:
                    warnings.append(f"Missing statistics: {missing_stats}")
        
        # Validate alerts data
        if 'alerts' in dashboard_data:
            alerts = dashboard_data['alerts']
            if not isinstance(alerts, list):
                errors.append("Alerts must be a list")
            elif len(alerts) > 100:
                warnings.append(f"Large number of alerts: {len(alerts)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'sections_present': len([s for s in expected_sections if s in dashboard_data]),
            'total_sections_expected': len(expected_sections),
            'transaction_count': len(dashboard_data.get('transactions', [])),
            'alert_count': len(dashboard_data.get('alerts', []))
        }
        
    except Exception as e:
        errors.append(f"Dashboard data validation error: {str(e)}")
        return {'valid': False, 'errors': errors, 'warnings': warnings}


def validate_model_predictions(predictions: np.ndarray, expected_shape: tuple = None) -> Dict[str, Any]:
    """
    Validate ML model prediction outputs.
    
    Args:
        predictions: Model prediction array
        expected_shape: Expected shape of predictions (optional)
        
    Returns:
        Dict: Validation results for model predictions
    """
    errors = []
    warnings = []
    
    try:
        if predictions is None:
            errors.append("Predictions array is None")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        if not isinstance(predictions, np.ndarray):
            try:
                predictions = np.array(predictions)
            except Exception as e:
                errors.append(f"Cannot convert predictions to numpy array: {str(e)}")
                return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check array shape
        if expected_shape and predictions.shape != expected_shape:
            errors.append(f"Predictions shape {predictions.shape} does not match expected {expected_shape}")
        
        # Check for invalid values
        nan_count = np.isnan(predictions).sum()
        if nan_count > 0:
            warnings.append(f"Predictions contain {nan_count} NaN values")
        
        inf_count = np.isinf(predictions).sum()
        if inf_count > 0:
            warnings.append(f"Predictions contain {inf_count} infinite values")
        
        # Check prediction range for anomaly scores (typically -1 to 1)
        if len(predictions) > 0:
            min_pred, max_pred = np.nanmin(predictions), np.nanmax(predictions)
            if min_pred < -2 or max_pred > 2:
                warnings.append(f"Predictions outside typical range [-2, 2]: [{min_pred:.3f}, {max_pred:.3f}]")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'shape': predictions.shape,
            'nan_count': nan_count,
            'inf_count': inf_count,
            'min_value': np.nanmin(predictions) if len(predictions) > 0 else None,
            'max_value': np.nanmax(predictions) if len(predictions) > 0 else None
        }
        
    except Exception as e:
        errors.append(f"Model predictions validation error: {str(e)}")
        return {'valid': False, 'errors': errors, 'warnings': warnings}


class ErrorHandlers:
    """
    Comprehensive error handling utilities for TRINETRA AI system.
    
    This class provides common error handlers that can be used across different modules
    for consistent error handling, logging, user-friendly messages, retry logic,
    and graceful degradation strategies.
    
    Covers:
    1. API errors (Gemini API failures, network issues)
    2. Data validation errors (CSV loading, schema validation)
    3. Model errors (training failures, prediction errors)
    4. File system errors (model loading/saving, data file access)
    5. General application errors
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ErrorHandlers")
        self.retry_counts = {}
        self.error_counts = {}
    
    # 1. API Error Handlers
    
    def handle_gemini_api_error(self, error: Exception, context: str = "Gemini API call", 
                               retry_count: int = 0, max_retries: int = 3) -> Dict[str, Any]:
        """
        Handle Gemini API errors with retry logic and fallback explanations.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
            retry_count: Current retry attempt
            max_retries: Maximum number of retries
            
        Returns:
            Dict: Error handling result with fallback content
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # Log the error with context
        self.logger.error(f"Gemini API error in {context}: {error_type}: {error_message}")
        
        # Track error counts
        error_key = f"gemini_api_{error_type}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Handle specific Gemini error types
        if isinstance(error, GeminiQuotaExceededError):
            return {
                'success': False,
                'should_retry': False,
                'error_type': error_type,
                'error_message': "AI service quota exceeded for this session",
                'user_message': "AI explanation quota reached. Using rule-based analysis instead.",
                'fallback_content': self._generate_gemini_fallback('QuotaExceeded', context),
                'degraded_service': True,
                'quota_exceeded': True
            }
        
        elif isinstance(error, GeminiRateLimitError):
            # Rate limit errors should retry with longer delay
            should_retry = retry_count < max_retries
            delay = min(30 + (retry_count * 10), 120)  # 30-120 seconds for rate limits
            
            if should_retry:
                self.logger.info(f"Rate limit hit, retrying in {delay} seconds (attempt {retry_count + 1}/{max_retries})")
                return {
                    'success': False,
                    'should_retry': True,
                    'retry_delay': delay,
                    'retry_count': retry_count + 1,
                    'error_type': error_type,
                    'user_message': "AI service is busy, retrying..."
                }
        
        elif isinstance(error, GeminiTimeoutError):
            # Timeout errors should retry with shorter delay
            should_retry = retry_count < max_retries
            delay = min(5 + (retry_count * 2), 15)  # 5-15 seconds for timeouts
            
            if should_retry:
                self.logger.info(f"Timeout occurred, retrying in {delay} seconds (attempt {retry_count + 1}/{max_retries})")
                return {
                    'success': False,
                    'should_retry': True,
                    'retry_delay': delay,
                    'retry_count': retry_count + 1,
                    'error_type': error_type,
                    'user_message': "AI service timeout, retrying..."
                }
        
        elif isinstance(error, GeminiInitializationError):
            # Initialization errors should not retry
            return {
                'success': False,
                'should_retry': False,
                'error_type': error_type,
                'error_message': "AI service configuration error",
                'user_message': "AI explanation service is not properly configured",
                'fallback_content': self._generate_gemini_fallback('InitializationError', context),
                'degraded_service': True,
                'configuration_error': True
            }
        
        # Determine if retry is appropriate for generic errors
        retryable_errors = [
            "TimeoutError", "ConnectionError", "HTTPException", 
            "ServiceUnavailable", "TooManyRequests", "InternalServerError"
        ]
        
        should_retry = (
            retry_count < max_retries and 
            any(retryable in error_type for retryable in retryable_errors)
        )
        
        if should_retry:
            # Calculate exponential backoff delay
            delay = min(2 ** retry_count, 30)  # Max 30 seconds
            self.logger.info(f"Retrying Gemini API call in {delay} seconds (attempt {retry_count + 1}/{max_retries})")
            
            return {
                'success': False,
                'should_retry': True,
                'retry_delay': delay,
                'retry_count': retry_count + 1,
                'error_type': error_type,
                'error_message': error_message,
                'fallback_content': None
            }
        
        # Generate fallback explanation based on error type
        fallback_content = self._generate_gemini_fallback(error_type, context)
        
        self.logger.warning(f"Using fallback content for {context} after {retry_count} retries")
        
        return {
            'success': False,
            'should_retry': False,
            'retry_count': retry_count,
            'error_type': error_type,
            'error_message': "AI explanation service temporarily unavailable",
            'user_message': "Using rule-based analysis instead of AI explanation",
            'fallback_content': fallback_content,
            'degraded_service': True
        }
    
    def handle_network_error(self, error: Exception, endpoint: str = "unknown", 
                           retry_count: int = 0, max_retries: int = 2) -> Dict[str, Any]:
        """
        Handle network-related errors with appropriate retry logic.
        
        Args:
            error: Network exception
            endpoint: API endpoint or service name
            retry_count: Current retry attempt
            max_retries: Maximum retries for network errors
            
        Returns:
            Dict: Error handling result
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        self.logger.error(f"Network error for {endpoint}: {error_type}: {error_message}")
        
        # Track network error counts
        network_key = f"network_{endpoint}"
        self.error_counts[network_key] = self.error_counts.get(network_key, 0) + 1
        
        # Determine retry strategy
        should_retry = retry_count < max_retries
        
        if should_retry:
            delay = 2 ** retry_count  # Exponential backoff
            self.logger.info(f"Retrying network request to {endpoint} in {delay} seconds")
            
            return {
                'success': False,
                'should_retry': True,
                'retry_delay': delay,
                'retry_count': retry_count + 1,
                'error_type': error_type,
                'user_message': f"Connection issue with {endpoint}, retrying..."
            }
        
        return {
            'success': False,
            'should_retry': False,
            'error_type': error_type,
            'user_message': f"Unable to connect to {endpoint}. Please check your internet connection.",
            'technical_message': error_message,
            'suggested_action': "Try again later or contact support if the issue persists"
        }
    
    # 2. Data Validation Error Handlers
    
    def handle_csv_loading_error(self, error: Exception, file_path: str) -> Dict[str, Any]:
        """
        Handle CSV file loading errors with detailed diagnostics.
        
        Args:
            error: Exception from CSV loading
            file_path: Path to CSV file
            
        Returns:
            Dict: Error handling result with diagnostics
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        self.logger.error(f"CSV loading error for {file_path}: {error_type}: {error_message}")
        
        # Handle specific data loader error types
        if isinstance(error, DataLoaderError):
            if isinstance(error, SchemaValidationError):
                return {
                    'success': False,
                    'error_type': error_type,
                    'file_path': file_path,
                    'user_message': f"Data file schema validation failed: {file_path}",
                    'technical_message': error_message,
                    'error_category': 'schema_validation',
                    'suggested_actions': [
                        "Check that all required columns are present",
                        "Verify column names match expected schema",
                        "Ensure data types are correct",
                        "Review the data file format"
                    ]
                }
            
            elif isinstance(error, DataQualityError):
                return {
                    'success': False,
                    'error_type': error_type,
                    'file_path': file_path,
                    'user_message': f"Data quality issues detected in: {file_path}",
                    'technical_message': error_message,
                    'error_category': 'data_quality',
                    'suggested_actions': [
                        "Review data for missing values",
                        "Check for data inconsistencies",
                        "Validate data ranges and formats",
                        "Consider data cleaning procedures"
                    ]
                }
            
            else:
                # Generic DataLoaderError
                return {
                    'success': False,
                    'error_type': error_type,
                    'file_path': file_path,
                    'user_message': f"Data loading failed: {file_path}",
                    'technical_message': error_message,
                    'error_category': 'data_loading',
                    'suggested_actions': [
                        "Check file format and encoding",
                        "Verify file permissions",
                        "Ensure file is not corrupted",
                        "Review file path and location"
                    ]
                }
        
        # Diagnose specific CSV issues for non-custom errors
        diagnostics = self._diagnose_csv_error(error, file_path)
        
        # Generate user-friendly message
        user_message = self._generate_csv_error_message(error_type, file_path, diagnostics)
        
        return {
            'success': False,
            'error_type': error_type,
            'file_path': file_path,
            'user_message': user_message,
            'technical_message': error_message,
            'diagnostics': diagnostics,
            'suggested_actions': self._get_csv_error_suggestions(error_type, diagnostics)
        }
    
    def handle_schema_validation_error(self, validation_result: Dict[str, Any], 
                                     context: str = "data validation") -> Dict[str, Any]:
        """
        Handle schema validation errors with detailed reporting.
        
        Args:
            validation_result: Result from schema validation
            context: Context where validation occurred
            
        Returns:
            Dict: Processed error handling result
        """
        errors = validation_result.get('errors', [])
        warnings = validation_result.get('warnings', [])
        
        self.logger.error(f"Schema validation failed in {context}: {len(errors)} errors, {len(warnings)} warnings")
        
        # Categorize errors by severity
        critical_errors = []
        recoverable_errors = []
        
        for error in errors:
            if any(keyword in error.lower() for keyword in ['missing', 'required', 'empty']):
                critical_errors.append(error)
            else:
                recoverable_errors.append(error)
        
        # Generate user-friendly summary
        if critical_errors:
            user_message = f"Critical data issues found: {len(critical_errors)} missing required fields"
            can_continue = False
        elif recoverable_errors:
            user_message = f"Data quality issues detected: {len(recoverable_errors)} validation errors"
            can_continue = True
        else:
            user_message = f"Data validation completed with {len(warnings)} warnings"
            can_continue = True
        
        return {
            'success': len(critical_errors) == 0,
            'can_continue': can_continue,
            'user_message': user_message,
            'critical_errors': critical_errors,
            'recoverable_errors': recoverable_errors,
            'warnings': warnings,
            'error_summary': validation_result.get('summary', ''),
            'suggested_actions': self._get_validation_error_suggestions(critical_errors, recoverable_errors)
        }
    
    # 3. Model Error Handlers
    
    def handle_model_training_error(self, error: Exception, model_type: str = "IsolationForest",
                                  feature_count: int = 0) -> Dict[str, Any]:
        """
        Handle ML model training errors with diagnostics.
        
        Args:
            error: Training exception
            model_type: Type of model being trained
            feature_count: Number of features used
            
        Returns:
            Dict: Error handling result with diagnostics
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        self.logger.error(f"Model training error ({model_type}): {error_type}: {error_message}")
        
        # Handle specific model training error types
        if isinstance(error, ModelTrainingError):
            return {
                'success': False,
                'error_type': error_type,
                'model_type': model_type,
                'feature_count': feature_count,
                'user_message': f"Model training failed: {error_message}",
                'technical_message': error_message,
                'error_category': 'model_training',
                'recovery_actions': [
                    "Check training data quality",
                    "Verify feature engineering output",
                    "Review model parameters",
                    "Ensure sufficient training data"
                ],
                'can_retry': True
            }
        
        elif isinstance(error, FeatureEngineeringError):
            return {
                'success': False,
                'error_type': error_type,
                'model_type': model_type,
                'feature_count': feature_count,
                'user_message': "Feature engineering failed during model training",
                'technical_message': error_message,
                'error_category': 'feature_engineering',
                'recovery_actions': [
                    "Check input data for feature engineering",
                    "Verify feature calculation logic",
                    "Handle missing or invalid values",
                    "Review feature engineering pipeline"
                ],
                'can_retry': True
            }
        
        # Diagnose common training issues for generic errors
        diagnostics = self._diagnose_training_error(error, feature_count)
        
        # Generate recovery suggestions
        recovery_actions = self._get_training_error_recovery(error_type, diagnostics)
        
        return {
            'success': False,
            'error_type': error_type,
            'model_type': model_type,
            'feature_count': feature_count,
            'user_message': f"Model training failed: {diagnostics.get('likely_cause', 'Unknown issue')}",
            'technical_message': error_message,
            'diagnostics': diagnostics,
            'recovery_actions': recovery_actions,
            'can_retry': diagnostics.get('retryable', False)
        }
    
    def handle_model_prediction_error(self, error: Exception, input_shape: tuple = None,
                                    model_type: str = "IsolationForest") -> Dict[str, Any]:
        """
        Handle ML model prediction errors.
        
        Args:
            error: Prediction exception
            input_shape: Shape of input data
            model_type: Type of model
            
        Returns:
            Dict: Error handling result
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        self.logger.error(f"Model prediction error ({model_type}): {error_type}: {error_message}")
        
        # Handle specific model prediction error types
        if isinstance(error, ModelPredictionError):
            return {
                'success': False,
                'error_type': error_type,
                'model_type': model_type,
                'user_message': "Model prediction failed, using default risk assessment",
                'technical_message': error_message,
                'error_category': 'model_prediction',
                'fallback_scores': self._generate_fallback_scores(input_shape),
                'degraded_service': True,
                'recovery_actions': [
                    "Check input data format",
                    "Verify model is properly loaded",
                    "Validate feature engineering output",
                    "Consider retraining the model"
                ]
            }
        
        # Diagnose prediction issues for generic errors
        diagnostics = {
            'input_shape': input_shape,
            'error_type': error_type,
            'likely_cause': self._diagnose_prediction_error(error, input_shape)
        }
        
        # Provide fallback scores if possible
        fallback_scores = self._generate_fallback_scores(input_shape)
        
        return {
            'success': False,
            'error_type': error_type,
            'model_type': model_type,
            'user_message': "Model prediction failed, using default risk assessment",
            'technical_message': error_message,
            'diagnostics': diagnostics,
            'fallback_scores': fallback_scores,
            'degraded_service': True
        }
    
    def handle_model_loading_error(self, error: Exception, model_path: str) -> Dict[str, Any]:
        """
        Handle model loading/saving errors.
        
        Args:
            error: Loading exception
            model_path: Path to model file
            
        Returns:
            Dict: Error handling result
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        self.logger.error(f"Model loading error from {model_path}: {error_type}: {error_message}")
        
        # Check file system issues
        file_diagnostics = self._diagnose_file_error(model_path)
        
        # Determine if we can retrain
        can_retrain = file_diagnostics.get('directory_writable', False)
        
        return {
            'success': False,
            'error_type': error_type,
            'model_path': model_path,
            'user_message': "Trained model not available, will retrain automatically" if can_retrain else "Model loading failed",
            'technical_message': error_message,
            'file_diagnostics': file_diagnostics,
            'can_retrain': can_retrain,
            'suggested_actions': ["Retrain model", "Check file permissions", "Verify model file integrity"]
        }
    
    # 4. File System Error Handlers
    
    def handle_file_system_error(self, error: Exception, file_path: str, 
                                operation: str = "access") -> Dict[str, Any]:
        """
        Handle file system errors (permissions, not found, etc.).
        
        Args:
            error: File system exception
            file_path: Path that caused the error
            operation: Operation being performed (read, write, delete, etc.)
            
        Returns:
            Dict: Error handling result
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        self.logger.error(f"File system error during {operation} on {file_path}: {error_type}: {error_message}")
        
        # Diagnose file system issues
        file_diagnostics = self._diagnose_file_error(file_path)
        
        # Generate user-friendly message
        user_message = self._generate_file_error_message(error_type, file_path, operation)
        
        return {
            'success': False,
            'error_type': error_type,
            'file_path': file_path,
            'operation': operation,
            'user_message': user_message,
            'technical_message': error_message,
            'file_diagnostics': file_diagnostics,
            'suggested_actions': self._get_file_error_suggestions(error_type, file_diagnostics, operation)
        }
    
    # 5. General Application Error Handlers
    
    def handle_alert_system_error(self, error: Exception, alert_context: str = "alert processing") -> Dict[str, Any]:
        """
        Handle alert system errors with appropriate fallback behavior.
        
        Args:
            error: Alert system exception
            alert_context: Context where alert error occurred
            
        Returns:
            Dict: Error handling result for alert system
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        self.logger.error(f"Alert system error in {alert_context}: {error_type}: {error_message}")
        
        # Handle specific alert system error types
        if isinstance(error, AlertSystemError):
            return {
                'success': False,
                'error_type': error_type,
                'context': alert_context,
                'user_message': "Alert system temporarily unavailable",
                'technical_message': error_message,
                'error_category': 'alert_system',
                'degraded_service': True,
                'fallback_behavior': 'continue_without_alerts',
                'recovery_actions': [
                    "Check alert configuration",
                    "Verify alert thresholds",
                    "Review alert processing logic",
                    "Check system resources"
                ]
            }
        
        # Handle generic alert errors
        return {
            'success': False,
            'error_type': error_type,
            'context': alert_context,
            'user_message': f"Alert processing issue in {alert_context}",
            'technical_message': error_message,
            'degraded_service': True,
            'fallback_behavior': 'continue_without_alerts'
        }
    
    def handle_feature_engineering_error(self, error: Exception, feature_context: str = "feature calculation") -> Dict[str, Any]:
        """
        Handle feature engineering errors with detailed diagnostics.
        
        Args:
            error: Feature engineering exception
            feature_context: Context where feature error occurred
            
        Returns:
            Dict: Error handling result for feature engineering
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        self.logger.error(f"Feature engineering error in {feature_context}: {error_type}: {error_message}")
        
        # Handle specific feature engineering error types
        if isinstance(error, FeatureEngineeringError):
            return {
                'success': False,
                'error_type': error_type,
                'context': feature_context,
                'user_message': f"Feature calculation failed: {feature_context}",
                'technical_message': error_message,
                'error_category': 'feature_engineering',
                'recovery_actions': [
                    "Check input data quality",
                    "Verify feature calculation logic",
                    "Handle division by zero cases",
                    "Review data preprocessing steps"
                ],
                'can_retry': True
            }
        
        # Handle generic feature engineering errors
        return {
            'success': False,
            'error_type': error_type,
            'context': feature_context,
            'user_message': f"Feature engineering failed in {feature_context}",
            'technical_message': error_message,
            'can_retry': True
        }
    
    def handle_general_error(self, error: Exception, context: str = "application",
                           user_facing: bool = True) -> Dict[str, Any]:
        """
        Handle general application errors with appropriate logging and user messages.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
            user_facing: Whether this error should be shown to users
            
        Returns:
            Dict: Error handling result
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # Log with appropriate level based on error type
        if error_type in ['ValueError', 'TypeError', 'KeyError']:
            self.logger.warning(f"Application error in {context}: {error_type}: {error_message}")
        else:
            self.logger.error(f"Unexpected error in {context}: {error_type}: {error_message}")
        
        # Generate user-friendly message
        if user_facing:
            user_message = self._generate_user_friendly_message(error_type, context)
        else:
            user_message = f"Internal error in {context}"
        
        return {
            'success': False,
            'error_type': error_type,
            'context': context,
            'user_message': user_message,
            'technical_message': error_message,
            'timestamp': time.time(),
            'should_report': error_type not in ['ValueError', 'TypeError', 'KeyError']
        }
    
    # Helper methods for error diagnosis and recovery
    
    def _generate_gemini_fallback(self, error_type: str, context: str) -> str:
        """Generate fallback content when Gemini API fails."""
        fallback_templates = {
            'TimeoutError': "Analysis timed out. This transaction shows suspicious patterns based on rule-based analysis.",
            'ConnectionError': "Unable to connect to AI service. Using automated risk assessment instead.",
            'QuotaExceeded': "AI service quota exceeded. This transaction requires manual review.",
            'GeminiQuotaExceededError': "AI explanation quota reached for this session. Using rule-based analysis.",
            'GeminiRateLimitError': "AI service is currently busy. Using automated fraud detection instead.",
            'GeminiTimeoutError': "AI analysis timed out. This transaction shows risk indicators based on automated analysis.",
            'GeminiInitializationError': "AI service is not available. Using rule-based fraud detection.",
            'GeminiAPIError': "AI explanation service encountered an error. Using automated analysis instead.",
            'default': "AI explanation unavailable. Please review transaction details manually."
        }
        
        return fallback_templates.get(error_type, fallback_templates['default'])
    
    def _diagnose_csv_error(self, error: Exception, file_path: str) -> Dict[str, Any]:
        """Diagnose CSV loading issues."""
        diagnostics = {
            'file_exists': os.path.exists(file_path),
            'file_readable': False,
            'file_size': 0,
            'likely_encoding_issue': False,
            'likely_format_issue': False
        }
        
        if diagnostics['file_exists']:
            try:
                diagnostics['file_readable'] = os.access(file_path, os.R_OK)
                diagnostics['file_size'] = os.path.getsize(file_path)
            except:
                pass
            
            # Check for common CSV issues
            error_message = str(error).lower()
            if 'encoding' in error_message or 'codec' in error_message:
                diagnostics['likely_encoding_issue'] = True
            if 'delimiter' in error_message or 'separator' in error_message:
                diagnostics['likely_format_issue'] = True
        
        return diagnostics
    
    def _generate_csv_error_message(self, error_type: str, file_path: str, 
                                  diagnostics: Dict[str, Any]) -> str:
        """Generate user-friendly CSV error message."""
        if not diagnostics['file_exists']:
            return f"Data file not found: {file_path}"
        elif not diagnostics['file_readable']:
            return f"Cannot read data file: {file_path} (check permissions)"
        elif diagnostics['file_size'] == 0:
            return f"Data file is empty: {file_path}"
        elif diagnostics['likely_encoding_issue']:
            return f"Data file encoding issue: {file_path} (try UTF-8 encoding)"
        elif diagnostics['likely_format_issue']:
            return f"Data file format issue: {file_path} (check CSV format)"
        else:
            return f"Unable to load data file: {file_path}"
    
    def _get_csv_error_suggestions(self, error_type: str, diagnostics: Dict[str, Any]) -> List[str]:
        """Get suggestions for CSV error recovery."""
        suggestions = []
        
        if not diagnostics['file_exists']:
            suggestions.extend([
                "Check if the file path is correct",
                "Ensure the data file is in the expected location",
                "Verify the filename and extension"
            ])
        elif diagnostics['likely_encoding_issue']:
            suggestions.extend([
                "Try saving the CSV file with UTF-8 encoding",
                "Check for special characters in the data",
                "Use a text editor to verify file encoding"
            ])
        elif diagnostics['likely_format_issue']:
            suggestions.extend([
                "Verify CSV uses comma separators",
                "Check for proper header row",
                "Ensure no extra commas or quotes in data"
            ])
        else:
            suggestions.extend([
                "Check file permissions",
                "Verify file is not corrupted",
                "Try opening file in a spreadsheet application"
            ])
        
        return suggestions
    
    def _get_validation_error_suggestions(self, critical_errors: List[str], 
                                        recoverable_errors: List[str]) -> List[str]:
        """Get suggestions for validation error recovery."""
        suggestions = []
        
        if critical_errors:
            suggestions.extend([
                "Check that all required columns are present in the data",
                "Verify column names match expected schema",
                "Ensure no required fields are empty"
            ])
        
        if recoverable_errors:
            suggestions.extend([
                "Review data quality warnings",
                "Consider data cleaning before processing",
                "Check for outliers or unusual values"
            ])
        
        return suggestions
    
    def _diagnose_training_error(self, error: Exception, feature_count: int) -> Dict[str, Any]:
        """Diagnose model training issues."""
        error_message = str(error).lower()
        
        diagnostics = {
            'feature_count': feature_count,
            'likely_cause': 'Unknown',
            'retryable': False
        }
        
        if 'memory' in error_message or 'ram' in error_message:
            diagnostics['likely_cause'] = 'Insufficient memory'
            diagnostics['retryable'] = True
        elif 'nan' in error_message or 'infinite' in error_message:
            diagnostics['likely_cause'] = 'Invalid data values (NaN or infinite)'
            diagnostics['retryable'] = True
        elif feature_count == 0:
            diagnostics['likely_cause'] = 'No features available for training'
            diagnostics['retryable'] = False
        elif 'shape' in error_message:
            diagnostics['likely_cause'] = 'Data shape mismatch'
            diagnostics['retryable'] = True
        else:
            diagnostics['likely_cause'] = 'Model configuration issue'
            diagnostics['retryable'] = True
        
        return diagnostics
    
    def _get_training_error_recovery(self, error_type: str, diagnostics: Dict[str, Any]) -> List[str]:
        """Get recovery actions for training errors."""
        actions = []
        
        likely_cause = diagnostics.get('likely_cause', '')
        
        if 'memory' in likely_cause:
            actions.extend([
                "Reduce dataset size",
                "Use data sampling",
                "Increase available memory"
            ])
        elif 'invalid data' in likely_cause:
            actions.extend([
                "Clean data to remove NaN values",
                "Handle infinite values",
                "Validate feature engineering output"
            ])
        elif 'no features' in likely_cause:
            actions.extend([
                "Run feature engineering first",
                "Check feature column names",
                "Verify data preprocessing"
            ])
        else:
            actions.extend([
                "Check model parameters",
                "Validate input data format",
                "Review training configuration"
            ])
        
        return actions
    
    def _diagnose_prediction_error(self, error: Exception, input_shape: tuple) -> str:
        """Diagnose model prediction issues."""
        error_message = str(error).lower()
        
        if 'shape' in error_message:
            return f"Input shape mismatch (got {input_shape})"
        elif 'nan' in error_message:
            return "Input contains NaN values"
        elif 'infinite' in error_message:
            return "Input contains infinite values"
        elif input_shape and len(input_shape) != 2:
            return f"Expected 2D input, got {len(input_shape)}D"
        elif input_shape and input_shape[1] != 6:
            return f"Expected 6 features, got {input_shape[1]}"
        else:
            return "Model prediction failed"
    
    def _generate_fallback_scores(self, input_shape: tuple) -> Optional[np.ndarray]:
        """Generate fallback risk scores when model prediction fails."""
        if input_shape and len(input_shape) == 2:
            # Generate neutral risk scores (0.0 = suspicious category)
            return np.zeros(input_shape[0])
        return None
    
    def _diagnose_file_error(self, file_path: str) -> Dict[str, Any]:
        """Diagnose file system issues."""
        diagnostics = {
            'file_exists': False,
            'file_readable': False,
            'file_writable': False,
            'directory_exists': False,
            'directory_writable': False,
            'file_size': 0
        }
        
        try:
            diagnostics['file_exists'] = os.path.exists(file_path)
            
            if diagnostics['file_exists']:
                diagnostics['file_readable'] = os.access(file_path, os.R_OK)
                diagnostics['file_writable'] = os.access(file_path, os.W_OK)
                diagnostics['file_size'] = os.path.getsize(file_path)
            
            # Check directory
            directory = os.path.dirname(file_path)
            if directory:
                diagnostics['directory_exists'] = os.path.exists(directory)
                if diagnostics['directory_exists']:
                    diagnostics['directory_writable'] = os.access(directory, os.W_OK)
        except Exception as e:
            self.logger.debug(f"Error diagnosing file {file_path}: {e}")
        
        return diagnostics
    
    def _generate_file_error_message(self, error_type: str, file_path: str, operation: str) -> str:
        """Generate user-friendly file error message."""
        if error_type == 'FileNotFoundError':
            return f"File not found: {file_path}"
        elif error_type == 'PermissionError':
            return f"Permission denied for {operation} operation on: {file_path}"
        elif error_type == 'IsADirectoryError':
            return f"Expected file but found directory: {file_path}"
        elif error_type == 'OSError':
            return f"System error accessing file: {file_path}"
        else:
            return f"File {operation} failed: {file_path}"
    
    def _get_file_error_suggestions(self, error_type: str, diagnostics: Dict[str, Any], 
                                  operation: str) -> List[str]:
        """Get suggestions for file error recovery."""
        suggestions = []
        
        if error_type == 'FileNotFoundError':
            suggestions.extend([
                "Check if the file path is correct",
                "Verify the file exists in the expected location",
                "Create the file if it should exist"
            ])
        elif error_type == 'PermissionError':
            suggestions.extend([
                "Check file permissions",
                "Run with appropriate user privileges",
                "Ensure file is not locked by another process"
            ])
        elif not diagnostics.get('directory_exists', True):
            suggestions.extend([
                "Create the required directory",
                "Check directory path is correct",
                "Verify parent directories exist"
            ])
        else:
            suggestions.extend([
                "Check disk space availability",
                "Verify file system integrity",
                "Try the operation again"
            ])
        
        return suggestions
    
    def _generate_user_friendly_message(self, error_type: str, context: str) -> str:
        """Generate user-friendly error messages."""
        friendly_messages = {
            'ValueError': f"Invalid data encountered in {context}",
            'TypeError': f"Data type issue in {context}",
            'KeyError': f"Missing required information in {context}",
            'ConnectionError': f"Connection problem in {context}",
            'TimeoutError': f"Operation timed out in {context}",
            'MemoryError': f"Insufficient memory for {context}",
            'default': f"An error occurred in {context}"
        }
        
        return friendly_messages.get(error_type, friendly_messages['default'])
    
    # Error reporting and statistics
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_breakdown': dict(self.error_counts),
            'most_common_errors': sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }
    
    def reset_error_counts(self):
        """Reset error tracking counters."""
        self.error_counts.clear()
        self.retry_counts.clear()
        self.logger.info("Error tracking counters reset")


# Global error handler instance
error_handlers = ErrorHandlers()

# Convenience functions for common error handling patterns

def handle_with_fallback(func, fallback_value=None, context: str = "operation", 
                        log_errors: bool = True):
    """
    Decorator/wrapper for handling errors with fallback values.
    
    Args:
        func: Function to execute
        fallback_value: Value to return on error
        context: Context description for logging
        log_errors: Whether to log errors
        
    Returns:
        Function result or fallback value
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            error_handlers.logger.error(f"Error in {context}: {type(e).__name__}: {str(e)}")
        return fallback_value

def handle_data_loader_error(error: Exception, file_path: str) -> Dict[str, Any]:
    """
    Convenience function for handling data loader errors.
    
    Args:
        error: Data loading exception
        file_path: Path to data file
        
    Returns:
        Dict: Error handling result
    """
    return error_handlers.handle_csv_loading_error(error, file_path)

def handle_gemini_error(error: Exception, context: str = "AI explanation", 
                       retry_count: int = 0) -> Dict[str, Any]:
    """
    Convenience function for handling Gemini API errors.
    
    Args:
        error: Gemini API exception
        context: Context description
        retry_count: Current retry attempt
        
    Returns:
        Dict: Error handling result
    """
    return error_handlers.handle_gemini_api_error(error, context, retry_count)

def handle_model_error(error: Exception, model_type: str = "IsolationForest", 
                      operation: str = "training") -> Dict[str, Any]:
    """
    Convenience function for handling model errors.
    
    Args:
        error: Model exception
        model_type: Type of model
        operation: Operation being performed (training, prediction, loading)
        
    Returns:
        Dict: Error handling result
    """
    if operation == "training":
        return error_handlers.handle_model_training_error(error, model_type)
    elif operation == "prediction":
        return error_handlers.handle_model_prediction_error(error, model_type=model_type)
    elif operation == "loading":
        return error_handlers.handle_model_loading_error(error, f"models/{model_type.lower()}.pkl")
    else:
        return error_handlers.handle_general_error(error, f"model {operation}")

def handle_feature_error(error: Exception, feature_name: str = "unknown") -> Dict[str, Any]:
    """
    Convenience function for handling feature engineering errors.
    
    Args:
        error: Feature engineering exception
        feature_name: Name of feature being calculated
        
    Returns:
        Dict: Error handling result
    """
    return error_handlers.handle_feature_engineering_error(error, f"calculating {feature_name}")

def handle_alert_error(error: Exception, alert_type: str = "unknown") -> Dict[str, Any]:
    """
    Convenience function for handling alert system errors.
    
    Args:
        error: Alert system exception
        alert_type: Type of alert being processed
        
    Returns:
        Dict: Error handling result
    """
    return error_handlers.handle_alert_system_error(error, f"processing {alert_type} alert")

def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0, 
                    backoff_factor: float = 2.0, context: str = "operation"):
    """
    Retry function execution on failure with exponential backoff.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff_factor: Multiplier for delay on each retry
        context: Context description for logging
        
    Returns:
        Function result or raises last exception
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                error_handlers.logger.warning(
                    f"Attempt {attempt + 1} failed in {context}: {type(e).__name__}: {str(e)}. "
                    f"Retrying in {current_delay} seconds..."
                )
                time.sleep(current_delay)
                current_delay *= backoff_factor
            else:
                error_handlers.logger.error(
                    f"All {max_retries + 1} attempts failed in {context}: {type(e).__name__}: {str(e)}"
                )
    
    raise last_exception

def safe_execute(func, default_return=None, error_message: str = None, 
                context: str = "operation"):
    """
    Safely execute a function with comprehensive error handling.
    
    Args:
        func: Function to execute
        default_return: Default value to return on error
        error_message: Custom error message for logging
        context: Context description
        
    Returns:
        Tuple of (success: bool, result: Any, error_info: Dict)
    """
    try:
        result = func()
        return True, result, None
    except Exception as e:
        error_info = error_handlers.handle_general_error(e, context)
        
        if error_message:
            error_handlers.logger.error(f"{error_message}: {str(e)}")
        
        return False, default_return, error_info


def validate_feature_engineering_output(df: pd.DataFrame, original_df: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Validate feature engineering output to ensure all required features are present and valid.
    
    Args:
        df: DataFrame with engineered features
        original_df: Original DataFrame before feature engineering (optional)
        
    Returns:
        Dict: Validation results for feature engineering output
    """
    errors = []
    warnings = []
    
    try:
        if df is None or df.empty:
            errors.append("Feature engineering output DataFrame is None or empty")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check for required engineered features
        required_features = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        
        missing_features = [f for f in required_features if f not in df.columns]
        if missing_features:
            errors.append(f"Missing required engineered features: {missing_features}")
        
        # Validate each feature
        for feature in required_features:
            if feature in df.columns:
                feature_data = df[feature].dropna()
                
                if len(feature_data) == 0:
                    warnings.append(f"Feature '{feature}' has no valid values")
                    continue
                
                # Check for negative values where they shouldn't exist
                if feature in ['price_anomaly_score', 'port_congestion_score', 'volume_spike_score']:
                    negative_count = (feature_data < 0).sum()
                    if negative_count > 0:
                        warnings.append(f"Feature '{feature}' has {negative_count} negative values")
                
                # Check for extreme values
                if np.isinf(feature_data).any():
                    inf_count = np.isinf(feature_data).sum()
                    warnings.append(f"Feature '{feature}' has {inf_count} infinite values")
        
        # Compare with original DataFrame if provided
        if original_df is not None:
            if len(df) != len(original_df):
                warnings.append(f"Row count changed during feature engineering: {len(original_df)} -> {len(df)}")
            
            # Check if original columns are preserved
            original_cols = set(original_df.columns)
            current_cols = set(df.columns)
            missing_original = original_cols - current_cols
            if missing_original:
                warnings.append(f"Original columns lost during feature engineering: {missing_original}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'features_present': len([f for f in required_features if f in df.columns]),
            'total_features_expected': len(required_features),
            'total_columns': len(df.columns),
            'row_count': len(df)
        }
        
    except Exception as e:
        errors.append(f"Feature engineering validation error: {str(e)}")
        return {'valid': False, 'errors': errors, 'warnings': warnings}


def validate_alert_data(alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate individual alert data structure and content.
    
    Args:
        alert: Alert dictionary to validate
        
    Returns:
        Dict: Validation results for alert data
    """
    errors = []
    warnings = []
    
    try:
        if not isinstance(alert, dict):
            errors.append("Alert must be a dictionary")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Required alert fields
        required_fields = ['alert_type', 'transaction_id', 'severity', 'message']
        for field in required_fields:
            if field not in alert:
                errors.append(f"Missing required alert field: {field}")
            elif not alert[field] or str(alert[field]).strip() == "":
                errors.append(f"Alert field '{field}' is empty")
        
        # Validate alert type
        if 'alert_type' in alert:
            valid_alert_types = [
                'PRICE_ANOMALY', 'ROUTE_ANOMALY', 'HIGH_RISK_COMPANY', 
                'PORT_CONGESTION', 'FRAUD_DETECTED'
            ]
            if alert['alert_type'] not in valid_alert_types:
                warnings.append(f"Unknown alert type: {alert['alert_type']}")
        
        # Validate severity
        if 'severity' in alert:
            valid_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            if alert['severity'] not in valid_severities:
                warnings.append(f"Invalid severity level: {alert['severity']}")
        
        # Validate transaction_id format
        if 'transaction_id' in alert:
            tx_id = str(alert['transaction_id'])
            if len(tx_id) > 50:
                warnings.append(f"Transaction ID is unusually long: {len(tx_id)} characters")
        
        # Validate message length
        if 'message' in alert:
            message = str(alert['message'])
            if len(message) > 500:
                warnings.append(f"Alert message is very long: {len(message)} characters")
            elif len(message) < 10:
                warnings.append(f"Alert message is very short: {len(message)} characters")
        
        # Validate timestamp if present
        if 'timestamp' in alert:
            try:
                if isinstance(alert['timestamp'], str):
                    pd.to_datetime(alert['timestamp'])
            except (ValueError, TypeError):
                warnings.append(f"Invalid timestamp format: {alert['timestamp']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'required_fields_present': len([f for f in required_fields if f in alert and alert[f]]),
            'total_required_fields': len(required_fields)
        }
        
    except Exception as e:
        errors.append(f"Alert validation error: {str(e)}")
        return {'valid': False, 'errors': errors, 'warnings': warnings}


def validate_session_data(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate session data for API quota management and user sessions.
    
    Args:
        session_data: Session data dictionary to validate
        
    Returns:
        Dict: Validation results for session data
    """
    errors = []
    warnings = []
    
    try:
        if not isinstance(session_data, dict):
            errors.append("Session data must be a dictionary")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check for session ID
        if 'session_id' not in session_data:
            errors.append("Missing session_id")
        elif not isinstance(session_data['session_id'], str) or len(session_data['session_id']) == 0:
            errors.append("Session ID must be a non-empty string")
        
        # Validate quota information
        if 'quota_used' in session_data:
            try:
                quota_used = int(session_data['quota_used'])
                if quota_used < 0:
                    warnings.append("Quota used cannot be negative")
            except (ValueError, TypeError):
                errors.append("Quota used must be an integer")
        
        if 'quota_limit' in session_data:
            try:
                quota_limit = int(session_data['quota_limit'])
                if quota_limit <= 0:
                    warnings.append("Quota limit should be positive")
            except (ValueError, TypeError):
                errors.append("Quota limit must be an integer")
        
        # Check quota consistency
        if 'quota_used' in session_data and 'quota_limit' in session_data:
            try:
                quota_used = int(session_data['quota_used'])
                quota_limit = int(session_data['quota_limit'])
                if quota_used > quota_limit:
                    warnings.append(f"Quota used ({quota_used}) exceeds limit ({quota_limit})")
            except (ValueError, TypeError):
                pass  # Already handled above
        
        # Validate timestamps
        timestamp_fields = ['created_at', 'last_activity', 'expires_at']
        for field in timestamp_fields:
            if field in session_data:
                try:
                    if isinstance(session_data[field], str):
                        pd.to_datetime(session_data[field])
                except (ValueError, TypeError):
                    warnings.append(f"Invalid timestamp format for {field}: {session_data[field]}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'has_session_id': 'session_id' in session_data,
            'has_quota_info': 'quota_used' in session_data and 'quota_limit' in session_data
        }
        
    except Exception as e:
        errors.append(f"Session data validation error: {str(e)}")
        return {'valid': False, 'errors': errors, 'warnings': warnings}


def validate_system_configuration(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Comprehensive system configuration validation for TRINETRA AI.
    
    Args:
        config: Optional configuration dictionary. If None, validates current system state.
        
    Returns:
        Dict: Comprehensive validation results for entire system configuration
    """
    errors = []
    warnings = []
    validation_results = []
    
    try:
        # If no config provided, create a basic config from environment/defaults
        if config is None:
            config = {
                'gemini_api_key': os.getenv('GEMINI_API_KEY', ''),
                'risk_thresholds': ConfigurationHelpers.get_risk_thresholds(),
                'alert_thresholds': ConfigurationHelpers.get_alert_thresholds(),
                'display_settings': ConfigurationHelpers.get_display_settings()
            }
        
        # Validate main configuration
        config_result = ValidationHelpers.validate_configuration(config)
        validation_results.append(('Configuration', config_result))
        
        # Validate risk thresholds specifically
        if 'risk_thresholds' in config:
            risk_result = validate_alert_thresholds(config['risk_thresholds'])
            validation_results.append(('Risk Thresholds', risk_result))
        
        # Validate alert thresholds specifically
        if 'alert_thresholds' in config:
            alert_result = validate_alert_thresholds(config['alert_thresholds'])
            validation_results.append(('Alert Thresholds', alert_result))
        
        # Check file system requirements
        required_dirs = ['data', 'models', 'logs', 'utils', 'backend']
        missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
        if missing_dirs:
            warnings.append(f"Missing required directories: {missing_dirs}")
        
        # Check for required files
        required_files = [
            'data/trinetra_trade_fraud_dataset_1000_rows_complex.csv',
            'utils/helpers.py',
            'backend/data_loader.py',
            'backend/model.py',
            'backend/fraud_detection.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            file_result = validate_file_path(file_path, must_exist=True)
            if not file_result['valid']:
                missing_files.append(file_path)
        
        if missing_files:
            warnings.append(f"Missing required files: {missing_files}")
        
        # Validate Python environment
        try:
            import pandas as pd
            import numpy as np
            import sklearn
            import fastapi
            import streamlit
            import plotly
        except ImportError as e:
            errors.append(f"Missing required Python package: {str(e)}")
        
        # Aggregate all validation results
        all_errors = []
        all_warnings = warnings.copy()
        
        for name, result in validation_results:
            if not result['valid']:
                all_errors.extend([f"{name}: {error}" for error in result['errors']])
            all_warnings.extend([f"{name}: {warning}" for warning in result['warnings']])
        
        # Calculate overall system health score
        total_checks = len(validation_results) + len(required_dirs) + len(required_files) + 1  # +1 for Python packages
        failed_checks = len([r for _, r in validation_results if not r['valid']]) + len(missing_dirs) + len(missing_files)
        if all_errors:
            failed_checks += 1  # Python packages failed
        
        health_score = ((total_checks - failed_checks) / total_checks) * 100
        
        return {
            'valid': len(all_errors) == 0,
            'errors': all_errors,
            'warnings': all_warnings,
            'health_score': health_score,
            'total_checks': total_checks,
            'passed_checks': total_checks - failed_checks,
            'failed_checks': failed_checks,
            'validation_details': {name: result for name, result in validation_results},
            'system_ready': len(all_errors) == 0 and health_score >= 80.0
        }
        
    except Exception as e:
        errors.append(f"System configuration validation error: {str(e)}")
        return {
            'valid': False,
            'errors': errors,
            'warnings': warnings,
            'health_score': 0.0,
            'system_ready': False
        }


# Export main classes and functions
__all__ = [
    # Core classes
    'DataFormatter',
    'ValidationHelpers', 
    'ConfigurationHelpers',
    'PerformanceTracker',
    'TimedOperation',
    'ErrorHandlers',
    
    # Custom error classes
    'DataLoaderError',
    'SchemaValidationError',
    'DataQualityError',
    'GeminiInitializationError',
    'GeminiAPIError',
    'GeminiRateLimitError',
    'GeminiTimeoutError',
    'GeminiQuotaExceededError',
    'ModelTrainingError',
    'ModelPredictionError',
    'FeatureEngineeringError',
    'AlertSystemError',
    
    # Logging functions
    'setup_logging',
    'log_system_startup',
    'log_system_shutdown',
    'log_error_with_context',
    'log_configuration_info',
    
    # Global instances
    'performance_tracker',
    'error_handlers',
    'logger',
    
    # Utility functions
    'format_large_number',
    'truncate_text',
    'safe_divide',
    'get_color_for_risk_category',
    'get_priority_color',
    
    # Validation functions
    'validate_file_path',
    'validate_dataframe_for_ml',
    'create_validation_report',
    'validate_risk_score_range',
    'validate_feature_engineering_output',
    'validate_alert_data',
    'validate_session_data',
    'validate_system_configuration',
    
    # Configuration functions
    'load_config_from_file',
    'merge_configs',
    'get_environment_info',
    'validate_environment_setup',
    'create_environment_report',
    'setup_configuration_logging',
    'get_system_config',
    'initialize_system_configuration',
    'update_runtime_config',
    'get_cached_system_config',
    'refresh_configuration_cache',
    'get_configuration_cache_stats',
    
    # Error handling convenience functions
    'handle_with_fallback',
    'handle_data_loader_error',
    'handle_gemini_error',
    'handle_model_error',
    'handle_feature_error',
    'handle_alert_error',
    'retry_on_failure',
    'safe_execute'
]