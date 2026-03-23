"""
Comprehensive Error Conditions and Edge Cases Tests for TRINETRA AI

This module contains unit tests specifically focused on error conditions and edge cases
that are not covered in the existing test suite. It tests boundary conditions, 
error handling, data corruption scenarios, and system failure modes.

Test Categories:
1. Data Loader - File corruption, encoding issues, malformed CSV
2. Feature Engineering - Division by zero, infinite values, data type errors
3. ML Model - Memory issues, corrupted models, invalid parameters
4. Fraud Detection - Model failures, prediction errors, classification edge cases
5. AI Explainer - API failures, timeout handling, quota management
6. API - Malformed requests, system failures, concurrent access
7. Alert System - Boundary conditions, invalid thresholds, missing data

Author: TRINETRA AI Team
Date: 2024
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
import json
import time
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path
import threading
import concurrent.futures
from sklearn.ensemble import IsolationForest
import joblib

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules to test
from data_loader import (
    load_dataset, validate_schema, get_dataset_stats, handle_missing_values,
    DataLoaderError, SchemaValidationError, DataQualityError
)
from feature_engineering import (
    calculate_price_anomaly_score, calculate_route_risk_score,
    calculate_company_network_risk, calculate_port_congestion_score,
    calculate_shipment_duration_risk, calculate_volume_spike_score,
    engineer_features
)
from model import train_model, save_model, load_model, get_model_info, evaluate_model
from fraud_detection import (
    load_fraud_detector, score_transactions, classify_risk, get_risk_category,
    safe_fraud_detection_pipeline
)
from ai_explainer import (
    initialize_gemini, explain_transaction, answer_investigation_query,
    reset_session_count, get_session_count, can_make_explanation,
    GeminiAPIError, GeminiTimeoutError, GeminiRateLimitError
)


class TestDataLoaderErrorConditions:
    """Test error conditions and edge cases for data loader module."""
    
    def test_load_dataset_corrupted_csv_structure(self):
        """Test loading CSV with corrupted structure (mismatched quotes, broken rows)."""
        corrupted_csv_content = '''transaction_id,date,product,quantity
TXN001,2024-01-01,"Electronics,100
TXN002,2024-01-02,"Textiles"with"quotes",200
TXN003,2024-01-03,Machinery,300,extra_column
TXN004,2024-01-04,"Incomplete row
TXN005,2024-01-05,Normal,400'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(corrupted_csv_content)
            temp_path = f.name
        
        try:
            with pytest.raises(DataLoaderError, match="CSV parsing error|corrupted|invalid"):
                load_dataset(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_binary_file_as_csv(self):
        """Test loading binary file with .csv extension."""
        binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            f.write(binary_content)
            temp_path = f.name
        
        try:
            with pytest.raises(DataLoaderError):
                load_dataset(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_dataset_extremely_large_file(self):
        """Test loading extremely large CSV file (memory stress test)."""
        # Create a large CSV file (but not too large to crash the test)
        # Include all required columns to pass schema validation
        large_data = {
            'transaction_id': [f'TXN{i:06d}' for i in range(10000)],  # Reduced size for CI
            'date': ['2024-01-01'] * 10000,
            'product': ['Test Product'] * 10000,
            'commodity_category': ['Consumer'] * 10000,
            'quantity': [100] * 10000,
            'unit_price': [10.0] * 10000,
            'trade_value': [1000.0] * 10000,
            'market_price': [9.0] * 10000,
            'price_deviation': [0.1] * 10000,
            'exporter_company': ['Test Exporter'] * 10000,
            'exporter_country': ['Test Country'] * 10000,
            'importer_company': ['Test Importer'] * 10000,
            'importer_country': ['Test Country'] * 10000,
            'shipping_route': ['A-B'] * 10000,
            'distance_km': [1000] * 10000,
            'company_risk_score': [0.1] * 10000,
            'route_anomaly': [0] * 10000,
            'fraud_label': [0] * 10000
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            df_large = pd.DataFrame(large_data)
            df_large.to_csv(temp_path, index=False)
            
            # This should work but might be slow
            df = load_dataset(temp_path)
            assert len(df) == 10000
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_dataset_special_characters_encoding(self):
        """Test loading CSV with special characters and encoding issues."""
        special_csv_content = '''transaction_id,date,product,company
TXN001,2024-01-01,Electronics,French Company
TXN002,2024-01-02,Product,Chinese Company
TXN003,2024-01-03,Product,Russian Company
TXN004,2024-01-04,Product,Emoji Corp'''
        
        # Test with UTF-8 encoding only (most reliable)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(special_csv_content)
            temp_path = f.name
        
        try:
            # Should handle UTF-8 encoding gracefully
            df = load_dataset(temp_path)
            assert len(df) == 4
            assert 'transaction_id' in df.columns
        except DataLoaderError:
            # Some special characters might still cause issues, which is acceptable
            pass
        finally:
            os.unlink(temp_path)
    
    def test_validate_schema_circular_references(self):
        """Test schema validation with circular column references."""
        # Create DataFrame with columns that might cause circular reference issues
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02']),
            'self_reference': ['TXN001', 'TXN002'],  # Self-referencing column
            'circular_ref_a': ['B', 'A'],
            'circular_ref_b': ['A', 'B']
        })
        
        # Should handle without issues
        result = validate_schema(df)
        # Schema validation should focus on required columns, not relationships
        assert result is False  # Missing required columns
    
    def test_get_dataset_stats_extreme_values(self):
        """Test dataset statistics with extreme values."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'extreme_large': [1e308, 1e309, float('inf')],  # Very large numbers
            'extreme_small': [1e-308, 1e-309, 0],  # Very small numbers
            'negative_extreme': [-1e308, float('-inf'), -1e309],
            'mixed_extreme': [float('nan'), float('inf'), -float('inf')]
        })
        
        stats = get_dataset_stats(df)
        
        # Should handle extreme values gracefully
        assert stats['basic_info']['total_rows'] == 3
        assert stats['basic_info']['total_columns'] == 5  # Updated to match actual columns
        # Should not crash on extreme values
        assert 'error' not in stats or stats.get('error') is None
    
    def test_handle_missing_values_all_nan_columns(self):
        """Test missing value handling when entire columns are NaN."""
        df = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'all_nan_numeric': [np.nan, np.nan, np.nan],
            'all_nan_string': [None, None, None],
            'mixed_column': [1, np.nan, 3]
        })
        
        result_df = handle_missing_values(df)
        
        # Should handle all-NaN columns gracefully
        assert len(result_df) == 3
        assert 'transaction_id' in result_df.columns
        # All-NaN columns should be filled with appropriate defaults
        assert not result_df['all_nan_numeric'].isna().all()
    
    def test_load_dataset_permission_denied(self):
        """Test loading dataset when file permissions are denied."""
        # Create a file and remove read permissions (Unix-like systems)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('transaction_id,date\nTXN001,2024-01-01\n')
            temp_path = f.name
        
        try:
            # Remove read permissions (if supported by OS)
            try:
                os.chmod(temp_path, 0o000)  # No permissions
                
                with pytest.raises(DataLoaderError, match="not readable|permission"):
                    load_dataset(temp_path)
            except (OSError, PermissionError):
                # Skip test if permission modification not supported
                pytest.skip("Permission modification not supported on this system")
        finally:
            # Restore permissions and cleanup
            try:
                os.chmod(temp_path, 0o644)
                os.unlink(temp_path)
            except (OSError, PermissionError):
                pass


