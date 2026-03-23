"""
Validation Tests for Test Data Generators
TRINETRA AI - Trade Fraud Intelligence System

This module validates that the test data generators produce valid data
that can be used across all property-based tests.
"""

import pytest
import pandas as pd
from hypothesis import given, settings, example, HealthCheck
from hypothesis import strategies as st

from test_data_generators import (
    # Basic field generators
    transaction_id_strategy,
    date_strategy,
    fraud_label_strategy,
    product_strategy,
    commodity_category_strategy,
    country_strategy,
    company_strategy,
    shipping_route_strategy,
    
    # Numeric field generators
    quantity_strategy,
    unit_price_strategy,
    trade_value_strategy,
    price_deviation_strategy,
    company_risk_score_strategy,
    port_activity_index_strategy,
    distance_km_strategy,
    shipment_duration_days_strategy,
    cargo_volume_strategy,
    route_anomaly_strategy,
    
    # Risk score generators
    risk_score_strategy,
    safe_risk_score_strategy,
    suspicious_risk_score_strategy,
    fraud_risk_score_strategy,
    boundary_risk_score_strategy,
    
    # Alert threshold generators
    alert_price_deviation_strategy,
    alert_company_risk_strategy,
    alert_port_activity_strategy,
    
    # Composite generators
    transaction_row_strategy,
    feature_engineering_input_strategy,
    alert_trigger_transaction_strategy,
    risk_classified_transaction_strategy,
    transaction_dataframe_strategy,
    feature_engineering_dataframe_strategy,
    
    # API response generators
    api_transaction_response_strategy,
    api_transactions_list_response_strategy,
    api_stats_response_strategy,
    
    # Edge case generators
    zero_value_strategy,
    negative_value_strategy,
    extreme_value_strategy,
    edge_case_transaction_strategy,
    
    # Utility functions
    create_test_dataframe,
    validate_transaction_schema
)


class TestBasicFieldGenerators:
    """Test basic field generators produce valid data."""
    
    @given(transaction_id=transaction_id_strategy())
    @settings(max_examples=20)
    def test_transaction_id_format(self, transaction_id):
        """Validate transaction ID format."""
        assert isinstance(transaction_id, str)
        assert transaction_id.startswith('TXN')
        assert len(transaction_id) == 8  # TXN + 5 digits
        assert transaction_id[3:].isdigit()
    
    @given(date=date_strategy())
    @settings(max_examples=20)
    def test_date_format(self, date):
        """Validate date format."""
        assert isinstance(date, str)
        assert len(date) == 10  # YYYY-MM-DD
        parts = date.split('-')
        assert len(parts) == 3
        assert 2020 <= int(parts[0]) <= 2024
        assert 1 <= int(parts[1]) <= 12
        assert 1 <= int(parts[2]) <= 31
    
    @given(fraud_label=fraud_label_strategy())
    @settings(max_examples=20)
    def test_fraud_label_values(self, fraud_label):
        """Validate fraud label values."""
        assert fraud_label in [0, 1]
    
    @given(product=product_strategy())
    @settings(max_examples=20)
    def test_product_values(self, product):
        """Validate product values."""
        assert isinstance(product, str)
        assert len(product) > 0


class TestNumericFieldGenerators:
    """Test numeric field generators produce valid ranges."""
    
    @given(quantity=quantity_strategy())
    @settings(max_examples=20)
    def test_quantity_range(self, quantity):
        """Validate quantity range."""
        assert 100 <= quantity <= 10000
    
    @given(price=unit_price_strategy())
    @settings(max_examples=20)
    def test_unit_price_range(self, price):
        """Validate unit price range."""
        assert 1.0 <= price <= 10000.0
    
    @given(deviation=price_deviation_strategy())
    @settings(max_examples=20)
    def test_price_deviation_range(self, deviation):
        """Validate price deviation range."""
        assert -2.0 <= deviation <= 2.0
    
    @given(risk_score=company_risk_score_strategy())
    @settings(max_examples=20)
    def test_company_risk_score_range(self, risk_score):
        """Validate company risk score range."""
        assert 0.0 <= risk_score <= 1.0
    
    @given(distance=distance_km_strategy())
    @settings(max_examples=20)
    def test_distance_range(self, distance):
        """Validate distance range."""
        assert 100.0 <= distance <= 20000.0


