#!/usr/bin/env python3
"""
Test script to validate the TRINETRA AI dataset loading and processing.

This script tests the system's ability to:
1. Load the CSV dataset from the specified path
2. Parse date columns correctly
3. Validate schema and data integrity
4. Handle missing values
5. Verify dataset has 1000+ rows and 30+ columns
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from backend.data_loader import (
    load_dataset,
    validate_schema,
    get_dataset_stats,
    validate_dataset_health,
    REQUIRED_COLUMNS
)

def test_dataset_file_exists():
    """Test that the dataset file exists at the specified path."""
    print("\n" + "="*60)
    print("TEST 1: Dataset File Existence")
    print("="*60)
    
    dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    
    if os.path.exists(dataset_path):
        file_size = os.path.getsize(dataset_path)
        print(f"✓ Dataset file exists: {dataset_path}")
        print(f"✓ File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
        return True, dataset_path
    else:
        print(f"✗ Dataset file NOT found: {dataset_path}")
        print(f"  Current directory: {os.getcwd()}")
        return False, dataset_path

def test_dataset_loading(dataset_path):
    """Test that the dataset loads successfully."""
    print("\n" + "="*60)
    print("TEST 2: Dataset Loading")
    print("="*60)
    
    try:
        df = load_dataset(dataset_path)
        print(f"✓ Dataset loaded successfully")
        print(f"✓ Shape: {df.shape} (rows: {df.shape[0]}, columns: {df.shape[1]})")
        return True, df
    except Exception as e:
        print(f"✗ Failed to load dataset: {e}")
        return False, None

def test_date_parsing(df):
    """Test that date columns are parsed correctly."""
    print("\n" + "="*60)
    print("TEST 3: Date Column Parsing")
    print("="*60)
    
    if 'date' not in df.columns:
        print("✗ Date column not found in dataset")
        return False
    
    try:
        if pd.api.types.is_datetime64_any_dtype(df['date']):
            print(f"✓ Date column is in datetime format")
            print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"✓ Date span: {(df['date'].max() - df['date'].min()).days} days")
            return True
        else:
            print(f"✗ Date column is not in datetime format: {df['date'].dtype}")
            return False
    except Exception as e:
        print(f"✗ Error checking date column: {e}")
        return False

def test_schema_validation(df):
    """Test that schema validation passes."""
    print("\n" + "="*60)
    print("TEST 4: Schema Validation")
    print("="*60)
    
    try:
        is_valid = validate_schema(df)
        
        if is_valid:
            print(f"✓ Schema validation passed")
            print(f"✓ All required columns present:")
            for col in REQUIRED_COLUMNS:
                if col in df.columns:
                    print(f"  - {col}: {df[col].dtype}")
            return True
        else:
            print(f"✗ Schema validation failed")
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                print(f"  Missing columns: {missing_cols}")
            return False
    except Exception as e:
        print(f"✗ Error during schema validation: {e}")
        return False

def test_data_dimensions(df):
    """Test that dataset has 1000+ rows and 30+ columns."""
    print("\n" + "="*60)
    print("TEST 5: Data Dimensions")
    print("="*60)
    
    rows, cols = df.shape
    
    # Check rows
    if rows >= 1000:
        print(f"✓ Dataset has {rows} rows (requirement: 1000+)")
    else:
        print(f"✗ Dataset has only {rows} rows (requirement: 1000+)")
        return False
    
    # Check columns
    if cols >= 30:
        print(f"✓ Dataset has {cols} columns (requirement: 30+)")
    else:
        print(f"✗ Dataset has only {cols} columns (requirement: 30+)")
        return False
    
    return True

def test_missing_values(df):
    """Test that missing values are handled gracefully."""
    print("\n" + "="*60)
    print("TEST 6: Missing Value Handling")
    print("="*60)
    
    try:
        missing_count = df.isnull().sum().sum()
        total_cells = df.shape[0] * df.shape[1]
        missing_percentage = (missing_count / total_cells) * 100
        
        print(f"✓ Missing values: {missing_count} ({missing_percentage:.2f}%)")
        
        # Check per column
        columns_with_missing = df.columns[df.isnull().any()].tolist()
        if columns_with_missing:
            print(f"  Columns with missing values: {len(columns_with_missing)}")
            for col in columns_with_missing[:5]:  # Show first 5
                col_missing = df[col].isnull().sum()
                col_missing_pct = (col_missing / len(df)) * 100
                print(f"    - {col}: {col_missing} ({col_missing_pct:.1f}%)")
            if len(columns_with_missing) > 5:
                print(f"    ... and {len(columns_with_missing) - 5} more")
        else:
            print(f"  No missing values found")
        
        return True
    except Exception as e:
        print(f"✗ Error checking missing values: {e}")
        return False

def test_data_quality(df):
    """Test data quality checks."""
    print("\n" + "="*60)
    print("TEST 7: Data Quality Checks")
    print("="*60)
    
    try:
        health = validate_dataset_health(df)
        
        print(f"✓ Overall health: {health['overall_health']}")
        print(f"✓ Metrics:")
        for key, value in health['metrics'].items():
            print(f"  - {key}: {value}")
        
        if health['issues']:
            print(f"  Issues found: {len(health['issues'])}")
            for issue in health['issues']:
                print(f"    - {issue}")
        
        if health['warnings']:
            print(f"  Warnings: {len(health['warnings'])}")
            for warning in health['warnings']:
                print(f"    - {warning}")
        
        return True
    except Exception as e:
        print(f"✗ Error during data quality check: {e}")
        return False

def test_dataset_statistics(df):
    """Test dataset statistics generation."""
    print("\n" + "="*60)
    print("TEST 8: Dataset Statistics")
    print("="*60)
    
    try:
        stats = get_dataset_stats(df)
        
        print(f"✓ Basic Info:")
        if 'basic_info' in stats:
            for key, value in stats['basic_info'].items():
                print(f"  - {key}: {value}")
        
        print(f"✓ Data Quality:")
        if 'data_quality' in stats:
            for key, value in stats['data_quality'].items():
                print(f"  - {key}: {value}")
        
        if 'fraud_distribution' in stats:
            print(f"✓ Fraud Distribution:")
            fraud_dist = stats['fraud_distribution']
            if 'counts' in fraud_dist:
                print(f"  - Counts: {fraud_dist['counts']}")
            if 'fraud_rate' in fraud_dist:
                print(f"  - Fraud rate: {fraud_dist['fraud_rate']:.2f}%")
        
        return True
    except Exception as e:
        print(f"✗ Error generating statistics: {e}")
        return False

def test_required_columns_data_types(df):
    """Test that required columns have correct data types."""
    print("\n" + "="*60)
    print("TEST 9: Column Data Types")
    print("="*60)
    
    try:
        # Numeric columns
        numeric_cols = ['quantity', 'unit_price', 'trade_value', 'market_price', 
                       'price_deviation', 'distance_km', 'company_risk_score', 
                       'route_anomaly', 'fraud_label']
        
        print(f"✓ Checking numeric columns:")
        for col in numeric_cols:
            if col in df.columns:
                is_numeric = pd.api.types.is_numeric_dtype(df[col])
                status = "✓" if is_numeric else "✗"
                print(f"  {status} {col}: {df[col].dtype}")
        
        # String columns
        string_cols = ['transaction_id', 'product', 'commodity_category', 
                      'exporter_company', 'exporter_country', 'importer_company', 
                      'importer_country', 'shipping_route']
        
        print(f"✓ Checking string columns:")
        for col in string_cols:
            if col in df.columns:
                is_string = pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col])
                status = "✓" if is_string else "✗"
                print(f"  {status} {col}: {df[col].dtype}")
        
        return True
    except Exception as e:
        print(f"✗ Error checking data types: {e}")
        return False

def test_fraud_label_values(df):
    """Test that fraud_label has valid values."""
    print("\n" + "="*60)
    print("TEST 10: Fraud Label Validation")
    print("="*60)
    
    try:
        if 'fraud_label' not in df.columns:
            print("✗ fraud_label column not found")
            return False
        
        unique_labels = sorted(df['fraud_label'].dropna().unique())
        print(f"✓ Unique fraud labels: {unique_labels}")
        
        # Count distribution
        label_counts = df['fraud_label'].value_counts()
        print(f"✓ Label distribution:")
        for label, count in label_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  - {label}: {count} ({percentage:.1f}%)")
        
        return True
    except Exception as e:
        print(f"✗ Error checking fraud labels: {e}")
        return False

def main():
    """Run all dataset validation tests."""
    print("\n" + "="*70)
    print("TRINETRA AI - DATASET VALIDATION TEST SUITE")
    print("="*70)
    print(f"Testing dataset loading and processing capabilities")
    print(f"Dataset: data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
    
    results = []
    
    # Test 1: File exists
    success, dataset_path = test_dataset_file_exists()
    results.append(("Dataset File Exists", success))
    
    if not success:
        print("\n" + "="*70)
        print("CRITICAL ERROR: Dataset file not found. Cannot proceed with tests.")
        print("="*70)
        return False
    
    # Test 2: Load dataset
    success, df = test_dataset_loading(dataset_path)
    results.append(("Dataset Loading", success))
    
    if not success or df is None:
        print("\n" + "="*70)
        print("CRITICAL ERROR: Failed to load dataset. Cannot proceed with tests.")
        print("="*70)
        return False
    
    # Test 3: Date parsing
    success = test_date_parsing(df)
    results.append(("Date Parsing", success))
    
    # Test 4: Schema validation
    success = test_schema_validation(df)
    results.append(("Schema Validation", success))
    
    # Test 5: Data dimensions
    success = test_data_dimensions(df)
    results.append(("Data Dimensions", success))
    
    # Test 6: Missing values
    success = test_missing_values(df)
    results.append(("Missing Value Handling", success))
    
    # Test 7: Data quality
    success = test_data_quality(df)
    results.append(("Data Quality", success))
    
    # Test 8: Statistics
    success = test_dataset_statistics(df)
    results.append(("Dataset Statistics", success))
    
    # Test 9: Data types
    success = test_required_columns_data_types(df)
    results.append(("Column Data Types", success))
    
    # Test 10: Fraud labels
    success = test_fraud_label_values(df)
    results.append(("Fraud Label Validation", success))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print("="*70)
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - Dataset is ready for processing!")
        return True
    else:
        print(f"\n✗ {total - passed} test(s) failed - Please review the issues above")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
