#!/usr/bin/env python3
"""
Test script for TRINETRA AI logging configuration.

This script tests the comprehensive logging system implemented in utils/helpers.py
to ensure it works correctly with file and console output, performance tracking,
and proper formatting.
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import (
    setup_logging, 
    log_system_startup, 
    log_system_shutdown,
    log_error_with_context,
    log_configuration_info,
    performance_tracker,
    TimedOperation,
    logger
)

def test_basic_logging():
    """Test basic logging functionality."""
    print("Testing basic logging functionality...")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

def test_performance_tracking():
    """Test performance tracking functionality."""
    print("Testing performance tracking...")
    
    # Test dataset load tracking
    performance_tracker.log_dataset_load(
        load_time=2.5,
        dataset_size=1000,
        file_path="data/test_dataset.csv"
    )
    
    # Test model training tracking
    performance_tracker.log_model_training(
        training_time=15.3,
        model_type="IsolationForest",
        feature_count=6
    )
    
    # Test API response tracking
    performance_tracker.log_api_response(
        endpoint="/transactions",
        response_time=0.25,
        status_code=200
    )
    
    # Test Gemini API tracking
    performance_tracker.log_gemini_call(
        success=True,
        response_time=3.2
    )
    
    performance_tracker.log_gemini_call(
        success=False,
        response_time=5.1,
        error_message="API quota exceeded"
    )
    
    # Test alert tracking
    performance_tracker.log_alert_triggered(
        alert_type="PRICE_ANOMALY",
        transaction_id="TXN001",
        alert_details={"price_deviation": 0.75, "threshold": 0.5}
    )

def test_error_logging():
    """Test error logging with context."""
    print("Testing error logging...")
    
    try:
        # Simulate an error
        result = 1 / 0
    except Exception as e:
        log_error_with_context(
            error=e,
            context="test_error_logging",
            additional_info={"operation": "division", "values": [1, 0]}
        )

def test_configuration_logging():
    """Test configuration logging."""
    print("Testing configuration logging...")
    
    test_config = {
        "model_type": "IsolationForest",
        "api_key": "secret_key_12345",
        "log_level": "INFO",
        "max_file_size": "10MB",
        "gemini_model": "gemini-pro"
    }
    
    log_configuration_info(test_config)

def test_timed_operation():
    """Test timed operation context manager."""
    print("Testing timed operation...")
    
    with TimedOperation("Loading test data"):
        time.sleep(1)  # Simulate work
    
    with TimedOperation("Processing transactions"):
        time.sleep(0.5)  # Simulate work
    
    # Test with error
    try:
        with TimedOperation("Operation that fails"):
            time.sleep(0.2)
            raise ValueError("Simulated error")
    except ValueError:
        pass  # Expected error

def test_log_file_creation():
    """Test that log files are created correctly."""
    print("Testing log file creation...")
    
    log_file = Path("logs/trinetra.log")
    
    if log_file.exists():
        print(f"✓ Log file created: {log_file.absolute()}")
        
        # Check file size
        file_size = log_file.stat().st_size
        print(f"✓ Log file size: {file_size} bytes")
        
        # Read last few lines
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                print(f"✓ Log file contains {len(lines)} lines")
                print("Last few log entries:")
                for line in lines[-3:]:
                    print(f"  {line.strip()}")
            else:
                print("⚠ Log file is empty")
    else:
        print(f"✗ Log file not found: {log_file.absolute()}")

def main():
    """Run all logging tests."""
    print("TRINETRA AI Logging Configuration Test")
    print("=" * 50)
    
    # Initialize logging system
    log_system_startup()
    
    try:
        # Run all tests
        test_basic_logging()
        print()
        
        test_performance_tracking()
        print()
        
        test_error_logging()
        print()
        
        test_configuration_logging()
        print()
        
        test_timed_operation()
        print()
        
        test_log_file_creation()
        print()
        
        # Get performance summary
        summary = performance_tracker.get_performance_summary()
        print("Performance Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        print("\n✓ All logging tests completed successfully!")
        
    except Exception as e:
        log_error_with_context(e, "main test execution")
        print(f"✗ Test failed: {e}")
    
    finally:
        log_system_shutdown()

if __name__ == "__main__":
    main()