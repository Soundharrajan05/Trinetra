"""
Comprehensive Unit Tests for TRINETRA AI Model Module

This module contains unit tests for the ML model functions in model.py.
Tests cover model training, persistence, evaluation, and error handling scenarios.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from sklearn.ensemble import IsolationForest
import joblib

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import (
    train_model,
    save_model,
    load_model,
    get_model_info,
    evaluate_model,
    calculate_feature_importance,
    calculate_supervised_metrics,
    generate_model_report,
    generate_training_report,
    FEATURE_COLUMNS
)


class TestTrainModel:
    """Test cases for the train_model() function."""
    
    def create_valid_training_data(self, num_rows: int = 100) -> pd.DataFrame:
        """Create valid training data with all required features."""
        np.random.seed(42)  # For reproducible tests
        
        data = {}
        for feature in FEATURE_COLUMNS:
            if 'score' in feature or 'risk' in feature:
                # Generate scores between 0 and 1
                data[feature] = np.random.uniform(0, 1, num_rows)
            else:
                # Generate other numeric features
                data[feature] = np.random.uniform(0, 10, num_rows)
        
        return pd.DataFrame(data)
    
    def test_train_model_success(self):
        """Test successful model training with valid data."""
        df = self.create_valid_training_data(200)
        
        model = train_model(df)
        
        # Verify model is trained
        assert isinstance(model, IsolationForest)
        assert hasattr(model, 'estimators_')
        assert len(model.estimators_) == 100  # n_estimators
        assert model.contamination == 0.1
        assert model.random_state == 42
    
    def test_train_model_missing_features(self):
        """Test training fails with missing required features."""
        # Create DataFrame missing some features
        df = pd.DataFrame({
            'price_anomaly_score': [0.1, 0.2, 0.3],
            'route_risk_score': [0.4, 0.5, 0.6]
            # Missing other required features
        })
        
        with pytest.raises(ValueError, match="Missing required features"):
            train_model(df)
    
    def test_train_model_empty_dataframe(self):
        """Test training fails with empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            train_model(df)
    
    def test_train_model_with_nan_values(self):
        """Test training handles NaN values correctly."""
        df = self.create_valid_training_data(100)
        
        # Introduce some NaN values
        df.loc[0:5, 'price_anomaly_score'] = np.nan
        df.loc[10:15, 'route_risk_score'] = np.nan
        
        model = train_model(df)
        
        # Should still train successfully
        assert isinstance(model, IsolationForest)
        assert hasattr(model, 'estimators_')
    
    def test_train_model_small_dataset(self):
        """Test training with minimum viable dataset."""
        df = self.create_valid_training_data(10)  # Very small dataset
        
        model = train_model(df)
        
        # Should still work but may log warnings
        assert isinstance(model, IsolationForest)
    
    def test_train_model_large_dataset(self):
        """Test training with large dataset."""
        df = self.create_valid_training_data(5000)  # Large dataset
        
        model = train_model(df)
        
        assert isinstance(model, IsolationForest)
        assert hasattr(model, 'estimators_')


