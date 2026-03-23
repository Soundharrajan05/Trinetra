"""
Comprehensive Unit Tests for TRINETRA AI Data Loader Module

This module contains unit tests for the data loading functions in data_loader.py.
Tests cover CSV loading, schema validation, data quality checks, and error handling.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import (
    load_dataset,
    validate_schema,
    get_dataset_stats,
    handle_missing_values,
    DataLoaderError,
    SchemaValidationError,
    DataQualityError,
    REQUIRED_COLUMNS
)


class TestLoadDataset:
    """Test cases for the load_dataset() function."""
    
    def create_test_csv(self, data: dict, file_path: str) -> None:
        """Create a test CSV file with given data."""
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
    
    def create_valid_test_data(self, num_rows: int = 10) -> dict:
        """Create valid test data for CSV creation."""
        return {
            'transaction_id': [f'TXN{i:03d}' for i in range(num_rows)],
            'date': ['2024-01-01', '2024-01-02'] * (num_rows // 2),
            'product': ['Electronics', 'Textiles'] * (num_rows // 2),
            'commodity_category': ['Consumer', 'Industrial'] * (num_rows // 2),
            'quantity': [100, 200] * (num_rows // 2),
            'unit_price': [10.0, 20.0] * (num_rows // 2),
            'trade_value': [1000.0, 4000.0] * (num_rows // 2),
            'market_price': [9.0, 19.0] * (num_rows // 2),
            'price_deviation': [0.1, 0.05] * (num_rows // 2),
            'shipping_route': ['A-B', 'C-D'] * (num_rows // 2),
            'distance_km': [1000, 2000] * (num_rows // 2),
            'company_risk_score': [0.1, 0.2] * (num_rows // 2),
            'port_activity_index': [1.0, 1.5] * (num_rows // 2),
            'route_anomaly': [0, 1] * (num_rows // 2),
            'cargo_volume': [100.0, 200.0] * (num_rows // 2),
            'shipment_duration_days': [10, 20] * (num_rows // 2),
            'fraud_label': [0, 1] * (num_rows // 2)
        }
    
    def test_load_dataset_success(self):
        """Test successful dataset loading."""
        data = self.create_valid_test_data(20)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            self.create_test_csv(data, temp_path)
            
            df = load_dataset(temp_path)
            
            # Check basic properties
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 20
            assert 'transaction_id' in df.columns
            assert 'date' in df.columns
            
            # Check date parsing
            assert pd.api.types.is_datetime64_any_dtype(df['date'])
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_dataset_file_not_found(self):
        """Test loading with non-existent file."""
        with pytest.raises(DataLoaderError, match="File not found"):
            load_dataset("nonexistent_file.csv")
    
    def test_load_dataset_empty_file(self):
        """Test loading empty CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            f.write("")  # Empty file
        
        try:
            with pytest.raises(DataLoaderError, match="empty or invalid"):
                load_dataset(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_invalid_csv(self):
        """Test loading invalid CSV format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            f.write("invalid,csv,format\nwith,missing,quotes\"and\nbroken,structure")
        
        try:
            with pytest.raises(DataLoaderError):
                load_dataset(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_missing_required_columns(self):
        """Test loading CSV with missing required columns."""
        data = {
            'transaction_id': ['TXN001', 'TXN002'],
            'date': ['2024-01-01', '2024-01-02']
            # Missing other required columns
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            self.create_test_csv(data, temp_path)
            
            with pytest.raises(SchemaValidationError, match="Missing required columns"):
                load_dataset(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_with_missing_values(self):
        """Test loading CSV with missing values."""
        data = self.create_valid_test_data(10)
        # Introduce missing values
        data['quantity'][2] = None
        data['unit_price'][3] = np.nan
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            self.create_test_csv(data, temp_path)
            
            df = load_dataset(temp_path)
            
            # Should handle missing values
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 10
            
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_with_invalid_dates(self):
        """Test loading CSV with invalid date formats."""
        data = self.create_valid_test_data(5)
        data['date'] = ['2024-01-01', 'invalid_date', '2024-01-03', '', '2024-01-05']
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            self.create_test_csv(data, temp_path)
            
            df = load_dataset(temp_path)
            
            # Should handle invalid dates
            assert isinstance(df, pd.DataFrame)
            assert 'date' in df.columns
            
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_large_file(self):
        """Test loading large CSV file."""
        data = self.create_valid_test_data(1000)  # Large dataset
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            self.create_test_csv(data, temp_path)
            
            df = load_dataset(temp_path)
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1000
            
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_custom_encoding(self):
        """Test loading CSV with different encodings."""
        data = self.create_valid_test_data(5)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            temp_path = f.name
        
        try:
            self.create_test_csv(data, temp_path)
            
            df = load_dataset(temp_path)
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 5
            
        finally:
            os.unlink(temp_path)


class TestValidateSchema:
    """Test cases for the validate_schema() function."""
    
    def create_valid_dataframe(self) -> pd.DataFrame:
        """Create a valid DataFrame for testing."""
        data = {
            'transaction_id': ['TXN001', 'TXN002'],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02']),
            'product': ['A', 'B'],
            'commodity_category': ['C', 'D'],
            'quantity': [100, 200],
            'unit_price': [10.0, 20.0],
            'trade_value': [1000.0, 4000.0],
            'market_price': [9.0, 19.0],
            'price_deviation': [0.1, 0.05],
            'shipping_route': ['A-B', 'C-D'],
            'distance_km': [1000, 2000],
            'company_risk_score': [0.1, 0.2],
            'port_activity_index': [1.0, 1.5],
            'route_anomaly': [0, 1],
            'cargo_volume': [100.0, 200.0],
            'shipment_duration_days': [10, 20],
            'fraud_label': [0, 1]
        }
        return pd.DataFrame(data)
    
    def test_validate_schema_success(self):
        """Test successful schema validation."""
        df = self.create_valid_dataframe()
        
        result = validate_schema(df)
        
        assert result is True
    
    def test_validate_schema_missing_columns(self):
        """Test schema validation with missing columns."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'date': ['2024-01-01']
            # Missing other required columns
        })
        
        with pytest.raises(SchemaValidationError, match="Missing required columns"):
            validate_schema(df)
    
    def test_validate_schema_empty_dataframe(self):
        """Test schema validation with empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(SchemaValidationError, match="empty"):
            validate_schema(df)
    
    def test_validate_schema_none_input(self):
        """Test schema validation with None input."""
        with pytest.raises(SchemaValidationError, match="None"):
            validate_schema(None)
    
    def test_validate_schema_extra_columns(self):
        """Test schema validation with extra columns (should pass)."""
        df = self.create_valid_dataframe()
        df['extra_column'] = [1, 2]
        
        result = validate_schema(df)
        
        assert result is True
    
    def test_validate_schema_wrong_data_types(self):
        """Test schema validation with wrong data types."""
        df = self.create_valid_dataframe()
        df['quantity'] = ['invalid', 'data']  # Should be numeric
        
        # Should still pass basic schema validation (type checking is separate)
        result = validate_schema(df)
        assert result is True


class TestGetDatasetStats:
    """Test cases for the get_dataset_stats() function."""
    
    def create_test_dataframe(self) -> pd.DataFrame:
        """Create test DataFrame with various data patterns."""
        return pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003', 'TXN004'],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04']),
            'product': ['A', 'B', 'A', 'C'],
            'quantity': [100, 200, np.nan, 400],
            'unit_price': [10.0, 20.0, 30.0, np.nan],
            'fraud_label': [0, 1, 0, 1]
        })
    
    def test_get_dataset_stats_success(self):
        """Test successful dataset statistics calculation."""
        df = self.create_test_dataframe()
        
        stats = get_dataset_stats(df)
        
        assert isinstance(stats, dict)
        assert stats['total_rows'] == 4
        assert stats['total_columns'] == 6
        assert 'missing_values' in stats
        assert 'data_types' in stats
        assert 'memory_usage_mb' in stats
    
    def test_get_dataset_stats_empty_dataframe(self):
        """Test statistics with empty DataFrame."""
        df = pd.DataFrame()
        
        stats = get_dataset_stats(df)
        
        assert stats['total_rows'] == 0
        assert stats['total_columns'] == 0
    
    def test_get_dataset_stats_missing_values(self):
        """Test statistics calculation with missing values."""
        df = self.create_test_dataframe()
        
        stats = get_dataset_stats(df)
        
        assert 'missing_values' in stats
        assert stats['missing_values']['quantity'] == 1
        assert stats['missing_values']['unit_price'] == 1
    
    def test_get_dataset_stats_data_types(self):
        """Test data type reporting in statistics."""
        df = self.create_test_dataframe()
        
        stats = get_dataset_stats(df)
        
        assert 'data_types' in stats
        assert 'object' in str(stats['data_types']['product'])
        assert 'float64' in str(stats['data_types']['quantity'])
    
    def test_get_dataset_stats_none_input(self):
        """Test statistics with None input."""
        with pytest.raises(ValueError, match="DataFrame cannot be None"):
            get_dataset_stats(None)


class TestHandleMissingValues:
    """Test cases for the handle_missing_values() function."""
    
    def create_dataframe_with_missing(self) -> pd.DataFrame:
        """Create DataFrame with missing values."""
        return pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'quantity': [100, np.nan, 300],
            'unit_price': [10.0, 20.0, np.nan],
            'product': ['A', None, 'C'],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
    
    def test_handle_missing_values_forward_fill(self):
        """Test missing value handling with forward fill strategy."""
        df = self.create_dataframe_with_missing()
        
        result_df = handle_missing_values(df, strategy='forward_fill')
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 3
        # Check that missing values were handled
        assert not result_df['quantity'].isna().any()
    
    def test_handle_missing_values_mean_imputation(self):
        """Test missing value handling with mean imputation."""
        df = self.create_dataframe_with_missing()
        
        result_df = handle_missing_values(df, strategy='mean')
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 3
        # Numeric columns should have no missing values
        assert not result_df['quantity'].isna().any()
        assert not result_df['unit_price'].isna().any()
    
    def test_handle_missing_values_drop_rows(self):
        """Test missing value handling by dropping rows."""
        df = self.create_dataframe_with_missing()
        
        result_df = handle_missing_values(df, strategy='drop')
        
        assert isinstance(result_df, pd.DataFrame)
        # Should have fewer rows after dropping
        assert len(result_df) < 3
    
    def test_handle_missing_values_invalid_strategy(self):
        """Test missing value handling with invalid strategy."""
        df = self.create_dataframe_with_missing()
        
        with pytest.raises(ValueError, match="Invalid strategy"):
            handle_missing_values(df, strategy='invalid_strategy')
    
    def test_handle_missing_values_empty_dataframe(self):
        """Test missing value handling with empty DataFrame."""
        df = pd.DataFrame()
        
        result_df = handle_missing_values(df)
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 0


class TestParseDateColumns:
    """Test cases for the parse_date_columns() function."""
    
    def test_parse_date_columns_success(self):
        """Test successful date column parsing."""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'other_column': [1, 2, 3]
        })
        
        result_df = parse_date_columns(df)
        
        assert isinstance(result_df, pd.DataFrame)
        assert pd.api.types.is_datetime64_any_dtype(result_df['date'])
    
    def test_parse_date_columns_invalid_dates(self):
        """Test date parsing with invalid date strings."""
        df = pd.DataFrame({
            'date': ['2024-01-01', 'invalid_date', '2024-01-03'],
            'other_column': [1, 2, 3]
        })
        
        result_df = parse_date_columns(df)
        
        assert isinstance(result_df, pd.DataFrame)
        # Should handle invalid dates gracefully
        assert 'date' in result_df.columns
    
    def test_parse_date_columns_missing_date_column(self):
        """Test date parsing when date column is missing."""
        df = pd.DataFrame({
            'other_column': [1, 2, 3]
        })
        
        result_df = parse_date_columns(df)
        
        # Should return DataFrame unchanged
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df.columns) == 1
    
    def test_parse_date_columns_already_datetime(self):
        """Test date parsing when column is already datetime."""
        df = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
            'other_column': [1, 2, 3]
        })
        
        result_df = parse_date_columns(df)
        
        assert isinstance(result_df, pd.DataFrame)
        assert pd.api.types.is_datetime64_any_dtype(result_df['date'])


class TestCheckDataQuality:
    """Test cases for the check_data_quality() function."""
    
    def create_quality_test_dataframe(self) -> pd.DataFrame:
        """Create DataFrame for data quality testing."""
        return pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN001', 'TXN004'],  # Duplicate
            'quantity': [100, -50, 300, 0],  # Negative value
            'unit_price': [10.0, 20.0, 30.0, 40.0],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'])
        })
    
    def test_check_data_quality_success(self):
        """Test data quality checking."""
        df = self.create_quality_test_dataframe()
        
        quality_report = check_data_quality(df)
        
        assert isinstance(quality_report, dict)
        assert 'duplicate_transactions' in quality_report
        assert 'negative_values' in quality_report
        assert 'data_quality_score' in quality_report
    
    def test_check_data_quality_duplicates(self):
        """Test duplicate detection in data quality check."""
        df = self.create_quality_test_dataframe()
        
        quality_report = check_data_quality(df)
        
        assert quality_report['duplicate_transactions'] > 0
    
    def test_check_data_quality_negative_values(self):
        """Test negative value detection."""
        df = self.create_quality_test_dataframe()
        
        quality_report = check_data_quality(df)
        
        assert 'negative_values' in quality_report
    
    def test_check_data_quality_empty_dataframe(self):
        """Test data quality check with empty DataFrame."""
        df = pd.DataFrame()
        
        quality_report = check_data_quality(df)
        
        assert isinstance(quality_report, dict)
        assert quality_report['data_quality_score'] == 0.0


class TestErrorHandling:
    """Test cases for error handling and custom exceptions."""
    
    def test_data_loader_error(self):
        """Test DataLoaderError exception."""
        with pytest.raises(DataLoaderError):
            raise DataLoaderError("Test error message")
    
    def test_schema_validation_error(self):
        """Test SchemaValidationError exception."""
        with pytest.raises(SchemaValidationError):
            raise SchemaValidationError("Schema validation failed")
    
    def test_data_quality_error(self):
        """Test DataQualityError exception."""
        with pytest.raises(DataQualityError):
            raise DataQualityError("Data quality check failed")


class TestIntegration:
    """Integration tests for data loader functionality."""
    
    def create_complete_test_dataset(self) -> dict:
        """Create a complete test dataset with all required columns."""
        return {
            'transaction_id': [f'TXN{i:03d}' for i in range(50)],
            'date': ['2024-01-01', '2024-01-02'] * 25,
            'product': ['Electronics', 'Textiles'] * 25,
            'commodity_category': ['Consumer', 'Industrial'] * 25,
            'quantity': [100, 200] * 25,
            'unit_price': [10.0, 20.0] * 25,
            'trade_value': [1000.0, 4000.0] * 25,
            'market_price': [9.0, 19.0] * 25,
            'price_deviation': [0.1, 0.05] * 25,
            'shipping_route': ['A-B', 'C-D'] * 25,
            'distance_km': [1000, 2000] * 25,
            'company_risk_score': [0.1, 0.2] * 25,
            'port_activity_index': [1.0, 1.5] * 25,
            'route_anomaly': [0, 1] * 25,
            'cargo_volume': [100.0, 200.0] * 25,
            'shipment_duration_days': [10, 20] * 25,
            'fraud_label': [0, 1] * 25
        }
    
    def test_complete_data_loading_pipeline(self):
        """Test complete data loading pipeline."""
        data = self.create_complete_test_dataset()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            # Create CSV file
            df_original = pd.DataFrame(data)
            df_original.to_csv(temp_path, index=False)
            
            # Load dataset
            df = load_dataset(temp_path)
            
            # Validate schema
            assert validate_schema(df) is True
            
            # Get statistics
            stats = get_dataset_stats(df)
            assert stats['total_rows'] == 50
            
            # Check data quality
            quality_report = check_data_quality(df)
            assert isinstance(quality_report, dict)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_data_loading_with_quality_issues(self):
        """Test data loading pipeline with data quality issues."""
        data = self.create_complete_test_dataset()
        
        # Introduce quality issues
        data['transaction_id'][5] = data['transaction_id'][0]  # Duplicate
        data['quantity'][10] = -100  # Negative value
        data['unit_price'][15] = None  # Missing value
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            # Create CSV file
            df_original = pd.DataFrame(data)
            df_original.to_csv(temp_path, index=False)
            
            # Load dataset (should handle issues gracefully)
            df = load_dataset(temp_path)
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
            
            # Check data quality (should detect issues)
            quality_report = check_data_quality(df)
            assert quality_report['duplicate_transactions'] > 0
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])