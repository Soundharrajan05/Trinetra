"""
Comprehensive Unit Tests for TRINETRA AI Fraud Detection Module

This module contains unit tests for the fraud detection functions in fraud_detection.py.
Tests cover model loading, transaction scoring, risk classification, and error handling.
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

from fraud_detection import (
    load_fraud_detector,
    score_transactions,
    get_risk_category,
    classify_risk,
    create_fallback_model,
    validate_dataframe_schema,
    safe_fraud_detection_pipeline,
    _rule_based_fraud_classification
)


class TestLoadFraudDetector:
    """Test cases for the load_fraud_detector() function."""
    
    def create_test_model(self) -> IsolationForest:
        """Create a test model for saving/loading."""
        model = IsolationForest(n_estimators=10, contamination=0.1, random_state=42)
        # Fit with dummy data to make it a trained model
        X = np.random.rand(50, 6)
        model.fit(X)
        return model
    
    def test_load_fraud_detector_success(self):
        """Test successful model loading."""
        model = self.create_test_model()
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = f.name
        
        try:
            # Save model
            joblib.dump(model, temp_path)
            
            # Load model
            loaded_model = load_fraud_detector(temp_path)
            
            assert isinstance(loaded_model, IsolationForest)
            assert loaded_model.n_estimators == 10
            assert loaded_model.contamination == 0.1
            assert hasattr(loaded_model, 'estimators_')
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_fraud_detector_file_not_found(self):
        """Test loading with non-existent file."""
        with pytest.raises(FileNotFoundError, match="Model file not found"):
            load_fraud_detector("nonexistent_model.pkl")
    
    def test_load_fraud_detector_alternative_paths(self):
        """Test loading with alternative paths when default fails."""
        # This tests the fallback logic for finding models in alternative locations
        with pytest.raises(FileNotFoundError):
            load_fraud_detector("models/isolation_forest.pkl")
    
    def test_load_fraud_detector_corrupted_file(self):
        """Test loading corrupted model file."""
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            f.write(b"corrupted data")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="appears to be corrupted"):
                load_fraud_detector(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_fraud_detector_empty_file(self):
        """Test loading empty model file."""
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="is empty"):
                load_fraud_detector(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_fraud_detector_wrong_model_type(self):
        """Test loading file with wrong model type."""
        wrong_model = "not a model"
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = f.name
        
        try:
            joblib.dump(wrong_model, temp_path)
            
            with pytest.raises(ValueError, match="Expected IsolationForest model"):
                load_fraud_detector(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_fraud_detector_unfitted_model(self):
        """Test loading unfitted model."""
        unfitted_model = IsolationForest()
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = f.name
        
        try:
            joblib.dump(unfitted_model, temp_path)
            
            with pytest.raises(ValueError, match="Model has not been fitted"):
                load_fraud_detector(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_fraud_detector_invalid_path_type(self):
        """Test loading with invalid path type."""
        with pytest.raises(ValueError, match="Model path must be a non-empty string"):
            load_fraud_detector(None)
        
        with pytest.raises(ValueError, match="Model path must be a non-empty string"):
            load_fraud_detector("")


class TestScoreTransactions:
    """Test cases for the score_transactions() function."""
    
    def create_test_model(self) -> IsolationForest:
        """Create a trained test model."""
        model = IsolationForest(n_estimators=10, contamination=0.1, random_state=42)
        # Train with dummy data
        X = np.random.rand(100, 6)
        model.fit(X)
        return model
    
    def create_test_dataframe(self, num_rows: int = 50) -> pd.DataFrame:
        """Create test DataFrame with required features."""
        np.random.seed(42)
        
        feature_columns = [
            'price_anomaly_score',
            'route_risk_score', 
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        
        data = {}
        for col in feature_columns:
            data[col] = np.random.uniform(0, 1, num_rows)
        
        # Add some additional columns
        data['transaction_id'] = [f'TXN{i:03d}' for i in range(num_rows)]
        data['product'] = [f'Product_{i % 5}' for i in range(num_rows)]
        
        return pd.DataFrame(data)
    
    def test_score_transactions_success(self):
        """Test successful transaction scoring."""
        model = self.create_test_model()
        df = self.create_test_dataframe(100)
        
        result_df = score_transactions(df, model)
        
        # Check that risk_score column was added
        assert 'risk_score' in result_df.columns
        assert len(result_df) == 100
        
        # Check that risk scores are numeric
        assert pd.api.types.is_numeric_dtype(result_df['risk_score'])
        
        # Check that all scores are finite
        assert result_df['risk_score'].isna().sum() == 0
        assert np.isfinite(result_df['risk_score']).all()
        
        # Check that original columns are preserved
        assert 'transaction_id' in result_df.columns
        assert 'product' in result_df.columns
    
    def test_score_transactions_empty_dataframe(self):
        """Test scoring with empty DataFrame."""
        model = self.create_test_model()
        df = pd.DataFrame()
        
        result_df = score_transactions(df, model)
        
        assert len(result_df) == 0
        assert 'risk_score' in result_df.columns
    
    def test_score_transactions_missing_features(self):
        """Test scoring with missing required features."""
        model = self.create_test_model()
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'price_anomaly_score': [0.1, 0.2]
            # Missing other required features
        })
        
        with pytest.raises(ValueError, match="Missing required features"):
            score_transactions(df, model)
    
    def test_score_transactions_with_missing_values(self):
        """Test scoring with missing values in features."""
        model = self.create_test_model()
        df = self.create_test_dataframe(50)
        
        # Introduce missing values
        df.loc[0:5, 'price_anomaly_score'] = np.nan
        df.loc[10:15, 'route_risk_score'] = np.nan
        
        result_df = score_transactions(df, model)
        
        # Should handle missing values and still produce scores
        assert 'risk_score' in result_df.columns
        assert len(result_df) == 50
        assert result_df['risk_score'].isna().sum() == 0
    
    def test_score_transactions_with_infinite_values(self):
        """Test scoring with infinite values in features."""
        model = self.create_test_model()
        df = self.create_test_dataframe(20)
        
        # Introduce infinite values
        df.loc[0, 'price_anomaly_score'] = float('inf')
        df.loc[1, 'route_risk_score'] = float('-inf')
        
        result_df = score_transactions(df, model)
        
        # Should handle infinite values
        assert 'risk_score' in result_df.columns
        assert len(result_df) == 20
        assert np.isfinite(result_df['risk_score']).all()
    
    def test_score_transactions_invalid_inputs(self):
        """Test scoring with invalid inputs."""
        model = self.create_test_model()
        
        # Test with None DataFrame
        with pytest.raises(ValueError, match="DataFrame cannot be None"):
            score_transactions(None, model)
        
        # Test with wrong DataFrame type
        with pytest.raises(TypeError, match="Expected pandas DataFrame"):
            score_transactions("not a dataframe", model)
        
        # Test with None model
        df = self.create_test_dataframe(10)
        with pytest.raises(ValueError, match="Model cannot be None"):
            score_transactions(df, None)
        
        # Test with wrong model type
        with pytest.raises(TypeError, match="Expected IsolationForest model"):
            score_transactions(df, "not a model")
    
    def test_score_transactions_non_numeric_features(self):
        """Test scoring with non-numeric feature values."""
        model = self.create_test_model()
        df = self.create_test_dataframe(10)
        
        # Make one feature non-numeric
        df['price_anomaly_score'] = ['high', 'low', 'medium'] * 3 + ['high']
        
        result_df = score_transactions(df, model)
        
        # Should convert to numeric and handle gracefully
        assert 'risk_score' in result_df.columns
        assert len(result_df) == 10


class TestGetRiskCategory:
    """Test cases for the get_risk_category() function."""
    
    def test_get_risk_category_safe(self):
        """Test risk category for SAFE scores."""
        assert get_risk_category(-0.5) == "SAFE"
        assert get_risk_category(-0.3) == "SAFE"
        assert get_risk_category(-0.21) == "SAFE"
    
    def test_get_risk_category_suspicious(self):
        """Test risk category for SUSPICIOUS scores."""
        assert get_risk_category(-0.2) == "SUSPICIOUS"
        assert get_risk_category(-0.1) == "SUSPICIOUS"
        assert get_risk_category(0.0) == "SUSPICIOUS"
        assert get_risk_category(0.1) == "SUSPICIOUS"
        assert get_risk_category(0.19) == "SUSPICIOUS"
    
    def test_get_risk_category_fraud(self):
        """Test risk category for FRAUD scores."""
        assert get_risk_category(0.2) == "FRAUD"
        assert get_risk_category(0.3) == "FRAUD"
        assert get_risk_category(0.5) == "FRAUD"
        assert get_risk_category(1.0) == "FRAUD"
    
    def test_get_risk_category_boundary_conditions(self):
        """Test risk category at exact boundary values."""
        assert get_risk_category(-0.2) == "SUSPICIOUS"  # Exactly at boundary
        assert get_risk_category(0.2) == "FRAUD"        # Exactly at boundary
    
    def test_get_risk_category_special_values(self):
        """Test risk category with special values."""
        assert get_risk_category(None) == "SUSPICIOUS"
        assert get_risk_category(np.nan) == "SUSPICIOUS"
        assert get_risk_category(float('inf')) == "FRAUD"
        assert get_risk_category(float('-inf')) == "SAFE"
    
    def test_get_risk_category_string_conversion(self):
        """Test risk category with string inputs."""
        assert get_risk_category("0.5") == "FRAUD"
        assert get_risk_category("-0.3") == "SAFE"
        assert get_risk_category("0.1") == "SUSPICIOUS"
    
    def test_get_risk_category_invalid_inputs(self):
        """Test risk category with invalid inputs."""
        assert get_risk_category("invalid") == "SUSPICIOUS"
        assert get_risk_category([1, 2, 3]) == "SUSPICIOUS"
        assert get_risk_category({"score": 0.5}) == "SUSPICIOUS"


class TestClassifyRisk:
    """Test cases for the classify_risk() function."""
    
    def create_test_dataframe_with_scores(self, num_rows: int = 20) -> pd.DataFrame:
        """Create test DataFrame with risk scores."""
        np.random.seed(42)
        
        data = {
            'transaction_id': [f'TXN{i:03d}' for i in range(num_rows)],
            'risk_score': np.random.uniform(-0.5, 0.5, num_rows)
        }
        
        return pd.DataFrame(data)
    
    def test_classify_risk_success(self):
        """Test successful risk classification."""
        df = self.create_test_dataframe_with_scores(50)
        
        result_df = classify_risk(df)
        
        # Check that risk_category column was added
        assert 'risk_category' in result_df.columns
        assert len(result_df) == 50
        
        # Check that all categories are valid
        valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
        actual_categories = set(result_df['risk_category'].unique())
        assert actual_categories.issubset(valid_categories)
        
        # Check that original columns are preserved
        assert 'transaction_id' in result_df.columns
        assert 'risk_score' in result_df.columns
    
    def test_classify_risk_specific_scores(self):
        """Test classification with specific score values."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003', 'TXN004'],
            'risk_score': [-0.3, -0.1, 0.1, 0.3]
        })
        
        result_df = classify_risk(df)
        
        expected_categories = ['SAFE', 'SUSPICIOUS', 'SUSPICIOUS', 'FRAUD']
        actual_categories = result_df['risk_category'].tolist()
        
        assert actual_categories == expected_categories
    
    def test_classify_risk_empty_dataframe(self):
        """Test classification with empty DataFrame."""
        df = pd.DataFrame()
        
        result_df = classify_risk(df)
        
        assert len(result_df) == 0
        assert 'risk_category' in result_df.columns
    
    def test_classify_risk_missing_risk_score(self):
        """Test classification without risk_score column."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'product': ['A', 'B']
        })
        
        with pytest.raises(ValueError, match="must contain 'risk_score' column"):
            classify_risk(df)
    
    def test_classify_risk_with_missing_scores(self):
        """Test classification with missing risk scores."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'risk_score': [0.1, np.nan, 0.3]
        })
        
        result_df = classify_risk(df)
        
        # Should handle missing values
        assert 'risk_category' in result_df.columns
        assert len(result_df) == 3
        assert result_df['risk_category'].isna().sum() == 0  # Should fill missing
    
    def test_classify_risk_non_numeric_scores(self):
        """Test classification with non-numeric risk scores."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'risk_score': ['high', 'low']
        })
        
        result_df = classify_risk(df)
        
        # Should handle conversion and classify
        assert 'risk_category' in result_df.columns
        assert len(result_df) == 2
    
    def test_classify_risk_invalid_inputs(self):
        """Test classification with invalid inputs."""
        # Test with None
        with pytest.raises(ValueError, match="DataFrame cannot be None"):
            classify_risk(None)
        
        # Test with wrong type
        with pytest.raises(TypeError, match="Expected pandas DataFrame"):
            classify_risk("not a dataframe")


class TestCreateFallbackModel:
    """Test cases for the create_fallback_model() function."""
    
    def test_create_fallback_model_success(self):
        """Test successful fallback model creation."""
        model = create_fallback_model()
        
        assert isinstance(model, IsolationForest)
        assert model.n_estimators == 100
        assert model.contamination == 0.1
        assert model.random_state == 42
        assert model.n_jobs == 1


class TestValidateDataframeSchema:
    """Test cases for the validate_dataframe_schema() function."""
    
    def create_valid_dataframe(self) -> pd.DataFrame:
        """Create DataFrame with valid schema."""
        feature_columns = [
            'price_anomaly_score',
            'route_risk_score', 
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        
        data = {col: [0.1, 0.2, 0.3] for col in feature_columns}
        return pd.DataFrame(data)
    
    def test_validate_dataframe_schema_valid(self):
        """Test validation with valid DataFrame."""
        df = self.create_valid_dataframe()
        
        is_valid, missing_cols = validate_dataframe_schema(df)
        
        assert is_valid is True
        assert missing_cols == []
    
    def test_validate_dataframe_schema_missing_columns(self):
        """Test validation with missing columns."""
        df = pd.DataFrame({
            'price_anomaly_score': [0.1, 0.2],
            'route_risk_score': [0.3, 0.4]
            # Missing other required columns
        })
        
        is_valid, missing_cols = validate_dataframe_schema(df)
        
        assert is_valid is False
        assert len(missing_cols) > 0
    
    def test_validate_dataframe_schema_empty(self):
        """Test validation with empty DataFrame."""
        df = pd.DataFrame()
        
        is_valid, missing_cols = validate_dataframe_schema(df)
        
        assert is_valid is True  # Empty is considered valid
        assert missing_cols == []
    
    def test_validate_dataframe_schema_none(self):
        """Test validation with None DataFrame."""
        is_valid, missing_cols = validate_dataframe_schema(None)
        
        assert is_valid is False
        assert len(missing_cols) > 0
    
    def test_validate_dataframe_schema_custom_columns(self):
        """Test validation with custom required columns."""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6]
        })
        
        required_cols = ['col1', 'col2', 'col3']
        is_valid, missing_cols = validate_dataframe_schema(df, required_cols)
        
        assert is_valid is False
        assert 'col3' in missing_cols


class TestSafeFraudDetectionPipeline:
    """Test cases for the safe_fraud_detection_pipeline() function."""
    
    def create_test_model_file(self) -> str:
        """Create a temporary model file for testing."""
        model = IsolationForest(n_estimators=5, contamination=0.1, random_state=42)
        X = np.random.rand(50, 6)
        model.fit(X)
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.pkl', delete=False)
        joblib.dump(model, temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    def create_valid_dataframe(self) -> pd.DataFrame:
        """Create valid DataFrame for pipeline testing."""
        feature_columns = [
            'price_anomaly_score',
            'route_risk_score', 
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        
        np.random.seed(42)
        data = {col: np.random.uniform(0, 1, 20) for col in feature_columns}
        data['transaction_id'] = [f'TXN{i:03d}' for i in range(20)]
        
        return pd.DataFrame(data)
    
    def test_safe_fraud_detection_pipeline_success(self):
        """Test successful pipeline execution."""
        model_path = self.create_test_model_file()
        df = self.create_valid_dataframe()
        
        try:
            result_df = safe_fraud_detection_pipeline(df, model_path)
            
            # Check that both risk_score and risk_category were added
            assert 'risk_score' in result_df.columns
            assert 'risk_category' in result_df.columns
            assert len(result_df) == 20
            
            # Check that categories are valid
            valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
            actual_categories = set(result_df['risk_category'].unique())
            assert actual_categories.issubset(valid_categories)
            
        finally:
            os.unlink(model_path)
    
    def test_safe_fraud_detection_pipeline_model_not_found(self):
        """Test pipeline with non-existent model file."""
        df = self.create_valid_dataframe()
        
        result_df = safe_fraud_detection_pipeline(df, "nonexistent_model.pkl")
        
        # Should fall back to rule-based classification
        assert 'risk_score' in result_df.columns
        assert 'risk_category' in result_df.columns
        assert len(result_df) == 20
    
    def test_safe_fraud_detection_pipeline_invalid_dataframe(self):
        """Test pipeline with invalid DataFrame."""
        model_path = self.create_test_model_file()
        
        try:
            # Test with None
            with pytest.raises(ValueError, match="Input DataFrame is empty or None"):
                safe_fraud_detection_pipeline(None, model_path)
            
            # Test with empty DataFrame
            with pytest.raises(ValueError, match="Input DataFrame is empty or None"):
                safe_fraud_detection_pipeline(pd.DataFrame(), model_path)
            
        finally:
            os.unlink(model_path)
    
    def test_safe_fraud_detection_pipeline_missing_features(self):
        """Test pipeline with missing required features."""
        model_path = self.create_test_model_file()
        df = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'price_anomaly_score': [0.1]
            # Missing other required features
        })
        
        try:
            with pytest.raises(ValueError, match="Missing required columns"):
                safe_fraud_detection_pipeline(df, model_path)
        finally:
            os.unlink(model_path)


class TestRuleBasedFraudClassification:
    """Test cases for the _rule_based_fraud_classification() function."""
    
    def create_test_dataframe(self) -> pd.DataFrame:
        """Create test DataFrame for rule-based classification."""
        feature_columns = [
            'price_anomaly_score',
            'route_risk_score', 
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        
        np.random.seed(42)
        data = {col: np.random.uniform(0, 1, 10) for col in feature_columns}
        data['transaction_id'] = [f'TXN{i:03d}' for i in range(10)]
        
        return pd.DataFrame(data)
    
    def test_rule_based_fraud_classification_success(self):
        """Test successful rule-based classification."""
        df = self.create_test_dataframe()
        
        result_df = _rule_based_fraud_classification(df)
        
        # Check that risk_score and risk_category were added
        assert 'risk_score' in result_df.columns
        assert 'risk_category' in result_df.columns
        assert len(result_df) == 10
        
        # Check that scores are numeric
        assert pd.api.types.is_numeric_dtype(result_df['risk_score'])
        
        # Check that categories are valid
        valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
        actual_categories = set(result_df['risk_category'].unique())
        assert actual_categories.issubset(valid_categories)
    
    def test_rule_based_fraud_classification_missing_features(self):
        """Test rule-based classification with missing features."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'price_anomaly_score': [0.1, 0.2]
            # Missing other features
        })
        
        result_df = _rule_based_fraud_classification(df)
        
        # Should handle missing features gracefully
        assert 'risk_score' in result_df.columns
        assert 'risk_category' in result_df.columns
        assert len(result_df) == 2


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])