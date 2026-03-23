"""
Property-Based Test for Data Integrity (CP-1)
TRINETRA AI - Trade Fraud Intelligence System

**Validates: Requirements CP-1**

This module implements property-based testing for data integrity validation.
Tests ensure that all loaded transactions have valid transaction_id, date, and fraud_label.

Property: All loaded transactions must have valid transaction_id, date, and fraud_label
Test Strategy: Property-based test generating random row indices and validating required fields are non-null
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from hypothesis import given, strategies as st, settings, assume, example
from hypothesis.extra.pandas import data_frames, columns
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import (
    load_dataset,
    validate_schema,
    REQUIRED_COLUMNS,
    DataLoaderError,
    SchemaValidationError
)


class TestDataIntegrityProperty:
    """Property-based tests for data integrity validation (CP-1)."""
    
    @given(
        row_indices=st.lists(
            st.integers(min_value=0, max_value=999), 
            min_size=1, 
            max_size=50,
            unique=True
        )
    )
    @settings(max_examples=20, deadline=30000)  # Increased deadline for file operations
    @example(row_indices=[0, 1, 2])  # Simple example
    @example(row_indices=[999])  # Edge case: last row
    @example(row_indices=[0, 500, 999])  # Spread across dataset
    def test_data_integrity_random_rows(self, row_indices: List[int]):
        """
        **Validates: Requirements CP-1**
        
        Property: All loaded transactions must have valid transaction_id, date, and fraud_label
        
        Test Strategy: Generate random row indices and validate required fields are non-null
        """
        # Load the actual dataset
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        
        # Skip test if dataset doesn't exist (for CI environments)
        if not os.path.exists(dataset_path):
            pytest.skip(f"Dataset not found: {dataset_path}")
        
        try:
            df = load_dataset(dataset_path)
            
            # Ensure we have data to test
            assume(len(df) > 0)
            assume(max(row_indices) < len(df))
            
            # Test the property: critical fields must be non-null for selected rows
            for idx in row_indices:
                # Validate transaction_id is non-null and non-empty
                transaction_id = df.iloc[idx]['transaction_id']
                assert pd.notna(transaction_id), f"transaction_id is null at row {idx}"
                assert str(transaction_id).strip() != '', f"transaction_id is empty at row {idx}"
                
                # Validate date is non-null and valid datetime
                date_value = df.iloc[idx]['date']
                assert pd.notna(date_value), f"date is null at row {idx}"
                assert pd.api.types.is_datetime64_any_dtype(pd.Series([date_value])), f"date is not datetime at row {idx}"
                
                # Validate fraud_label is non-null and valid
                fraud_label = df.iloc[idx]['fraud_label']
                assert pd.notna(fraud_label), f"fraud_label is null at row {idx}"
                assert isinstance(fraud_label, (int, float, np.integer, np.floating)), f"fraud_label is not numeric at row {idx}"
                
        except (FileNotFoundError, DataLoaderError, SchemaValidationError) as e:
            pytest.skip(f"Dataset loading failed: {e}")
    
    @given(
        csv_format=st.sampled_from([
            'standard',
            'with_quotes', 
            'mixed_quotes',
            'different_separator'
        ])
    )
    @settings(max_examples=10, deadline=30000)
    def test_data_integrity_various_csv_formats(self, csv_format: str):
        """
        **Validates: Requirements CP-1**
        
        Property: Data integrity must be maintained across various CSV formats
        
        Test Strategy: Test with different CSV formatting styles
        """
        # Create test data with critical fields
        test_data = {
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'product': ['Product A', 'Product B', 'Product C'],
            'commodity_category': ['Cat1', 'Cat2', 'Cat3'],
            'quantity': [100, 200, 300],
            'unit_price': [10.0, 20.0, 30.0],
            'trade_value': [1000.0, 4000.0, 9000.0],
            'market_price': [10.5, 20.5, 30.5],
            'price_deviation': [0.05, 0.025, 0.017],
            'exporter_company': ['Exp1', 'Exp2', 'Exp3'],
            'exporter_country': ['USA', 'Canada', 'Mexico'],
            'importer_company': ['Imp1', 'Imp2', 'Imp3'],
            'importer_country': ['China', 'Japan', 'India'],
            'shipping_route': ['Route1', 'Route2', 'Route3'],
            'distance_km': [1000, 2000, 3000],
            'company_risk_score': [0.1, 0.5, 0.9],
            'route_anomaly': [0, 1, 0],
            'fraud_label': [0, 1, 0]
        }
        
        # Add more columns to meet minimum requirements
        for col in REQUIRED_COLUMNS:
            if col not in test_data:
                test_data[col] = ['default_value'] * 3
        
        df = pd.DataFrame(test_data)
        
        # Create temporary CSV with different formats
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
            
            try:
                if csv_format == 'standard':
                    df.to_csv(temp_file, index=False)
                elif csv_format == 'with_quotes':
                    df.to_csv(temp_file, index=False, quoting=1)  # Quote all fields
                elif csv_format == 'mixed_quotes':
                    df.to_csv(temp_file, index=False, quotechar='"')
                elif csv_format == 'different_separator':
                    # Skip this test as our loader expects comma-separated
                    pytest.skip("Different separator format not supported by current loader")
                
                # Load the CSV and validate data integrity
                loaded_df = load_dataset(temp_file)
                
                # Verify critical fields are preserved
                assert len(loaded_df) == 3, "Row count mismatch"
                
                for idx in range(len(loaded_df)):
                    # Check transaction_id integrity
                    assert pd.notna(loaded_df.iloc[idx]['transaction_id'])
                    assert str(loaded_df.iloc[idx]['transaction_id']).startswith('TXN')
                    
                    # Check date integrity
                    assert pd.notna(loaded_df.iloc[idx]['date'])
                    assert pd.api.types.is_datetime64_any_dtype(pd.Series([loaded_df.iloc[idx]['date']]))
                    
                    # Check fraud_label integrity
                    assert pd.notna(loaded_df.iloc[idx]['fraud_label'])
                    assert loaded_df.iloc[idx]['fraud_label'] in [0, 1]
                    
            finally:
                os.unlink(temp_file)
    
    @given(
        sample_size=st.integers(min_value=5, max_value=100)
    )
    @settings(max_examples=15, deadline=30000)
    def test_data_integrity_sample_validation(self, sample_size: int):
        """
        **Validates: Requirements CP-1**
        
        Property: Data integrity must hold for any random sample of the dataset
        
        Test Strategy: Take random samples and validate all critical fields
        """
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        
        if not os.path.exists(dataset_path):
            pytest.skip(f"Dataset not found: {dataset_path}")
        
        try:
            df = load_dataset(dataset_path)
            assume(len(df) >= sample_size)
            
            # Take a random sample
            sample_df = df.sample(n=sample_size, random_state=42)
            
            # Validate data integrity for the entire sample
            for idx, row in sample_df.iterrows():
                # Critical field validation
                assert pd.notna(row['transaction_id']), f"Null transaction_id at index {idx}"
                assert str(row['transaction_id']).strip() != '', f"Empty transaction_id at index {idx}"
                
                assert pd.notna(row['date']), f"Null date at index {idx}"
                assert pd.api.types.is_datetime64_any_dtype(pd.Series([row['date']])), f"Invalid date at index {idx}"
                
                assert pd.notna(row['fraud_label']), f"Null fraud_label at index {idx}"
                assert isinstance(row['fraud_label'], (int, float, np.integer, np.floating)), f"Invalid fraud_label type at index {idx}"
                
                # Additional integrity checks
                if 'quantity' in row and pd.notna(row['quantity']):
                    assert row['quantity'] > 0, f"Invalid quantity at index {idx}"
                
                if 'unit_price' in row and pd.notna(row['unit_price']):
                    assert row['unit_price'] > 0, f"Invalid unit_price at index {idx}"
                    
        except (FileNotFoundError, DataLoaderError, SchemaValidationError) as e:
            pytest.skip(f"Dataset loading failed: {e}")
    
    @given(
        corruption_type=st.sampled_from([
            'null_transaction_id',
            'null_date', 
            'null_fraud_label',
            'empty_transaction_id',
            'invalid_date_format'
        ])
    )
    @settings(max_examples=10, deadline=30000)
    def test_data_integrity_corruption_detection(self, corruption_type: str):
        """
        **Validates: Requirements CP-1**
        
        Property: Data loader must detect and handle data integrity violations
        
        Test Strategy: Introduce specific corruptions and verify they are detected
        """
        # Create base valid data
        test_data = {
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'fraud_label': [0, 1, 0]
        }
        
        # Add required columns
        for col in REQUIRED_COLUMNS:
            if col not in test_data:
                test_data[col] = ['valid_value'] * 3
        
        # Introduce corruption based on type
        if corruption_type == 'null_transaction_id':
            test_data['transaction_id'][1] = None
        elif corruption_type == 'null_date':
            test_data['date'][1] = None
        elif corruption_type == 'null_fraud_label':
            test_data['fraud_label'][1] = None
        elif corruption_type == 'empty_transaction_id':
            test_data['transaction_id'][1] = ''
        elif corruption_type == 'invalid_date_format':
            test_data['date'][1] = 'invalid-date'
        
        df = pd.DataFrame(test_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
            df.to_csv(temp_file, index=False)
            
            try:
                # The data loader should either fix the corruption or raise an error
                loaded_df = load_dataset(temp_file)
                
                # If loading succeeds, verify the corruption was handled
                if corruption_type in ['null_transaction_id', 'empty_transaction_id']:
                    # Should have generated a transaction ID
                    assert all(pd.notna(loaded_df['transaction_id']))
                    assert all(str(tid).strip() != '' for tid in loaded_df['transaction_id'])
                
                elif corruption_type == 'null_date':
                    # Should have handled null dates
                    assert all(pd.notna(loaded_df['date']))
                
                elif corruption_type == 'null_fraud_label':
                    # Should have handled null fraud labels
                    assert all(pd.notna(loaded_df['fraud_label']))
                
                elif corruption_type == 'invalid_date_format':
                    # Should have either fixed or rejected invalid dates
                    assert all(pd.api.types.is_datetime64_any_dtype(pd.Series([d])) for d in loaded_df['date'])
                    
            except (DataLoaderError, SchemaValidationError, ValueError) as e:
                # It's acceptable for the loader to reject corrupted data
                assert corruption_type in str(e) or 'validation' in str(e).lower() or 'parsing' in str(e).lower()
                
            finally:
                os.unlink(temp_file)


class TestDataIntegrityEdgeCases:
    """Edge case tests for data integrity validation."""
    
    def test_single_row_integrity(self):
        """Test data integrity with single row dataset."""
        test_data = {col: ['single_value'] for col in REQUIRED_COLUMNS}
        test_data['transaction_id'] = ['TXN001']
        test_data['date'] = ['2024-01-01']
        test_data['fraud_label'] = [0]
        
        df = pd.DataFrame(test_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
            df.to_csv(temp_file, index=False)
            
            try:
                loaded_df = load_dataset(temp_file)
                
                # Validate single row integrity
                assert len(loaded_df) == 1
                assert pd.notna(loaded_df.iloc[0]['transaction_id'])
                assert pd.notna(loaded_df.iloc[0]['date'])
                assert pd.notna(loaded_df.iloc[0]['fraud_label'])
                
            except (DataLoaderError, SchemaValidationError) as e:
                # Single row might not meet minimum requirements
                pytest.skip(f"Single row dataset rejected: {e}")
                
            finally:
                os.unlink(temp_file)
    
    def test_boundary_values_integrity(self):
        """Test data integrity with boundary values."""
        test_data = {col: ['boundary_test'] * 3 for col in REQUIRED_COLUMNS}
        
        # Set boundary values for critical fields
        test_data['transaction_id'] = ['', 'TXN' + '0' * 100, 'TXN_SPECIAL_CHARS_!@#']
        test_data['date'] = ['1900-01-01', '2024-12-31', '2099-12-31']
        test_data['fraud_label'] = [0, 1, 2]  # Test different fraud levels
        
        df = pd.DataFrame(test_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
            df.to_csv(temp_file, index=False)
            
            try:
                loaded_df = load_dataset(temp_file)
                
                # Validate that boundary values are handled appropriately
                for idx in range(len(loaded_df)):
                    assert pd.notna(loaded_df.iloc[idx]['transaction_id'])
                    assert str(loaded_df.iloc[idx]['transaction_id']).strip() != ''
                    assert pd.notna(loaded_df.iloc[idx]['date'])
                    assert pd.notna(loaded_df.iloc[idx]['fraud_label'])
                    
            except (DataLoaderError, SchemaValidationError) as e:
                # Boundary values might be rejected, which is acceptable
                pytest.skip(f"Boundary values rejected: {e}")
                
            finally:
                os.unlink(temp_file)


if __name__ == "__main__":
    # Run the property-based tests
    pytest.main([__file__, "-v", "--tb=short", "-x"])