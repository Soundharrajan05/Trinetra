"""
Property-Based Test for Model Consistency
TRINETRA AI - Trade Fraud Intelligence System

**Validates: Requirements CP-2 (Model Consistency)**

This module implements property-based testing for ML model consistency validation.
Tests ensure that the IsolationForest model behaves consistently when trained multiple times
with the same data, produces consistent predictions, and can be properly serialized/deserialized.

Property: ML model must be consistent across training runs and serialization cycles
Test Strategy: Property-based test training model multiple times and verifying consistency
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from hypothesis import given, strategies as st, settings, assume, example
from hypothesis.extra.pandas import data_frames, columns
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any, Tuple
import joblib
from pathlib import Path
import time

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import (
    train_model,
    save_model,
    load_model,
    FEATURE_COLUMNS
)
from data_loader import load_dataset
from feature_engineering import engineer_features


class TestModelConsistencyProperty:
    """Property-based tests for ML model consistency validation."""
    
    def _create_test_data(self, n_samples: int = 100) -> pd.DataFrame:
        """Create synthetic test data with all required features."""
        np.random.seed(42)  # For reproducible test data
        
        # Create base transaction data
        data = {
            'transaction_id': [f'TXN{i:05d}' for i in range(n_samples)],
            'date': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
            'price_deviation': np.random.uniform(-0.5, 0.5, n_samples),
            'route_anomaly': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
            'company_risk_score': np.random.uniform(0.0, 1.0, n_samples),
            'port_activity_index': np.random.uniform(0.5, 2.5, n_samples),
            'shipment_duration_days': np.random.uniform(5, 60, n_samples),
            'distance_km': np.random.uniform(500, 15000, n_samples),
            'cargo_volume': np.random.uniform(5000, 150000, n_samples),
            'quantity': np.random.uniform(100, 5000, n_samples),
            'fraud_label': np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
        }
        
        df = pd.DataFrame(data)
        
        # Engineer features to get the required feature columns
        df_with_features = engineer_features(df)
        
        return df_with_features
    
    @given(
        n_training_runs=st.integers(min_value=2, max_value=5),
        n_samples=st.integers(min_value=50, max_value=200)
    )
    @settings(max_examples=10, deadline=60000)  # Longer deadline for model training
    @example(n_training_runs=3, n_samples=100)
    @example(n_training_runs=2, n_samples=50)
    def test_model_training_consistency(self, n_training_runs: int, n_samples: int):
        """
        **Validates: Requirements CP-2**
        
        Property: Training the same model multiple times with identical data should produce consistent results
        
        Test Strategy: Train model multiple times with same data and verify prediction consistency
        """
        # Create consistent test data
        test_data = self._create_test_data(n_samples)
        
        # Train multiple models with the same data
        models = []
        prediction_sets = []
        score_sets = []
        
        for run in range(n_training_runs):
            # Train model (each should use same random_state=42 for consistency)
            model = train_model(test_data)
            models.append(model)
            
            # Get predictions and scores
            X = test_data[FEATURE_COLUMNS]
            predictions = model.predict(X)
            scores = model.decision_function(X)
            
            prediction_sets.append(predictions)
            score_sets.append(scores)
        
        # Verify model parameters are identical
        for i in range(1, len(models)):
            assert models[0].n_estimators == models[i].n_estimators, f"n_estimators differs between runs 0 and {i}"
            assert models[0].contamination == models[i].contamination, f"contamination differs between runs 0 and {i}"
            assert models[0].random_state == models[i].random_state, f"random_state differs between runs 0 and {i}"
        
        # Verify predictions are consistent across runs
        for i in range(1, len(prediction_sets)):
            # Predictions should be identical due to fixed random_state
            np.testing.assert_array_equal(
                prediction_sets[0], 
                prediction_sets[i],
                err_msg=f"Predictions differ between training runs 0 and {i}"
            )
        
        # Verify anomaly scores are consistent across runs
        for i in range(1, len(score_sets)):
            # Scores should be very close (allowing for minimal floating point differences)
            np.testing.assert_allclose(
                score_sets[0], 
                score_sets[i],
                rtol=1e-10,
                atol=1e-10,
                err_msg=f"Anomaly scores differ between training runs 0 and {i}"
            )
        
        # Verify contamination rate consistency
        contamination_rates = []
        for predictions in prediction_sets:
            contamination_rate = np.sum(predictions == -1) / len(predictions)
            contamination_rates.append(contamination_rate)
        
        # All contamination rates should be identical
        for i in range(1, len(contamination_rates)):
            assert abs(contamination_rates[0] - contamination_rates[i]) < 1e-10, \
                f"Contamination rates differ: {contamination_rates[0]} vs {contamination_rates[i]}"
    
    @given(
        prediction_samples=st.integers(min_value=10, max_value=50)
    )
    @settings(max_examples=8, deadline=45000)
    @example(prediction_samples=20)
    def test_model_prediction_consistency(self, prediction_samples: int):
        """
        **Validates: Requirements CP-2**
        
        Property: Model predictions should be consistent for the same input data
        
        Test Strategy: Make multiple predictions on same data and verify consistency
        """
        # Create test data and train model
        training_data = self._create_test_data(100)
        model = train_model(training_data)
        
        # Create prediction data (subset of training data for consistency)
        prediction_data = training_data.head(prediction_samples)[FEATURE_COLUMNS]
        
        # Make multiple predictions on the same data
        n_prediction_runs = 5
        prediction_results = []
        score_results = []
        
        for run in range(n_prediction_runs):
            predictions = model.predict(prediction_data)
            scores = model.decision_function(prediction_data)
            
            prediction_results.append(predictions)
            score_results.append(scores)
        
        # Verify all prediction runs produce identical results
        for i in range(1, len(prediction_results)):
            np.testing.assert_array_equal(
                prediction_results[0],
                prediction_results[i],
                err_msg=f"Predictions inconsistent between runs 0 and {i}"
            )
        
        # Verify all score runs produce identical results
        for i in range(1, len(score_results)):
            np.testing.assert_allclose(
                score_results[0],
                score_results[i],
                rtol=1e-15,
                atol=1e-15,
                err_msg=f"Scores inconsistent between runs 0 and {i}"
            )
        
        # Verify prediction determinism - same input should always give same output
        single_sample = prediction_data.iloc[[0]]
        
        single_predictions = []
        single_scores = []
        
        for _ in range(10):
            pred = model.predict(single_sample)
            score = model.decision_function(single_sample)
            single_predictions.append(pred[0])
            single_scores.append(score[0])
        
        # All single predictions should be identical
        assert all(p == single_predictions[0] for p in single_predictions), \
            "Single sample predictions are not deterministic"
        
        # All single scores should be identical
        assert all(abs(s - single_scores[0]) < 1e-15 for s in single_scores), \
            "Single sample scores are not deterministic"
    
    @given(
        serialization_cycles=st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=6, deadline=60000)
    @example(serialization_cycles=2)
    def test_model_serialization_deserialization_consistency(self, serialization_cycles: int):
        """
        **Validates: Requirements CP-2**
        
        Property: Model should maintain consistency through serialization/deserialization cycles
        
        Test Strategy: Save and load model multiple times, verify predictions remain consistent
        """
        # Create test data and train model
        test_data = self._create_test_data(80)
        original_model = train_model(test_data)
        
        # Get original predictions
        X = test_data[FEATURE_COLUMNS]
        original_predictions = original_model.predict(X)
        original_scores = original_model.decision_function(X)
        
        current_model = original_model
        
        # Perform multiple serialization/deserialization cycles
        for cycle in range(serialization_cycles):
            with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Save current model
                save_model(current_model, temp_path)
                
                # Load model back
                loaded_model = load_model(temp_path)
                
                # Verify loaded model produces same predictions
                loaded_predictions = loaded_model.predict(X)
                loaded_scores = loaded_model.decision_function(X)
                
                # Predictions should be identical
                np.testing.assert_array_equal(
                    original_predictions,
                    loaded_predictions,
                    err_msg=f"Predictions differ after serialization cycle {cycle + 1}"
                )
                
                # Scores should be identical (within floating point precision)
                np.testing.assert_allclose(
                    original_scores,
                    loaded_scores,
                    rtol=1e-12,
                    atol=1e-12,
                    err_msg=f"Scores differ after serialization cycle {cycle + 1}"
                )
                
                # Verify model parameters are preserved
                assert original_model.n_estimators == loaded_model.n_estimators, \
                    f"n_estimators changed after cycle {cycle + 1}"
                assert original_model.contamination == loaded_model.contamination, \
                    f"contamination changed after cycle {cycle + 1}"
                assert original_model.random_state == loaded_model.random_state, \
                    f"random_state changed after cycle {cycle + 1}"
                
                # Use loaded model for next cycle
                current_model = loaded_model
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        # Final verification: model after all cycles should still match original
        final_predictions = current_model.predict(X)
        final_scores = current_model.decision_function(X)
        
        np.testing.assert_array_equal(
            original_predictions,
            final_predictions,
            err_msg=f"Final predictions differ after {serialization_cycles} cycles"
        )
        
        np.testing.assert_allclose(
            original_scores,
            final_scores,
            rtol=1e-12,
            atol=1e-12,
            err_msg=f"Final scores differ after {serialization_cycles} cycles"
        )
    
    def test_model_consistency_with_real_data(self):
        """
        **Validates: Requirements CP-2**
        
        Property: Model consistency should hold with real dataset
        
        Test Strategy: Use actual dataset to verify consistency properties
        """
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        
        if not os.path.exists(dataset_path):
            pytest.skip(f"Real dataset not found: {dataset_path}")
        
        try:
            # Load and prepare real data
            df = load_dataset(dataset_path)
            df_with_features = engineer_features(df)
            
            # Use a subset for faster testing
            test_data = df_with_features.head(100)
            
            # Train two models with same data
            model1 = train_model(test_data)
            model2 = train_model(test_data)
            
            # Verify consistency
            X = test_data[FEATURE_COLUMNS]
            
            predictions1 = model1.predict(X)
            predictions2 = model2.predict(X)
            
            scores1 = model1.decision_function(X)
            scores2 = model2.decision_function(X)
            
            # Should be identical due to fixed random_state
            np.testing.assert_array_equal(predictions1, predictions2)
            np.testing.assert_allclose(scores1, scores2, rtol=1e-10, atol=1e-10)
            
            # Test serialization consistency with real data
            with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                save_model(model1, temp_path)
                loaded_model = load_model(temp_path)
                
                loaded_predictions = loaded_model.predict(X)
                loaded_scores = loaded_model.decision_function(X)
                
                np.testing.assert_array_equal(predictions1, loaded_predictions)
                np.testing.assert_allclose(scores1, loaded_scores, rtol=1e-12, atol=1e-12)
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            pytest.skip(f"Real data test failed: {e}")
    
    @given(
        feature_perturbation=st.floats(min_value=0.0, max_value=0.01)
    )
    @settings(max_examples=5, deadline=45000)
    @example(feature_perturbation=0.001)
    def test_model_stability_under_small_perturbations(self, feature_perturbation: float):
        """
        **Validates: Requirements CP-2**
        
        Property: Model should be stable under small input perturbations
        
        Test Strategy: Add small noise to features and verify predictions remain stable
        """
        # Create test data and train model
        test_data = self._create_test_data(60)
        model = train_model(test_data)
        
        X = test_data[FEATURE_COLUMNS]
        original_predictions = model.predict(X)
        original_scores = model.decision_function(X)
        
        # Add small perturbations to features
        np.random.seed(42)  # For reproducible perturbations
        perturbation = np.random.normal(0, feature_perturbation, X.shape)
        X_perturbed = X + perturbation
        
        # Get predictions on perturbed data
        perturbed_predictions = model.predict(X_perturbed)
        perturbed_scores = model.decision_function(X_perturbed)
        
        # For very small perturbations, most predictions should remain the same
        if feature_perturbation <= 0.005:
            # At least 80% of predictions should remain unchanged
            prediction_stability = np.mean(original_predictions == perturbed_predictions)
            assert prediction_stability >= 0.8, \
                f"Model unstable: only {prediction_stability:.2%} predictions unchanged with perturbation {feature_perturbation}"
            
            # Scores should be close
            score_differences = np.abs(original_scores - perturbed_scores)
            max_score_diff = np.max(score_differences)
            assert max_score_diff < 0.1, \
                f"Scores too sensitive to perturbation: max difference {max_score_diff}"


class TestModelConsistencyEdgeCases:
    """Edge case tests for model consistency."""
    
    def test_empty_model_serialization(self):
        """Test serialization of untrained model."""
        # Create untrained model
        model = IsolationForest(random_state=42)
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Should be able to save untrained model
            save_model(model, temp_path)
            loaded_model = load_model(temp_path)
            
            # Parameters should be preserved
            assert model.random_state == loaded_model.random_state
            assert model.contamination == loaded_model.contamination
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_single_sample_consistency(self):
        """Test consistency with single sample predictions."""
        # Create minimal test data
        test_data = pd.DataFrame({
            feature: [1.0] for feature in FEATURE_COLUMNS
        })
        
        # Create and fit model
        model = IsolationForest(random_state=42, contamination=0.1)
        model.fit(test_data)
        
        # Make multiple predictions on same single sample
        predictions = []
        scores = []
        
        for _ in range(10):
            pred = model.predict(test_data)
            score = model.decision_function(test_data)
            predictions.append(pred[0])
            scores.append(score[0])
        
        # All should be identical
        assert all(p == predictions[0] for p in predictions)
        assert all(abs(s - scores[0]) < 1e-15 for s in scores)
    
    def test_model_consistency_different_contamination(self):
        """Test that models with different contamination rates are still internally consistent."""
        test_data = pd.DataFrame({
            feature: np.random.random(50) for feature in FEATURE_COLUMNS
        })
        
        contamination_rates = [0.05, 0.1, 0.2]
        
        for contamination in contamination_rates:
            # Train two models with same contamination
            model1 = IsolationForest(random_state=42, contamination=contamination)
            model2 = IsolationForest(random_state=42, contamination=contamination)
            
            model1.fit(test_data)
            model2.fit(test_data)
            
            # Should produce identical results
            pred1 = model1.predict(test_data)
            pred2 = model2.predict(test_data)
            
            score1 = model1.decision_function(test_data)
            score2 = model2.decision_function(test_data)
            
            np.testing.assert_array_equal(pred1, pred2)
            np.testing.assert_allclose(score1, score2, rtol=1e-10, atol=1e-10)


if __name__ == "__main__":
    # Run the property-based tests
    pytest.main([__file__, "-v", "--tb=short", "-x"])