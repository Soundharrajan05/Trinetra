#!/usr/bin/env python3
"""
Demo script showing TRINETRA AI error handlers in action.
This script demonstrates various error scenarios and how they are handled gracefully.
"""

import sys
import os
sys.path.append('.')

from utils.helpers import (
    error_handlers, 
    safe_execute, 
    retry_on_failure, 
    handle_with_fallback,
    ValidationHelpers
)
import pandas as pd
import numpy as np

def demo_csv_loading_errors():
    """Demo CSV loading error handling."""
    print("\n=== CSV Loading Error Handling Demo ===")
    
    # Test 1: File not found
    try:
        df = pd.read_csv('nonexistent_dataset.csv')
    except Exception as e:
        result = error_handlers.handle_csv_loading_error(e, 'nonexistent_dataset.csv')
        print(f"❌ File not found error handled:")
        print(f"   User message: {result['user_message']}")
        print(f"   Suggestions: {', '.join(result['suggested_actions'][:2])}")
    
    # Test 2: Using safe_execute for CSV loading
    def load_csv_safely():
        return pd.read_csv('missing_file.csv')
    
    success, result, error_info = safe_execute(
        load_csv_safely, 
        default_return=pd.DataFrame(),
        context="CSV loading"
    )
    print(f"✓ Safe CSV loading: success={success}, fallback DataFrame shape={result.shape}")

def demo_model_errors():
    """Demo model error handling."""
    print("\n=== Model Error Handling Demo ===")
    
    # Test 1: Model training with invalid data
    def train_with_invalid_data():
        # Simulate training with NaN data
        X = np.array([[np.nan, 1, 2], [3, np.inf, 5]])
        from sklearn.ensemble import IsolationForest
        model = IsolationForest()
        model.fit(X)
        return model
    
    try:
        model = train_with_invalid_data()
    except Exception as e:
        result = error_handlers.handle_model_training_error(e, "IsolationForest", 3)
        print(f"❌ Model training error handled:")
        print(f"   User message: {result['user_message']}")
        print(f"   Can retry: {result['can_retry']}")
        print(f"   Recovery actions: {', '.join(result['recovery_actions'][:2])}")
    
    # Test 2: Model prediction with wrong shape
    def predict_with_wrong_shape():
        from sklearn.ensemble import IsolationForest
        model = IsolationForest()
        # Train with correct shape
        X_train = np.random.rand(100, 6)
        model.fit(X_train)
        # Try to predict with wrong shape
        X_test = np.random.rand(10, 3)  # Wrong number of features
        return model.predict(X_test)
    
    try:
        predictions = predict_with_wrong_shape()
    except Exception as e:
        result = error_handlers.handle_model_prediction_error(e, (10, 3), "IsolationForest")
        print(f"❌ Model prediction error handled:")
        print(f"   User message: {result['user_message']}")
        print(f"   Fallback available: {result['fallback_scores'] is not None}")

def demo_api_errors():
    """Demo API error handling."""
    print("\n=== API Error Handling Demo ===")
    
    # Test 1: Gemini API timeout simulation
    timeout_error = TimeoutError("Request timed out after 10 seconds")
    result = error_handlers.handle_gemini_api_error(timeout_error, "transaction explanation")
    print(f"❌ Gemini API timeout handled:")
    print(f"   Should retry: {result['should_retry']}")
    print(f"   Retry delay: {result.get('retry_delay', 'N/A')} seconds")
    print(f"   Fallback content: {result.get('fallback_content', 'N/A')}")
    
    # Test 2: Network error with retry
    network_error = ConnectionError("Network connection failed")
    result = error_handlers.handle_network_error(network_error, "/api/transactions")
    print(f"❌ Network error handled:")
    print(f"   Should retry: {result['should_retry']}")
    print(f"   User message: {result['user_message']}")

