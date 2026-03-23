"""
Comprehensive Unit Tests for TRINETRA AI Feature Engineering Module

This module contains unit tests for the feature engineering functions in feature_engineering.py.
Tests cover all feature calculation functions, edge cases, and error handling scenarios.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import patch

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feature_engineering import (
    calculate_price_anomaly_score,
    calculate_route_risk_score,
    calculate_company_network_risk,
    calculate_port_congestion_score,
    calculate_shipment_duration_risk,
    calculate_volume_spike_score,
    engineer_features,
    validate_feature_inputs,
    handle_feature_errors
)


class TestCalculatePriceAnomalyScore:
    """Test cases for the calculate_price_anomaly_score() function."""
    
    def test_calculate_price_anomaly_score_success(self):
        """Test successful price anomaly score calculation."""
        df = pd.DataFrame({
            'price_deviation': [0.1, -0.2, 0.5, -0.3, 0.0]
        })
        
        result = calculate_price_anomaly_score(df)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 5
        assert result.iloc[0] == 0.1  # abs(0.1)
        assert result.iloc[1] == 0.2  # abs(-0.2)
        assert result.iloc[2] == 0.5  # abs(0.5)
        assert result.iloc[3] == 0.3  # abs(-0.3)
        assert result.iloc[4] == 0.0  # abs(0.0)
    
    def test_calculate_price_anomaly_score_missing_column(self):
        """Test price anomaly calculation with missing column."""
        df = pd.DataFrame({
            'other_column': [1, 2, 3]
        })
        
        with pytest.raises(KeyError, match="price_deviation"):
            calculate_price_anomaly_score(df)
    
    def test_calculate_price_anomaly_score_empty_dataframe(self):
        """Test price anomaly calculation with empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="empty"):
            calculate_price_anomaly_score(df)
    
    def test_calculate_price_anomaly_score_none_input(self):
        """Test price anomaly calculation with None input."""
        with pytest.raises(ValueError, match="None"):
            calculate_price_anomaly_score(None)
    
    def test_calculate_price_anomaly_score_with_nan(self):
        """Test price anomaly calculation with NaN values."""
        df = pd.DataFrame({
            'price_deviation': [0.1, np.nan, 0.5, np.nan, 0.0]
        })
        
        result = calculate_price_anomaly_score(df)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 5
        assert result.iloc[0] == 0.1
        assert pd.isna(result.iloc[1])  # NaN should remain NaN
        assert result.iloc[2] == 0.5
        assert pd.isna(result.iloc[3])
        assert result.iloc[4] == 0.0
    
    def test_calculate_price_anomaly_score_with_infinity(self):
        """Test price anomaly calculation with infinite values."""
        df = pd.DataFrame({
            'price_deviation': [0.1, float('inf'), -float('inf'), 0.5]
        })
        
        result = calculate_price_anomaly_score(df)
        
        assert isinstance(result, pd.Series)
        assert result.iloc[0] == 0.1
        assert result.iloc[1] == float('inf')
        assert result.iloc[2] == float('inf')  # abs(-inf) = inf
        assert result.iloc[3] == 0.5
    
    def test_calculate_price_anomaly_score_string_conversion(self):
        """Test price anomaly calculation with string values."""
        df = pd.DataFrame({
            'price_deviation': ['0.1', '-0.2', '0.5']
        })
        
        result = calculate_price_anomaly_score(df)
        
        assert isinstance(result, pd.Series)
        assert result.iloc[0] == 0.1
        assert result.iloc[1] == 0.2
        assert result.iloc[2] == 0.5


class TestCalculateRouteRiskScore:
    """Test cases for the calculate_route_risk_score() function."""
    
    def test_calculate_route_risk_score_success(self):
        """Test successful route risk score calculation."""