#!/usr/bin/env python3
"""
TRINETRA AI - Error Handling System Demonstration

This script demonstrates the comprehensive error handling capabilities
implemented in the utils/helpers.py module for the TRINETRA AI system.

Author: TRINETRA AI Team
Date: 2024
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import *

def demonstrate_error_handling():
    """Demonstrate all error handling capabilities."""
    
    print("=" * 60)
    print("TRINETRA AI - Error Handling System Demonstration")
    print("=" * 60)
    
    # 1. Gemini API Error Handling
    print("\n1. GEMINI API ERROR HANDLING")
    print("-" * 40)
    
    gemini_errors = [
        ("Rate Limit Error", GeminiRateLimitError("API rate limit exceeded")),
        ("Timeout Error", GeminiTimeoutError("Request timed out after 10 seconds")),
        ("Quota Exceeded", GeminiQuotaExceededError("Daily quota limit reached")),
        ("Initialization Error", GeminiInitializationError("Invalid API key")),
        ("Generic API Error", GeminiAPIError("Service temporarily unavailable"))
    ]
    
    for error_name, error in gemini_errors:
        result = handle_gemini_error(error, "transaction explanation")
        print(f"  {error_name}:")
        print(f"    Should Retry: {result.get('should_retry', False)}")
        print(f"    User Message: {result['user_message']}")
        if 'fallback_content' in result and result['fallback_content']:
            print(f"    Fallback: {result['fallback_content'][:50]}...")
        print()
    
    # 2. Data Loading Error Handling
    print("\n2. DATA LOADING ERROR HANDLING")
    print("-" * 40)
    
    data_errors = [
        ("Schema Validation", SchemaValidationError("Missing required columns: transaction_id, date")),
        ("Data Quality", DataQualityError("Invalid data values detected in price_deviation column")),
        ("Generic Data Loader", DataLoaderError("Unable to parse CSV file format"))
    ]
    
    for error_name, error in data_errors:
        result = handle_data_loader_error(error, "data/fraud_dataset.csv")
        print(f"  {error_name}:")
        print(f"    Error Category: {result.get('error_category', 'unknown')}")
        print(f"    User Message: {result['user_message']}")
        print(f"    Suggested Actions: {len(result.get('suggested_actions', []))} available")
        print()
    
    # 3. Model Error Handling
    print("\n3. MODEL ERROR HANDLING")
    print("-" * 40)
    
    # Training errors
    training_error = ModelTrainingError("Insufficient memory for model training")
    result = handle_model_error(training_error, "IsolationForest", "training")
    print(f"  Model Training Error:")
    print(f"    Can Retry: {result['can_retry']}")
    print(f"    User Message: {result['user_message']}")
    print()
    
    # Prediction errors
    prediction_error = ModelPredictionError("Input shape mismatch: expected (n, 6), got (n, 5)")
    result = handle_model_error(prediction_error, "IsolationForest", "prediction")
    print(f"  Model Prediction Error:")
    print(f"    Degraded Service: {result['degraded_service']}")
    print(f"    Has Fallback Scores: {'fallback_scores' in result}")
    print()
    
    # 4. Feature Engineering Error Handling
    print("\n4. FEATURE ENGINEERING ERROR HANDLING")
    print("-" * 40)
    
    feature_error = FeatureEngineeringError("Division by zero in shipment_duration_risk calculation")
    result = handle_feature_error(feature_error, "shipment_duration_risk")
    print(f"  Feature Engineering Error:")
    print(f"    Error Category: {result.get('error_category', 'unknown')}")
    print(f"    Can Retry: {result['can_retry']}")
    print(f"    Recovery Actions: {len(result.get('recovery_actions', []))} available")
    print()
    
    # 5. Alert System Error Handling
    print("\n5. ALERT SYSTEM ERROR HANDLING")
    print("-" * 40)
    
    alert_error = AlertSystemError("Alert threshold configuration invalid")
    result = handle_alert_error(alert_error, "PRICE_ANOMALY")
    print(f"  Alert System Error:")
    print(f"    Fallback Behavior: {result.get('fallback_behavior', 'unknown')}")
    print(f"    Degraded Service: {result['degraded_service']}")
    print()
    
    # 6. Error Statistics
    print("\n6. ERROR STATISTICS")
    print("-" * 40)
    
    stats = error_handlers.get_error_statistics()
    print(f"  Total Errors Tracked: {stats['total_errors']}")
    print(f"  Unique Error Types: {len(stats['error_breakdown'])}")
    
    if stats['most_common_errors']:
        print("  Most Common Errors:")
        for error_type, count in stats['most_common_errors']:
            print(f"    - {error_type}: {count} occurrences")
    
    # 7. Utility Functions
    print("\n7. UTILITY FUNCTIONS")
    print("-" * 40)
    
    # Safe execution
    def risky_operation():
        raise ValueError("This operation always fails")
    
    success, result, error_info = safe_execute(
        risky_operation, 
        default_return="fallback_value",
        context="demonstration"
    )
    
    print(f"  Safe Execute:")
    print(f"    Success: {success}")
    print(f"    Result: {result}")
    print(f"    Error Handled: {error_info is not None}")
    print()
    
    # Handle with fallback
    fallback_result = handle_with_fallback(
        lambda: 1/0,  # Division by zero
        fallback_value="calculation_failed",
        context="math operation"
    )
    
    print(f"  Handle with Fallback:")
    print(f"    Result: {fallback_result}")
    print()
    
    print("=" * 60)
    print("Error Handling Demonstration Complete!")
    print("=" * 60)
    
    # Reset error counts for clean slate
    error_handlers.reset_error_counts()
    print("\nError tracking counters reset.")

if __name__ == "__main__":
    demonstrate_error_handling()