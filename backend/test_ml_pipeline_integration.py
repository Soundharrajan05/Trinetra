"""
ML Pipeline Integration Test for TRINETRA AI

This test validates the complete ML pipeline integration including:
- Data loading → Feature engineering → Model training/loading → Fraud detection

**Validates: Task 12.2 Integration Testing - Test ML pipeline integration**
**Validates: Requirements US-1, US-2, US-3, FR-2**
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
import shutil
from pathlib import Path
import joblib
from sklearn.ensemble import IsolationForest

# Import ML pipeline modules
from data_loader import load_dataset, validate_schema, get_dataset_stats
from feature_engineering import engineer_features
from model import train_model, save_model, load_model, FEATURE_COLUMNS
from fraud_detection import (
    load_fraud_detector, 
    score_transactions, 
    classify_risk,
    get_risk_category
)


class TestMLPipelineIntegration:
    """Integration tests for the complete ML pipeline."""
    
    @pytest.fixture
    def sample_trade_data(self):
        """Create sample trade transaction data for testing."""
        return {
            'transaction_id': [f'TXN{i:03d}' for i in range(1, 21)],
            'date': pd.date_range('2024-01-01', periods=20, freq='D'),
            'fraud_label': [0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            'product': ['Electronics', 'Textiles', 'Machinery'] * 6 + ['Chemicals', 'Food'],
            'commodity_category': ['Tech', 'Apparel', 'Industrial'] * 6 + ['Chemical', 'Agriculture'],
            'unit_price': np.random.uniform(50, 200, 20),
            'trade_value': np.random.uniform(1000, 5000, 20),
            'market_price': np.random.uniform(45, 195, 20),
            'price_deviation': np.random.uniform(-0.3, 0.3, 20),
            'quantity': np.random.randint(5, 50, 20),
            'exporter_company': [f'Company{chr(65+i%5)}' for i in range(20)],
            'exporter_country': ['USA', 'Germany', 'Japan', 'China'] * 5,
            'importer_company': [f'Importer{chr(88+i%3)}' for i in range(20)],
            'importer_country': ['UK', 'France', 'Spain', 'Italy'] * 5,
            'cargo_volume': np.random.uniform(50, 500, 20),
            'shipping_route': [f'Route_{chr(65+i%4)}' for i in range(20)],
            'route_anomaly': [0, 1, 0, 1, 0] * 4,
            'distance_km': np.random.uniform(800, 3000, 20),
            'shipment_duration_days': np.random.uniform(5, 30, 20),
            'company_risk_score': np.random.uniform(0.1, 0.9, 20),
            'port_activity_index': np.random.uniform(0.5, 2.5, 20),
            'export_port': [f'Port_{chr(65+i%3)}' for i in range(20)],
            'import_port': [f'Port_{chr(88+i%3)}' for i in range(20)]
        }
    
    @pytest.fixture
    def sample_csv_file(self, sample_trade_data):
        """Create temporary CSV file with sample data."""
        df = pd.DataFrame(sample_trade_data)
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        yield temp_file.name
        
        # Cleanup
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    @pytest.fixture
    def temp_model_dir(self):
        """Create temporary directory for model storage."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_data_loading_integration(self, sample_csv_file):
        """Test 1: Data loading produces valid DataFrame for pipeline."""
        print("\n🔄 Test 1: Data Loading Integration")
        
        # Load data
        df = load_dataset(sample_csv_file)
        
        # Validate data loading
        assert isinstance(df, pd.DataFrame), "Should return DataFrame"
        assert len(df) == 20, "Should load all 20 transactions"
        assert not df.empty, "DataFrame should not be empty"
        
        # Validate required columns for pipeline
        required_cols = ['transaction_id', 'date', 'fraud_label', 'price_deviation', 
                        'route_anomaly', 'company_risk_score', 'port_activity_index',
                        'shipment_duration_days', 'distance_km', 'cargo_volume', 'quantity']
        
        for col in required_cols:
            assert col in df.columns, f"Missing required column: {col}"
        
        # Validate data types
        assert pd.api.types.is_datetime64_any_dtype(df['date']), "Date should be datetime"
        assert pd.api.types.is_numeric_dtype(df['fraud_label']), "Fraud label should be numeric"
        
        print("✅ Data loading integration passed")
    
    def test_feature_engineering_integration(self, sample_csv_file):
        """Test 2: Feature engineering produces valid features for ML model."""
        print("\n🔧 Test 2: Feature Engineering Integration")
        
        # Load data
        df_raw = load_dataset(sample_csv_file)
        
        # Engineer features
        df_features = engineer_features(df_raw)
        
        # Validate feature engineering output
        assert isinstance(df_features, pd.DataFrame), "Should return DataFrame"
        assert len(df_features) == len(df_raw), "Should preserve all rows"
        
        # Validate all required features exist
        expected_features = [
            'price_anomaly_score',
            'route_risk_score',
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        
        for feature in expected_features:
            assert feature in df_features.columns, f"Missing feature: {feature}"
            assert pd.api.types.is_numeric_dtype(df_features[feature]), f"{feature} should be numeric"
            assert not df_features[feature].isna().any(), f"{feature} should not have NaN values"
        
        # Validate feature calculations
        # price_anomaly_score = abs(price_deviation)
        assert np.allclose(
            df_features['price_anomaly_score'], 
            df_raw['price_deviation'].abs(),
            rtol=1e-5
        ), "Price anomaly score calculation incorrect"
        
        # route_risk_score = route_anomaly
        assert (df_features['route_risk_score'] == df_raw['route_anomaly']).all(), \
            "Route risk score should equal route_anomaly"
        
        # company_network_risk = company_risk_score
        assert (df_features['company_network_risk'] == df_raw['company_risk_score']).all(), \
            "Company network risk should equal company_risk_score"
        
        # port_congestion_score = port_activity_index
        assert (df_features['port_congestion_score'] == df_raw['port_activity_index']).all(), \
            "Port congestion score should equal port_activity_index"
        
        # shipment_duration_risk = shipment_duration_days / distance_km
        expected_duration_risk = df_raw['shipment_duration_days'] / df_raw['distance_km'].replace(0, 1)
        assert np.allclose(
            df_features['shipment_duration_risk'],
            expected_duration_risk,
            rtol=1e-5
        ), "Shipment duration risk calculation incorrect"
        
        # volume_spike_score = cargo_volume / quantity
        expected_volume_spike = df_raw['cargo_volume'] / df_raw['quantity'].replace(0, 1)
        assert np.allclose(
            df_features['volume_spike_score'],
            expected_volume_spike,
            rtol=1e-5
        ), "Volume spike score calculation incorrect"
        
        # Validate feature ranges are reasonable
        for feature in expected_features:
            assert df_features[feature].min() >= -1e6, f"{feature} has unreasonably low values"
            assert df_features[feature].max() <= 1e6, f"{feature} has unreasonably high values"
            assert not np.isinf(df_features[feature]).any(), f"{feature} contains infinite values"
        
        print("✅ Feature engineering integration passed")
    
    def test_model_training_integration(self, sample_csv_file):
        """Test 3: Model training works correctly with engineered features."""
        print("\n🤖 Test 3: Model Training Integration")
        
        # Load and prepare data
        df_raw = load_dataset(sample_csv_file)
        df_features = engineer_features(df_raw)
        
        # Train model
        model = train_model(df_features)
        
        # Validate model training
        assert isinstance(model, IsolationForest), "Should return IsolationForest model"
        assert hasattr(model, 'predict'), "Model should have predict method"
        assert hasattr(model, 'decision_function'), "Model should have decision_function method"
        assert hasattr(model, 'estimators_'), "Model should be fitted"
        
        # Validate model parameters
        assert model.n_estimators == 100, "Should have 100 estimators"
        assert model.contamination == 0.1, "Should have 0.1 contamination rate"
        assert model.random_state == 42, "Should have random_state=42"
        
        # Test model can make predictions
        feature_cols = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        X = df_features[feature_cols]
        
        predictions = model.predict(X)
        assert len(predictions) == len(df_features), "Should predict for all samples"
        assert set(predictions).issubset({-1, 1}), "Predictions should be -1 or 1"
        
        scores = model.decision_function(X)
        assert len(scores) == len(df_features), "Should score all samples"
        assert not np.isnan(scores).any(), "Scores should not be NaN"
        
        print("✅ Model training integration passed")
    
    def test_model_persistence_integration(self, sample_csv_file, temp_model_dir):
        """Test 4: Model can be saved and loaded correctly."""
        print("\n💾 Test 4: Model Persistence Integration")
        
        # Train model
        df_raw = load_dataset(sample_csv_file)
        df_features = engineer_features(df_raw)
        model = train_model(df_features)
        
        # Save model
        model_path = os.path.join(temp_model_dir, 'test_model.pkl')
        save_model(model, model_path)
        
        # Validate file was created
        assert os.path.exists(model_path), "Model file should exist"
        assert os.path.getsize(model_path) > 0, "Model file should not be empty"
        
        # Load model
        loaded_model = load_model(model_path)
        
        # Validate loaded model
        assert isinstance(loaded_model, IsolationForest), "Loaded model should be IsolationForest"
        assert hasattr(loaded_model, 'estimators_'), "Loaded model should be fitted"
        
        # Verify loaded model produces same predictions
        feature_cols = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        X = df_features[feature_cols]
        
        original_scores = model.decision_function(X)
        loaded_scores = loaded_model.decision_function(X)
        
        assert np.allclose(original_scores, loaded_scores, rtol=1e-5), \
            "Loaded model should produce same scores as original"
        
        print("✅ Model persistence integration passed")
    
    def test_fraud_detection_scoring_integration(self, sample_csv_file, temp_model_dir):
        """Test 5: Fraud detection scoring works correctly with trained model."""
        print("\n🎯 Test 5: Fraud Detection Scoring Integration")
        
        # Prepare pipeline
        df_raw = load_dataset(sample_csv_file)
        df_features = engineer_features(df_raw)
        model = train_model(df_features)
        
        # Save and load model (test full persistence cycle)
        model_path = os.path.join(temp_model_dir, 'fraud_model.pkl')
        save_model(model, model_path)
        loaded_model = load_fraud_detector(model_path)
        
        # Score transactions
        df_scored = score_transactions(df_features, loaded_model)
        
        # Validate scoring output
        assert isinstance(df_scored, pd.DataFrame), "Should return DataFrame"
        assert len(df_scored) == len(df_features), "Should preserve all rows"
        assert 'risk_score' in df_scored.columns, "Should have risk_score column"
        
        # Validate risk scores
        risk_scores = df_scored['risk_score']
        assert pd.api.types.is_numeric_dtype(risk_scores), "Risk scores should be numeric"
        assert not risk_scores.isna().any(), "Risk scores should not be NaN"
        assert not np.isinf(risk_scores).any(), "Risk scores should not be infinite"
        
        # Validate score distribution
        assert risk_scores.std() > 0, "Risk scores should have variation"
        assert len(risk_scores.unique()) > 1, "Risk scores should not all be identical"
        
        # Validate original data is preserved
        assert all(col in df_scored.columns for col in df_features.columns), \
            "Should preserve all original columns"
        
        print("✅ Fraud detection scoring integration passed")
    
    def test_risk_classification_integration(self, sample_csv_file, temp_model_dir):
        """Test 6: Risk classification works correctly with scored transactions."""
        print("\n🏷️  Test 6: Risk Classification Integration")
        
        # Prepare pipeline
        df_raw = load_dataset(sample_csv_file)
        df_features = engineer_features(df_raw)
        model = train_model(df_features)
        df_scored = score_transactions(df_features, model)
        
        # Classify risk
        df_classified = classify_risk(df_scored)
        
        # Validate classification output
        assert isinstance(df_classified, pd.DataFrame), "Should return DataFrame"
        assert len(df_classified) == len(df_scored), "Should preserve all rows"
        assert 'risk_category' in df_classified.columns, "Should have risk_category column"
        
        # Validate risk categories
        risk_categories = df_classified['risk_category']
        valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
        assert risk_categories.isin(valid_categories).all(), \
            f"All categories should be in {valid_categories}"
        
        # Validate category-score consistency
        safe_mask = df_classified['risk_category'] == 'SAFE'
        suspicious_mask = df_classified['risk_category'] == 'SUSPICIOUS'
        fraud_mask = df_classified['risk_category'] == 'FRAUD'
        
        if safe_mask.any():
            assert (df_classified.loc[safe_mask, 'risk_score'] < -0.2).all(), \
                "SAFE transactions should have score < -0.2"
        
        if suspicious_mask.any():
            suspicious_scores = df_classified.loc[suspicious_mask, 'risk_score']
            assert ((suspicious_scores >= -0.2) & (suspicious_scores < 0.2)).all(), \
                "SUSPICIOUS transactions should have score between -0.2 and 0.2"
        
        if fraud_mask.any():
            assert (df_classified.loc[fraud_mask, 'risk_score'] >= 0.2).all(), \
                "FRAUD transactions should have score >= 0.2"
        
        # Validate distribution
        category_counts = risk_categories.value_counts()
        assert len(category_counts) >= 1, "Should have at least one category"
        
        print(f"   Category distribution: {category_counts.to_dict()}")
        print("✅ Risk classification integration passed")
    
    def test_end_to_end_pipeline_integration(self, sample_csv_file, temp_model_dir):
        """Test 7: Complete end-to-end ML pipeline integration."""
        print("\n🔄 Test 7: End-to-End Pipeline Integration")
        
        # Step 1: Data Loading
        print("   Step 1: Loading data...")
        df_raw = load_dataset(sample_csv_file)
        assert len(df_raw) == 20, "Should load 20 transactions"
        
        # Step 2: Schema Validation
        print("   Step 2: Validating schema...")
        schema_valid = validate_schema(df_raw)
        assert schema_valid, "Schema should be valid"
        
        # Step 3: Dataset Statistics
        print("   Step 3: Computing statistics...")
        stats = get_dataset_stats(df_raw)
        assert stats['basic_info']['total_rows'] == 20, "Stats should show 20 rows"
        
        # Step 4: Feature Engineering
        print("   Step 4: Engineering features...")
        df_features = engineer_features(df_raw)
        assert len(df_features.columns) > len(df_raw.columns), "Should add new features"
        
        # Step 5: Model Training
        print("   Step 5: Training model...")
        model = train_model(df_features)
        assert isinstance(model, IsolationForest), "Should train IsolationForest"
        
        # Step 6: Model Persistence
        print("   Step 6: Saving model...")
        model_path = os.path.join(temp_model_dir, 'pipeline_model.pkl')
        save_model(model, model_path)
        assert os.path.exists(model_path), "Model should be saved"
        
        # Step 7: Model Loading
        print("   Step 7: Loading model...")
        loaded_model = load_fraud_detector(model_path)
        assert isinstance(loaded_model, IsolationForest), "Should load IsolationForest"
        
        # Step 8: Transaction Scoring
        print("   Step 8: Scoring transactions...")
        df_scored = score_transactions(df_features, loaded_model)
        assert 'risk_score' in df_scored.columns, "Should have risk scores"
        
        # Step 9: Risk Classification
        print("   Step 9: Classifying risk...")
        df_final = classify_risk(df_scored)
        assert 'risk_category' in df_final.columns, "Should have risk categories"
        
        # Step 10: End-to-End Validation
        print("   Step 10: Validating end-to-end results...")
        
        # Validate data integrity
        assert len(df_final) == len(df_raw), "Should preserve transaction count"
        assert df_final['transaction_id'].equals(df_raw['transaction_id']), \
            "Should preserve transaction IDs"
        
        # Validate all pipeline outputs exist
        required_outputs = [
            'transaction_id', 'fraud_label', 'risk_score', 'risk_category',
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        
        for col in required_outputs:
            assert col in df_final.columns, f"Final output should have {col}"
        
        # Validate no data corruption
        assert not df_final['risk_score'].isna().any(), "No NaN risk scores"
        assert not df_final['risk_category'].isna().any(), "No NaN risk categories"
        
        # Validate risk score and category consistency
        for idx, row in df_final.iterrows():
            score = row['risk_score']
            category = row['risk_category']
            expected_category = get_risk_category(score)
            assert category == expected_category, \
                f"Row {idx}: category {category} inconsistent with score {score}"
        
        print("✅ End-to-end pipeline integration passed")
    
    def test_pipeline_with_real_dataset(self):
        """Test 8: Pipeline integration with real TRINETRA dataset."""
        print("\n📊 Test 8: Real Dataset Pipeline Integration")
        
        # Try both relative paths (from backend dir and from root)
        dataset_paths = [
            "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv",
            "../data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        ]
        
        dataset_path = None
        for path in dataset_paths:
            if os.path.exists(path):
                dataset_path = path
                break
        
        if dataset_path is None:
            pytest.skip("Real dataset not available for integration test")
        
        # Load real dataset
        print("   Loading real dataset...")
        df_raw = load_dataset(dataset_path)
        assert len(df_raw) > 0, "Real dataset should have transactions"
        print(f"   Loaded {len(df_raw)} transactions")
        
        # Run through complete pipeline
        print("   Engineering features...")
        df_features = engineer_features(df_raw)
        
        print("   Training model...")
        model = train_model(df_features)
        
        print("   Scoring transactions...")
        df_scored = score_transactions(df_features, model)
        
        print("   Classifying risk...")
        df_final = classify_risk(df_scored)
        
        # Validate results
        assert len(df_final) == len(df_raw), "Should preserve all transactions"
        assert 'risk_score' in df_final.columns, "Should have risk scores"
        assert 'risk_category' in df_final.columns, "Should have risk categories"
        
        # Analyze distribution
        category_counts = df_final['risk_category'].value_counts()
        fraud_rate = (df_final['risk_category'] == 'FRAUD').sum() / len(df_final)
        
        print(f"   Risk category distribution:")
        for category, count in category_counts.items():
            percentage = (count / len(df_final)) * 100
            print(f"     {category}: {count} ({percentage:.1f}%)")
        
        print(f"   Fraud detection rate: {fraud_rate:.1%}")
        
        # Validate reasonable distribution
        assert len(category_counts) >= 1, "Should have at least one category"
        assert fraud_rate >= 0.0 and fraud_rate <= 1.0, "Fraud rate should be between 0 and 1"
        
        print("✅ Real dataset pipeline integration passed")
    
    def test_pipeline_error_handling(self):
        """Test 9: Pipeline error handling and robustness."""
        print("\n⚠️  Test 9: Pipeline Error Handling")
        
        # Test missing file
        with pytest.raises(FileNotFoundError):
            load_dataset("nonexistent_file.csv")
        print("   ✓ Handles missing data file")
        
        # Test missing model
        with pytest.raises(FileNotFoundError):
            load_fraud_detector("nonexistent_model.pkl")
        print("   ✓ Handles missing model file")
        
        # Test empty DataFrame
        empty_df = pd.DataFrame()
        schema_valid = validate_schema(empty_df)
        assert not schema_valid, "Empty DataFrame should fail validation"
        print("   ✓ Handles empty DataFrame")
        
        # Test DataFrame with missing features
        incomplete_df = pd.DataFrame({
            'transaction_id': ['TXN001'],
            'price_deviation': [0.1]
        })
        
        with pytest.raises((KeyError, ValueError)):
            engineer_features(incomplete_df)
        print("   ✓ Handles missing required columns")
        
        print("✅ Pipeline error handling passed")
    
    def test_pipeline_data_flow_integrity(self, sample_csv_file):
        """Test 10: Data flow integrity through entire pipeline."""
        print("\n🔍 Test 10: Data Flow Integrity")
        
        # Load initial data
        df_raw = load_dataset(sample_csv_file)
        initial_txn_ids = df_raw['transaction_id'].tolist()
        initial_count = len(df_raw)
        
        # Track data through pipeline
        df_features = engineer_features(df_raw)
        assert df_features['transaction_id'].tolist() == initial_txn_ids, \
            "Feature engineering should preserve transaction IDs"
        assert len(df_features) == initial_count, \
            "Feature engineering should preserve row count"
        
        model = train_model(df_features)
        df_scored = score_transactions(df_features, model)
        assert df_scored['transaction_id'].tolist() == initial_txn_ids, \
            "Scoring should preserve transaction IDs"
        assert len(df_scored) == initial_count, \
            "Scoring should preserve row count"
        
        df_final = classify_risk(df_scored)
        assert df_final['transaction_id'].tolist() == initial_txn_ids, \
            "Classification should preserve transaction IDs"
        assert len(df_final) == initial_count, \
            "Classification should preserve row count"
        
        # Verify no data loss or duplication
        assert df_final['transaction_id'].nunique() == initial_count, \
            "Should have no duplicate transaction IDs"
        
        print("✅ Data flow integrity passed")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])