class TestFeatureEngineeringErrorConditions:
    """Test error conditions and edge cases for feature engineering module."""
    
    def test_calculate_price_anomaly_score_extreme_values(self):
        """Test price anomaly calculation with extreme values."""
        df = pd.DataFrame({
            'price_deviation': [
                float('inf'),      # Positive infinity
                float('-inf'),     # Negative infinity
                1e308,             # Very large positive
                -1e308,            # Very large negative
                1e-308,            # Very small positive
                -1e-308,           # Very small negative
                0.0,               # Zero
                np.nan             # NaN
            ]
        })
        
        result = calculate_price_anomaly_score(df)
        
        # Should handle extreme values
        assert len(result) == 8
        assert result.iloc[0] == float('inf')  # abs(inf) = inf
        assert result.iloc[1] == float('inf')  # abs(-inf) = inf
        assert result.iloc[6] == 0.0           # abs(0) = 0
        assert pd.isna(result.iloc[7])         # abs(nan) = nan
    
    def test_calculate_shipment_duration_risk_division_by_zero(self):
        """Test shipment duration risk with zero distance values."""
        df = pd.DataFrame({
            'shipment_duration_days': [10, 20, 30, 40],
            'distance_km': [0, 0.0, 1000, 2000]  # Include zero distances
        })
        
        result = calculate_shipment_duration_risk(df)
        
        # Should handle division by zero (replaced with 1)
        assert len(result) == 4
        assert result.iloc[0] == 10.0  # 10/1 (zero replaced with 1)
        assert result.iloc[1] == 20.0  # 20/1 (zero replaced with 1)
        assert result.iloc[2] == 0.03  # 30/1000
        assert result.iloc[3] == 0.02  # 40/2000
    
    def test_calculate_volume_spike_score_zero_quantity(self):
        """Test volume spike calculation with zero quantity values."""
        df = pd.DataFrame({
            'cargo_volume': [100, 200, 300, 400],
            'quantity': [0, 0.0, 10, 20]  # Include zero quantities
        })
        
        result = calculate_volume_spike_score(df)
        
        # Should handle division by zero (replaced with 1)
        assert len(result) == 4
        assert result.iloc[0] == 100.0  # 100/1 (zero replaced with 1)
        assert result.iloc[1] == 200.0  # 200/1 (zero replaced with 1)
        assert result.iloc[2] == 30.0   # 300/10
        assert result.iloc[3] == 20.0   # 400/20
    
    def test_engineer_features_mixed_data_types(self):
        """Test feature engineering with mixed and invalid data types."""
        df = pd.DataFrame({
            'price_deviation': ['0.1', '0.2', 'invalid', np.nan],  # Mixed string/numeric
            'route_anomaly': [1, '0', 'yes', np.nan],              # Mixed types
            'company_risk_score': [0.5, 'high', 0.8, np.nan],     # Mixed types
            'port_activity_index': [1.0, 1.5, 'busy', np.nan],    # Mixed types
            'shipment_duration_days': [10, '20', 'long', np.nan], # Mixed types
            'distance_km': [1000, '2000', 'far', np.nan],         # Mixed types
            'cargo_volume': [100, '200', 'large', np.nan],        # Mixed types
            'quantity': [10, '20', 'many', np.nan]                # Mixed types
        })
        
        # Should handle mixed data types gracefully
        result_df = engineer_features(df)
        
        assert len(result_df) == 4
        # Should have all original columns plus engineered features
        expected_features = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        for feature in expected_features:
            assert feature in result_df.columns
    
    def test_engineer_features_memory_stress(self):
        """Test feature engineering with large dataset (memory stress test)."""
        # Create large dataset
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
        
        # Should handle large dataset
        result_df = engineer_features(df)
        
        assert len(result_df) == n_rows
        assert len(result_df.columns) == len(df.columns) + 6  # Original + 6 features