class TestSaveLoadModel:
    """Test cases for model persistence functions."""
    
    def create_test_model(self) -> IsolationForest:
        """Create a simple trained model for testing."""
        model = IsolationForest(n_estimators=10, contamination=0.1, random_state=42)
        # Create minimal training data
        X = np.random.rand(50, 6)
        model.fit(X)
        return model
    
    def test_save_model_success(self):
        """Test successful model saving."""
        model = self.create_test_model()
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = f.name
        
        try:
            save_model(model, temp_path)
            
            # Verify file was created
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_model_creates_directory(self):
        """Test that save_model creates directory if it doesn't exist."""
        model = self.create_test_model()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = os.path.join(temp_dir, 'subdir', 'model.pkl')
            
            save_model(model, model_path)
            
            assert os.path.exists(model_path)
    
    def test_save_model_invalid_path(self):
        """Test save_model with invalid path."""
        model = self.create_test_model()
        
        # Try to save to a path that can't be created
        invalid_path = "/invalid/path/that/cannot/exist/model.pkl"
        
        with pytest.raises(RuntimeError, match="Failed to save model"):
            save_model(model, invalid_path)
    
    def test_load_model_success(self):
        """Test successful model loading."""
        original_model = self.create_test_model()
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = f.name
        
        try:
            # Save model
            save_model(original_model, temp_path)
            
            # Load model
            loaded_model = load_model(temp_path)
            
            # Verify loaded model
            assert isinstance(loaded_model, IsolationForest)
            assert loaded_model.n_estimators == original_model.n_estimators
            assert loaded_model.contamination == original_model.contamination
            assert loaded_model.random_state == original_model.random_state
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_model_file_not_found(self):
        """Test load_model with non-existent file."""
        with pytest.raises(FileNotFoundError, match="Model file not found"):
            load_model("nonexistent_model.pkl")
    
    def test_load_model_corrupted_file(self):
        """Test load_model with corrupted file."""
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            # Write invalid data
            f.write(b"invalid model data")
            temp_path = f.name
        
        try:
            with pytest.raises(RuntimeError, match="Failed to load model"):
                load_model(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_model_empty_file(self):
        """Test load_model with empty file."""
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(RuntimeError, match="Failed to load model"):
                load_model(temp_path)
        finally:
            os.unlink(temp_path)


class TestGetModelInfo:
    """Test cases for the get_model_info() function."""
    
    def create_test_model(self) -> IsolationForest:
        """Create a test model."""
        model = IsolationForest(n_estimators=50, contamination=0.15, random_state=123)
        X = np.random.rand(100, 6)
        model.fit(X)
        return model
    
    def test_get_model_info_success(self):
        """Test successful model info retrieval."""
        model = self.create_test_model()
        
        info = get_model_info(model)
        
        assert info['model_type'] == 'IsolationForest'
        assert info['n_estimators'] == 50
        assert info['contamination'] == 0.15
        assert info['random_state'] == 123
        assert info['n_features'] == len(FEATURE_COLUMNS)
        assert info['feature_columns'] == FEATURE_COLUMNS
        assert info['n_trained_estimators'] == 50
    
    def test_get_model_info_untrained_model(self):
        """Test model info for untrained model."""
        model = IsolationForest(n_estimators=25, contamination=0.2)
        
        info = get_model_info(model)
        
        assert info['model_type'] == 'IsolationForest'
        assert info['n_estimators'] == 25
        assert info['contamination'] == 0.2
        assert 'n_trained_estimators' not in info  # Not trained yet
    
    def test_get_model_info_error_handling(self):
        """Test error handling in get_model_info."""
        # Test with None
        info = get_model_info(None)
        assert 'error' in info
        
        # Test with invalid object
        info = get_model_info("not a model")
        assert 'error' in info


class TestEvaluateModel:
    """Test cases for the evaluate_model() function."""
    
    def create_test_data(self, n_samples: int = 100) -> tuple:
        """Create test data for evaluation."""
        np.random.seed(42)
        
        # Create feature matrix
        feature_data = {}
        for feature in FEATURE_COLUMNS:
            feature_data[feature] = np.random.uniform(0, 1, n_samples)
        
        X = pd.DataFrame(feature_data)
        
        # Create trained model
        model = IsolationForest(n_estimators=10, contamination=0.1, random_state=42)
        model.fit(X)
        
        # Create optional true labels
        y_true = pd.Series(np.random.choice([-1, 1], n_samples))
        
        return model, X, y_true
    
    def test_evaluate_model_without_labels(self):
        """Test model evaluation without true labels."""
        model, X, _ = self.create_test_data()
        
        results = evaluate_model(model, X)
        
        # Check structure
        assert 'model_info' in results
        assert 'performance_metrics' in results
        assert 'anomaly_analysis' in results
        assert 'feature_analysis' in results
        
        # Check model info
        model_info = results['model_info']
        assert model_info['model_type'] == 'IsolationForest'
        assert model_info['n_samples'] == 100
        assert model_info['n_features'] == len(FEATURE_COLUMNS)
        
        # Check performance metrics
        perf = results['performance_metrics']
        assert 'prediction_time_seconds' in perf
        assert 'predictions_per_second' in perf
        assert perf['prediction_time_seconds'] > 0
        
        # Check anomaly analysis
        anomaly = results['anomaly_analysis']
        assert 'predicted_anomalies' in anomaly
        assert 'predicted_normal' in anomaly
        assert 'actual_contamination_rate' in anomaly
        assert anomaly['predicted_anomalies'] + anomaly['predicted_normal'] == 100
    
    def test_evaluate_model_with_labels(self):
        """Test model evaluation with true labels."""
        model, X, y_true = self.create_test_data()
        
        results = evaluate_model(model, X, y_true)
        
        # Should have supervised metrics
        assert 'supervised_metrics' in results
        
        supervised = results['supervised_metrics']
        if 'error' not in supervised:
            assert 'accuracy' in supervised
            assert 'precision' in supervised
            assert 'recall' in supervised
            assert 'f1_score' in supervised
    
    def test_evaluate_model_empty_data(self):
        """Test evaluation with empty data."""
        model = IsolationForest()
        X = pd.DataFrame()
        
        with pytest.raises(ValueError, match="Feature matrix X cannot be empty"):
            evaluate_model(model, X)
    
    def test_evaluate_model_single_cluster(self):
        """Test evaluation when model predicts only one cluster."""
        # Create data that will likely result in single cluster
        X = pd.DataFrame({col: [0.5] * 10 for col in FEATURE_COLUMNS})
        model = IsolationForest(contamination=0.0, random_state=42)
        model.fit(X)
        
        results = evaluate_model(model, X)
        
        # Should handle single cluster gracefully
        assert results['anomaly_analysis']['silhouette_score'] is None


class TestCalculateFeatureImportance:
    """Test cases for the calculate_feature_importance() function."""
    
    def create_test_setup(self) -> tuple:
        """Create test model and data."""
        np.random.seed(42)
        
        # Create feature data with some features more important than others
        n_samples = 200
        feature_data = {}
        
        for i, feature in enumerate(FEATURE_COLUMNS):
            if i == 0:  # Make first feature more important
                feature_data[feature] = np.random.normal(0, 2, n_samples)
            else:
                feature_data[feature] = np.random.normal(0, 0.5, n_samples)
        
        X = pd.DataFrame(feature_data)
        
        model = IsolationForest(n_estimators=10, contamination=0.1, random_state=42)
        model.fit(X)
        
        return model, X
    
    def test_calculate_feature_importance_success(self):
        """Test successful feature importance calculation."""
        model, X = self.create_test_setup()
        
        importance = calculate_feature_importance(model, X)
        
        # Check structure
        assert 'feature_importance_scores' in importance
        assert 'feature_ranking' in importance
        assert 'most_important_feature' in importance
        assert 'least_important_feature' in importance
        
        # Check that all features are included
        scores = importance['feature_importance_scores']
        assert len(scores) == len(FEATURE_COLUMNS)
        for feature in FEATURE_COLUMNS:
            assert feature in scores
            assert 0 <= scores[feature] <= 1
        
        # Check that scores sum to approximately 1
        total_score = sum(scores.values())
        assert abs(total_score - 1.0) < 0.01
        
        # Check ranking
        ranking = importance['feature_ranking']
        assert len(ranking) == len(FEATURE_COLUMNS)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in ranking)
        
        # Check that ranking is sorted (highest first)
        scores_in_ranking = [score for _, score in ranking]
        assert scores_in_ranking == sorted(scores_in_ranking, reverse=True)
    
    def test_calculate_feature_importance_error_handling(self):
        """Test error handling in feature importance calculation."""
        # Test with invalid model
        X = pd.DataFrame({col: [1, 2, 3] for col in FEATURE_COLUMNS})
        
        result = calculate_feature_importance(None, X)
        assert 'error' in result
    
    def test_calculate_feature_importance_single_sample(self):
        """Test feature importance with single sample."""
        X = pd.DataFrame({col: [0.5] for col in FEATURE_COLUMNS})
        model = IsolationForest(n_estimators=5, random_state=42)
        model.fit(X)
        
        importance = calculate_feature_importance(model, X)
        
        # Should handle gracefully
        assert 'feature_importance_scores' in importance