def demo_validation_errors():
    """Demo data validation error handling."""
    print("\n=== Data Validation Error Handling Demo ===")
    
    # Create invalid DataFrame
    invalid_df = pd.DataFrame({
        'transaction_id': [None, 'TXN002', 'TXN003'],  # Missing required field
        'date': ['2024-01-01', 'invalid-date', '2024-01-03'],  # Invalid date
        'amount': [-100, 'not_a_number', 500]  # Invalid numeric data
    })
    
    # Test schema validation
    validation_result = ValidationHelpers.validate_dataset_schema(invalid_df, strict=False)
    if not validation_result['valid']:
        result = error_handlers.handle_schema_validation_error(validation_result, "demo data")
        print(f"❌ Schema validation errors handled:")
        print(f"   Can continue: {result['can_continue']}")
        print(f"   Critical errors: {len(result['critical_errors'])}")
        print(f"   User message: {result['user_message']}")

def demo_retry_mechanisms():
    """Demo retry mechanisms."""
    print("\n=== Retry Mechanisms Demo ===")
    
    # Simulate unreliable operation that fails first few times
    attempt_count = 0
    def unreliable_operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError(f"Attempt {attempt_count} failed")
        return f"Success on attempt {attempt_count}"
    
    try:
        result = retry_on_failure(
            unreliable_operation,
            max_retries=3,
            delay=0.1,  # Short delay for demo
            context="unreliable service"
        )
        print(f"✓ Retry mechanism succeeded: {result}")
    except Exception as e:
        print(f"❌ Retry mechanism failed: {e}")

def demo_fallback_mechanisms():
    """Demo fallback mechanisms."""
    print("\n=== Fallback Mechanisms Demo ===")
    
    # Test handle_with_fallback
    def failing_config_load():
        raise FileNotFoundError("Config file not found")
    
    config = handle_with_fallback(
        failing_config_load,
        fallback_value={'theme': 'dark', 'language': 'en', 'timeout': 30},
        context="configuration loading"
    )
    print(f"✓ Fallback configuration loaded: {config}")
    
    # Test safe_execute with complex operation
    def complex_calculation():
        # Simulate complex calculation that might fail
        data = np.random.rand(1000, 100)
        if np.random.random() < 0.3:  # 30% chance of failure
            raise MemoryError("Insufficient memory for calculation")
        return np.mean(data)
    
    success, result, error_info = safe_execute(
        complex_calculation,
        default_return=0.5,  # Reasonable default
        context="statistical calculation"
    )
    print(f"✓ Complex calculation: success={success}, result={result:.4f}")

def demo_error_statistics():
    """Demo error statistics tracking."""
    print("\n=== Error Statistics Demo ===")
    
    # Generate some errors to track
    errors_to_generate = [
        (FileNotFoundError("File missing"), "file_ops"),
        (ValueError("Invalid value"), "data_processing"),
        (ConnectionError("Network down"), "api_calls"),
        (TimeoutError("Request timeout"), "external_service")
    ]
    
    for error, context in errors_to_generate:
        error_handlers.handle_general_error(error, context)
    
    # Get statistics
    stats = error_handlers.get_error_statistics()
    print(f"📊 Error Statistics:")
    print(f"   Total errors tracked: {stats['total_errors']}")
    print(f"   Error types: {len(stats['error_breakdown'])}")
    if stats['most_common_errors']:
        print(f"   Most common: {stats['most_common_errors'][0][0]} ({stats['most_common_errors'][0][1]} occurrences)")

def main():
    """Run all error handling demos."""
    print("🚀 TRINETRA AI Error Handlers Demo")
    print("=" * 50)
    
    try:
        demo_csv_loading_errors()
        demo_model_errors()
        demo_api_errors()
        demo_validation_errors()
        demo_retry_mechanisms()
        demo_fallback_mechanisms()
        demo_error_statistics()
        
        print("\n" + "=" * 50)
        print("✅ All error handling demos completed successfully!")
        print("🛡️  TRINETRA AI error handlers are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Demo failed with unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)