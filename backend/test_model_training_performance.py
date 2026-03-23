"""
ML Model Training Performance Test for TRINETRA AI

This module tests the ML model training time performance requirement:
NFR-1: ML model training must complete within 30 seconds

Task: Test ML model training time (<30 seconds)
Spec: .kiro/specs/trinetra-ai-fraud-detection

Author: TRINETRA AI Team
Date: 2024
"""

import pytest
import pandas as pd
import time
import sys
import os
from pathlib import Path

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_dataset
from feature_engineering import engineer_features
from model import train_model


class TestModelTrainingPerformance:
    """Performance tests for ML model training time."""
    
    # Performance threshold from NFR-1
    MAX_TRAINING_TIME = 30.0  # seconds
    
    # Dataset path
    DATASET_PATH = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    
    def test_model_training_time_under_30_seconds(self):
        """
        Test that ML model training completes within 30 seconds.
        
        This test validates NFR-1: ML model training time requirement.
        
        Test Steps:
        1. Load the dataset (1000 rows)
        2. Engineer features
        3. Time the model training process
        4. Verify training completes in under 30 seconds
        5. Report the actual training time
        
        Expected Result:
        - Training time < 30 seconds
        - Model is successfully trained
        """
        print("\n" + "="*70)
        print("ML MODEL TRAINING PERFORMANCE TEST")
        print("="*70)
        print(f"Requirement: NFR-1 - Model training within {self.MAX_TRAINING_TIME} seconds")
        print(f"Dataset: {self.DATASET_PATH}")
        print("="*70)
        
        # Step 1: Load dataset
        print("\n[1/3] Loading dataset...")
        load_start = time.time()
        df_raw = load_dataset(self.DATASET_PATH)
        load_time = time.time() - load_start
        print(f"✓ Dataset loaded: {len(df_raw)} rows in {load_time:.2f}s")
        
        # Step 2: Engineer features
        print("\n[2/3] Engineering features...")
        feature_start = time.time()
        df_features = engineer_features(df_raw)
        feature_time = time.time() - feature_start
        print(f"✓ Features engineered in {feature_time:.2f}s")
        
        # Verify all required features are present
        required_features = [
            'price_anomaly_score',
            'route_risk_score',
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        
        for feature in required_features:
            assert feature in df_features.columns, f"Missing feature: {feature}"
        
        print(f"✓ All {len(required_features)} required features present")
        
        # Step 3: Train model and measure time
        print("\n[3/3] Training ML model...")
        print(f"Model: IsolationForest (n_estimators=100, contamination=0.1)")
        print(f"Training samples: {len(df_features)}")
        print(f"Features: {len(required_features)}")
        
        training_start = time.time()
        model = train_model(df_features)
        training_time = time.time() - training_start
        
        # Step 4: Verify model is trained
        assert model is not None, "Model should not be None"
        assert hasattr(model, 'estimators_'), "Model should be fitted"
        
        # Step 5: Report results
        print("\n" + "="*70)
        print("PERFORMANCE TEST RESULTS")
        print("="*70)
        print(f"Dataset Load Time:        {load_time:.3f} seconds")
        print(f"Feature Engineering Time: {feature_time:.3f} seconds")
        print(f"Model Training Time:      {training_time:.3f} seconds")
        print(f"Total Pipeline Time:      {load_time + feature_time + training_time:.3f} seconds")
        print("="*70)
        print(f"Performance Threshold:    {self.MAX_TRAINING_TIME:.1f} seconds")
        print(f"Actual Training Time:     {training_time:.3f} seconds")
        print(f"Time Margin:              {self.MAX_TRAINING_TIME - training_time:.3f} seconds")
        print(f"Performance Ratio:        {(training_time / self.MAX_TRAINING_TIME) * 100:.1f}%")
        print("="*70)
        
        # Determine pass/fail
        if training_time < self.MAX_TRAINING_TIME:
            print(f"✅ PASS - Training completed in {training_time:.3f}s (under {self.MAX_TRAINING_TIME}s)")
            print("="*70)
        else:
            print(f"❌ FAIL - Training took {training_time:.3f}s (exceeds {self.MAX_TRAINING_TIME}s)")
            print("="*70)
            pytest.fail(
                f"Model training time {training_time:.3f}s exceeds threshold of {self.MAX_TRAINING_TIME}s"
            )
        
        # Assert the performance requirement
        assert training_time < self.MAX_TRAINING_TIME, (
            f"Model training time {training_time:.3f}s exceeds the {self.MAX_TRAINING_TIME}s threshold"
        )
    
    def test_model_training_repeatability(self):
        """
        Test that model training time is consistent across multiple runs.
        
        This test ensures the performance is repeatable and not a one-time fluke.
        
        Expected Result:
        - All training runs complete within 30 seconds
        - Training times are relatively consistent (within 50% variance)
        """
        print("\n" + "="*70)
        print("ML MODEL TRAINING REPEATABILITY TEST")
        print("="*70)
        print(f"Running {3} training iterations to verify consistency")
        print("="*70)
        
        # Load and prepare data once
        df_raw = load_dataset(self.DATASET_PATH)
        df_features = engineer_features(df_raw)
        
        training_times = []
        
        for i in range(3):
            print(f"\n[Run {i+1}/3] Training model...")
            
            training_start = time.time()
            model = train_model(df_features)
            training_time = time.time() - training_start
            
            training_times.append(training_time)
            
            print(f"✓ Training time: {training_time:.3f}s")
            
            # Verify each run meets the threshold
            assert training_time < self.MAX_TRAINING_TIME, (
                f"Run {i+1} training time {training_time:.3f}s exceeds threshold"
            )
        
        # Calculate statistics
        avg_time = sum(training_times) / len(training_times)
        min_time = min(training_times)
        max_time = max(training_times)
        variance = max_time - min_time
        variance_pct = (variance / avg_time) * 100
        
        print("\n" + "="*70)
        print("REPEATABILITY TEST RESULTS")
        print("="*70)
        print(f"Training Times: {[f'{t:.3f}s' for t in training_times]}")
        print(f"Average Time:   {avg_time:.3f} seconds")
        print(f"Min Time:       {min_time:.3f} seconds")
        print(f"Max Time:       {max_time:.3f} seconds")
        print(f"Variance:       {variance:.3f} seconds ({variance_pct:.1f}%)")
        print("="*70)
        
        if variance_pct < 50:
            print(f"✅ PASS - Training time is consistent (variance: {variance_pct:.1f}%)")
        else:
            print(f"⚠️  WARNING - High variance in training time: {variance_pct:.1f}%")
        
        print("="*70)
        
        # All runs should pass the threshold
        assert all(t < self.MAX_TRAINING_TIME for t in training_times), (
            "All training runs must complete within the threshold"
        )


def main():
    """Run performance tests and generate report."""
    print("\n" + "="*70)
    print("TRINETRA AI - ML Model Training Performance Test Suite")
    print("="*70)
    print("\nTesting NFR-1: ML model training within 30 seconds")
    print("\nStarting performance tests...\n")
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "-s"  # Show print statements
    ])
    
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
