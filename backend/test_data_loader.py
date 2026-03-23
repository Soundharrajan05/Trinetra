"""
Unit Tests for Data Loader Module - TRINETRA AI

This module contains comprehensive unit tests for the data_loader.py module,
testing all functions with various scenarios including edge cases and error conditions.
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the module under test
from backend.data_loader import (
    load_dataset, validate_schema, handle_missing_values, get_dataset_stats,
    validate_dataset_health, DataLoaderError, SchemaValidationError, DataQualityError
)


class TestDataLoader:
    """Test class for data loader functionality."""
    
    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data for testing."""
        return {
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'product': ['Electronics', 'Textiles', 'Machinery'],
            'commodity_category': ['Consumer', 'Industrial', 'Capital'],
            'quantity': [100, 200, 150],
            'unit_price': [10.50, 25.00, 500.00],
            'trade_value': [1050.00, 5000.00, 75000.00],
            'market_price': [10.00, 24.00, 480.00],
            'price_deviation': [0.05, 0.04, 0.04],
            'exporter_company': ['CompanyA', 'CompanyB', 'CompanyC'],
            'exporter_country': ['China', 'India', 'Germany'],
            'importer_company': ['ImporterA', 'ImporterB', 'ImporterC'],
            'importer_country': ['USA', 'UK', 'France'],
            'shipping_route': ['Shanghai-LA', 'Mumbai-London', 'Hamburg-Paris'],
            'distance_km': [11000, 8000, 1000],
            'company_risk_score': [0.2, 0.3, 0.1],
            'route_anomaly': [0, 1, 0],
            'fraud_label': [0, 1, 0]
        }
    
    @pytest.fixture
    def sample_csv_file(self, sample_csv_data, tmp_path):
        """Create a temporary CSV file for testing."""
        df = pd.DataFrame(sample_csv_data)
        csv_file = tmp_path / "test_data.csv"
        df.to_csv(csv_file, index=False)
        return str(csv_file)
    
    @pytest.fixture
    def invalid_csv_file(self, tmp_path):
        """Create an invalid CSV file for testing."""
        csv_file = tmp_path / "invalid_data.csv"
        with open(csv_file, 'w') as f:
            f.write("invalid,csv,data\n1,2\n3,4,5,6\n")  # Inconsistent columns
        return str(csv_file)
    
    def test_load_dataset_success(self, sample_csv_file):
        """Test successful dataset loading."""
        df = load_dataset(sample_csv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'transaction_id' in df.columns
        assert 'date' in df.columns
        assert pd.api.types.is_datetime64_any_dtype(df['date'])
    
    def test_load_dataset_file_not_found(self):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_dataset("non_existent_file.csv")
    
    def test_load_dataset_empty_file(self, tmp_path):
        """Test loading empty CSV file."""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")
        
        with pytest.raises(FileNotFoundError, match="File is empty"):
            load_dataset(str(empty_file))
    
    def test_load_dataset_invalid_csv(self, invalid_csv_file):
        """Test loading invalid CSV file."""
        # Should handle parsing errors gracefully
        df = load_dataset(invalid_csv_file)
        assert isinstance(df, pd.DataFrame)
    
    def test_load_dataset_missing_columns(self, tmp_path):
        """Test loading CSV with missing required columns."""
        # Create CSV with only some required columns
        minimal_data = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'date': ['2024-01-01']
        })
        csv_file = tmp_path / "minimal.csv"
        minimal_data.to_csv(csv_file, index=False)
        
        with pytest.raises(SchemaValidationError):
            load_dataset(str(csv_file))
    
    def test_validate_schema_success(self, sample_csv_data):
        """Test successful schema validation."""
        df = pd.DataFrame(sample_csv_data)
        result = validate_schema(df)
        assert result is True
    
    def test_validate_schema_missing_columns(self):
        """Test schema validation with missing columns."""
        df = pd.DataFrame({'transaction_id': ['TXN001']})
        result = validate_schema(df)
        assert result is False
    
    def test_handle_missing_values_success(self, sample_csv_data):
        """Test successful missing value handling."""
        df = pd.DataFrame(sample_csv_data)
        # Introduce some missing values
        df.loc[0, 'unit_price'] = np.nan
        df.loc[1, 'quantity'] = np.nan
        
        result_df = handle_missing_values(df)
        
        assert not result_df['unit_price'].isna().any()
        assert not result_df['quantity'].isna().any()
        assert len(result_df) == len(df)
    
    def test_handle_missing_values_all_missing(self):
        """Test handling when entire column is missing."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'unit_price': [np.nan, np.nan],
            'quantity': [100, 200]
        })
        
        result_df = handle_missing_values(df)
        
        # Should fill with appropriate defaults
        assert not result_df['unit_price'].isna().any()
    
    def test_handle_missing_values_empty_dataframe(self):
        """Test handling missing values with empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(DataQualityError):
            handle_missing_values(df)
    
    def test_get_dataset_stats_success(self, sample_csv_data):
        """Test successful dataset statistics calculation."""
        df = pd.DataFrame(sample_csv_data)
        stats = get_dataset_stats(df)
        
        assert isinstance(stats, dict)
        assert 'basic_info' in stats
        assert 'data_quality' in stats
        assert stats['basic_info']['total_rows'] == 3
        assert stats['basic_info']['total_columns'] == len(df.columns)
    
    def test_get_dataset_stats_with_missing_data(self, sample_csv_data):
        """Test dataset statistics with missing data."""
        df = pd.DataFrame(sample_csv_data)
        df.loc[0, 'unit_price'] = np.nan
        df.loc[1, 'quantity'] = np.nan
        
        stats = get_dataset_stats(df)
        
        assert stats['data_quality']['missing_values'] == 2
        assert stats['data_quality']['missing_percentage'] > 0
    
    def test_get_dataset_stats_empty_dataframe(self):
        """Test dataset statistics with empty DataFrame."""
        df = pd.DataFrame()
        stats = get_dataset_stats(df)
        
        assert 'error' in stats
        assert stats['basic_info']['total_rows'] == 0
    
    def test_validate_dataset_health_excellent(self, sample_csv_data):
        """Test dataset health validation with excellent data."""
        df = pd.DataFrame(sample_csv_data)
        health = validate_dataset_health(df)
        
        assert health['overall_health'] in ['EXCELLENT', 'GOOD']
        assert len(health['issues']) == 0
    
    def test_validate_dataset_health_poor(self):
        """Test dataset health validation with poor data."""
        # Create DataFrame with many issues
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN001'],  # Duplicates
            'unit_price': [np.nan, np.nan],  # All missing
            'quantity': [100, 200]
        })
        
        health = validate_dataset_health(df)
        
        assert health['overall_health'] in ['POOR', 'FAIR']
        assert len(health['issues']) > 0 or len(health['warnings']) > 0
    
    def test_validate_dataset_health_empty(self):
        """Test dataset health validation with empty DataFrame."""
        df = pd.DataFrame()
        health = validate_dataset_health(df)
        
        assert health['overall_health'] == 'POOR'
        assert 'Dataset is empty' in health['issues']
    
    @patch('backend.data_loader.pd.read_csv')
    def test_load_dataset_encoding_fallback(self, mock_read_csv, tmp_path):
        """Test CSV loading with encoding fallback."""
        # Mock UTF-8 failure, then success with latin-1
        mock_read_csv.side_effect = [
            UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte'),
            pd.DataFrame({'transaction_id': ['TXN001'], 'date': ['2024-01-01']})
        ]
        
        csv_file = tmp_path / "encoded.csv"
        csv_file.write_text("transaction_id,date\nTXN001,2024-01-01")
        
        # Should not raise exception due to fallback
        with pytest.raises(SchemaValidationError):  # Will fail schema validation
            load_dataset(str(csv_file))
    
    def test_load_dataset_with_date_parsing(self, tmp_path):
        """Test CSV loading with various date formats."""
        data = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'date': ['2024-01-01', '01/02/2024'],
            'product': ['A', 'B'],
            'commodity_category': ['C', 'D'],
            'quantity': [1, 2],
            'unit_price': [10, 20],
            'trade_value': [10, 40],
            'market_price': [9, 19],
            'price_deviation': [0.1, 0.05],
            'exporter_company': ['E1', 'E2'],
            'exporter_country': ['C1', 'C2'],
            'importer_company': ['I1', 'I2'],
            'importer_country': ['IC1', 'IC2'],
            'shipping_route': ['R1', 'R2'],
            'distance_km': [1000, 2000],
            'company_risk_score': [0.1, 0.2],
            'route_anomaly': [0, 1],
            'fraud_label': [0, 1]
        })
        
        csv_file = tmp_path / "dates.csv"
        data.to_csv(csv_file, index=False)
        
        df = load_dataset(str(csv_file))
        assert pd.api.types.is_datetime64_any_dtype(df['date'])
    
    def test_error_handling_with_corrupted_data(self, tmp_path):
        """Test error handling with corrupted CSV data."""
        # Create a file with mixed data types in numeric columns
        corrupted_file = tmp_path / "corrupted.csv"
        with open(corrupted_file, 'w') as f:
            f.write("transaction_id,quantity,unit_price\n")
            f.write("TXN001,100,10.50\n")
            f.write("TXN002,invalid,not_a_number\n")
        
        # Should handle gracefully and convert invalid values
        df = load_dataset(str(corrupted_file))
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2


class TestDataLoaderEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_load_dataset_permission_denied(self, tmp_path):
        """Test loading file with permission issues."""
        csv_file = tmp_path / "no_permission.csv"
        csv_file.write_text("data")
        
        # Mock permission error
        with patch('os.access', return_value=False):
            with pytest.raises(FileNotFoundError):
                load_dataset(str(csv_file))
    
    def test_load_dataset_very_large_file(self, tmp_path):
        """Test loading very large file (memory considerations)."""
        # Create a larger dataset
        large_data = {
            'transaction_id': [f'TXN{i:06d}' for i in range(1000)],
            'date': ['2024-01-01'] * 1000,
            'product': ['Product'] * 1000,
            'commodity_category': ['Category'] * 1000,
            'quantity': [100] * 1000,
            'unit_price': [10.0] * 1000,
            'trade_value': [1000.0] * 1000,
            'market_price': [9.5] * 1000,
            'price_deviation': [0.05] * 1000,
            'exporter_company': ['Exporter'] * 1000,
            'exporter_country': ['Country'] * 1000,
            'importer_company': ['Importer'] * 1000,
            'importer_country': ['Country2'] * 1000,
            'shipping_route': ['Route'] * 1000,
            'distance_km': [5000] * 1000,
            'company_risk_score': [0.1] * 1000,
            'route_anomaly': [0] * 1000,
            'fraud_label': [0] * 1000
        }
        
        df = pd.DataFrame(large_data)
        csv_file = tmp_path / "large.csv"
        df.to_csv(csv_file, index=False)
        
        result_df = load_dataset(str(csv_file))
        assert len(result_df) == 1000
        assert isinstance(result_df, pd.DataFrame)
    
    def test_handle_missing_values_critical_columns(self):
        """Test handling missing values in critical columns."""
        df = pd.DataFrame({
            'transaction_id': [np.nan, 'TXN002'],  # Missing critical field
            'date': ['2024-01-01', np.nan],  # Missing critical field
            'quantity': [100, 200]
        })
        
        result_df = handle_missing_values(df)
        
        # Should generate transaction IDs for missing ones
        assert not result_df['transaction_id'].isna().any()
    
    def test_schema_validation_with_extra_columns(self, sample_csv_data):
        """Test schema validation with extra columns."""
        df = pd.DataFrame(sample_csv_data)
        df['extra_column'] = ['extra1', 'extra2', 'extra3']
        
        # Should pass validation (extra columns are allowed)
        result = validate_schema(df)
        assert result is True
    
    def test_data_quality_thresholds(self):
        """Test data quality threshold enforcement."""
        # Create DataFrame that violates quality thresholds
        df = pd.DataFrame({
            'transaction_id': ['TXN001'] * 50,  # Many duplicates
            'date': ['2024-01-01'] * 50,
            'product': [np.nan] * 50,  # All missing
            'commodity_category': ['Cat'] * 50,
            'quantity': [100] * 50,
            'unit_price': [10] * 50,
            'trade_value': [1000] * 50,
            'market_price': [9] * 50,
            'price_deviation': [0.1] * 50,
            'exporter_company': ['Exp'] * 50,
            'exporter_country': ['Country'] * 50,
            'importer_company': ['Imp'] * 50,
            'importer_country': ['Country2'] * 50,
            'shipping_route': ['Route'] * 50,
            'distance_km': [1000] * 50,
            'company_risk_score': [0.1] * 50,
            'route_anomaly': [0] * 50,
            'fraud_label': [0] * 50
        })
        
        health = validate_dataset_health(df)
        
        # Should detect quality issues
        assert len(health['warnings']) > 0 or len(health['issues']) > 0


if __name__ == "__main__":
    pytest.main([__file__])