class TestRiskScoreGenerators:
    """Test risk score generators produce correct categories."""
    
    @given(score=safe_risk_score_strategy())
    @settings(max_examples=20)
    def test_safe_risk_scores(self, score):
        """Validate SAFE risk scores."""
        assert score < -0.2
    
    @given(score=suspicious_risk_score_strategy())
    @settings(max_examples=20)
    def test_suspicious_risk_scores(self, score):
        """Validate SUSPICIOUS risk scores."""
        assert -0.2 <= score < 0.2
    
    @given(score=fraud_risk_score_strategy())
    @settings(max_examples=20)
    def test_fraud_risk_scores(self, score):
        """Validate FRAUD risk scores."""
        assert score >= 0.2
    
    @given(score=boundary_risk_score_strategy())
    @settings(max_examples=10)
    def test_boundary_risk_scores(self, score):
        """Validate boundary risk scores."""
        # Should be near -0.2 or 0.2
        assert abs(score + 0.2) < 0.1 or abs(score - 0.2) < 0.1


class TestCompositeGenerators:
    """Test composite generators produce complete data structures."""
    
    @given(transaction=transaction_row_strategy())
    @settings(max_examples=20, suppress_health_check=[HealthCheck.data_too_large])
    def test_transaction_row_completeness(self, transaction):
        """Validate transaction row has all required fields."""
        assert validate_transaction_schema(transaction)
        assert isinstance(transaction['transaction_id'], str)
        assert isinstance(transaction['date'], str)
        assert transaction['fraud_label'] in [0, 1]
    
    @given(features=feature_engineering_input_strategy())
    @settings(max_examples=20, suppress_health_check=[HealthCheck.data_too_large])
    def test_feature_engineering_input(self, features):
        """Validate feature engineering input data."""
        required_fields = [
            'price_deviation', 'route_anomaly', 'company_risk_score',
            'port_activity_index', 'shipment_duration_days', 'distance_km',
            'cargo_volume', 'quantity'
        ]
        for field in required_fields:
            assert field in features
    
    @given(transaction=alert_trigger_transaction_strategy())
    @settings(max_examples=20, suppress_health_check=[HealthCheck.data_too_large])
    def test_alert_trigger_transaction(self, transaction):
        """Validate alert trigger transaction data."""
        assert 'transaction_id' in transaction
        assert 'price_deviation' in transaction
        assert 'route_anomaly' in transaction
        assert 'company_risk_score' in transaction
        assert 'port_activity_index' in transaction
    
    @given(transaction=risk_classified_transaction_strategy())
    @settings(max_examples=20)
    def test_risk_classified_transaction(self, transaction):
        """Validate risk classified transaction consistency."""
        score = transaction['risk_score']
        category = transaction['risk_category']
        
        # Verify category matches score
        if score < -0.2:
            assert category == "SAFE"
        elif score < 0.2:
            assert category == "SUSPICIOUS"
        else:
            assert category == "FRAUD"


class TestDataFrameGenerators:
    """Test DataFrame generators produce valid DataFrames."""
    
    @given(df=transaction_dataframe_strategy(min_rows=5, max_rows=20))
    @settings(max_examples=10, deadline=30000)
    def test_transaction_dataframe(self, df):
        """Validate transaction DataFrame structure."""
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 5
        assert len(df) <= 20
        assert 'transaction_id' in df.columns
        assert 'date' in df.columns
        assert 'fraud_label' in df.columns
    
    @given(df=feature_engineering_dataframe_strategy(min_rows=3, max_rows=10))
    @settings(max_examples=10, deadline=30000)
    def test_feature_engineering_dataframe(self, df):
        """Validate feature engineering DataFrame structure."""
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 3
        assert len(df) <= 10
        assert 'price_deviation' in df.columns
        assert 'distance_km' in df.columns
        assert 'cargo_volume' in df.columns


