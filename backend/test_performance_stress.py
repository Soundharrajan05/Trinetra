"""
Performance and Stress Tests for TRINETRA AI

This module contains performance and stress tests to ensure the system
handles edge cases related to resource constraints, large datasets,
and high-load scenarios.

Author: TRINETRA AI Team
Date: 2024
"""

import pytest
import pandas as pd
import numpy as np
import time
import threading
import concurrent.futures
import tempfile
import os
import sys
from unittest.mock import patch
import psutil
import gc

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_dataset
from feature_engineering import engineer_features
from model import train_model
from fraud_detection import score_transactions, classify_risk
from ai_explainer import explain_transaction, reset_session_count


class TestPerformanceStress:
    """Performance and stress tests for system components."""
    
    def test_large_dataset_processing(self):
        """Test processing of large datasets."""
        # Create large dataset (but manageable for CI)
        n_rows = 50000
        
        large_df = pd.DataFrame({
            'transaction_id': [f'TXN{i:06d}' for i in range(n_rows)],
            'date': pd.date_range('2024-01-01', periods=n_rows, freq='1min'),
            'product': np.random.choice(['Electronics', 'Textiles', 'Machinery'], n_rows),
            'price_deviation': np.random.uniform(-1, 1, n_rows),
            'route_anomaly': np.random.choice([0, 1], n_rows),
            'company_risk_score': np.random.uniform(0, 1, n_rows),
            'port_activity_index': np.random.uniform(0.5, 2.0, n_rows),
            'shipment_duration_days': np.random.uniform(1, 30, n_rows),
            'distance_km': np.random.uniform(100, 20000, n_rows),
            'cargo_volume': np.random.uniform(10, 1000, n_rows),
            'quantity': np.random.uniform(1, 100, n_rows),
            'fraud_label': np.random.choice([0, 1], n_rows)
        })
        
        start_time = time.time()
        
        # Test feature engineering on large dataset
        result_df = engineer_features(large_df)
        
        processing_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert processing_time < 30.0  # 30 seconds max
        assert len(result_df) == n_rows
        assert 'price_anomaly_score' in result_df.columns
    
    def test_memory_usage_monitoring(self):
        """Test memory usage during processing."""
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create moderately large dataset
        n_rows = 10000
        df = pd.DataFrame({
            'price_deviation': np.random.uniform(-1, 1, n_rows),
            'route_anomaly': np.random.choice([0, 1], n_rows),
            'company_risk_score': np.random.uniform(0, 1, n_rows),
            'port_activity_index': np.random.uniform(0.5, 2.0, n_rows),
            'shipment_duration_days': np.random.uniform(1, 30, n_rows),
            'distance_km': np.random.uniform(100, 20000, n_rows),
            'cargo_volume': np.random.uniform(10, 1000, n_rows),
            'quantity': np.random.uniform(1, 100, n_rows)
        })
        
        # Process data and monitor memory
        result_df = engineer_features(df)
        
        # Get peak memory usage
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Memory increase should be reasonable (adjust threshold as needed)
        assert memory_increase < 500  # Less than 500MB increase
        
        # Cleanup
        del df, result_df
        gc.collect()
    
    def test_concurrent_processing(self):
        """Test concurrent processing of multiple datasets."""
        def process_dataset(dataset_id):
            # Create small dataset for each thread
            df = pd.DataFrame({
                'price_deviation': np.random.uniform(-1, 1, 1000),
                'route_anomaly': np.random.choice([0, 1], 1000),
                'company_risk_score': np.random.uniform(0, 1, 1000),
                'port_activity_index': np.random.uniform(0.5, 2.0, 1000),
                'shipment_duration_days': np.random.uniform(1, 30, 1000),
                'distance_km': np.random.uniform(100, 20000, 1000),
                'cargo_volume': np.random.uniform(10, 1000, 1000),
                'quantity': np.random.uniform(1, 100, 1000)
            })
            
            result_df = engineer_features(df)
            return len(result_df)
        
        # Run concurrent processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_dataset, i) for i in range(8)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All should complete successfully
        assert len(results) == 8
        assert all(result == 1000 for result in results)
    
    def test_repeated_processing_memory_leak(self):
        """Test for memory leaks during repeated processing."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Repeat processing many times
        for i in range(100):
            df = pd.DataFrame({
                'price_deviation': np.random.uniform(-1, 1, 100),
                'route_anomaly': np.random.choice([0, 1], 100),
                'company_risk_score': np.random.uniform(0, 1, 100),
                'port_activity_index': np.random.uniform(0.5, 2.0, 100),
                'shipment_duration_days': np.random.uniform(1, 30, 100),
                'distance_km': np.random.uniform(100, 20000, 100),
                'cargo_volume': np.random.uniform(10, 1000, 100),
                'quantity': np.random.uniform(1, 100, 100)
            })
            
            result_df = engineer_features(df)
            
            # Explicit cleanup
            del df, result_df
            
            # Force garbage collection every 10 iterations
            if i % 10 == 0:
                gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (no significant leaks)
        assert memory_increase < 100  # Less than 100MB increase after 100 iterations
    
    def test_high_frequency_api_calls(self):
        """Test high-frequency API-like calls."""
        reset_session_count()
        
        # Simulate high-frequency explanation requests
        transaction = {
            'transaction_id': 'TXN001',
            'price_deviation': 0.2,
            'route_anomaly': 0,
            'company_risk_score': 0.3,
            'port_activity_index': 1.0,
            'risk_score': 0.1,
            'risk_category': 'SUSPICIOUS'
        }
        
        start_time = time.time()
        
        # Make many rapid requests (using fallback to avoid API limits)
        results = []
        for i in range(1000):
            explanation = explain_transaction(transaction, force_api=False)
            results.append(explanation)
        
        processing_time = time.time() - start_time
        
        # Should handle high frequency requests efficiently
        assert processing_time < 10.0  # Less than 10 seconds for 1000 requests
        assert len(results) == 1000
        assert all(isinstance(result, str) and len(result) > 0 for result in results)
    
    def test_extreme_data_values_performance(self):
        """Test performance with extreme data values."""
        # Create dataset with extreme values
        n_rows = 5000
        df = pd.DataFrame({
            'price_deviation': np.concatenate([
                np.full(1000, float('inf')),
                np.full(1000, float('-inf')),
                np.full(1000, 1e308),
                np.full(1000, -1e308),
                np.full(1000, np.nan)
            ]),
            'route_anomaly': np.random.choice([0, 1], n_rows),
            'company_risk_score': np.concatenate([
                np.full(1000, 1e10),  # Extremely large
                np.full(1000, -1e10), # Extremely negative
                np.full(1000, 1e-10), # Extremely small
                np.full(1000, np.nan),
                np.random.uniform(0, 1, 1000)
            ]),
            'port_activity_index': np.random.uniform(0.5, 2.0, n_rows),
            'shipment_duration_days': np.random.uniform(1, 30, n_rows),
            'distance_km': np.concatenate([
                np.full(1000, 0),     # Zero distances
                np.full(1000, 1e-10), # Tiny distances
                np.full(1000, 1e10),  # Huge distances
                np.random.uniform(100, 20000, 2000)
            ]),
            'cargo_volume': np.random.uniform(10, 1000, n_rows),
            'quantity': np.concatenate([
                np.full(1000, 0),     # Zero quantities
                np.full(1000, 1e-10), # Tiny quantities
                np.full(1000, 1e10),  # Huge quantities
                np.random.uniform(1, 100, 2000)
            ])
        })
        
        start_time = time.time()
        
        # Should handle extreme values without crashing
        result_df = engineer_features(df)
        
        processing_time = time.time() - start_time
        
        # Should complete within reasonable time despite extreme values
        assert processing_time < 30.0
        assert len(result_df) == n_rows
        assert 'price_anomaly_score' in result_df.columns
        
        # Check that extreme values were handled (no infinite results)
        for col in ['price_anomaly_score', 'shipment_duration_risk', 'volume_spike_score']:
            if col in result_df.columns:
                finite_values = result_df[col][np.isfinite(result_df[col])]
                # Should have some finite values
                assert len(finite_values) > 0
    
    def test_file_io_stress(self):
        """Test file I/O operations under stress."""
        # Create multiple temporary files and process them concurrently
        temp_files = []
        
        try:
            # Create multiple CSV files
            for i in range(10):
                df = pd.DataFrame({
                    'transaction_id': [f'TXN{j:03d}' for j in range(100)],
                    'date': ['2024-01-01'] * 100,
                    'product': ['Test Product'] * 100,
                    'quantity': [100] * 100,
                    'unit_price': [10.0] * 100,
                    'fraud_label': [0] * 100
                })
                
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
                df.to_csv(temp_file.name, index=False)
                temp_files.append(temp_file.name)
                temp_file.close()
            
            def load_file(file_path):
                return load_dataset(file_path)
            
            start_time = time.time()
            
            # Load all files concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(load_file, file_path) for file_path in temp_files]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            processing_time = time.time() - start_time
            
            # Should handle concurrent file I/O efficiently
            assert processing_time < 15.0  # Less than 15 seconds
            assert len(results) == 10
            assert all(len(df) == 100 for df in results)
            
        finally:
            # Cleanup temporary files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    def test_model_training_stress(self):
        """Test ML model training under stress conditions."""
        # Create challenging dataset for model training
        n_rows = 10000
        n_features = 6
        
        # Create dataset with various challenging characteristics
        feature_data = {}
        feature_names = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        
        for i, feature in enumerate(feature_names):
            if i == 0:
                # First feature: mix of normal and extreme values
                feature_data[feature] = np.concatenate([
                    np.random.normal(0, 1, 8000),
                    np.random.uniform(-100, 100, 2000)  # Extreme outliers
                ])
            elif i == 1:
                # Second feature: highly skewed distribution
                feature_data[feature] = np.random.exponential(0.1, n_rows)
            elif i == 2:
                # Third feature: bimodal distribution
                feature_data[feature] = np.concatenate([
                    np.random.normal(-2, 0.5, 5000),
                    np.random.normal(2, 0.5, 5000)
                ])
            else:
                # Other features: various distributions
                feature_data[feature] = np.random.uniform(0, 1, n_rows)
        
        df = pd.DataFrame(feature_data)
        
        start_time = time.time()
        
        # Train model on challenging dataset
        model = train_model(df)
        
        training_time = time.time() - start_time
        
        # Should complete training within reasonable time
        assert training_time < 60.0  # Less than 1 minute
        assert model is not None
        assert hasattr(model, 'decision_function')
    
    def test_classification_boundary_stress(self):
        """Test risk classification with boundary value stress."""
        # Create dataset with many boundary values
        boundary_scores = []
        
        # Add exact boundary values
        for _ in range(1000):
            boundary_scores.extend([-0.2, 0.2])  # Exact boundaries
        
        # Add near-boundary values
        for _ in range(1000):
            boundary_scores.extend([
                -0.2 + np.random.uniform(-1e-10, 1e-10),  # Very close to -0.2
                0.2 + np.random.uniform(-1e-10, 1e-10)    # Very close to 0.2
            ])
        
        df = pd.DataFrame({
            'transaction_id': [f'TXN{i:06d}' for i in range(len(boundary_scores))],
            'risk_score': boundary_scores
        })
        
        start_time = time.time()
        
        # Classify all boundary cases
        result_df = classify_risk(df)
        
        processing_time = time.time() - start_time
        
        # Should handle boundary cases efficiently
        assert processing_time < 5.0  # Less than 5 seconds
        assert len(result_df) == len(boundary_scores)
        assert 'risk_category' in result_df.columns
        
        # Check that all classifications are valid
        valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
        actual_categories = set(result_df['risk_category'].unique())
        assert actual_categories.issubset(valid_categories)


class TestResourceConstraints:
    """Test system behavior under resource constraints."""
    
    @pytest.mark.skipif(psutil.virtual_memory().total < 4 * 1024**3, 
                       reason="Requires at least 4GB RAM")
    def test_low_memory_conditions(self):
        """Test behavior under simulated low memory conditions."""
        # This test simulates low memory by creating large objects
        # and then testing system behavior
        
        # Consume significant memory
        memory_hogs = []
        try:
            # Create large arrays to consume memory
            for i in range(5):
                memory_hogs.append(np.random.rand(1000000))  # ~8MB each
            
            # Now test normal operations under memory pressure
            df = pd.DataFrame({
                'price_deviation': np.random.uniform(-1, 1, 1000),
                'route_anomaly': np.random.choice([0, 1], 1000),
                'company_risk_score': np.random.uniform(0, 1, 1000),
                'port_activity_index': np.random.uniform(0.5, 2.0, 1000),
                'shipment_duration_days': np.random.uniform(1, 30, 1000),
                'distance_km': np.random.uniform(100, 20000, 1000),
                'cargo_volume': np.random.uniform(10, 1000, 1000),
                'quantity': np.random.uniform(1, 100, 1000)
            })
            
            # Should still work under memory pressure
            result_df = engineer_features(df)
            assert len(result_df) == 1000
            
        finally:
            # Cleanup memory
            del memory_hogs
            gc.collect()
    
    def test_cpu_intensive_operations(self):
        """Test CPU-intensive operations."""
        # Create computationally intensive scenario
        n_iterations = 1000
        results = []
        
        start_time = time.time()
        
        for i in range(n_iterations):
            # Simulate CPU-intensive feature calculation
            data = np.random.uniform(0, 1, 100)
            
            # Perform multiple mathematical operations
            result = np.sum(np.sqrt(np.abs(data))) / np.mean(data)
            results.append(result)
        
        processing_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert processing_time < 30.0  # Adjust based on expected performance
        assert len(results) == n_iterations
        assert all(np.isfinite(result) for result in results)


if __name__ == "__main__":
    # Run with specific markers for performance tests
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])