class TestCalculateSupervisedMetrics:
    """Test cases for the calculate_supervised_metrics() function."""
    
    def test_calculate_supervised_metrics_perfect_prediction(self):
        """Test metrics with perfect predictions."""
        y_true = np.array([1, 1, -1, -1, 1, -1])
        predictions = np.array([1, 1, -1, -1, 1, -1])
        
        metrics = calculate_supervised_metrics(predictions, y_true)
        
        assert metrics['accuracy'] == 1.0
        assert metrics['precision'] == 1.0
        assert metrics['recall'] == 1.0
        assert metrics['f1_score'] == 1.0
        
        # Check confusion matrix
        cm = metrics['confusion_matrix']
        assert cm['true_positive'] == 3  # Correctly identified anomalies
        assert cm['true_negative'] == 3  # Correctly identified normal
        assert cm['false_positive'] == 0
        assert cm['false_negative'] == 0
    
    def test_calculate_supervised_metrics_mixed_prediction(self):
        """Test metrics with mixed predictions."""
        y_true = np.array([1, 1, 1, -1, -1, -1])
        predictions = np.array([1, 1, -1, -1, -1, 1])  # 2 errors
        
        metrics = calculate_supervised_metrics(predictions, y_true)
        
        assert 0 < metrics['accuracy'] < 1
        assert 0 < metrics['precision'] <= 1
        assert 0 < metrics['recall'] <= 1
        assert 0 < metrics['f1_score'] <= 1
        
        # Check that all metrics are reasonable
        assert all(0 <= v <= 1 for k, v in metrics.items() 
                  if k not in ['confusion_matrix', 'support'])
    
    def test_calculate_supervised_metrics_all_normal(self):
        """Test metrics when all samples are predicted as normal."""
        y_true = np.array([1, -1, 1, -1])
        predictions = np.array([1, 1, 1, 1])  # All predicted as normal
        
        metrics = calculate_supervised_metrics(predictions, y_true)
        
        # Precision should be 0 (no true positives)
        assert metrics['precision'] == 0.0
        # Recall should be 0 (no anomalies detected)
        assert metrics['recall'] == 0.0
    
    def test_calculate_supervised_metrics_error_handling(self):
        """Test error handling in supervised metrics calculation."""
        # Test with mismatched lengths
        y_true = np.array([1, -1])
        predictions = np.array([1, -1, 1])
        
        result = calculate_supervised_metrics(predictions, y_true)
        assert 'error' in result


