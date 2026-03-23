"""
Comprehensive test suite to achieve >80% code coverage for TRINETRA AI backend modules.
This test file focuses on testing the main functionality of each module to maximize coverage.
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
import joblib
from unittest.mock import Mock, patch, MagicMock
from sklearn.ensemble import IsolationForest

# Import all backend modules
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import (
    load_dataset, validate_schema, get_dataset_stats, handle_missing_values,
    DataLoaderError, SchemaValidationError, DataQualityError
)
from feature_engineering import (
    engineer_features, calculate_price_anomaly_score, calculate_route_risk_score,
    calculate_company_network_risk, calculate_port_congestion_score,
    calculate_shipment_duration_risk, calculate_volume_spike_score
)
from model import train_model, save_model, load_model
from fraud_detection import load_fraud_detector, score_transactions, classify_risk
from ai_explainer import explain_transaction, answer_investigation_query
from alerts import check_alerts, prioritize_alert, create_alert_summary


class TestDataLoaderCoverage:
    """Comprehensive tests for data_loader.py to improve coverage."""
    
    def test_load_dataset_success(self):
        """Test successful dataset loading."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("transaction_id,date,product,commodity_category,quantity,unit_price,trade_value,market_price,price_deviation,exporter_company,exporter_country,importer_company,importer_country,shipping_route,distance_km,company_risk_score,route_anomaly,fraud_label\n")
            f.write("TXN001,2024-01-01,Electronics,Consumer Goods,100,10.5,1050,10.0,0.05,CompanyA,USA,CompanyB,UK,USA-UK,5000,0.2,0,0\n")
            temp_path = f.name
        
        try:
            df = load_dataset(temp_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1
            assert 'transaction_id' in df.columns
        finally:
            os.unlink(temp_path)
    
    def test_validate_schema_success(self):
        """Test schema validation with valid data."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'date': ['2024-01-01'],
            'product': ['Electronics'],
            'commodity_category': ['Consumer Goods'],
            'quantity': [100],
            'unit_price': [10.5],
            'trade_value': [1050],
            'market_price': [10.0],
            'price_deviation': [0.05],
            'exporter_company': ['CompanyA'],
            'exporter_country': ['USA'],
            'importer_company': ['CompanyB'],
            'importer_country': ['UK'],
            'shipping_route': ['USA-UK'],
            'distance_km': [5000],
            'company_risk_score': [0.2],
            'route_anomaly': [0],
            'fraud_label': [0]
        })
        
        result = validate_schema(df)
        assert result is True
    
    def test_get_dataset_stats_success(self):
        """Test dataset statistics calculation."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'unit_price': [10.5, 20.0],
            'quantity': [100, 200]
        })
        
        stats = get_dataset_stats(df)
        assert isinstance(stats, dict)
        assert 'basic_info' in stats
        assert stats['basic_info']['total_rows'] == 2
    
    def test_handle_missing_values_success(self):
        """Test missing value handling."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'unit_price': [10.5, None],
            'quantity': [100, 200]
        })
        
        result_df = handle_missing_values(df)
        assert isinstance(result_df, pd.DataFrame)
        assert not result_df['unit_price'].isnull().any()


class TestFeatureEngineeringCoverage:
    """Comprehensive tests for feature_engineering.py to improve coverage."""
    
    def test_calculate_price_anomaly_score(self):
        """Test price anomaly score calculation."""
        df = pd.DataFrame({
            'price_deviation': [0.1, -0.2, 0.5]
        })
        
        result = calculate_price_anomaly_score(df)
        expected = pd.Series([0.1, 0.2, 0.5])
        pd.testing.assert_series_equal(result, expected)
    
    def test_calculate_route_risk_score(self):
        """Test route risk score calculation."""
        df = pd.DataFrame({
            'route_anomaly': [0, 1, 0]
        })
        
        result = calculate_route_risk_score(df)
        expected = pd.Series([0, 1, 0])
        pd.testing.assert_series_equal(result, expected)
    
    def test_calculate_company_network_risk(self):
        """Test company network risk calculation."""
        df = pd.DataFrame({
            'company_risk_score': [0.1, 0.5, 0.9]
        })
        
        result = calculate_company_network_risk(df)
        expected = pd.Series([0.1, 0.5, 0.9])
        pd.testing.assert_series_equal(result, expected)
    
    def test_calculate_port_congestion_score(self):
        """Test port congestion score calculation."""
        df = pd.DataFrame({
            'port_activity_index': [1.0, 1.5, 2.0]
        })
        
        result = calculate_port_congestion_score(df)
        expected = pd.Series([1.0, 1.5, 2.0])
        pd.testing.assert_series_equal(result, expected)
    
    def test_calculate_shipment_duration_risk(self):
        """Test shipment duration risk calculation."""
        df = pd.DataFrame({
            'shipment_duration_days': [10, 20, 30],
            'distance_km': [1000, 2000, 3000]
        })
        
        result = calculate_shipment_duration_risk(df)
        expected = pd.Series([0.01, 0.01, 0.01])
        pd.testing.assert_series_equal(result, expected)
    
    def test_calculate_volume_spike_score(self):
        """Test volume spike score calculation."""
        df = pd.DataFrame({
            'cargo_volume': [100, 200, 300],
            'quantity': [10, 20, 30]
        })
        
        result = calculate_volume_spike_score(df)
        expected = pd.Series([10.0, 10.0, 10.0])
        pd.testing.assert_series_equal(result, expected)
    
    def test_engineer_features_complete(self):
        """Test complete feature engineering pipeline."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'price_deviation': [0.1],
            'route_anomaly': [1],
            'company_risk_score': [0.5],
            'port_activity_index': [1.5],
            'shipment_duration_days': [10],
            'distance_km': [1000],
            'cargo_volume': [100],
            'quantity': [10]
        })
        
        result_df = engineer_features(df)
        assert 'price_anomaly_score' in result_df.columns
        assert 'route_risk_score' in result_df.columns
        assert 'company_network_risk' in result_df.columns
        assert 'port_congestion_score' in result_df.columns
        assert 'shipment_duration_risk' in result_df.columns
        assert 'volume_spike_score' in result_df.columns


