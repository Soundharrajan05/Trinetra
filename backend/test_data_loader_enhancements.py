#!/usr/bin/env python3
"""
Test script to verify the enhanced error handling and logging in data_loader.py
"""

import os
import sys
import tempfile
import pandas as pd
from data_loader import (
    load_dataset, 
    validate_schema, 
    handle_missing_values,
    get_dataset_stats,
    validate_dataset_health,
    DataLoaderError,
    SchemaValidationError,
    DataQualityError
)

def test_file_not_found():
    """Test error handling for non-existent files."""
    print("Testing file not found error handling...")
    try:
        load_dataset("nonexistent_file.csv")
        print("❌ FAILED: Should have raised FileNotFoundError")
        return False
    except FileNotFoundError as e:
        print(f"✅ PASSED: Correctly raised FileNotFoundError: {e}")
        return True
    except Exception as e:
        print(f"❌ FAILED: Unexpected exception: {e}")
        return False

def test_empty_file():
    """Test error handling for empty files."""
    print("Testing empty file error handling...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_file = f.name
    
    try:
        load_dataset(temp_file)
        print("❌ FAILED: Should have raised FileNotFoundError for empty file")
        return False
    except FileNotFoundError as e:
        print(f"✅ PASSED: Correctly handled empty file: {e}")
        return True
    except Exception as e:
        print(f"❌ FAILED: Unexpected exception: {e}")
        return False
    finally:
        os.unlink(temp_file)

def test_invalid_csv():
    """Test error handling for invalid CSV content."""
    print("Testing invalid CSV error handling...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("invalid,csv,content\nwith,missing,quotes\"and\nbad,formatting")
        temp_file = f.name
    
    try:
        load_dataset(temp_file)
        print("❌ FAILED: Should have raised DataLoaderError for invalid CSV")
        return False
    except (DataLoaderError, SchemaValidationError) as e:
        print(f"✅ PASSED: Correctly handled invalid CSV: {e}")
        return True
    except Exception as e:
        print(f"❌ FAILED: Unexpected exception: {e}")
        return False
    finally:
        os.unlink(temp_file)

def test_missing_required_columns():
    """Test schema validation for missing required columns."""
    print("Testing missing required columns...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("col1,col2,col3\n1,2,3\n4,5,6\n")
        temp_file = f.name
    
    try:
        load_dataset(temp_file)
        print("❌ FAILED: Should have raised SchemaValidationError")
        return False
    except SchemaValidationError as e:
        print(f"✅ PASSED: Correctly detected missing columns: {e}")
        return True
    except Exception as e:
        print(f"❌ FAILED: Unexpected exception: {e}")
        return False
    finally:
        os.unlink(temp_file)

def test_dataset_health_check():
    """Test dataset health check functionality."""
    print("Testing dataset health check...")
    
    # Create a simple test DataFrame
    test_data = {
        'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
        'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
        'fraud_label': [0, 1, 0]
    }
    df = pd.DataFrame(test_data)
    
    try:
        health_report = validate_dataset_health(df)
        print(f"✅ PASSED: Health check completed. Overall health: {health_report['overall_health']}")
        return True
    except Exception as e:
        print(f"❌ FAILED: Health check failed: {e}")
        return False

def test_comprehensive_stats():
    """Test comprehensive statistics calculation."""
    print("Testing comprehensive statistics...")
    
    # Create test data with various scenarios
    test_data = {
        'transaction_id': ['TXN001', 'TXN002', 'TXN003', 'TXN004'],
        'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04']),
        'product': ['A', 'B', 'A', 'C'],
        'trade_value': [1000.0, 2000.0, 1500.0, 3000.0],
        'exporter_country': ['USA', 'Canada', 'USA', 'Mexico'],
        'importer_country': ['China', 'Japan', 'China', 'India'],
        'company_risk_score': [0.1, 0.9, 0.3, 0.7],
        'route_anomaly': [0, 1, 0, 0],
        'price_deviation': [0.1, 0.8, 0.2, 0.3],
        'fraud_label': [0, 1, 0, 2]
    }
    df = pd.DataFrame(test_data)
    
    try:
        stats = get_dataset_stats(df)
        
        # Verify key statistics are present
        assert 'basic_info' in stats
        assert 'data_quality' in stats
        assert 'fraud_distribution' in stats
        assert 'trade_value_stats' in stats
        assert 'risk_indicators' in stats
        
        print("✅ PASSED: Comprehensive statistics calculated successfully")
        return True
    except Exception as e:
        print(f"❌ FAILED: Statistics calculation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING ENHANCED DATA LOADER ERROR HANDLING AND LOGGING")
    print("=" * 60)
    
    tests = [
        test_file_not_found,
        test_empty_file,
        test_invalid_csv,
        test_missing_required_columns,
        test_dataset_health_check,
        test_comprehensive_stats
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ FAILED: Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Enhanced error handling and logging working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())