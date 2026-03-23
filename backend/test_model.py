"""
Unit Tests for ML Model Module - TRINETRA AI

This module contains comprehensive unit tests for the model.py module,
testing model training, saving, loading, and evaluation functionality.
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
import joblib
from unittest.mock import patch, MagicMock
from sklearn.ensemble import IsolationForest

# Import the module under test
from backend.model import (
    train_model, save_model, load_model, get_model_info,
    evaluate_model, calculate_feature_importance, FEATURE_COLUMNS
)


class TestModelModule:
    """Test class for ML model functionality."""
    
    @pytest.fixture
    def sample_feature_data(self):
        """Create sample feature data for testing."""
        np.random.seed(42)  # For reproducible tests
        return pd.DataFrame({
            'price_anomaly_score': np.random.uniform(0, 1, 100),
            'route_risk_score': np.random.choice([0, 1], 100),
            'company_network_risk': np.random.uniform(0, 1, 100),
            'port_congestion_score': np.random.uniform(0.5, 3.0, 100),
            'shipment_duration_risk': np.random.uniform(0, 0.5, 100),
            'volume_spike_score': np.random.uniform(1, 100, 100)
        })
    
    @pytest.fixture
    def trained_model(self, sample_feature_data):
        """Create a trained model for testing."""
        return train_model(sample_feature_data)
    
    def test_train_model_success(self, sample_feature_data):
        """Test successful model training."""
        model = train_model(sample_feature_data)
        
        assert isinstance(model, IsolationForest)
        assert hasattr(model, 'estimators_')  # Model should be fitted
        assert model.n_estimators == 100
        assert model.contamination == 0.1
        assert model.random_state == 42
    
    def test_train_model_missing_features(self):
        """Test model training with missing features."""
        # DataFrame missing required features
        df = pd.DataFrame({
            'price_anomaly_score': [0.1, 0.2, 0.3],
            'route_risk_score': [0, 1, 0]
            # Missing other required features
        })
        
        with pytest.raises(ValueError, match="Missing required features"):
            train_model(df)
    
    def test_train_model_empty_dataframe(self):
        """Test model training with empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            train_model(df)
    
    def test_train_model_with_nan_values(self, sample_feature_data):
        """Test model training with NaN values."""
        # Introduce some NaN values
        sample_feature_data.loc[0, 'price_anomaly_score'] = np.nan
        sample_feature_data.loc[1, 'route_risk_score'] = np.nan
        
        model = train_model(sample_feature_data)
        
        assert isinstance(model, IsolationForest)
        assert hasattr(model, 'estimators_')
    
    def test_save_model_success(self, trained_model, tmp_path):
        """Test successful model saving."""
        model_path = tmp_path / "test_model.pkl"
        
        save_model(trained_model, str(model_path))
        
        assert model_path.exists()
        assert model_path.stat().st_size > 0
    
    def test_save_model_create_directory(self, trained_model, tmp_path):
        """Test model saving with directory creation."""
        model_path = tmp_path / "new_dir" / "test_model.pkl"
        
        save_model(trained_model, str(model_path))
        
        assert model_path.exists()
        assert model_path.parent.exists()
    
    def test_save_model_invalid_path(self, trained_model):
        """Test model saving with invalid path."""
        # Try to save to a path that can't be created
        with pytest.raises(RuntimeError):
            save_model(trained_model, "/invalid/path/model.pkl")
    
    def test_load_model_success(self, trained_model, tmp_path):
        """Test successful model loading."""
        model_path = tmp_path / "test_model.pkl"
        save_model(trained_model, str(model_path))
        
        loaded_model = load_model(str(model_path))
        
        assert isinstance(loaded_model, IsolationForest)
        assert loaded_model.n_estimators == trained_model.n_estimators
        assert loaded_model.contamination == trained_model.contamination
    
    def test_load_model_file_not_found(self):
        """Test loading non-existent model file."""
        with pytest.raises(FileNotFoundError):
            load_model("non_existent_model.pkl")
    
    def test_load_model_corrupted_file(self, tmp_path):
        """Test loading corrupted model file."""
        model_path = tmp_path / "corrupted_model.pkl"
        
        # Create a corrupted file
        with open(model_path, 'w') as f:
            f.write("This is not a valid pickle file")
        
        with pytest.raises(RuntimeError):
            load_model(str(model_path))
    
    def test_get_model_info(self, trained_model):
        """Test getting model information."""
        info = get_model_info(trained_model)
        
        assert isinstance(info, dict)
        assert info['model_type'] == 'IsolationForest'
        assert info['n_estimators'] == 100
        assert info['contamination'] == 0.1
        assert info['n_features'] == len(FEATURE_COLUMNS)
        assert info['feature_columns'] == FEATURE_COLUMNS
    
    def test_evaluate_model_success(self, trained_model, sample_feature_data):
        """Test successful model evaluation."""
        evaluation = evaluate_model(trained_model, sample_feature_data)
        
        assert isinstance(evaluation, dict)
        assert 'model_info' in evaluation
        assert 'performance_metrics' in evaluation
        assert 'anomaly_analysis' in evaluation
        assert 'feature_analysis' in evaluation
        
        # Check specific metrics
        assert evaluation['model_info']['n_samples'] == 100
        assert evaluation['model_info']['n_features'] == 6
        assert 'prediction_time_seconds' in evaluation['performance_metrics']
        assert 'anomaly_score_mean' in evaluation['anomaly_analysis']
    
    def test_evaluate_model_with_true_labels(self, trained_model, sample_feature_data):
        """Test model evaluation with true labels."""
        # Create synthetic true labels
        y_true = pd.Series(np.random.choice([-1, 1], 100))  # -1 for anomaly, 1 for normal
        
        evaluation = evaluate_model(trained_model, sample_feature_data, y_true)
        
        assert 'supervised_metrics' in evaluation
        assert 'accuracy' in evaluation['supervised_metrics']
        assert 'precision' in evaluation['supervised_metrics']
        assert 'recall' in evaluation['supervised_metrics']
        assert 'f1_score' in evaluation['supervised_metrics']
    
    def test_evaluate_model_empty_dataframe(self, trained_model):
        """Test model evaluation with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            evaluate_model(trained_model, empty_df)
    
    def test_calculate_feature_importance(self, trained_model, sample_feature_data):
        """Test feature importance calculation."""
        importance = calculate_feature_importance(trained_model, sample_feature_data)
        
        assert isinstance(importance, dict)
        assert 'feature_importance_scores' in importance
        assert 'feature_ranking' in importance
        assert 'most_important_feature' in importance
        assert 'least_important_feature' in importance
        
        # Check that all features are included
        assert len(importance['feature_importance_scores']) == len(FEATURE_COLUMNS)
        assert len(importance['feature_ranking']) == len(FEATURE_COLUMNS)
    
    def test_model_predictions_consistency(self, trained_model, sample_feature_data):
        """Test that model predictions are consistent."""
        # Get predictions twice
        predictions1 = trained_model.predict(sample_feature_data)
        predictions2 = trained_model.predict(sample_feature_data)
        
        # Should be identical (model is deterministic)
        np.testing.assert_array_equal(predictions1, predictions2)
    
    def test_model_decision_function(self, trained_model, sample_feature_data):
        """Test model decision function."""
        scores = trained_model.decision_function(sample_feature_data)
        
        assert isinstance(scores, np.ndarray)
        assert len(scores) == len(sample_feature_data)
        assert not np.isnan(scores).any()  # No NaN values
        assert not np.isinf(scores).any()  # No infinite values


class TestModelEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_train_model_single_row(self):
        """Test model training with single row."""
        df = pd.DataFrame({
            'price_anomaly_score': [0.5],
            'route_risk_score': [1],
            'company_network_risk': [0.3],
            'port_congestion_score': [1.5],
            'shipment_duration_risk': [0.1],
            'volume_spike_score': [10.0]
        })
        
        # Should handle single row gracefully
        model = train_model(df)
        assert isinstance(model, IsolationForest)
    
    def test_train_model_extreme_values(self):
        """Test model training with extreme values."""
        df = pd.DataFrame({
            'price_anomaly_score': [0, 1, 0.5, 1000],  # Including extreme value
            'route_risk_score': [0, 1, 0, 1],
            'company_network_risk': [0, 1, 0.5, 0.8],
            'port_congestion_score': [0.1, 100, 1.5, 2.0],  # Including extreme value
            'shipment_duration_risk': [0, 10, 0.1, 0.5],  # Including extreme value
            'volume_spike_score': [1, 1000, 10, 50]  # Including extreme value
        })
        
        model = train_model(df)
        assert isinstance(model, IsolationForest)
        
        # Model should still make predictions
        predictions = model.predict(df)
        assert len(predictions) == 4
    
    def test_model_serialization_deserialization(self, sample_feature_data, tmp_path):
        """Test complete model serialization and deserialization cycle."""
        # Train model
        original_model = train_model(sample_feature_data)
        
        # Get original predictions
        original_predictions = original_model.predict(sample_feature_data)
        original_scores = original_model.decision_function(sample_feature_data)
        
        # Save and load model
        model_path = tmp_path / "cycle_test_model.pkl"
        save_model(original_model, str(model_path))
        loaded_model = load_model(str(model_path))
        
        # Get loaded model predictions
        loaded_predictions = loaded_model.predict(sample_feature_data)
        loaded_scores = loaded_model.decision_function(sample_feature_data)
        
        # Predictions should be identical
        np.testing.assert_array_equal(original_predictions, loaded_predictions)
        np.testing.assert_array_almost_equal(original_scores, loaded_scores)
    
    def test_model_with_all_same_values(self):
        """Test model training with all identical values."""
        df = pd.DataFrame({
            'price_anomaly_score': [0.5] * 50,
            'route_risk_score': [0] * 50,
            'company_network_risk': [0.3] * 50,
            'port_congestion_score': [1.5] * 50,
            'shipment_duration_risk': [0.1] * 50,
            'volume_spike_score': [10.0] * 50
        })
        
        # Should handle constant features
        model = train_model(df)
        assert isinstance(model, IsolationForest)
        
        # Should still make predictions (though they may not be meaningful)
        predictions = model.predict(df)
        assert len(predictions) == 50
    
    @patch('backend.model.logger')
    def test_logging_functionality(self, mock_logger, sample_feature_data):
        """Test that logging is working correctly."""
        train_model(sample_feature_data)
        
        # Verify that logging calls were made
        assert mock_logger.info.called
        
        # Check for specific log messages
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("STARTING ML MODEL TRAINING SESSION" in call for call in log_calls)
        assert any("MODEL TRAINING SESSION COMPLETED SUCCESSFULLY" in call for call in log_calls)
    
    def test_model_performance_metrics(self, sample_feature_data):
        """Test model performance and timing."""
        import time
        
        start_time = time.time()
        model = train_model(sample_feature_data)
        training_time = time.time() - start_time
        
        # Training should complete within reasonable time
        assert training_time < 10.0  # Less than 10 seconds
        
        # Prediction should be fast
        start_time = time.time()
        predictions = model.predict(sample_feature_data)
        prediction_time = time.time() - start_time
        
        assert prediction_time < 1.0  # Less than 1 second
        assert len(predictions) == len(sample_feature_data)
    
    def test_model_contamination_parameter(self):
        """Test model with different contamination parameters."""
        df = pd.DataFrame({
            'price_anomaly_score': np.random.uniform(0, 1, 100),
            'route_risk_score': np.random.choice([0, 1], 100),
            'company_network_risk': np.random.uniform(0, 1, 100),
            'port_congestion_score': np.random.uniform(0.5, 3.0, 100),
            'shipment_duration_risk': np.random.uniform(0, 0.5, 100),
            'volume_spike_score': np.random.uniform(1, 100, 100)
        })
        
        model = train_model(df)
        predictions = model.predict(df)
        
        # Count anomalies (predictions == -1)
        anomaly_count = np.sum(predictions == -1)
        expected_anomalies = int(len(df) * 0.1)  # 10% contamination
        
        # Should be approximately 10% anomalies (within reasonable range)
        assert abs(anomaly_count - expected_anomalies) <= 5
    
    def test_feature_importance_edge_cases(self, sample_feature_data):
        """Test feature importance calculation with edge cases."""
        # Create model with minimal data
        small_df = sample_feature_data.head(10)
        model = train_model(small_df)
        
        importance = calculate_feature_importance(model, small_df)
        
        assert isinstance(importance, dict)
        assert len(importance['feature_ranking']) == len(FEATURE_COLUMNS)
        
        # All importance scores should sum to approximately 1
        total_importance = sum(importance['feature_importance_scores'].values())
        assert abs(total_importance - 1.0) < 0.01


class TestModelIntegration:
    """Integration tests for model functionality."""
    
    def test_complete_model_workflow(self, tmp_path):
        """Test complete model workflow from training to evaluation."""
        # Create synthetic data
        np.random.seed(42)
        df = pd.DataFrame({
            'price_anomaly_score': np.random.uniform(0, 1, 200),
            'route_risk_score': np.random.choice([0, 1], 200),
            'company_network_risk': np.random.uniform(0, 1, 200),
            'port_congestion_score': np.random.uniform(0.5, 3.0, 200),
            'shipment_duration_risk': np.random.uniform(0, 0.5, 200),
            'volume_spike_score': np.random.uniform(1, 100, 200)
        })
        
        # Step 1: Train model
        model = train_model(df)
        assert isinstance(model, IsolationForest)
        
        # Step 2: Save model
        model_path = tmp_path / "workflow_model.pkl"
        save_model(model, str(model_path))
        assert model_path.exists()
        
        # Step 3: Load model
        loaded_model = load_model(str(model_path))
        assert isinstance(loaded_model, IsolationForest)
        
        # Step 4: Evaluate model
        evaluation = evaluate_model(loaded_model, df)
        assert isinstance(evaluation, dict)
        assert 'model_info' in evaluation
        
        # Step 5: Get model info
        info = get_model_info(loaded_model)
        assert info['model_type'] == 'IsolationForest'
        
        # Step 6: Calculate feature importance
        importance = calculate_feature_importance(loaded_model, df)
        assert isinstance(importance, dict)
        
        # Verify consistency across loaded model
        original_predictions = model.predict(df)
        loaded_predictions = loaded_model.predict(df)
        np.testing.assert_array_equal(original_predictions, loaded_predictions)


if __name__ == "__main__":
    pytest.main([__file__])