class TestAPIResponseGenerators:
    """Test API response generators produce valid responses."""
    
    @given(response=api_transaction_response_strategy())
    @settings(max_examples=20, suppress_health_check=[HealthCheck.data_too_large])
    def test_api_transaction_response(self, response):
        """Validate API transaction response structure."""
        assert 'status' in response
        assert 'data' in response
        assert 'message' in response
        assert response['status'] == 'success'
        assert validate_transaction_schema(response['data'])
    
    @given(response=api_transactions_list_response_strategy(min_items=1, max_items=5))
    @settings(max_examples=10, deadline=30000)
    def test_api_transactions_list_response(self, response):
        """Validate API transactions list response structure."""
        assert 'status' in response
        assert 'data' in response
        assert isinstance(response['data'], list)
        assert len(response['data']) >= 1
        assert len(response['data']) <= 5
    
    @given(response=api_stats_response_strategy())
    @settings(max_examples=20)
    def test_api_stats_response(self, response):
        """Validate API stats response structure."""
        assert 'status' in response
        assert 'data' in response
        assert 'total_transactions' in response['data']
        assert 'fraud_count' in response['data']
        assert 'fraud_rate' in response['data']


class TestEdgeCaseGenerators:
    """Test edge case generators produce boundary values."""
    
    @given(value=zero_value_strategy())
    @settings(max_examples=10)
    def test_zero_value(self, value):
        """Validate zero value generator."""
        assert value == 0
    
    @given(value=negative_value_strategy())
    @settings(max_examples=20)
    def test_negative_value(self, value):
        """Validate negative value generator."""
        assert value < 0
    
    @given(value=extreme_value_strategy())
    @settings(max_examples=20)
    def test_extreme_value(self, value):
        """Validate extreme value generator."""
        assert abs(value) > 1000 or abs(value) < 0.001
    
    @given(transaction=edge_case_transaction_strategy(edge_case_type='zero'))
    @settings(max_examples=10)
    def test_zero_edge_case_transaction(self, transaction):
        """Validate zero edge case transaction."""
        assert transaction['distance_km'] == 0
        assert transaction['quantity'] == 0


class TestUtilityFunctions:
    """Test utility functions work correctly."""
    
    def test_create_test_dataframe(self):
        """Test DataFrame creation from transaction list."""
        transactions = [
            {'transaction_id': 'TXN001', 'date': '2024-01-01', 'fraud_label': 0},
            {'transaction_id': 'TXN002', 'date': '2024-01-02', 'fraud_label': 1}
        ]
        df = create_test_dataframe(transactions)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert 'transaction_id' in df.columns
    
    def test_validate_transaction_schema_valid(self):
        """Test schema validation with valid transaction."""
        transaction = {
            'transaction_id': 'TXN001',
            'date': '2024-01-01',
            'product': 'Electronics',
            'commodity_category': 'Electronics',
            'quantity': 100,
            'unit_price': 10.0,
            'trade_value': 1000.0,
            'market_price': 10.5,
            'price_deviation': 0.05,
            'exporter_company': 'Company A',
            'exporter_country': 'USA',
            'importer_company': 'Company B',
            'importer_country': 'China',
            'shipping_route': 'Pacific Route',
            'distance_km': 5000.0,
            'company_risk_score': 0.5,
            'port_activity_index': 1.2,
            'route_anomaly': 0,
            'shipment_duration_days': 20.0,
            'cargo_volume': 10000.0,
            'fraud_label': 0
        }
        assert validate_transaction_schema(transaction)
    
    def test_validate_transaction_schema_invalid(self):
        """Test schema validation with invalid transaction."""
        transaction = {
            'transaction_id': 'TXN001',
            'date': '2024-01-01'
            # Missing required fields
        }
        assert not validate_transaction_schema(transaction)


if __name__ == "__main__":
    # Run the validation tests
    pytest.main([__file__, "-v", "--tb=short"])