class TestGenerateModelReport:
    """Test cases for the generate_model_report() function."""
    
    def create_test_setup(self) -> tuple:
        """Create test model and data for report generation."""
        np.random.seed(42)
        
        feature_data = {col: np.random.uniform(0, 1, 100) for col in FEATURE_COLUMNS}
        X = pd.DataFrame(feature_data)
        
        model = IsolationForest(n_estimators=10, contamination=0.1, random_state=42)
        model.fit(X)
        
        y_true = pd.Series(np.random.choice([-1, 1], 100))
        
        return model, X, y_true
    
    def test_generate_model_report_without_labels(self):
        """Test report generation without true labels."""
        model, X, _ = self.create_test_setup()
        
        report = generate_model_report(model, X)
        
        # Check that report is a string
        assert isinstance(report, str)
        assert len(report) > 0
        
        # Check for key sections
        assert "MODEL INFORMATION" in report
        assert "PERFORMANCE METRICS" in report
        assert "ANOMALY DETECTION ANALYSIS" in report
        assert "FEATURE IMPORTANCE ANALYSIS" in report
        
        # Check for specific values
        assert "IsolationForest" in report
        assert "10" in report  # n_estimators
        assert "0.1" in report  # contamination
    
    def test_generate_model_report_with_labels(self):
        """Test report generation with true labels."""
        model, X, y_true = self.create_test_setup()
        
        report = generate_model_report(model, X, y_true)
        
        # Should include supervised metrics section
        assert "SUPERVISED LEARNING METRICS" in report
        assert "Accuracy" in report
        assert "Precision" in report
        assert "Confusion Matrix" in report
    
    def test_generate_model_report_error_handling(self):
        """Test report generation error handling."""
        # Test with invalid inputs
        report = generate_model_report(None, pd.DataFrame())
        
        assert isinstance(report, str)
        assert "Error generating report" in report


class TestGenerateTrainingReport:
    """Test cases for the generate_training_report() function."""
    
    def test_generate_training_report_success(self):
        """Test successful training report generation."""
        # Create mock data
        model = IsolationForest(n_estimators=10, contamination=0.1, random_state=42)
        X = pd.DataFrame({col: np.random.rand(50) for col in FEATURE_COLUMNS})
        predictions = np.array([1] * 45 + [-1] * 5)  # 10% anomalies
        anomaly_scores = np.random.uniform(-0.5, 0.5, 50)
        training_time = 2.5
        total_time = 3.0
        feature_importance = {
            'feature_ranking': [(col, 0.1) for col in FEATURE_COLUMNS],
            'most_important_feature': FEATURE_COLUMNS[0],
            'least_important_feature': FEATURE_COLUMNS[-1]
        }
        
        report = generate_training_report(
            model, X, predictions, anomaly_scores, 
            training_time, total_time, feature_importance
        )
        
        # Check report structure
        assert isinstance(report, str)
        assert len(report) > 0
        
        # Check for key sections
        assert "TRAINING SESSION INFORMATION" in report
        assert "DATASET INFORMATION" in report
        assert "MODEL CONFIGURATION" in report
        assert "TRAINING RESULTS" in report
        assert "FEATURE IMPORTANCE RANKING" in report
        assert "PERFORMANCE METRICS" in report
        
        # Check for specific values
        assert "2.5" in report  # training time
        assert "3.0" in report  # total time
        assert "50" in report   # sample count
    
    def test_generate_training_report_error_handling(self):
        """Test training report error handling."""
        # Test with invalid inputs
        report = generate_training_report(None, None, None, None, 0, 0, None)
        
        assert isinstance(report, str)
        assert "Error generating training report" in report


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])