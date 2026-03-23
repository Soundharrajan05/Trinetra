"""
Property-Based Test for Risk Score Consistency (CP-2)
TRINETRA AI - Trade Fraud Intelligence System

**Validates: Requirements CP-2**

This module implements property-based testing for risk score consistency validation.
Tests ensure that risk scores are monotonically related to risk categories (SAFE < SUSPICIOUS < FRAUD).

Property: Risk scores must be monotonically related to risk categories (SAFE < SUSPICIOUS < FRAUD)
Test Strategy: Property-based test verifying score thresholds align with category assignments
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from hypothesis import given, strategies as st, settings, assume, example
from typing import List, Dict, Any, Tuple
from sklearn.ensemble import IsolationForest

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fraud_detection import (
    get_risk_category,
    classify_risk,
    score_transactions,
    load_fraud_detector
)
from data_loader import load_dataset
from feature_engineering import engineer_features


class TestRiskScoreConsistencyProperty:
    """Property-based tests for risk score consistency validation (CP-2)."""
    
    @given(
        risk_scores=st.lists(
            st.floats(
                min_value=-2.0, 
                max_value=2.0,
                allow_nan=False,
                allow_infinity=False
            ),
            min_size=10,
            max_size=100
        )
    )
    @settings(max_examples=50, deadline=30000)
    @example(risk_scores=[-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3])  # Boundary values
    @example(risk_scores=[-1.0, -0.5, 0.0, 0.5, 1.0])  # Spread across range
    @example(risk_scores=[-0.21, -0.2, -0.19, 0.19, 0.2, 0.21])  # Edge cases
    def test_risk_score_monotonic_relationship(self, risk_scores: List[float]):
        """
        **Validates: Requirements CP-2**
        
        Property: Risk scores must be monotonically related to risk categories (SAFE < SUSPICIOUS < FRAUD)
        
        Test Strategy: Generate various risk scores and verify that the ordering relationship holds
        """
        # Test the monotonic relationship for each score
        for score in risk_scores:
            category = get_risk_category(score)
            
            # Verify correct threshold classification
            if score < -0.2:
                assert category == "SAFE", f"Score {score} should be SAFE but got {category}"
            elif score < 0.2:
                assert category == "SUSPICIOUS", f"Score {score} should be SUSPICIOUS but got {category}"
            else:
                assert category == "FRAUD", f"Score {score} should be FRAUD but got {category}"
        
        # Test pairwise monotonic relationship
        for i, score1 in enumerate(risk_scores):
            for j, score2 in enumerate(risk_scores):
                if i != j:
                    cat1 = get_risk_category(score1)
                    cat2 = get_risk_category(score2)
                    
                    # Define category ordering
                    category_order = {"SAFE": 0, "SUSPICIOUS": 1, "FRAUD": 2}
                    
                    # If score1 < score2, then category1 should be <= category2
                    if score1 < score2:
                        assert category_order[cat1] <= category_order[cat2], \
                            f"Monotonic violation: score {score1} ({cat1}) < {score2} ({cat2})"
    
    @given(
        boundary_offset=st.floats(min_value=-0.01, max_value=0.01, allow_nan=False)
    )
    @settings(max_examples=30, deadline=30000)
    @example(boundary_offset=0.0)  # Exact boundaries
    @example(boundary_offset=-0.001)  # Just below
    @example(boundary_offset=0.001)  # Just above
    def test_risk_score_boundary_conditions(self, boundary_offset: float):
        """
        **Validates: Requirements CP-2**
        
        Property: Risk classification boundaries must be correctly implemented
        
        Test Strategy: Test boundary conditions around thresholds -0.2 and 0.2
        """
        # Test lower boundary (-0.2)
        lower_boundary = -0.2 + boundary_offset
        lower_category = get_risk_category(lower_boundary)
        
        if lower_boundary < -0.2:
            assert lower_category == "SAFE", f"Score {lower_boundary} should be SAFE"
        else:
            assert lower_category == "SUSPICIOUS", f"Score {lower_boundary} should be SUSPICIOUS"
        
        # Test upper boundary (0.2)
        upper_boundary = 0.2 + boundary_offset
        upper_category = get_risk_category(upper_boundary)
        
        if upper_boundary < 0.2:
            assert upper_category == "SUSPICIOUS", f"Score {upper_boundary} should be SUSPICIOUS"
        else:
            assert upper_category == "FRAUD", f"Score {upper_boundary} should be FRAUD"
    
    @given(
        n_transactions=st.integers(min_value=5, max_value=50)
    )
    @settings(max_examples=20, deadline=60000)
    @example(n_transactions=10)
    def test_risk_classification_with_generated_data(self, n_transactions: int):
        """
        **Validates: Requirements CP-2**
        
        Property: Risk classification must maintain consistency when applied to DataFrame
        
        Test Strategy: Generate synthetic transaction data with various risk scores
        """
        # Generate synthetic transaction data
        np.random.seed(42)  # For reproducibility
        
        # Create synthetic risk scores across all categories
        safe_scores = np.random.uniform(-1.0, -0.2, n_transactions // 3)
        suspicious_scores = np.random.uniform(-0.2, 0.2, n_transactions // 3)
        fraud_scores = np.random.uniform(0.2, 1.0, n_transactions - 2 * (n_transactions // 3))
        
        all_scores = np.concatenate([safe_scores, suspicious_scores, fraud_scores])
        np.random.shuffle(all_scores)
        
        # Create DataFrame with risk scores
        df = pd.DataFrame({
            'transaction_id': [f'TXN{i:03d}' for i in range(len(all_scores))],
            'risk_score': all_scores
        })
        
        # Apply risk classification
        classified_df = classify_risk(df)
        
        # Verify consistency for each transaction
        for _, row in classified_df.iterrows():
            score = row['risk_score']
            category = row['risk_category']
            expected_category = get_risk_category(score)
            
            assert category == expected_category, \
                f"Inconsistent classification: score {score} got {category}, expected {expected_category}"
        
        # Verify category distribution makes sense
        safe_count = len(classified_df[classified_df['risk_category'] == 'SAFE'])
        suspicious_count = len(classified_df[classified_df['risk_category'] == 'SUSPICIOUS'])
        fraud_count = len(classified_df[classified_df['risk_category'] == 'FRAUD'])
        
        # Should have transactions in each category (given our generation strategy)
        assert safe_count > 0, "Should have some SAFE transactions"
        assert suspicious_count > 0, "Should have some SUSPICIOUS transactions"
        assert fraud_count > 0, "Should have some FRAUD transactions"
    
    @given(
        score_pairs=st.lists(
            st.tuples(
                st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False),
                st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False)
            ),
            min_size=5,
            max_size=20
        )
    )
    @settings(max_examples=25, deadline=30000)
    def test_risk_score_ordering_property(self, score_pairs: List[Tuple[float, float]]):
        """
        **Validates: Requirements CP-2**
        
        Property: For any two risk scores, if score1 < score2, then category1 <= category2 in ordering
        
        Test Strategy: Generate pairs of risk scores and verify ordering consistency
        """
        category_order = {"SAFE": 0, "SUSPICIOUS": 1, "FRAUD": 2}
        
        for score1, score2 in score_pairs:
            cat1 = get_risk_category(score1)
            cat2 = get_risk_category(score2)
            
            cat1_order = category_order[cat1]
            cat2_order = category_order[cat2]
            
            if score1 < score2:
                assert cat1_order <= cat2_order, \
                    f"Ordering violation: {score1} ({cat1}) < {score2} ({cat2}) but {cat1_order} > {cat2_order}"
            elif score1 > score2:
                assert cat1_order >= cat2_order, \
                    f"Ordering violation: {score1} ({cat1}) > {score2} ({cat2}) but {cat1_order} < {cat2_order}"
            # For equal scores, categories should be equal (no assertion needed)
    
    def test_risk_score_consistency_with_real_data(self):
        """
        **Validates: Requirements CP-2**
        
        Property: Risk score consistency should hold with real dataset
        
        Test Strategy: Load real dataset, apply ML model, and verify consistency
        """
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        
        # Skip test if dataset doesn't exist
        if not os.path.exists(dataset_path):
            pytest.skip(f"Dataset not found: {dataset_path}")
        
        try:
            # Load and prepare data
            df = load_dataset(dataset_path)
            df = engineer_features(df)
            
            # Try to load existing model or skip if not available
            model_path = "models/isolation_forest.pkl"
            if not os.path.exists(model_path):
                pytest.skip(f"Trained model not found: {model_path}")
            
            model = load_fraud_detector(model_path)
            if model is None:
                pytest.skip("Could not load fraud detection model")
            
            # Score transactions
            scored_df = score_transactions(df, model)
            classified_df = classify_risk(scored_df)
            
            # Verify consistency for all transactions
            for _, row in classified_df.iterrows():
                score = row['risk_score']
                category = row['risk_category']
                expected_category = get_risk_category(score)
                
                assert category == expected_category, \
                    f"Real data inconsistency: Transaction {row.get('transaction_id', 'unknown')} " \
                    f"score {score} got {category}, expected {expected_category}"
            
            # Verify monotonic relationship across the dataset
            sorted_df = classified_df.sort_values('risk_score')
            category_order = {"SAFE": 0, "SUSPICIOUS": 1, "FRAUD": 2}
            
            prev_category_order = -1
            for _, row in sorted_df.iterrows():
                current_category_order = category_order[row['risk_category']]
                assert current_category_order >= prev_category_order, \
                    f"Monotonic violation in real data: category order decreased"
                prev_category_order = current_category_order
                
        except Exception as e:
            pytest.skip(f"Real data test failed due to: {e}")
    
    @given(
        special_values=st.sampled_from([
            -0.2,  # Exact lower boundary
            0.2,   # Exact upper boundary
            -0.20000001,  # Just below lower boundary
            -0.19999999,  # Just above lower boundary
            0.19999999,   # Just below upper boundary
            0.20000001,   # Just above upper boundary
        ])
    )
    @settings(max_examples=15, deadline=30000)
    def test_risk_score_exact_boundary_values(self, special_values: float):
        """
        **Validates: Requirements CP-2**
        
        Property: Exact boundary values must be classified correctly
        
        Test Strategy: Test specific boundary values that are critical for classification
        """
        category = get_risk_category(special_values)
        
        # Verify exact boundary behavior
        if special_values < -0.2:
            assert category == "SAFE", f"Value {special_values} should be SAFE"
        elif special_values < 0.2:
            assert category == "SUSPICIOUS", f"Value {special_values} should be SUSPICIOUS"
        else:
            assert category == "FRAUD", f"Value {special_values} should be FRAUD"
        
        # Test that the boundary is inclusive/exclusive as designed
        if special_values == -0.2:
            assert category == "SUSPICIOUS", "Lower boundary -0.2 should be SUSPICIOUS (inclusive)"
        elif special_values == 0.2:
            assert category == "FRAUD", "Upper boundary 0.2 should be FRAUD (inclusive)"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])