"""
Test Complete Data Pipeline - System Integration Test

This test validates the complete data processing pipeline from CSV loading
through feature engineering, ML model training, and fraud detection scoring.

**Validates: Requirements US-1, US-2, US-3, FR-1, FR-2**
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

# Import modules to test
from data_loader import load_dataset, validate_schema, get_dataset_stats
from feature_engineering import engineer_features
from model import train_model, save_model, load_model
from fraud_detection import score_transactions, classify_risk


class TestCompleteDataPipeline:
    """Integration test for the complete data processing pipeline."""
    
    @pytest.fixture
    def sample_dataset_path(self):
        """Create a temporary CSV file with sample trade data."""
        # Create sample data that matches the expected schema
        sample_data = {
            'transaction_id': ['TXN001', 'TXN002', 'TXN003', 'TXN004', 'TXN005'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
            'fraud_label': [0, 1, 0, 1, 0],
            'product': ['Electronics', 'Textiles', 'Machinery', 'Chemicals', 'Food'],
            'commodity_category': ['Tech', 'Apparel', 'Industrial', 'Chemical', 'Agriculture'],
            'unit_price': [100.0, 50.0, 200.0, 75.0, 25.0],
            'trade_value': [1000.0, 1000.0, 1000.0, 1125.0, 1000.0],
            'market_price': [95.0, 60.0, 180.0, 80.0, 30.0],
            'price_deviation': [0.05, -0.17, 0.11, -0.06, -0.17],
            'quantity': [10, 20, 5, 15, 40],
            'exporter_company': ['CompanyA', 'CompanyB', 'CompanyA', 'CompanyC', 'CompanyB'],
            'exporter_country': ['USA', 'Germany', 'USA', 'Japan', 'Germany'],
            'importer_company': ['ImporterX', 'ImporterY', 'ImporterZ', 'ImporterX', 'ImporterY'],
            'importer_country': ['UK', 'France', 'Spain', 'UK', 'France'],
            'cargo_volume': [100, 200, 50, 150, 400],
            'shipping_route': ['Route_A', 'Route_B', 'Route_A', 'Route_C', 'Route_B'],
            'route_anomaly': [0, 1, 0, 1, 0],
            'distance_km': [1000, 2000, 1500, 800, 1200],
            'shipment_duration_days': [10, 25, 12, 15, 18],
            'company_risk_score': [0.2, 0.8, 0.3, 0.9, 0.1],
            'port_activity_index': [1.0, 2.0, 1.2, 1.8, 0.8],
            'export_port': ['Port_A', 'Port_B', 'Port_A', 'Port_C', 'Port_B'],
            'import_port': ['Port_X', 'Port_Y', 'Port_Z', 'Port_X', 'Port_Y']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        yield temp_file.name
        
        # Cleanup
        os.unlink(temp_file.name)
    
    @pytest.fixture
    def temp_model_dir(self):
        """Create temporary directory for model storage."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_complete_pipeline_flow(self, sample_dataset_path, temp_model_dir):
        """Test the complete data pipeline from CSV to fraud detection."""
        
        # Step 1: Data Loading
        print("Step 1: Testing data loading...")
        df_raw = load_dataset(sample_dataset_path)
        
        # Validate data loading
        assert isinstance(df_raw, pd.DataFrame), "Data loading should return DataFrame"
        assert len(df_raw) == 5, "Should load all 5 sample transactions"
        assert 'transaction_id' in df_raw.columns, "Should have transaction_id column"
        assert 'fraud_label' in df_raw.columns, "Should have fraud_label column"
        
        # Step 2: Schema Validation
        print("Step 2: Testing schema validation...")
        schema_valid = validate_schema(df_raw)
        assert schema_valid, "Schema validation should pass for valid data"
        
        # Step 3: Dataset Statistics
        print("Step 3: Testing dataset statistics...")
        stats = get_dataset_stats(df_raw)
        assert isinstance(stats, dict), "Stats should return dictionary"
        assert 'basic_info' in stats, "Should include basic_info section"
        assert stats['basic_info']['total_rows'] == 5, "Should count 5 transactions"
        
        # Step 4: Feature Engineering
        print("Step 4: Testing feature engineering...")
        df_features = engineer_features(df_raw.copy())
        
        # Validate feature engineering
        expected_features = [
            'price_anomaly_score',
            'route_risk_score', 
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        
        for feature in expected_features:
            assert feature in df_features.columns, f"Should have {feature} column"
            assert not df_features[feature].isna().any(), f"{feature} should not have NaN values"
        
        # Validate feature calculations
        assert df_features['price_anomaly_score'].iloc[0] == abs(0.05), "Price anomaly should be abs(price_deviation)"
        assert df_features['route_risk_score'].iloc[1] == 1, "Route risk should match route_anomaly"
        assert df_features['company_network_risk'].iloc[0] == 0.2, "Company risk should match company_risk_score"
        
        # Step 5: ML Model Training
        print("Step 5: Testing ML model training...")
        model = train_model(df_features)
        
        # Validate model training
        assert isinstance(model, IsolationForest), "Should return IsolationForest model"
        assert hasattr(model, 'predict'), "Model should have predict method"
        assert hasattr(model, 'decision_function'), "Model should have decision_function method"
        
        # Step 6: Model Persistence
        print("Step 6: Testing model persistence...")
        model_path = os.path.join(temp_model_dir, 'test_model.pkl')
        save_model(model, model_path)
        
        assert os.path.exists(model_path), "Model file should be saved"
        
        # Step 7: Model Loading
        print("Step 7: Testing model loading...")
        loaded_model = load_model(model_path)
        
        assert isinstance(loaded_model, IsolationForest), "Loaded model should be IsolationForest"
        
        # Step 8: Transaction Scoring
        print("Step 8: Testing transaction scoring...")
        df_scored = score_transactions(df_features.copy(), loaded_model)
        
        # Validate scoring
        assert 'risk_score' in df_scored.columns, "Should have risk_score column"
        assert not df_scored['risk_score'].isna().any(), "Risk scores should not be NaN"
        assert len(df_scored) == len(df_features), "Should preserve all transactions"
        
        # Step 9: Risk Classification
        print("Step 9: Testing risk classification...")
        df_final = classify_risk(df_scored.copy())
        
        # Validate classification
        assert 'risk_category' in df_final.columns, "Should have risk_category column"
        assert not df_final['risk_category'].isna().any(), "Risk categories should not be NaN"
        
        valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
        assert df_final['risk_category'].isin(valid_categories).all(), "All categories should be valid"
        
        # Step 10: End-to-End Validation
        print("Step 10: Testing end-to-end validation...")
        
        # Verify data integrity throughout pipeline
        assert len(df_final) == len(df_raw), "Should preserve transaction count"
        assert df_final['transaction_id'].equals(df_raw['transaction_id']), "Should preserve transaction IDs"
        
        # Verify all required columns exist
        required_columns = [
            'transaction_id', 'fraud_label', 'risk_score', 'risk_category'
        ] + expected_features
        
        for col in required_columns:
            assert col in df_final.columns, f"Final dataset should have {col} column"
        
        # Verify risk score consistency with categories
        safe_scores = df_final[df_final['risk_category'] == 'SAFE']['risk_score']
        suspicious_scores = df_final[df_final['risk_category'] == 'SUSPICIOUS']['risk_score']
        fraud_scores = df_final[df_final['risk_category'] == 'FRAUD']['risk_score']
        
        if len(safe_scores) > 0:
            assert (safe_scores < -0.2).all(), "SAFE transactions should have scores < -0.2"
        
        if len(suspicious_scores) > 0:
            assert ((suspicious_scores >= -0.2) & (suspicious_scores < 0.2)).all(), \
                "SUSPICIOUS transactions should have scores between -0.2 and 0.2"
        
        if len(fraud_scores) > 0:
            assert (fraud_scores >= 0.2).all(), "FRAUD transactions should have scores >= 0.2"
        
        print("✅ Complete data pipeline test passed!")
        
        # Don't return the dataframe to avoid pytest warning
    
    def test_pipeline_with_real_dataset(self):
        """Test pipeline with the actual TRINETRA dataset if available."""
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        
        if not os.path.exists(dataset_path):
            pytest.skip("Real dataset not available for testing")
        
        print("Testing with real TRINETRA dataset...")
        
        # Load real dataset
        df_raw = load_dataset(dataset_path)
        assert len(df_raw) > 0, "Real dataset should have transactions"
        
        # Run through pipeline
        df_features = engineer_features(df_raw.copy())
        model = train_model(df_features)
        df_scored = score_transactions(df_features, model)
        df_final = classify_risk(df_scored)
        
        # Validate results
        assert len(df_final) == len(df_raw), "Should preserve all transactions"
        assert 'risk_score' in df_final.columns, "Should have risk scores"
        assert 'risk_category' in df_final.columns, "Should have risk categories"
        
        # Check distribution of risk categories
        category_counts = df_final['risk_category'].value_counts()
        print(f"Risk category distribution: {category_counts.to_dict()}")
        
        # Should have at least one risk category
        assert len(category_counts) >= 1, "Should have at least one risk category"
        
        # If all transactions are in one category, that's still valid for the pipeline test
        if len(category_counts) == 1:
            print("Note: All transactions classified into single category - this is acceptable for pipeline testing")
        
        print("✅ Real dataset pipeline test passed!")
    
    def test_pipeline_error_handling(self, temp_model_dir):
        """Test pipeline error handling with invalid data."""
        
        # Test with missing file
        with pytest.raises(FileNotFoundError):
            load_dataset("nonexistent_file.csv")
        
        # Test with invalid model path
        with pytest.raises(FileNotFoundError):
            load_model("nonexistent_model.pkl")
        
        # Test with empty DataFrame - validate_schema should return False
        empty_df = pd.DataFrame()
        schema_valid = validate_schema(empty_df)
        assert not schema_valid, "Empty DataFrame should fail schema validation"
        
        print("✅ Pipeline error handling test passed!")
    
    def test_pipeline_performance(self, sample_dataset_path):
        """Test pipeline performance benchmarks."""
        import time
        
        # Measure data loading time
        start_time = time.time()
        df_raw = load_dataset(sample_dataset_path)
        load_time = time.time() - start_time
        
        # Measure feature engineering time
        start_time = time.time()
        df_features = engineer_features(df_raw.copy())
        feature_time = time.time() - start_time
        
        # Measure model training time
        start_time = time.time()
        model = train_model(df_features)
        train_time = time.time() - start_time
        
        # Measure scoring time
        start_time = time.time()
        df_scored = score_transactions(df_features, model)
        df_final = classify_risk(df_scored)
        score_time = time.time() - start_time
        
        print(f"Performance metrics:")
        print(f"  Data loading: {load_time:.3f}s")
        print(f"  Feature engineering: {feature_time:.3f}s")
        print(f"  Model training: {train_time:.3f}s")
        print(f"  Scoring & classification: {score_time:.3f}s")
        print(f"  Total pipeline time: {load_time + feature_time + train_time + score_time:.3f}s")
        
        # Performance assertions (reasonable for small dataset)
        assert load_time < 1.0, "Data loading should be fast for small dataset"
        assert feature_time < 1.0, "Feature engineering should be fast"
        assert train_time < 5.0, "Model training should complete quickly"
        assert score_time < 1.0, "Scoring should be fast"
        
        print("✅ Pipeline performance test passed!")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])