class TestModelCoverage:
    """Comprehensive tests for model.py to improve coverage."""
    
    def test_train_model_success(self):
        """Test successful model training."""
        df = pd.DataFrame({
            'price_anomaly_score': np.random.uniform(0, 1, 100),
            'route_risk_score': np.random.choice([0, 1], 100),
            'company_network_risk': np.random.uniform(0, 1, 100),
            'port_congestion_score': np.random.uniform(0.5, 3.0, 100),
            'shipment_duration_risk': np.random.uniform(0, 0.5, 100),
            'volume_spike_score': np.random.uniform(1, 100, 100)
        })
        
        model = train_model(df)
        assert isinstance(model, IsolationForest)
        assert hasattr(model, 'decision_function')
    
    def test_save_and_load_model(self):
        """Test model saving and loading."""
        # Create a simple model
        model = IsolationForest(n_estimators=10, random_state=42)
        X = np.random.rand(50, 6)
        model.fit(X)
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = f.name
        
        try:
            # Test saving
            save_model(model, temp_path)
            assert os.path.exists(temp_path)
            
            # Test loading
            loaded_model = load_model(temp_path)
            assert isinstance(loaded_model, IsolationForest)
            assert loaded_model.n_estimators == model.n_estimators
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestFraudDetectionCoverage:
    """Comprehensive tests for fraud_detection.py to improve coverage."""
    
    def test_score_transactions_with_mock_model(self):
        """Test transaction scoring with a mock model."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'price_anomaly_score': [0.1, 0.8],
            'route_risk_score': [0, 1],
            'company_network_risk': [0.2, 0.9],
            'port_congestion_score': [1.0, 2.5],
            'shipment_duration_risk': [0.1, 0.4],
            'volume_spike_score': [10.0, 90.0]
        })
        
        # Create a real model for testing
        model = IsolationForest(n_estimators=10, random_state=42)
        X = df.drop('transaction_id', axis=1)
        model.fit(X)
        
        result_df = score_transactions(df, model)
        assert 'risk_score' in result_df.columns
        assert len(result_df) == 2
    
    def test_classify_risk_categories(self):
        """Test risk classification."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'risk_score': [-0.3, 0.0, 0.3]
        })
        
        result_df = classify_risk(df)
        assert 'risk_category' in result_df.columns
        assert result_df.iloc[0]['risk_category'] == 'SAFE'
        assert result_df.iloc[1]['risk_category'] == 'SUSPICIOUS'
        assert result_df.iloc[2]['risk_category'] == 'FRAUD'


