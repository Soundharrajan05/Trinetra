"""
Unit Tests for Feature Engineering Module - TRINETRA AI

This module contains comprehensive unit tests for the feature_engineering.py module,
testing all feature calculation functions with various scenarios and edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch

# Import the module under test
from backend.feature_engineering import (
    calculate_price_anomaly_score,
    calculate_route_risk_score,
    calculate_company_network_risk,
    calculate_port_congestion_score,
    calculate_shipment_duration_risk,
    calculate_volume_spike_score,
    engineer_features
)


class TestFeatureEngineering:
    """Test class for feature engineering functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'price_deviation': [0.1, -0.2, 0.5],
            'route_anomaly': [0, 1, 0],
            'company_risk_score': [0.3, 0.7, 0.1],
            'port_activity_index': [1.2, 2.5, 0.8],
            'shipment_duration_days': [10, 15, 5],
            'distance_km': [1000, 2000, 500],
            'cargo_volume': [100, 200, 50],
            'quantity': [10, 20, 5]
        })
    
    def test_calculate_price_anomaly_score_success(self, sample_data):
        """Test successful price anomaly score calculation."""
        result = calculate_price_anomaly_score(sample_data)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert result.iloc[0] == 0.1  # abs(0.1)
        assert result.iloc[1] == 0.2  # abs(-0.2)
        assert result.iloc[2] == 0.5  # abs(0.5)
    
    def test_calculate_price_anomaly_score_with_nan(self):
        """Test price anomaly score calculation with NaN values."""
        df = pd.DataFrame({
            'price_deviation': [0.1, np.nan, 0.3]
        })
        
        result = calculate_price_anomaly_score(df)
        
        assert len(result) == 3
        assert result.iloc[0] == 0.1
        assert result.iloc[1] == 0.0  # NaN should be filled with 0
        assert result.iloc[2] == 0.3
    
    def test_calculate_price_anomaly_score_missing_column(self):
        """Test price anomaly score calculation with missing column."""
        df = pd.DataFrame({'other_column': [1, 2, 3]})
        
        with pytest.raises(KeyError):
            calculate_price_anomaly_score(df)
    
    def test_calculate_price_anomaly_score_empty_dataframe(self):
        """Test price anomaly score calculation with empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            calculate_price_anomaly_score(df)
    
    def test_calculate_route_risk_score_success(self, sample_data):
        """Test successful route risk score calculation."""
        result = calculate_route_risk_score(sample_data)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert result.iloc[0] == 0
        assert result.iloc[1] == 1
        assert result.iloc[2] == 0
    
    def test_calculate_route_risk_score_with_nan(self):
        """Test route risk score calculation with NaN values."""
        df = pd.DataFrame({
            'route_anomaly': [1, np.nan, 0]
        })
        
        result = calculate_route_risk_score(df)
        
        assert len(result) == 3
        assert result.iloc[0] == 1
        assert result.iloc[1] == 0.0  # NaN should be filled with 0
        assert result.iloc[2] == 0
    
    def test_calculate_company_network_risk_success(self, sample_data):
        """Test successful company network risk calculation."""
        result = calculate_company_network_risk(sample_data)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert result.iloc[0] == 0.3
        assert result.iloc[1] == 0.7
        assert result.iloc[2] == 0.1
    
    def test_calculate_port_congestion_score_success(self, sample_data):
        """Test successful port congestion score calculation."""
        result = calculate_port_congestion_score(sample_data)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert result.iloc[0] == 1.2
        assert result.iloc[1] == 2.5
        assert result.iloc[2] == 0.8
    
    def test_calculate_port_congestion_score_with_nan(self):
        """Test port congestion score calculation with NaN values."""
        df = pd.DataFrame({
            'port_activity_index': [1.5, np.nan, 2.0]
        })
        
        result = calculate_port_congestion_score(df)
        
        assert len(result) == 3
        assert result.iloc[0] == 1.5
        assert result.iloc[1] == 1.0  # NaN should be filled with 1.0 (normal activity)
        assert result.iloc[2] == 2.0
    
    def test_calculate_shipment_duration_risk_success(self, sample_data):
        """Test successful shipment duration risk calculation."""
        result = calculate_shipment_duration_risk(sample_data)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert result.iloc[0] == 10 / 1000  # 10 days / 1000 km
        assert result.iloc[1] == 15 / 2000  # 15 days / 2000 km
        assert result.iloc[2] == 5 / 500    # 5 days / 500 km
    
    def test_calculate_shipment_duration_risk_zero_distance(self):
        """Test shipment duration risk calculation with zero distance."""
        df = pd.DataFrame({
            'shipment_duration_days': [10, 15],
            'distance_km': [0, 1000]  # Zero distance should be handled
        })
        
        result = calculate_shipment_duration_risk(df)
        
        assert len(result) == 2
        assert result.iloc[0] == 10 / 1  # Zero distance replaced with 1
        assert result.iloc[1] == 15 / 1000
    
    def test_calculate_shipment_duration_risk_missing_columns(self):
        """Test shipment duration risk calculation with missing columns."""
        df = pd.DataFrame({'other_column': [1, 2, 3]})
        
        with pytest.raises(KeyError):
            calculate_shipment_duration_risk(df)
    
    def test_calculate_volume_spike_score_success(self, sample_data):
        """Test successful volume spike score calculation."""
        result = calculate_volume_spike_score(sample_data)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert result.iloc[0] == 100 / 10  # 100 volume / 10 quantity
        assert result.iloc[1] == 200 / 20  # 200 volume / 20 quantity
        assert result.iloc[2] == 50 / 5    # 50 volume / 5 quantity
    
    def test_calculate_volume_spike_score_zero_quantity(self):
        """Test volume spike score calculation with zero quantity."""
        df = pd.DataFrame({
            'cargo_volume': [100, 200],
            'quantity': [0, 10]  # Zero quantity should be handled
        })
        
        result = calculate_volume_spike_score(df)
        
        assert len(result) == 2
        assert result.iloc[0] == 100 / 1  # Zero quantity replaced with 1
        assert result.iloc[1] == 200 / 10
    
    def test_engineer_features_success(self, sample_data):
        """Test successful feature engineering pipeline."""
        result_df = engineer_features(sample_data)
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == len(sample_data)
        
        # Check that all new features are added
        expected_features = [
            'price_anomaly_score',
            'route_risk_score',
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        
        for feature in expected_features:
            assert feature in result_df.columns
        
        # Check that original columns are preserved
        for col in sample_data.columns:
            assert col in result_df.columns
    
    def test_engineer_features_empty_dataframe(self):
        """Test feature engineering with empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            engineer_features(df)
    
    def test_engineer_features_none_input(self):
        """Test feature engineering with None input."""
        with pytest.raises(ValueError):
            engineer_features(None)


class TestFeatureEngineeringEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_all_functions_with_negative_values(self):
        """Test all feature functions with negative input values."""
        df = pd.DataFrame({
            'price_deviation': [-0.5, -0.3, -0.1],
            'route_anomaly': [0, 1, 0],  # Should be 0 or 1
            'company_risk_score': [0.1, 0.2, 0.3],  # Should be positive
            'port_activity_index': [0.5, 1.0, 1.5],  # Should be positive
            'shipment_duration_days': [5, 10, 15],  # Should be positive
            'distance_km': [500, 1000, 1500],  # Should be positive
            'cargo_volume': [50, 100, 150],  # Should be positive
            'quantity': [5, 10, 15]  # Should be positive
        })
        
        # All functions should handle negative price deviations correctly
        price_scores = calculate_price_anomaly_score(df)
        assert all(score >= 0 for score in price_scores)  # Absolute values
        
        # Other functions should work normally
        route_scores = calculate_route_risk_score(df)
        company_scores = calculate_company_network_risk(df)
        port_scores = calculate_port_congestion_score(df)
        duration_scores = calculate_shipment_duration_risk(df)
        volume_scores = calculate_volume_spike_score(df)
        
        assert len(route_scores) == 3
        assert len(company_scores) == 3
        assert len(port_scores) == 3
        assert len(duration_scores) == 3
        assert len(volume_scores) == 3
    
    def test_extreme_values(self):
        """Test feature calculations with extreme values."""
        df = pd.DataFrame({
            'price_deviation': [10.0, -10.0, 0.0],  # Extreme deviations
            'route_anomaly': [1, 0, 1],
            'company_risk_score': [1.0, 0.0, 0.5],  # Max and min risk
            'port_activity_index': [100.0, 0.1, 50.0],  # Extreme activity
            'shipment_duration_days': [365, 1, 30],  # Very long/short durations
            'distance_km': [50000, 1, 10000],  # Very long/short distances
            'cargo_volume': [1000000, 1, 5000],  # Very large/small volumes
            'quantity': [10000, 1, 100]  # Very large/small quantities
        })
        
        # Should handle extreme values without errors
        result_df = engineer_features(df)
        
        assert len(result_df) == 3
        assert not result_df.isnull().any().any()  # No NaN values should be introduced
    
    def test_mixed_data_types(self):
        """Test feature calculations with mixed data types."""
        df = pd.DataFrame({
            'price_deviation': ['0.1', '0.2', '0.3'],  # String numbers
            'route_anomaly': [0.0, 1.0, 0.0],  # Float instead of int
            'company_risk_score': [0.1, 0.2, 0.3],
            'port_activity_index': [1.1, 1.2, 1.3],
            'shipment_duration_days': [10.5, 15.7, 5.2],  # Float days
            'distance_km': [1000.0, 2000.0, 500.0],
            'cargo_volume': [100.0, 200.0, 50.0],
            'quantity': [10.0, 20.0, 5.0]  # Float quantities
        })
        
        # Convert string columns to numeric (pandas should handle this)
        df['price_deviation'] = pd.to_numeric(df['price_deviation'])
        
        result_df = engineer_features(df)
        
        assert len(result_df) == 3
        assert isinstance(result_df, pd.DataFrame)
    
    def test_large_dataset_performance(self):
        """Test feature engineering performance with large dataset."""
        # Create a larger dataset to test performance
        n_rows = 10000
        large_df = pd.DataFrame({
            'price_deviation': np.random.uniform(-1, 1, n_rows),
            'route_anomaly': np.random.choice([0, 1], n_rows),
            'company_risk_score': np.random.uniform(0, 1, n_rows),
            'port_activity_index': np.random.uniform(0.5, 3.0, n_rows),
            'shipment_duration_days': np.random.uniform(1, 30, n_rows),
            'distance_km': np.random.uniform(100, 20000, n_rows),
            'cargo_volume': np.random.uniform(10, 10000, n_rows),
            'quantity': np.random.uniform(1, 1000, n_rows)
        })
        
        import time
        start_time = time.time()
        result_df = engineer_features(large_df)
        end_time = time.time()
        
        # Should complete within reasonable time (less than 5 seconds)
        assert (end_time - start_time) < 5.0
        assert len(result_df) == n_rows
        assert len(result_df.columns) == len(large_df.columns) + 6  # 6 new features
    
    @patch('backend.feature_engineering.logger')
    def test_logging_functionality(self, mock_logger, sample_data):
        """Test that logging is working correctly."""
        engineer_features(sample_data)
        
        # Verify that logging calls were made
        assert mock_logger.info.called
        
        # Check specific log messages
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Starting feature engineering pipeline" in call for call in log_calls)
        assert any("Feature engineering completed successfully" in call for call in log_calls)
    
    def test_feature_value_ranges(self, sample_data):
        """Test that engineered features have reasonable value ranges."""
        result_df = engineer_features(sample_data)
        
        # Price anomaly score should be non-negative
        assert all(result_df['price_anomaly_score'] >= 0)
        
        # Route risk score should be 0 or 1
        assert all(score in [0, 1] for score in result_df['route_risk_score'])
        
        # Company network risk should be between 0 and 1
        assert all(0 <= score <= 1 for score in result_df['company_network_risk'])
        
        # Port congestion score should be positive
        assert all(result_df['port_congestion_score'] > 0)
        
        # Duration and volume scores should be positive
        assert all(result_df['shipment_duration_risk'] >= 0)
        assert all(result_df['volume_spike_score'] >= 0)
    
    def test_feature_consistency(self):
        """Test that feature calculations are consistent across multiple runs."""
        df = pd.DataFrame({
            'price_deviation': [0.1, 0.2, 0.3],
            'route_anomaly': [0, 1, 0],
            'company_risk_score': [0.1, 0.2, 0.3],
            'port_activity_index': [1.1, 1.2, 1.3],
            'shipment_duration_days': [10, 15, 5],
            'distance_km': [1000, 2000, 500],
            'cargo_volume': [100, 200, 50],
            'quantity': [10, 20, 5]
        })
        
        # Run feature engineering multiple times
        result1 = engineer_features(df)
        result2 = engineer_features(df)
        
        # Results should be identical
        pd.testing.assert_frame_equal(result1, result2)


if __name__ == "__main__":
    pytest.main([__file__])