"""
Unit Tests for Fraud Detection Module - TRINETRA AI

This module contains comprehensive unit tests for the fraud_detection.py module,
testing fraud detection pipeline, risk scoring, and classification functionality.
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
from unittest.mock import patch, MagicMock
from sklearn.ensemble import IsolationForest

# Import the module under test
from backend.fraud_detection import (
    load_fraud_detector, score_transactions, classify_risk, get_risk_category,
    safe_fraud_detection_pipeline, validate_dataframe_schema,
    get_fraud_detection_health_status
)


class TestFraudDetection:
    """Test class for fraud detection functionality."""
    
    @pytest.fixture
    def sample_feature_data(self):
        """Create sample feature data for testing."""
        return pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'price_anomaly_score': [0.1, 0.5, 0.8],
            'route_risk_score': [0, 1, 0],
            'company_network_risk': [0.2, 0.7, 0.3],
            'port_congestion_score': [1.0, 2.5, 1.2],
            'shipment_duration_risk': [0.05, 0.15, 0.08],
            'volume_spike_score': [10.0, 50.0, 25.0]
        })
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock IsolationForest model for testing."""
        model = MagicMock(spec=IsolationForest)
        model.decision_function.return_value = np.array([-0.3, 0.1, 0.4])
        model.predict.return_value = np.array([1, -1, -1])
        return model
    
    @pytest.fixture
    def trained_model(self, sample_feature_data):
        """Create a real trained model for testing."""
        model = IsolationForest(n_estimators=10, contamination=0.3, random_state=42)
        model.fit(sample_feature_data.drop('transaction_id', axis=1))
        return model
    
    def test_load_fraud_detector_success(self, tmp_path, trained_model):
        """Test successful fraud detector loading."""
        model_path = tmp_path / "test_model.pkl"
        
        # Save model first
        import joblib
        joblib.dump(trained_model, model_path)
        
        loaded_model = load_fraud_detector(str(model_path))
        
        assert isinstance(loaded_model, IsolationForest)
        assert hasattr(loaded_model, 'decision_function')
    
    def test_load_fraud_detector_file_not_found(self):
        """Test loading non-existent model file."""
        with pytest.raises(FileNotFoundError):
            load_fraud_detector("non_existent_model.pkl")
    
    def test_load_fraud_detector_corrupted_file(self, tmp_path):
        """Test loading corrupted model file."""
        model_path = tmp_path / "corrupted.pkl"
        
        # Create corrupted file
        with open(model_path, 'w') as f:
            f.write("not a pickle file")
        
        with pytest.raises(ValueError):
            load_fraud_detector(str(model_path))
    
    def test_load_fraud_detector_wrong_type(self, tmp_path):
        """Test loading file with wrong object type."""
        model_path = tmp_path / "wrong_type.pkl"
        
        # Save wrong type of object
        import joblib
        joblib.dump("not a model", model_path)
        
        with pytest.raises(ValueError):
            load_fraud_detector(str(model_path))
    
    def test_score_transactions_success(self, sample_feature_data, mock_model):
        """Test successful transaction scoring."""
        result_df = score_transactions(sample_feature_data, mock_model)
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'risk_score' in result_df.columns
        assert len(result_df) == len(sample_feature_data)
        
        # Check that risk scores match mock return values
        expected_scores = [-0.3, 0.1, 0.4]
        np.testing.assert_array_equal(result_df['risk_score'].values, expected_scores)
    
    def test_score_transactions_empty_dataframe(self, mock_model):
        """Test scoring with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        result_df = score_transactions(empty_df, mock_model)
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'risk_score' in result_df.columns
        assert len(result_df) == 0
    
    def test_score_transactions_missing_features(self, mock_model):
        """Test scoring with missing required features."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'price_anomaly_score': [0.1]
            # Missing other required features
        })
        
        with pytest.raises(ValueError, match="Missing required features"):
            score_transactions(df, mock_model)
    
    def test_score_transactions_with_nan_values(self, mock_model):
        """Test scoring with NaN values in features."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'price_anomaly_score': [0.1, np.nan],
            'route_risk_score': [0, 1],
            'company_network_risk': [0.2, 0.7],
            'port_congestion_score': [1.0, 2.5],
            'shipment_duration_risk': [0.05, 0.15],
            'volume_spike_score': [10.0, 50.0]
        })
        
        mock_model.decision_function.return_value = np.array([-0.3, 0.1])
        
        result_df = score_transactions(df, mock_model)
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'risk_score' in result_df.columns
        assert not result_df['risk_score'].isna().any()  # NaN should be handled
    
    def test_get_risk_category_safe(self):
        """Test risk category classification for safe transactions."""
        assert get_risk_category(-0.5) == "SAFE"
        assert get_risk_category(-0.3) == "SAFE"
        assert get_risk_category(-0.21) == "SAFE"
    
    def test_get_risk_category_suspicious(self):
        """Test risk category classification for suspicious transactions."""
        assert get_risk_category(-0.1) == "SUSPICIOUS"
        assert get_risk_category(0.0) == "SUSPICIOUS"
        assert get_risk_category(0.1) == "SUSPICIOUS"
        assert get_risk_category(0.19) == "SUSPICIOUS"
    
    def test_get_risk_category_fraud(self):
        """Test risk category classification for fraud transactions."""
        assert get_risk_category(0.2) == "FRAUD"
        assert get_risk_category(0.5) == "FRAUD"
        assert get_risk_category(1.0) == "FRAUD"
    
    def test_get_risk_category_edge_cases(self):
        """Test risk category classification with edge cases."""
        assert get_risk_category(None) == "SUSPICIOUS"  # Default for None
        assert get_risk_category(np.nan) == "SUSPICIOUS"  # Default for NaN
        assert get_risk_category(float('inf')) == "FRAUD"  # Positive infinity
        assert get_risk_category(float('-inf')) == "SAFE"  # Negative infinity
        assert get_risk_category("0.1") == "SUSPICIOUS"  # String conversion
    
    def test_classify_risk_success(self, sample_feature_data):
        """Test successful risk classification."""
        # Add risk scores to the DataFrame
        sample_feature_data['risk_score'] = [-0.3, 0.1, 0.4]
        
        result_df = classify_risk(sample_feature_data)
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'risk_category' in result_df.columns
        assert len(result_df) == len(sample_feature_data)
        
        # Check classifications
        assert result_df.loc[0, 'risk_category'] == "SAFE"
        assert result_df.loc[1, 'risk_category'] == "SUSPICIOUS"
        assert result_df.loc[2, 'risk_category'] == "FRAUD"
    
    def test_classify_risk_missing_risk_score(self, sample_feature_data):
        """Test risk classification without risk_score column."""
        with pytest.raises(ValueError, match="must contain 'risk_score' column"):
            classify_risk(sample_feature_data)
    
    def test_classify_risk_empty_dataframe(self):
        """Test risk classification with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        result_df = classify_risk(empty_df)
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'risk_category' in result_df.columns
        assert len(result_df) == 0
    
    def test_classify_risk_with_nan_scores(self):
        """Test risk classification with NaN risk scores."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'risk_score': [0.1, np.nan]
        })
        
        result_df = classify_risk(df)
        
        assert len(result_df) == 2
        assert result_df.loc[0, 'risk_category'] == "SUSPICIOUS"
        assert result_df.loc[1, 'risk_category'] == "SUSPICIOUS"  # NaN handled as SUSPICIOUS
    
    def test_validate_dataframe_schema_success(self, sample_feature_data):
        """Test successful DataFrame schema validation."""
        is_valid, missing_cols = validate_dataframe_schema(sample_feature_data)
        
        assert is_valid is True
        assert len(missing_cols) == 0
    
    def test_validate_dataframe_schema_missing_columns(self):
        """Test schema validation with missing columns."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'price_anomaly_score': [0.1]
            # Missing other required features
        })
        
        is_valid, missing_cols = validate_dataframe_schema(df)
        
        assert is_valid is False
        assert len(missing_cols) > 0
    
    def test_validate_dataframe_schema_empty_dataframe(self):
        """Test schema validation with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        is_valid, missing_cols = validate_dataframe_schema(empty_df)
        
        assert is_valid is True  # Empty is considered valid
        assert len(missing_cols) == 0
    
    def test_safe_fraud_detection_pipeline_success(self, sample_feature_data, tmp_path, trained_model):
        """Test successful fraud detection pipeline."""
        # Save model for pipeline to load
        model_path = tmp_path / "pipeline_model.pkl"
        import joblib
        joblib.dump(trained_model, model_path)
        
        result_df = safe_fraud_detection_pipeline(sample_feature_data, str(model_path))
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'risk_score' in result_df.columns
        assert 'risk_category' in result_df.columns
        assert len(result_df) == len(sample_feature_data)
    
    def test_safe_fraud_detection_pipeline_model_not_found(self, sample_feature_data):
        """Test pipeline with non-existent model (should use fallback)."""
        result_df = safe_fraud_detection_pipeline(sample_feature_data, "non_existent_model.pkl")
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'risk_score' in result_df.columns
        assert 'risk_category' in result_df.columns
        assert len(result_df) == len(sample_feature_data)
    
    def test_safe_fraud_detection_pipeline_invalid_data(self):
        """Test pipeline with invalid data (should use final fallback)."""
        invalid_df = pd.DataFrame({'invalid_column': [1, 2, 3]})
        
        result_df = safe_fraud_detection_pipeline(invalid_df)
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'risk_score' in result_df.columns
        assert 'risk_category' in result_df.columns
        assert all(result_df['risk_category'] == 'SUSPICIOUS')  # Default fallback
    
    def test_get_fraud_detection_health_status_healthy(self, tmp_path, trained_model):
        """Test health status with available model."""
        model_path = tmp_path / "health_model.pkl"
        import joblib
        joblib.dump(trained_model, model_path)
        
        # Mock the default model path
        with patch('backend.fraud_detection.load_fraud_detector') as mock_load:
            mock_load.return_value = trained_model
            
            health = get_fraud_detection_health_status()
            
            assert isinstance(health, dict)
            assert health['system_ready'] is True
            assert health['model_available'] is True
            assert health['fallback_available'] is True
    
    def test_get_fraud_detection_health_status_no_model(self):
        """Test health status without available model."""
        with patch('backend.fraud_detection.load_fraud_detector') as mock_load:
            mock_load.side_effect = FileNotFoundError("Model not found")
            
            health = get_fraud_detection_health_status()
            
            assert isinstance(health, dict)
            assert health['model_available'] is False
            assert len(health['errors']) > 0


class TestFraudDetectionEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_score_transactions_extreme_values(self, mock_model):
        """Test scoring with extreme feature values."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'price_anomaly_score': [1000.0, -1000.0],  # Extreme values
            'route_risk_score': [0, 1],
            'company_network_risk': [0.0, 1.0],
            'port_congestion_score': [0.001, 1000.0],  # Extreme values
            'shipment_duration_risk': [0.0, 100.0],  # Extreme values
            'volume_spike_score': [0.001, 10000.0]  # Extreme values
        })
        
        mock_model.decision_function.return_value = np.array([0.5, -0.5])
        
        result_df = score_transactions(df, mock_model)
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'risk_score' in result_df.columns
        assert len(result_df) == 2
    
    def test_model_prediction_failure_handling(self, sample_feature_data):
        """Test handling of model prediction failures."""
        mock_model = MagicMock()
        mock_model.decision_function.side_effect = Exception("Model prediction failed")
        
        with pytest.raises(Exception):
            score_transactions(sample_feature_data, mock_model)
    
    def test_risk_classification_with_string_scores(self):
        """Test risk classification with string risk scores."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'risk_score': ['0.1', 'invalid']  # String values
        })
        
        result_df = classify_risk(df)
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'risk_category' in result_df.columns
        # Should handle conversion gracefully
    
    def test_large_dataset_performance(self, trained_model):
        """Test fraud detection with large dataset."""
        # Create large dataset
        n_rows = 10000
        large_df = pd.DataFrame({
            'transaction_id': [f'TXN{i:06d}' for i in range(n_rows)],
            'price_anomaly_score': np.random.uniform(0, 1, n_rows),
            'route_risk_score': np.random.choice([0, 1], n_rows),
            'company_network_risk': np.random.uniform(0, 1, n_rows),
            'port_congestion_score': np.random.uniform(0.5, 3.0, n_rows),
            'shipment_duration_risk': np.random.uniform(0, 0.5, n_rows),
            'volume_spike_score': np.random.uniform(1, 100, n_rows)
        })
        
        import time
        start_time = time.time()
        result_df = score_transactions(large_df, trained_model)
        result_df = classify_risk(result_df)
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 10.0  # Less than 10 seconds
        assert len(result_df) == n_rows
        assert 'risk_score' in result_df.columns
        assert 'risk_category' in result_df.columns
    
    @patch('backend.fraud_detection.logger')
    def test_logging_functionality(self, mock_logger, sample_feature_data, mock_model):
        """Test that logging is working correctly."""
        score_transactions(sample_feature_data, mock_model)
        
        # Verify that logging calls were made
        assert mock_logger.info.called
    
    def test_risk_category_distribution(self, trained_model):
        """Test that risk categories are distributed reasonably."""
        # Create balanced dataset
        df = pd.DataFrame({
            'transaction_id': [f'TXN{i:03d}' for i in range(300)],
            'price_anomaly_score': np.random.uniform(0, 1, 300),
            'route_risk_score': np.random.choice([0, 1], 300),
            'company_network_risk': np.random.uniform(0, 1, 300),
            'port_congestion_score': np.random.uniform(0.5, 3.0, 300),
            'shipment_duration_risk': np.random.uniform(0, 0.5, 300),
            'volume_spike_score': np.random.uniform(1, 100, 300)
        })
        
        result_df = score_transactions(df, trained_model)
        result_df = classify_risk(result_df)
        
        # Check category distribution
        category_counts = result_df['risk_category'].value_counts()
        
        # Should have all three categories represented
        assert 'SAFE' in category_counts.index
        assert 'SUSPICIOUS' in category_counts.index
        assert 'FRAUD' in category_counts.index
        
        # No single category should dominate completely (>90%)
        max_percentage = category_counts.max() / len(result_df)
        assert max_percentage < 0.9


class TestFraudDetectionIntegration:
    """Integration tests for fraud detection functionality."""
    
    def test_complete_fraud_detection_workflow(self, tmp_path):
        """Test complete fraud detection workflow."""
        # Create synthetic data
        np.random.seed(42)
        df = pd.DataFrame({
            'transaction_id': [f'TXN{i:03d}' for i in range(100)],
            'price_anomaly_score': np.random.uniform(0, 1, 100),
            'route_risk_score': np.random.choice([0, 1], 100),
            'company_network_risk': np.random.uniform(0, 1, 100),
            'port_congestion_score': np.random.uniform(0.5, 3.0, 100),
            'shipment_duration_risk': np.random.uniform(0, 0.5, 100),
            'volume_spike_score': np.random.uniform(1, 100, 100)
        })
        
        # Train and save model
        model = IsolationForest(n_estimators=50, contamination=0.1, random_state=42)
        model.fit(df.drop('transaction_id', axis=1))
        
        model_path = tmp_path / "integration_model.pkl"
        import joblib
        joblib.dump(model, model_path)
        
        # Test complete pipeline
        result_df = safe_fraud_detection_pipeline(df, str(model_path))
        
        # Verify results
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 100
        assert 'risk_score' in result_df.columns
        assert 'risk_category' in result_df.columns
        
        # Check that all categories are strings
        assert all(isinstance(cat, str) for cat in result_df['risk_category'])
        
        # Check that all risk scores are numeric
        assert all(isinstance(score, (int, float)) for score in result_df['risk_score'])
        
        # Verify category distribution makes sense
        category_counts = result_df['risk_category'].value_counts()
        assert len(category_counts) >= 2  # At least 2 different categories


if __name__ == "__main__":
    pytest.main([__file__])