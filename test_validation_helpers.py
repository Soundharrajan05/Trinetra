#!/usr/bin/env python3
"""
Test script for validation helper functions in utils/helpers.py

This script tests the newly implemented validation helper functions
to ensure they work correctly for the TRINETRA AI fraud detection system.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import ValidationHelpers, validate_file_path, validate_dataframe_for_ml, create_validation_report

def test_dataset_schema_validation():
    """Test dataset schema validation functionality."""
    print("Testing dataset schema validation...")
    
    # Create a valid test dataset
    valid_data = {
        'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
        'date': [datetime.now(), datetime.now(), datetime.now()],
        'product': ['Product A', 'Product B', 'Product C'],
        'commodity_category': ['Category 1', 'Category 2', 'Category 3'],
        'quantity': [100, 200, 150],
        'unit_price': [10.5, 20.0, 15.75],
        'trade_value': [1050, 4000, 2362.5],
        'market_price': [10.0, 19.5, 16.0],
        'exporter_company': ['Company A', 'Company B', 'Company C'],
        'exporter_country': ['USA', 'Germany', 'Japan'],
        'importer_company': ['Company X', 'Company Y', 'Company Z'],
        'importer_country': ['Canada', 'France', 'UK'],
        'shipping_route': ['Route 1', 'Route 2', 'Route 3'],
        'export_port': ['Port A', 'Port B', 'Port C'],
        'import_port': ['Port X', 'Port Y', 'Port Z'],
        'distance_km': [5000, 8000, 6500],
        'price_deviation': [0.05, 0.025, -0.015],
        'company_risk_score': [0.2, 0.1, 0.3],
        'route_anomaly': [0, 1, 0],
        'fraud_label': [0, 1, 0]
    }
    
    valid_df = pd.DataFrame(valid_data)
    
    # Test valid dataset
    result = ValidationHelpers.validate_dataset_schema(valid_df, strict=True)
    print(f"Valid dataset validation: {'PASSED' if result['valid'] else 'FAILED'}")
    if result['errors']:
        print(f"  Errors: {result['errors']}")
    if result['warnings']:
        print(f"  Warnings: {result['warnings']}")
    
    # Test dataset with missing columns
    invalid_df = valid_df.drop(['product', 'quantity'], axis=1)
    result = ValidationHelpers.validate_dataset_schema(invalid_df, strict=True)
    print(f"Invalid dataset validation: {'FAILED' if not result['valid'] else 'UNEXPECTED PASS'}")
    print(f"  Expected errors found: {len(result['errors'])} errors")
    
    print("Dataset schema validation tests completed.\n")

def test_transaction_validation():
    """Test individual transaction validation."""
    print("Testing transaction validation...")
    
    # Valid transaction
    valid_transaction = {
        'transaction_id': 'TXN001',
        'date': '2024-01-15',
        'product': 'Electronics',
        'commodity_category': 'Technology',
        'quantity': 100,
        'unit_price': 25.50,
        'trade_value': 2550.0,
        'market_price': 24.00
    }
    
    result = ValidationHelpers.validate_transaction_data(valid_transaction)
    print(f"Valid transaction validation: {'PASSED' if result['valid'] else 'FAILED'}")
    
    # Invalid transaction (missing required fields)
    invalid_transaction = {
        'transaction_id': 'TXN002',
        'product': 'Electronics'
        # Missing date, commodity_category, etc.
    }
    
    result = ValidationHelpers.validate_transaction_data(invalid_transaction)
    print(f"Invalid transaction validation: {'FAILED' if not result['valid'] else 'UNEXPECTED PASS'}")
    print(f"  Expected errors found: {len(result['errors'])} errors")
    
    # Transaction with out-of-range values
    extreme_transaction = {
        'transaction_id': 'TXN003',
        'date': '2024-01-15',
        'product': 'Electronics',
        'commodity_category': 'Technology',
        'quantity': -50,  # Negative quantity
        'unit_price': -10.0,  # Negative price
        'trade_value': 1000000000,  # Very large value
        'market_price': 25.00,
        'risk_score': 2.0  # Out of range [-1, 1]
    }
    
    result = ValidationHelpers.validate_transaction_data(extreme_transaction)
    print(f"Extreme values transaction: {'PASSED' if result['valid'] else 'FAILED'}")
    print(f"  Warnings found: {len(result['warnings'])} warnings")
    
    print("Transaction validation tests completed.\n")

def test_api_input_validation():
    """Test API input validation."""
    print("Testing API input validation...")
    
    # Valid query input
    valid_query = {'query': 'Why is transaction TXN001 suspicious?'}
    result = ValidationHelpers.validate_api_input(valid_query, 'query')
    print(f"Valid query validation: {'PASSED' if result['valid'] else 'FAILED'}")
    
    # Invalid query (empty)
    invalid_query = {'query': ''}
    result = ValidationHelpers.validate_api_input(invalid_query, 'query')
    print(f"Invalid query validation: {'FAILED' if not result['valid'] else 'UNEXPECTED PASS'}")
    
    # Valid explanation request
    valid_explain = {'transaction_id': 'TXN001', 'force_ai': True}
    result = ValidationHelpers.validate_api_input(valid_explain, 'explain')
    print(f"Valid explanation request: {'PASSED' if result['valid'] else 'FAILED'}")
    
    # Invalid explanation request (missing transaction_id)
    invalid_explain = {'force_ai': True}
    result = ValidationHelpers.validate_api_input(invalid_explain, 'explain')
    print(f"Invalid explanation request: {'FAILED' if not result['valid'] else 'UNEXPECTED PASS'}")
    
    print("API input validation tests completed.\n")

def test_feature_validation():
    """Test feature data validation."""
    print("Testing feature validation...")
    
    # Create test data with features
    feature_data = {
        'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
        'price_anomaly_score': [0.1, 0.3, 0.05],
        'route_risk_score': [0, 1, 0],
        'company_network_risk': [0.2, 0.8, 0.1],
        'port_congestion_score': [1.2, 2.5, 0.8],
        'shipment_duration_risk': [0.5, 1.2, 0.3],
        'volume_spike_score': [2.1, 5.0, 1.8]
    }
    
    feature_df = pd.DataFrame(feature_data)
    
    result = ValidationHelpers.validate_feature_data(feature_df)
    print(f"Feature validation: {'PASSED' if result['valid'] else 'FAILED'}")
    if result['warnings']:
        print(f"  Warnings: {result['warnings']}")
    
    print("Feature validation tests completed.\n")

def test_string_sanitization():
    """Test string sanitization functionality."""
    print("Testing string sanitization...")
    
    # Test various dangerous inputs
    test_strings = [
        "Normal string",
        "<script>alert('xss')</script>",
        "SELECT * FROM users; DROP TABLE users;",
        "String with 'quotes' and \"double quotes\"",
        "Very long string " + "x" * 1000,
        "String with\nmultiple\nlines\nand\ttabs"
    ]
    
    for test_str in test_strings:
        sanitized = ValidationHelpers.sanitize_string_input(test_str)
        print(f"Original: {test_str[:50]}{'...' if len(test_str) > 50 else ''}")
        print(f"Sanitized: {sanitized[:50]}{'...' if len(sanitized) > 50 else ''}")
        print()
    
    print("String sanitization tests completed.\n")

def test_validation_report():
    """Test validation report generation."""
    print("Testing validation report generation...")
    
    # Create sample validation results
    sample_results = {
        'valid': False,
        'errors': ['Missing required field: transaction_id', 'Invalid numeric value for quantity'],
        'warnings': ['Price deviation outside expected range', 'Transaction ID is unusually long'],
        'summary': 'Transaction validation failed with 2 errors and 2 warnings',
        'details': {
            'fields_checked': 8,
            'required_fields_present': 6,
            'numeric_fields_valid': 5
        }
    }
    
    report = create_validation_report(sample_results, "Sample Validation Report")
    print("Generated validation report:")
    print(report)
    
    print("Validation report tests completed.\n")

def main():
    """Run all validation helper tests."""
    print("Starting validation helper function tests...\n")
    
    try:
        test_dataset_schema_validation()
        test_transaction_validation()
        test_api_input_validation()
        test_feature_validation()
        test_string_sanitization()
        test_validation_report()
        
        print("All validation helper tests completed successfully!")
        
    except Exception as e:
        print(f"Test execution failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)