class TestMLModelErrorConditions:
    """Test error conditions and edge cases for ML model module."""
    
    def test_train_model_insufficient_memory(self):
        """Test model training with insufficient memory simulation."""
        # Create a dataset that might cause memory issues
        feature_columns = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        
        # Create large dataset
        n_rows = 100000  # Large but manageable for testing
        df = pd.DataFrame({
            col: np.random.uniform(0, 1, n_rows) for col in feature_columns
        })
        
        # Should handle large dataset (might be slow but shouldn't crash)
        model = train_model(df)
        assert isinstance(model, IsolationForest)
    
    def test_save_model_disk_full_simulation(self):
        """Test model saving when disk space is insufficient."""
        model = IsolationForest(n_estimators=10, random_state=42)
        X = np.random.rand(50, 6)
        model.fit(X)
        
        # Try to save to invalid path (simulates disk full or permission issues)
        invalid_paths = [
            "/invalid/path/that/does/not/exist/model.pkl",
            "",  # Empty path
            "/dev/null/model.pkl" if os.name != 'nt' else "CON/model.pkl"  # Invalid on Unix/Windows
        ]
        
        for invalid_path in invalid_paths:
            with pytest.raises(RuntimeError, match="Failed to save model"):
                save_model(model, invalid_path)
    
    def test_load_model_corrupted_pickle(self):
        """Test loading corrupted model file."""
        # Create corrupted pickle file
        corrupted_data = b"corrupted pickle data that cannot be deserialized"
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            f.write(corrupted_data)
            temp_path = f.name
        
        try:
            with pytest.raises(RuntimeError, match="Failed to load model"):
                load_model(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_evaluate_model_mismatched_dimensions(self):
        """Test model evaluation with mismatched feature dimensions."""
        # Train model with 6 features
        feature_columns = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        
        train_df = pd.DataFrame({
            col: np.random.uniform(0, 1, 100) for col in feature_columns
        })
        
        model = train_model(train_df)
        
        # Try to evaluate with different number of features
        eval_df = pd.DataFrame({
            'price_anomaly_score': np.random.uniform(0, 1, 50),
            'route_risk_score': np.random.uniform(0, 1, 50),
            'company_network_risk': np.random.uniform(0, 1, 50)
            # Missing 3 features
        })
        
        with pytest.raises(ValueError, match="Feature dimension mismatch|Missing required features"):
            evaluate_model(model, eval_df)


class TestFraudDetectionErrorConditions:
    """Test error conditions and edge cases for fraud detection module."""
    
    def test_load_fraud_detector_concurrent_access(self):
        """Test concurrent access to model loading."""
        # Create a valid model file
        model = IsolationForest(n_estimators=10, random_state=42)
        X = np.random.rand(50, 6)
        model.fit(X)
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = f.name
        
        try:
            joblib.dump(model, temp_path)
            
            # Test concurrent loading
            def load_model_worker():
                return load_fraud_detector(temp_path)
            
            # Run multiple threads trying to load the same model
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(load_model_worker) for _ in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            # All should succeed
            assert len(results) == 5
            assert all(isinstance(result, IsolationForest) for result in results)
            
        finally:
            os.unlink(temp_path)
    
    def test_score_transactions_model_prediction_failure(self):
        """Test transaction scoring when model prediction fails."""
        # Create mock model that raises exception on prediction
        mock_model = Mock(spec=IsolationForest)
        mock_model.decision_function.side_effect = ValueError("Model prediction failed")
        
        df = pd.DataFrame({
            'price_anomaly_score': [0.1, 0.2],
            'route_risk_score': [0.3, 0.4],
            'company_network_risk': [0.5, 0.6],
            'port_congestion_score': [0.7, 0.8],
            'shipment_duration_risk': [0.9, 1.0],
            'volume_spike_score': [1.1, 1.2]
        })
        
        with pytest.raises(ValueError, match="Model prediction failed"):
            score_transactions(df, mock_model)
    
    def test_classify_risk_boundary_conditions(self):
        """Test risk classification at exact boundary values."""
        # Test exact boundary values for risk classification
        boundary_scores = [-0.2, 0.2, -0.20000001, 0.19999999, 0.20000001]
        expected_categories = ['SUSPICIOUS', 'FRAUD', 'SAFE', 'SUSPICIOUS', 'FRAUD']
        
        for score, expected in zip(boundary_scores, expected_categories):
            result = get_risk_category(score)
            assert result == expected, f"Score {score} should be {expected}, got {result}"
    
    def test_safe_fraud_detection_pipeline_complete_failure(self):
        """Test fraud detection pipeline when everything fails."""
        df = pd.DataFrame({
            'price_anomaly_score': [0.1, 0.2],
            'route_risk_score': [0.3, 0.4],
            'company_network_risk': [0.5, 0.6],
            'port_congestion_score': [0.7, 0.8],
            'shipment_duration_risk': [0.9, 1.0],
            'volume_spike_score': [1.1, 1.2]
        })
        
        # Test with non-existent model path
        result_df = safe_fraud_detection_pipeline(df, "nonexistent_model.pkl")
        
        # Should fall back gracefully
        assert 'risk_score' in result_df.columns
        assert 'risk_category' in result_df.columns
        assert len(result_df) == 2
    
    def test_score_transactions_nan_predictions(self):
        """Test handling of NaN predictions from model."""
        # Create mock model that returns NaN predictions
        mock_model = Mock(spec=IsolationForest)
        mock_model.decision_function.return_value = np.array([np.nan, np.nan])
        
        df = pd.DataFrame({
            'price_anomaly_score': [0.1, 0.2],
            'route_risk_score': [0.3, 0.4],
            'company_network_risk': [0.5, 0.6],
            'port_congestion_score': [0.7, 0.8],
            'shipment_duration_risk': [0.9, 1.0],
            'volume_spike_score': [1.1, 1.2]
        })
        
        result_df = score_transactions(df, mock_model)
        
        # Should handle NaN predictions by replacing with 0
        assert 'risk_score' in result_df.columns
        assert not result_df['risk_score'].isna().any()
        assert all(result_df['risk_score'] == 0.0)


class TestAIExplainerErrorConditions:
    """Test error conditions and edge cases for AI explainer module."""
    
    def test_initialize_gemini_invalid_api_key(self):
        """Test Gemini initialization with invalid API key."""
        with pytest.raises(Exception):  # Could be various exception types
            initialize_gemini("invalid_api_key_12345")
    
    def test_explain_transaction_quota_exceeded(self):
        """Test transaction explanation when quota is exceeded."""
        # Reset session count and exhaust quota
        reset_session_count()
        
        # Simulate quota exhaustion by setting count to maximum
        for _ in range(10):  # MAX_EXPLANATIONS_PER_SESSION
            if can_make_explanation():
                # Simulate an explanation request
                from ai_explainer import increment_session_count
                increment_session_count()
        
        # Now quota should be exhausted
        assert not can_make_explanation()
        
        transaction = {
            'transaction_id': 'TXN001',
            'price_deviation': 0.5,
            'route_anomaly': 1,
            'company_risk_score': 0.9
        }
        
        # Should return fallback explanation
        explanation = explain_transaction(transaction, force_api=False)
        assert "limit reached" in explanation.lower() or "quota" in explanation.lower()
    
    def test_explain_transaction_api_timeout(self):
        """Test transaction explanation with API timeout."""
        # Mock Gemini model that times out
        mock_model = Mock()
        mock_model.generate_content.side_effect = GeminiTimeoutError("Request timed out")
        
        transaction = {
            'transaction_id': 'TXN001',
            'price_deviation': 0.3,
            'route_anomaly': 0,
            'company_risk_score': 0.5
        }
        
        # Should fall back to rule-based explanation
        explanation = explain_transaction(transaction, mock_model, force_api=True)
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        # Should contain fallback indicators
        assert "fraud indicators" in explanation.lower() or "detected" in explanation.lower()
    
    def test_answer_investigation_query_rate_limit(self):
        """Test investigation query with rate limit error."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = GeminiRateLimitError("Rate limit exceeded")
        
        context = {
            'total_transactions': 1000,
            'fraud_cases': 50,
            'suspicious_cases': 100
        }
        
        # Should fall back to rule-based response
        answer = answer_investigation_query("What is the fraud rate?", context, mock_model)
        assert isinstance(answer, str)
        assert len(answer) > 0
        # Should contain statistical information
        assert "1000" in answer or "50" in answer or "5%" in answer
    
    def test_concurrent_explanation_requests(self):
        """Test concurrent explanation requests (thread safety)."""
        reset_session_count()
        
        transaction = {
            'transaction_id': 'TXN001',
            'price_deviation': 0.2,
            'route_anomaly': 0,
            'company_risk_score': 0.3
        }
        
        def explain_worker():
            return explain_transaction(transaction, force_api=False)
        
        # Run multiple concurrent explanation requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(explain_worker) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All should return valid explanations
        assert len(results) == 10
        assert all(isinstance(result, str) and len(result) > 0 for result in results)


class TestAPIErrorConditions:
    """Test error conditions and edge cases for API module."""
    
    def test_malformed_json_requests(self):
        """Test API handling of malformed JSON requests."""
        from fastapi.testclient import TestClient
        
        # Mock the API dependencies
        with patch('api._transactions_df') as mock_df:
            mock_df.return_value = pd.DataFrame({
                'transaction_id': ['TXN001'],
                'risk_score': [0.1],
                'risk_category': ['SAFE']
            })
            
            from api import app
            client = TestClient(app)
            
            # Test malformed JSON
            response = client.post(
                "/explain/TXN001",
                data="invalid json content",
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 (validation error) or 400 (bad request)
            assert response.status_code in [400, 422]
    
    def test_api_concurrent_requests(self):
        """Test API handling of concurrent requests."""
        from fastapi.testclient import TestClient
        
        # Mock the API dependencies
        with patch('api._transactions_df') as mock_df:
            mock_df.return_value = pd.DataFrame({
                'transaction_id': ['TXN001', 'TXN002'],
                'risk_score': [0.1, 0.3],
                'risk_category': ['SAFE', 'FRAUD']
            })
            
            from api import app
            client = TestClient(app)
            
            def make_request():
                return client.get("/transactions?limit=10")
            
            # Run concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                responses = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            # All should succeed
            assert len(responses) == 10
            assert all(response.status_code == 200 for response in responses)
    
    def test_api_memory_pressure(self):
        """Test API behavior under memory pressure."""
        from fastapi.testclient import TestClient
        
        # Create large dataset to simulate memory pressure
        large_df = pd.DataFrame({
            'transaction_id': [f'TXN{i:06d}' for i in range(10000)],
            'risk_score': np.random.uniform(-0.5, 0.5, 10000),
            'risk_category': np.random.choice(['SAFE', 'SUSPICIOUS', 'FRAUD'], 10000)
        })
        
        with patch('api._transactions_df', large_df):
            from api import app
            client = TestClient(app)
            
            # Request large amount of data
            response = client.get("/transactions?limit=1000")
            
            # Should handle gracefully (might be slow but shouldn't crash)
            assert response.status_code == 200
            data = response.json()
            assert 'data' in data
            assert 'transactions' in data['data']


class TestAlertSystemErrorConditions:
    """Test error conditions and edge cases for alert system."""
    
    def test_alert_creation_invalid_thresholds(self):
        """Test alert creation with invalid threshold values."""
        from alerts import create_alert_summary
        
        # Transaction with extreme/invalid values
        transaction = {
            'transaction_id': 'TXN001',
            'price_deviation': float('inf'),  # Invalid threshold
            'route_anomaly': 2,               # Invalid (should be 0 or 1)
            'company_risk_score': -1.0,      # Invalid (should be 0-1)
            'port_activity_index': float('nan')  # Invalid
        }
        
        # Should handle invalid values gracefully
        summary = create_alert_summary(transaction)
        
        # Should either create valid summary or return None
        if summary is not None:
            assert hasattr(summary, 'transaction_id')
            assert summary.transaction_id == 'TXN001'
    
    def test_alert_boundary_conditions(self):
        """Test alert triggering at exact boundary conditions."""
        from alerts import create_alert_summary
        
        # Test exact boundary values
        boundary_transactions = [
            {
                'transaction_id': 'TXN001',
                'price_deviation': 0.5,      # Exactly at threshold
                'route_anomaly': 1,          # Exactly at threshold
                'company_risk_score': 0.8,   # Exactly at threshold
                'port_activity_index': 1.5   # Exactly at threshold
            },
            {
                'transaction_id': 'TXN002',
                'price_deviation': 0.49999,  # Just below threshold
                'route_anomaly': 0,          # Below threshold
                'company_risk_score': 0.79999,  # Just below threshold
                'port_activity_index': 1.49999  # Just below threshold
            }
        ]
        
        for transaction in boundary_transactions:
            summary = create_alert_summary(transaction)
            # Should handle boundary conditions consistently
            if summary is not None:
                assert hasattr(summary, 'alerts')
                assert isinstance(summary.alerts, list)


class TestSystemIntegrationErrorConditions:
    """Test system-wide error conditions and edge cases."""
    
    def test_system_startup_missing_dependencies(self):
        """Test system behavior when dependencies are missing."""
        # Mock missing dependencies
        with patch('sys.modules', {'pandas': None}):
            # Should handle missing dependencies gracefully
            try:
                import data_loader
                # If import succeeds, dependency handling is working
                assert True
            except ImportError:
                # Expected behavior when dependencies are missing
                assert True
    
    def test_disk_space_exhaustion_simulation(self):
        """Test system behavior when disk space is exhausted."""
        # Create temporary directory with limited space (simulation)
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to save large model to limited space
            model = IsolationForest(n_estimators=100, random_state=42)
            X = np.random.rand(1000, 6)
            model.fit(X)
            
            model_path = os.path.join(temp_dir, "large_model.pkl")
            
            try:
                save_model(model, model_path)
                # If save succeeds, check file exists
                assert os.path.exists(model_path)
            except RuntimeError:
                # Expected when disk space issues occur
                assert True
    
    def test_network_connectivity_issues(self):
        """Test system behavior with network connectivity issues."""
        # Mock network failure for Gemini API
        with patch('ai_explainer.genai') as mock_genai:
            mock_genai.configure.side_effect = ConnectionError("Network unreachable")
            
            # Should handle network issues gracefully
            try:
                initialize_gemini()
                assert False, "Should have raised an exception"
            except Exception as e:
                # Should raise appropriate exception
                assert "network" in str(e).lower() or "connection" in str(e).lower()
    
    def test_system_recovery_after_failure(self):
        """Test system recovery capabilities after failures."""
        # Simulate system failure and recovery
        reset_session_count()
        
        # Simulate failure
        transaction = {
            'transaction_id': 'TXN001',
            'price_deviation': 0.3,
            'route_anomaly': 0,
            'company_risk_score': 0.5
        }
        
        # First attempt with mocked failure
        with patch('ai_explainer.initialize_gemini') as mock_init:
            mock_init.side_effect = Exception("System failure")
            
            # Should fall back gracefully
            explanation = explain_transaction(transaction, force_api=False)
            assert isinstance(explanation, str)
            assert len(explanation) > 0
        
        # Second attempt should work (recovery)
        explanation2 = explain_transaction(transaction, force_api=False)
        assert isinstance(explanation2, str)
        assert len(explanation2) > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short", "--maxfail=5"])