class TestAIExplainerCoverage:
    """Comprehensive tests for ai_explainer.py to improve coverage."""
    
    @patch('backend.ai_explainer.genai')
    def test_explain_transaction_fallback(self, mock_genai):
        """Test transaction explanation with fallback."""
        transaction = {
            'transaction_id': 'TXN001',
            'product': 'Electronics',
            'commodity_category': 'Consumer Goods',
            'market_price': 1000,
            'unit_price': 1500,
            'price_deviation': 0.5,
            'shipping_route': 'USA-UK',
            'distance_km': 5000,
            'company_risk_score': 0.8,
            'port_activity_index': 2.0,
            'route_anomaly': 1
        }
        
        # Mock API failure to trigger fallback
        mock_genai.configure.side_effect = Exception("API Error")
        
        explanation = explain_transaction(transaction)
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    @patch('backend.ai_explainer.genai')
    def test_answer_investigation_query_fallback(self, mock_genai):
        """Test investigation query with fallback."""
        query = "What is the fraud rate?"
        context = {'total_transactions': 1000, 'fraud_count': 50}
        
        # Mock API failure to trigger fallback
        mock_genai.configure.side_effect = Exception("API Error")
        
        response = answer_investigation_query(query, context)
        assert isinstance(response, str)
        assert len(response) > 0


class TestAlertsCoverage:
    """Comprehensive tests for alerts.py to improve coverage."""
    
    def test_check_alerts_all_conditions(self):
        """Test alert checking with various conditions."""
        # Test transaction that triggers all alerts
        transaction = {
            'transaction_id': 'TXN001',
            'price_deviation': 0.6,  # > 0.5
            'route_anomaly': 1,      # == 1
            'company_risk_score': 0.9,  # > 0.8
            'port_activity_index': 2.0   # > 1.5
        }
        
        alerts = check_alerts(transaction)
        assert len(alerts) == 4
        assert 'PRICE_ANOMALY' in alerts
        assert 'ROUTE_ANOMALY' in alerts
        assert 'HIGH_RISK_COMPANY' in alerts
        assert 'PORT_CONGESTION' in alerts
    
    def test_check_alerts_no_conditions(self):
        """Test alert checking with no conditions met."""
        transaction = {
            'transaction_id': 'TXN002',
            'price_deviation': 0.1,  # <= 0.5
            'route_anomaly': 0,      # != 1
            'company_risk_score': 0.3,  # <= 0.8
            'port_activity_index': 1.0   # <= 1.5
        }
        
        alerts = check_alerts(transaction)
        assert len(alerts) == 0
    
    def test_prioritize_alert(self):
        """Test alert priority calculation."""
        transaction = {'transaction_id': 'TXN001', 'price_deviation': 0.6}
        alerts = ['PRICE_ANOMALY', 'ROUTE_ANOMALY']
        priority, details = prioritize_alert(transaction, alerts)
        assert priority is not None
        assert isinstance(details, dict)
    
    def test_create_alert_summary(self):
        """Test alert summary creation."""
        transaction = {
            'transaction_id': 'TXN001',
            'price_deviation': 0.6,
            'route_anomaly': 1,
            'company_risk_score': 0.9,
            'port_activity_index': 2.0
        }
        
        summary = create_alert_summary(transaction)
        assert summary is not None


class TestIntegrationCoverage:
    """Integration tests to improve overall coverage."""
    
    def test_complete_pipeline_with_synthetic_data(self):
        """Test complete fraud detection pipeline."""
        # Create synthetic data
        np.random.seed(42)
        df = pd.DataFrame({
            'transaction_id': [f'TXN{i:03d}' for i in range(50)],
            'price_deviation': np.random.uniform(-0.5, 1.0, 50),
            'route_anomaly': np.random.choice([0, 1], 50),
            'company_risk_score': np.random.uniform(0, 1, 50),
            'port_activity_index': np.random.uniform(0.5, 3.0, 50),
            'shipment_duration_days': np.random.uniform(1, 30, 50),
            'distance_km': np.random.uniform(500, 10000, 50),
            'cargo_volume': np.random.uniform(10, 1000, 50),
            'quantity': np.random.uniform(1, 100, 50)
        })
        
        # Test feature engineering
        df_with_features = engineer_features(df)
        assert len(df_with_features.columns) > len(df.columns)
        
        # Test model training
        model = train_model(df_with_features)
        assert isinstance(model, IsolationForest)
        
        # Test scoring
        df_scored = score_transactions(df_with_features, model)
        assert 'risk_score' in df_scored.columns
        
        # Test classification
        df_classified = classify_risk(df_scored)
        assert 'risk_category' in df_classified.columns
        
        # Test alerts for each transaction
        for _, transaction in df_classified.iterrows():
            alerts = check_alerts(transaction.to_dict())
            assert isinstance(alerts, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])