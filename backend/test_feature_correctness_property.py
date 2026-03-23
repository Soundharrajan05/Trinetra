"""
Property-Based Test for Feature Engineering Correctness (CP-3)
TRINETRA AI - Trade Fraud Intelligence System

**Validates: Requirements CP-3**

This module implements property-based testing for feature engineering correctness validation.
Tests ensure that engineered features are mathematically correct and within expected ranges.

Property: Engineered features must be mathematically correct and within expected ranges
Test Strategy: Property-based test with known input values verifying feature calculations
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from hypothesis import given, strategies as st, settings, assume, example
from hypothesis.extra.pandas import data_frames, columns
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Tuple
import math

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feature_engineering import (
    calculate_price_anomaly_score,
    calculate_route_risk_score,
    calculate_company_network_risk,
    calculate_port_congestion_score,
    calculate_shipment_duration_risk,
    calculate_volume_spike_score,
    engineer_features
)


class TestFeatureCorrectnessProperty:
    """Property-based tests for feature engineering correctness (CP-3)."""
    
    @given(
        price_deviations=st.lists(
            st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=50, deadline=10000)
    @example(price_deviations=[0.0, 0.5, -0.5, 1.0, -1.0])
    @example(price_deviations=[0.1, -0.1, 0.05, -0.05])
    def test_price_anomaly_score_mathematical_correctness(self, price_deviations: List[float]):
        """
        **Validates: Requirements CP-3**
        
        Property: price_anomaly_score = abs(price_deviation) must be mathematically correct
        
        Test Strategy: Generate various price deviations and verify absolute value calculation
        """
        # Create test DataFrame
        df = pd.DataFrame({'price_deviation': price_deviations})
        
        # Calculate feature
        result = calculate_price_anomaly_score(df)
        
        # Verify mathematical correctness
        for i, price_dev in enumerate(price_deviations):
            expected = abs(price_dev)
            actual = result.iloc[i]
            
            # Allow for floating point precision issues
            assert abs(actual - expected) < 1e-10, f"Price anomaly calculation incorrect: expected {expected}, got {actual}"
            
            # Verify non-negative result
            assert actual >= 0, f"Price anomaly score must be non-negative, got {actual}"
            
            # Verify range is reasonable (should match input range)
            assert actual <= 2.0, f"Price anomaly score out of expected range: {actual}"
    
    @given(
        route_anomalies=st.lists(
            st.sampled_from([0, 1, 0.0, 1.0]),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=30, deadline=10000)
    @example(route_anomalies=[0, 1, 0, 1])
    @example(route_anomalies=[0.0, 1.0])
    def test_route_risk_score_mathematical_correctness(self, route_anomalies: List[float]):
        """
        **Validates: Requirements CP-3**
        
        Property: route_risk_score = route_anomaly must be mathematically correct
        
        Test Strategy: Generate route anomaly values and verify direct assignment
        """
        # Create test DataFrame
        df = pd.DataFrame({'route_anomaly': route_anomalies})
        
        # Calculate feature
        result = calculate_route_risk_score(df)
        
        # Verify mathematical correctness (direct assignment)
        for i, route_anomaly in enumerate(route_anomalies):
            expected = route_anomaly
            actual = result.iloc[i]
            
            assert actual == expected, f"Route risk score calculation incorrect: expected {expected}, got {actual}"
            
            # Verify values are in expected range (0 or 1)
            assert actual in [0, 1, 0.0, 1.0], f"Route risk score out of expected range: {actual}"
    
    @given(
        company_risk_scores=st.lists(
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=30, deadline=10000)
    @example(company_risk_scores=[0.0, 0.5, 1.0])
    @example(company_risk_scores=[0.1, 0.3, 0.7, 0.9])
    def test_company_network_risk_mathematical_correctness(self, company_risk_scores: List[float]):
        """
        **Validates: Requirements CP-3**
        
        Property: company_network_risk = company_risk_score must be mathematically correct
        
        Test Strategy: Generate company risk scores and verify direct assignment
        """
        # Create test DataFrame
        df = pd.DataFrame({'company_risk_score': company_risk_scores})
        
        # Calculate feature
        result = calculate_company_network_risk(df)
        
        # Verify mathematical correctness (direct assignment)
        for i, company_risk in enumerate(company_risk_scores):
            expected = company_risk
            actual = result.iloc[i]
            
            assert abs(actual - expected) < 1e-10, f"Company network risk calculation incorrect: expected {expected}, got {actual}"
            
            # Verify values are in expected range (0.0 to 1.0)
            assert 0.0 <= actual <= 1.0, f"Company network risk out of expected range: {actual}"
    
    @given(
        port_activity_indices=st.lists(
            st.floats(min_value=0.1, max_value=3.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=30, deadline=10000)
    @example(port_activity_indices=[1.0, 1.5, 2.0])
    @example(port_activity_indices=[0.5, 1.16, 1.58, 1.6])
    def test_port_congestion_score_mathematical_correctness(self, port_activity_indices: List[float]):
        """
        **Validates: Requirements CP-3**
        
        Property: port_congestion_score = port_activity_index must be mathematically correct
        
        Test Strategy: Generate port activity indices and verify direct assignment
        """
        # Create test DataFrame
        df = pd.DataFrame({'port_activity_index': port_activity_indices})
        
        # Calculate feature
        result = calculate_port_congestion_score(df)
        
        # Verify mathematical correctness (direct assignment)
        for i, port_activity in enumerate(port_activity_indices):
            expected = port_activity
            actual = result.iloc[i]
            
            assert abs(actual - expected) < 1e-10, f"Port congestion score calculation incorrect: expected {expected}, got {actual}"
            
            # Verify values are in reasonable range
            assert 0.0 <= actual <= 5.0, f"Port congestion score out of reasonable range: {actual}"
    
    @given(
        shipment_data=st.lists(
            st.tuples(
                st.floats(min_value=1, max_value=365, allow_nan=False, allow_infinity=False),  # duration_days
                st.floats(min_value=100, max_value=20000, allow_nan=False, allow_infinity=False)  # distance_km
            ),
            min_size=1,
            max_size=50
        )
    )
    @settings(max_examples=40, deadline=10000)
    @example(shipment_data=[(21, 5600), (16, 7800), (14, 7800), (20, 7800)])
    @example(shipment_data=[(1, 100), (365, 20000)])  # Edge cases
    def test_shipment_duration_risk_mathematical_correctness(self, shipment_data: List[Tuple[float, float]]):
        """
        **Validates: Requirements CP-3**
        
        Property: shipment_duration_risk = shipment_duration_days / distance_km must be mathematically correct
        
        Test Strategy: Generate shipment duration and distance pairs and verify division calculation
        """
        # Create test DataFrame
        durations, distances = zip(*shipment_data)
        df = pd.DataFrame({
            'shipment_duration_days': durations,
            'distance_km': distances
        })
        
        # Calculate feature
        result = calculate_shipment_duration_risk(df)
        
        # Verify mathematical correctness
        for i, (duration, distance) in enumerate(shipment_data):
            expected = duration / distance
            actual = result.iloc[i]
            
            # Allow for floating point precision issues
            assert abs(actual - expected) < 1e-10, f"Shipment duration risk calculation incorrect: expected {expected}, got {actual}"
            
            # Verify result is positive
            assert actual > 0, f"Shipment duration risk must be positive, got {actual}"
            
            # Verify reasonable range (duration/distance should be small for normal shipments)
            assert actual <= 10.0, f"Shipment duration risk seems unreasonably high: {actual}"
    
    @given(
        volume_data=st.lists(
            st.tuples(
                st.floats(min_value=1000, max_value=200000, allow_nan=False, allow_infinity=False),  # cargo_volume
                st.floats(min_value=100, max_value=10000, allow_nan=False, allow_infinity=False)  # quantity
            ),
            min_size=1,
            max_size=50
        )
    )
    @settings(max_examples=40, deadline=10000)
    @example(volume_data=[(104493, 2330), (106884, 3836), (98270, 1572)])
    @example(volume_data=[(1000, 100), (200000, 10000)])  # Edge cases
    def test_volume_spike_score_mathematical_correctness(self, volume_data: List[Tuple[float, float]]):
        """
        **Validates: Requirements CP-3**
        
        Property: volume_spike_score = cargo_volume / quantity must be mathematically correct
        
        Test Strategy: Generate cargo volume and quantity pairs and verify division calculation
        """
        # Create test DataFrame
        volumes, quantities = zip(*volume_data)
        df = pd.DataFrame({
            'cargo_volume': volumes,
            'quantity': quantities
        })
        
        # Calculate feature
        result = calculate_volume_spike_score(df)
        
        # Verify mathematical correctness
        for i, (volume, quantity) in enumerate(volume_data):
            expected = volume / quantity
            actual = result.iloc[i]
            
            # Allow for floating point precision issues
            assert abs(actual - expected) < 1e-10, f"Volume spike score calculation incorrect: expected {expected}, got {actual}"
            
            # Verify result is positive
            assert actual > 0, f"Volume spike score must be positive, got {actual}"
            
            # Verify reasonable range (volume per unit should be reasonable)
            assert actual <= 5000, f"Volume spike score seems unreasonably high: {actual}"
    
    @given(
        zero_values=st.sampled_from(['distance', 'quantity', 'both'])
    )
    @settings(max_examples=10, deadline=10000)
    def test_division_by_zero_edge_cases(self, zero_values: str):
        """
        **Validates: Requirements CP-3**
        
        Property: Features must handle division by zero gracefully
        
        Test Strategy: Test edge cases with zero values in denominators
        """
        # Create test data with potential zero denominators
        if zero_values == 'distance':
            df = pd.DataFrame({
                'shipment_duration_days': [10, 20, 30],
                'distance_km': [0, 1000, 2000],
                'cargo_volume': [1000, 2000, 3000],
                'quantity': [100, 200, 300]
            })
        elif zero_values == 'quantity':
            df = pd.DataFrame({
                'shipment_duration_days': [10, 20, 30],
                'distance_km': [1000, 2000, 3000],
                'cargo_volume': [1000, 2000, 3000],
                'quantity': [0, 200, 300]
            })
        else:  # both
            df = pd.DataFrame({
                'shipment_duration_days': [10, 20, 30],
                'distance_km': [0, 1000, 2000],
                'cargo_volume': [1000, 2000, 3000],
                'quantity': [0, 200, 300]
            })
        
        # Test shipment duration risk with zero distance
        if zero_values in ['distance', 'both']:
            result = calculate_shipment_duration_risk(df)
            # Should handle zero distance by replacing with 1
            assert all(pd.notna(result)), "Shipment duration risk should handle zero distance"
            assert all(result > 0), "Shipment duration risk should be positive even with zero distance"
        
        # Test volume spike score with zero quantity
        if zero_values in ['quantity', 'both']:
            result = calculate_volume_spike_score(df)
            # Should handle zero quantity by replacing with 1
            assert all(pd.notna(result)), "Volume spike score should handle zero quantity"
            assert all(result > 0), "Volume spike score should be positive even with zero quantity"
    
    @given(
        negative_values=st.sampled_from(['price_deviation', 'duration', 'distance', 'volume', 'quantity'])
    )
    @settings(max_examples=15, deadline=10000)
    def test_negative_values_edge_cases(self, negative_values: str):
        """
        **Validates: Requirements CP-3**
        
        Property: Features must handle negative values appropriately
        
        Test Strategy: Test edge cases with negative input values
        """
        # Create test data with negative values
        base_data = {
            'price_deviation': [0.1, -0.2, 0.3],
            'route_anomaly': [0, 1, 0],
            'company_risk_score': [0.1, 0.5, 0.9],
            'port_activity_index': [1.0, 1.5, 2.0],
            'shipment_duration_days': [10, 20, 30],
            'distance_km': [1000, 2000, 3000],
            'cargo_volume': [1000, 2000, 3000],
            'quantity': [100, 200, 300]
        }
        
        # Introduce negative values
        if negative_values == 'price_deviation':
            base_data['price_deviation'] = [-0.5, -1.0, -0.1]
        elif negative_values == 'duration':
            base_data['shipment_duration_days'] = [-10, 20, 30]
        elif negative_values == 'distance':
            base_data['distance_km'] = [-1000, 2000, 3000]
        elif negative_values == 'volume':
            base_data['cargo_volume'] = [-1000, 2000, 3000]
        elif negative_values == 'quantity':
            base_data['quantity'] = [-100, 200, 300]
        
        df = pd.DataFrame(base_data)
        
        # Test price anomaly score with negative deviations
        if negative_values == 'price_deviation':
            result = calculate_price_anomaly_score(df)
            # Should take absolute value, so all results should be positive
            assert all(result >= 0), "Price anomaly score should be non-negative even with negative deviations"
            assert result.iloc[0] == 0.5, "abs(-0.5) should equal 0.5"
            assert result.iloc[1] == 1.0, "abs(-1.0) should equal 1.0"
        
        # Test other features with negative values
        # These should either handle gracefully or raise appropriate errors
        try:
            if negative_values in ['duration', 'distance']:
                result = calculate_shipment_duration_risk(df)
                # Should handle negative values appropriately
                assert all(pd.notna(result)), "Should handle negative duration/distance values"
            
            if negative_values in ['volume', 'quantity']:
                result = calculate_volume_spike_score(df)
                # Should handle negative values appropriately
                assert all(pd.notna(result)), "Should handle negative volume/quantity values"
                
        except (ValueError, ZeroDivisionError) as e:
            # It's acceptable to raise errors for invalid negative values
            assert "negative" in str(e).lower() or "invalid" in str(e).lower()
    
    @given(
        feature_ranges=st.fixed_dictionaries({
            'price_deviation': st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
            'route_anomaly': st.sampled_from([0, 1]),
            'company_risk_score': st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            'port_activity_index': st.floats(min_value=0.5, max_value=2.5, allow_nan=False),
            'shipment_duration_days': st.floats(min_value=1, max_value=60, allow_nan=False),
            'distance_km': st.floats(min_value=500, max_value=15000, allow_nan=False),
            'cargo_volume': st.floats(min_value=5000, max_value=150000, allow_nan=False),
            'quantity': st.floats(min_value=500, max_value=5000, allow_nan=False)
        })
    )
    @settings(max_examples=30, deadline=15000)
    def test_feature_ranges_are_reasonable(self, feature_ranges: Dict[str, float]):
        """
        **Validates: Requirements CP-3**
        
        Property: All engineered features must be within reasonable ranges
        
        Test Strategy: Generate realistic input ranges and verify output ranges
        """
        # Create single-row DataFrame with the generated values
        df = pd.DataFrame([feature_ranges])
        
        # Calculate all features
        result_df = engineer_features(df)
        
        # Verify price_anomaly_score range
        price_anomaly = result_df['price_anomaly_score'].iloc[0]
        assert 0 <= price_anomaly <= 1.0, f"Price anomaly score out of range: {price_anomaly}"
        
        # Verify route_risk_score range
        route_risk = result_df['route_risk_score'].iloc[0]
        assert route_risk in [0, 1], f"Route risk score out of range: {route_risk}"
        
        # Verify company_network_risk range
        company_risk = result_df['company_network_risk'].iloc[0]
        assert 0 <= company_risk <= 1.0, f"Company network risk out of range: {company_risk}"
        
        # Verify port_congestion_score range
        port_congestion = result_df['port_congestion_score'].iloc[0]
        assert 0.5 <= port_congestion <= 2.5, f"Port congestion score out of range: {port_congestion}"
        
        # Verify shipment_duration_risk range (should be small positive number)
        duration_risk = result_df['shipment_duration_risk'].iloc[0]
        assert 0 < duration_risk <= 0.2, f"Shipment duration risk out of reasonable range: {duration_risk}"
        
        # Verify volume_spike_score range (should be reasonable volume per unit)
        volume_spike = result_df['volume_spike_score'].iloc[0]
        assert 1 <= volume_spike <= 500, f"Volume spike score out of reasonable range: {volume_spike}"
    
    def test_known_input_values_correctness(self):
        """
        **Validates: Requirements CP-3**
        
        Property: Features must produce correct results for known input values
        
        Test Strategy: Use specific known values and verify exact calculations
        """
        # Test data based on actual dataset samples
        test_data = {
            'price_deviation': [-0.0649, 0.1049, -0.0216, 0.1331],
            'route_anomaly': [0, 0, 0, 0],
            'company_risk_score': [0.32, 0.51, 0.5, 0.75],
            'port_activity_index': [1.16, 1.58, 1.6, 1.23],
            'shipment_duration_days': [21, 16, 14, 20],
            'distance_km': [5600, 7800, 7800, 7800],
            'cargo_volume': [104493, 106884, 98270, 126186],
            'quantity': [2330, 3836, 1572, 2172]
        }
        
        df = pd.DataFrame(test_data)
        result_df = engineer_features(df)
        
        # Verify specific calculations
        # Row 0: price_deviation = -0.0649
        assert abs(result_df['price_anomaly_score'].iloc[0] - 0.0649) < 1e-10
        
        # Row 1: price_deviation = 0.1049
        assert abs(result_df['price_anomaly_score'].iloc[1] - 0.1049) < 1e-10
        
        # All route_risk_score should be 0
        assert all(result_df['route_risk_score'] == 0)
        
        # Company network risk should match company risk score
        for i in range(len(df)):
            assert abs(result_df['company_network_risk'].iloc[i] - test_data['company_risk_score'][i]) < 1e-10
        
        # Port congestion should match port activity index
        for i in range(len(df)):
            assert abs(result_df['port_congestion_score'].iloc[i] - test_data['port_activity_index'][i]) < 1e-10
        
        # Verify shipment duration risk calculations
        expected_duration_risks = [
            21 / 5600,  # 0.00375
            16 / 7800,  # 0.00205...
            14 / 7800,  # 0.00179...
            20 / 7800   # 0.00256...
        ]
        
        for i, expected in enumerate(expected_duration_risks):
            actual = result_df['shipment_duration_risk'].iloc[i]
            assert abs(actual - expected) < 1e-10, f"Shipment duration risk incorrect at row {i}: expected {expected}, got {actual}"
        
        # Verify volume spike score calculations
        expected_volume_spikes = [
            104493 / 2330,  # 44.84...
            106884 / 3836,  # 27.86...
            98270 / 1572,   # 62.52...
            126186 / 2172   # 58.11...
        ]
        
        for i, expected in enumerate(expected_volume_spikes):
            actual = result_df['volume_spike_score'].iloc[i]
            assert abs(actual - expected) < 1e-10, f"Volume spike score incorrect at row {i}: expected {expected}, got {actual}"


class TestFeatureCorrectnessIntegration:
    """Integration tests for complete feature engineering pipeline."""
    
    def test_real_dataset_feature_correctness(self):
        """
        **Validates: Requirements CP-3**
        
        Property: Feature engineering must work correctly on real dataset
        
        Test Strategy: Load actual dataset and verify feature calculations
        """
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        
        if not os.path.exists(dataset_path):
            pytest.skip(f"Dataset not found: {dataset_path}")
        
        # Load a small sample of the dataset
        df = pd.read_csv(dataset_path, nrows=10)
        
        # Ensure required columns exist
        required_columns = [
            'price_deviation', 'route_anomaly', 'company_risk_score',
            'port_activity_index', 'shipment_duration_days', 'distance_km',
            'cargo_volume', 'quantity'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            pytest.skip(f"Missing required columns: {missing_columns}")
        
        # Run feature engineering
        result_df = engineer_features(df)
        
        # Verify all features were added
        expected_features = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        
        for feature in expected_features:
            assert feature in result_df.columns, f"Feature {feature} not found in result"
            assert not result_df[feature].isna().any(), f"Feature {feature} contains NaN values"
        
        # Verify mathematical correctness for each row
        for i in range(len(df)):
            # Price anomaly score
            expected_price = abs(df['price_deviation'].iloc[i])
            actual_price = result_df['price_anomaly_score'].iloc[i]
            assert abs(actual_price - expected_price) < 1e-10
            
            # Route risk score
            expected_route = df['route_anomaly'].iloc[i]
            actual_route = result_df['route_risk_score'].iloc[i]
            assert actual_route == expected_route
            
            # Company network risk
            expected_company = df['company_risk_score'].iloc[i]
            actual_company = result_df['company_network_risk'].iloc[i]
            assert abs(actual_company - expected_company) < 1e-10
            
            # Port congestion score
            expected_port = df['port_activity_index'].iloc[i]
            actual_port = result_df['port_congestion_score'].iloc[i]
            assert abs(actual_port - expected_port) < 1e-10
            
            # Shipment duration risk
            expected_duration = df['shipment_duration_days'].iloc[i] / max(df['distance_km'].iloc[i], 1)
            actual_duration = result_df['shipment_duration_risk'].iloc[i]
            assert abs(actual_duration - expected_duration) < 1e-10
            
            # Volume spike score
            expected_volume = df['cargo_volume'].iloc[i] / max(df['quantity'].iloc[i], 1)
            actual_volume = result_df['volume_spike_score'].iloc[i]
            assert abs(actual_volume - expected_volume) < 1e-10
    
    def test_feature_consistency_across_runs(self):
        """
        **Validates: Requirements CP-3**
        
        Property: Feature calculations must be consistent across multiple runs
        
        Test Strategy: Run feature engineering multiple times and verify identical results
        """
        # Create test data
        test_data = {
            'price_deviation': [0.1, -0.2, 0.3, -0.4, 0.5],
            'route_anomaly': [0, 1, 0, 1, 0],
            'company_risk_score': [0.1, 0.3, 0.5, 0.7, 0.9],
            'port_activity_index': [1.0, 1.2, 1.4, 1.6, 1.8],
            'shipment_duration_days': [10, 15, 20, 25, 30],
            'distance_km': [1000, 2000, 3000, 4000, 5000],
            'cargo_volume': [10000, 20000, 30000, 40000, 50000],
            'quantity': [100, 200, 300, 400, 500]
        }
        
        df = pd.DataFrame(test_data)
        
        # Run feature engineering multiple times
        results = []
        for _ in range(5):
            result_df = engineer_features(df)
            results.append(result_df)
        
        # Verify all results are identical
        for i in range(1, len(results)):
            for feature in ['price_anomaly_score', 'route_risk_score', 'company_network_risk',
                          'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score']:
                try:
                    pd.testing.assert_series_equal(
                        results[0][feature], 
                        results[i][feature],
                        check_names=False
                    )
                except AssertionError as e:
                    pytest.fail(f"Feature {feature} inconsistent across runs: {e}")


if __name__ == "__main__":
    # Run the property-based tests
    pytest.main([__file__, "-v", "--tb=short", "-x"])