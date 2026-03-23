#!/usr/bin/env python3
"""
Test script for new validation helper functions added to utils/helpers.py

This script tests the additional validation functions:
- validate_risk_score_range()
- validate_alert_thresholds()
- validate_gemini_api_response()
- validate_dashboard_data()
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import (
    validate_risk_score_range,
    validate_alert_thresholds,
    validate_gemini_api_response,
    validate_dashboard_data
)

def test_risk_score_validation():
    """Test risk score range validation."""
    print("\nTesting risk score validation...")
    
    # Valid risk scores
    valid_scores = [0.0, 0.5, -0.3, 0.8, -0.1]
    for score in valid_scores:
        result = validate_risk_score_range(score)
        print(f"  Score {score}: {'PASSED' if result['valid'] else 'FAILED'}")
        if result['warnings']:
            print(f"    Warnings: {result['warnings']}")
    
    # Invalid risk scores
    invalid_scores = [float('nan'), float('inf'), "invalid", None]
    for score in invalid_scores:
        result = validate_risk_score_range(score)
        print(f"  Invalid score {score}: {'FAILED' if not result['valid'] else 'UNEXPECTED PASS'}")
        if result['errors']:
            print(f"    Expected errors: {result['errors']}")
    
    # Out of range scores
    extreme_scores = [-2.0, 3.5, -1.5, 2.0]
    for score in extreme_scores:
        result = validate_risk_score_range(score)
        print(f"  Extreme score {score}: {'PASSED' if result['valid'] else 'FAILED'}")
        print(f"    Normalized: {result['normalized_score']}")
        if result['warnings']:
            print(f"    Warnings: {result['warnings']}")
    
    print("Risk score validation tests completed.")


def test_alert_thresholds_validation():
    """Test alert thresholds validation."""
    print("\nTesting alert thresholds validation...")
    
    # Valid thresholds
    valid_thresholds = {
        'price_deviation_threshold': 0.5,
        'company_risk_threshold': 0.8,
        'port_activity_threshold': 1.5,
        'route_anomaly_threshold': 1.0
    }
    
    result = validate_alert_thresholds(valid_thresholds)
    print(f"Valid thresholds: {'PASSED' if result['valid'] else 'FAILED'}")
    
    # Missing thresholds
    incomplete_thresholds = {
        'price_deviation_threshold': 0.5,
        'company_risk_threshold': 0.8
    }
    
    result = validate_alert_thresholds(incomplete_thresholds)
    print(f"Incomplete thresholds: {'FAILED' if not result['valid'] else 'UNEXPECTED PASS'}")
    if result['errors']:
        print(f"  Expected errors: {result['errors']}")
    
    # Invalid threshold values
    invalid_thresholds = {
        'price_deviation_threshold': -0.5,  # Negative
        'company_risk_threshold': 'invalid',  # Non-numeric
        'port_activity_threshold': float('inf'),  # Infinite
        'route_anomaly_threshold': 1.0
    }
    
    result = validate_alert_thresholds(invalid_thresholds)
    print(f"Invalid thresholds: {'FAILED' if not result['valid'] else 'UNEXPECTED PASS'}")
    if result['errors']:
        print(f"  Expected errors: {result['errors']}")
    
    print("Alert thresholds validation tests completed.")


def test_gemini_api_response_validation():
    """Test Gemini API response validation."""
    print("\nTesting Gemini API response validation...")
    
    # Valid response
    valid_response = {
        'text': 'This transaction appears suspicious due to significant price deviation from market rates.',
        'usage': {
            'prompt_tokens': 150,
            'completion_tokens': 50
        }
    }
    
    result = validate_gemini_api_response(valid_response)
    print(f"Valid response: {'PASSED' if result['valid'] else 'FAILED'}")
    
    # Empty response
    empty_response = {'text': ''}
    result = validate_gemini_api_response(empty_response)
    print(f"Empty response: {'PASSED' if result['valid'] else 'FAILED'}")
    if result['warnings']:
        print(f"  Warnings: {result['warnings']}")
    
    # Error response
    error_response = {
        'error': {
            'message': 'API quota exceeded',
            'code': 429
        }
    }
    
    result = validate_gemini_api_response(error_response)
    print(f"Error response: {'PASSED' if result['valid'] else 'FAILED'}")
    if result['warnings']:
        print(f"  Warnings: {result['warnings']}")
    
    # Invalid response format
    invalid_response = "This is not a dictionary"
    result = validate_gemini_api_response(invalid_response)
    print(f"Invalid response format: {'FAILED' if not result['valid'] else 'UNEXPECTED PASS'}")
    if result['errors']:
        print(f"  Expected errors: {result['errors']}")
    
    print("Gemini API response validation tests completed.")


def test_dashboard_data_validation():
    """Test dashboard data validation."""
    print("\nTesting dashboard data validation...")
    
    # Valid dashboard data
    valid_data = {
        'transactions': [
            {
                'transaction_id': 'TXN001',
                'risk_score': 0.3,
                'risk_category': 'SUSPICIOUS',
                'product': 'Electronics'
            },
            {
                'transaction_id': 'TXN002',
                'risk_score': -0.1,
                'risk_category': 'SAFE',
                'product': 'Textiles'
            }
        ],
        'statistics': {
            'total_transactions': 1000,
            'fraud_rate': 0.05,
            'total_trade_value': 50000000
        },
        'alerts': [
            {'type': 'PRICE_ANOMALY', 'transaction_id': 'TXN001'},
            {'type': 'ROUTE_ANOMALY', 'transaction_id': 'TXN003'}
        ],
        'suspicious_transactions': [
            {'transaction_id': 'TXN001', 'risk_score': 0.3}
        ]
    }
    
    result = validate_dashboard_data(valid_data)
    print(f"Valid dashboard data: {'PASSED' if result['valid'] else 'FAILED'}")
    print(f"  Sections present: {result['sections_present']}/{result['total_sections_expected']}")
    print(f"  Transaction count: {result['transaction_count']}")
    print(f"  Alert count: {result['alert_count']}")
    
    # Missing sections
    incomplete_data = {
        'transactions': [],
        'statistics': {'total_transactions': 0}
    }
    
    result = validate_dashboard_data(incomplete_data)
    print(f"Incomplete dashboard data: {'PASSED' if result['valid'] else 'FAILED'}")
    if result['warnings']:
        print(f"  Warnings: {result['warnings']}")
    
    # Invalid transaction format
    invalid_data = {
        'transactions': [
            {'transaction_id': 'TXN001'},  # Missing required fields
            'invalid_transaction'  # Not a dictionary
        ],
        'statistics': 'invalid_stats',  # Not a dictionary
        'alerts': 'invalid_alerts'  # Not a list
    }
    
    result = validate_dashboard_data(invalid_data)
    print(f"Invalid dashboard data: {'FAILED' if not result['valid'] else 'UNEXPECTED PASS'}")
    if result['errors']:
        print(f"  Expected errors: {result['errors']}")
    
    print("Dashboard data validation tests completed.")


def main():
    """Run all validation function tests."""
    print("Starting new validation helper function tests...")
    
    try:
        test_risk_score_validation()
        test_alert_thresholds_validation()
        test_gemini_api_response_validation()
        test_dashboard_data_validation()
        
        print("\n✅ All new validation helper function tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)