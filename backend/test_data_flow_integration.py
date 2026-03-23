"""
Integration Test: Validate Data Flow Through System

This test validates the complete data pipeline from CSV loading through 
feature engineering, ML model training/scoring, fraud detection, and API integration.

Task: 12.2 - Validate data flow through system

**Validates: Requirements US-1, US-2, US-3, US-5, FR-1, FR-2, FR-4**

Data Flow:
CSV File → Data Loader (validation) → Feature Engineering (6 features) → 
ML Model Training/Loading → Fraud Detection (scoring + classification) → 
FastAPI Backend (REST endpoints) → Streamlit Dashboard (visualization) → 
Gemini API (explanations)
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
import shutil
from pathlib import Path

# Import modules to test
from data_loader import load_dataset, validate_schema
from feature_engineering import engineer_features
from model import train_model, save_model, load_model
from fraud_detection import score_transactions, classify_risk, load_fraud_detector


class TestDataFlowIntegration:
    """Integration test validating complete data flow through all system components."""
    
    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data matching the expected schema."""
        return {
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
    
    @pytest.fixture
    def temp_csv_file(self, sample_csv_data):
        """Create temporary CSV file."""
        df = pd.DataFrame(sample_csv_data)
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        yield temp_file.name
        
        os.unlink(temp_file.name)
    
    @pytest.fixture
    def temp_model_dir(self):
        """Create temporary directory for model storage."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_stage_1_csv_loading_and_validation(self, temp_csv_file):
        """
        Stage 1: CSV File → Data Loader (validation)
        
        Validates:
        - CSV data loads correctly with all required columns
        - Schema validation passes
        - Data types are correct
        """
        print("\n=== Stage 1: CSV Loading and Validation ===")
        
        # Load CSV data
        df = load_dataset(temp_csv_file)
        
        # Validate data loaded correctly
        assert isinstance(df, pd.DataFrame), "Should return DataFrame"
        assert len(df) == 5, "Should load all 5 transactions"
        
        # Validate required columns exist
        required_columns = [
            'transaction_id', 'date', 'fraud_label', 'product', 'commodity_category',
            'unit_price', 'trade_value', 'market_price', 'price_deviation', 'quantity',
            'exporter_company', 'exporter_country', 'importer_company', 'importer_country',
            'cargo_volume', 'shipping_route', 'route_anomaly', 'distance_km',
            'shipment_duration_days', 'company_risk_score', 'port_activity_index'
        ]
        
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"
        
        # Validate schema
        assert validate_schema(df), "Schema validation should pass"
        
        # Validate data types
        assert pd.api.types.is_datetime64_any_dtype(df['date']), "Date should be datetime"
        assert pd.api.types.is_numeric_dtype(df['unit_price']), "unit_price should be numeric"
        assert pd.api.types.is_numeric_dtype(df['fraud_label']), "fraud_label should be numeric"
        
        print("✅ Stage 1 passed: CSV data loaded and validated")
        return df
    
    def test_stage_2_feature_engineering(self, temp_csv_file):
        """
        Stage 2: Data Loader → Feature Engineering (6 features)
        
        Validates:
        - All 6 fraud detection features are generated
        - Feature calculations are correct
        - No missing values in features
        """
        print("\n=== Stage 2: Feature Engineering ===")
        
        # Load data
        df = load_dataset(temp_csv_file)
        
        # Engineer features
        df_features = engineer_features(df)
        
        # Validate 6 features exist
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
            assert not df_features[feature].isna().any(), f"{feature} has NaN values"
        
        # Validate feature calculations
        # price_anomaly_score = abs(price_deviation)
        assert np.allclose(
            df_features['price_anomaly_score'].values,
            np.abs(df_features['price_deviation'].values)
        ), "price_anomaly_score calculation incorrect"
        
        # route_risk_score = route_anomaly
        assert np.allclose(
            df_features['route_risk_score'].values,
            df_features['route_anomaly'].values
        ), "route_risk_score calculation incorrect"
        
        # company_network_risk = company_risk_score
        assert np.allclose(
            df_features['company_network_risk'].values,
            df_features['company_risk_score'].values
        ), "company_network_risk calculation incorrect"
        
        # port_congestion_score = port_activity_index
        assert np.allclose(
            df_features['port_congestion_score'].values,
            df_features['port_activity_index'].values
        ), "port_congestion_score calculation incorrect"
        
        # shipment_duration_risk = shipment_duration_days / distance_km
        expected_duration_risk = df_features['shipment_duration_days'] / df_features['distance_km'].replace(0, 1)
        assert np.allclose(
            df_features['shipment_duration_risk'].values,
            expected_duration_risk.values
        ), "shipment_duration_risk calculation incorrect"
        
        # volume_spike_score = cargo_volume / quantity
        expected_volume_spike = df_features['cargo_volume'] / df_features['quantity'].replace(0, 1)
        assert np.allclose(
            df_features['volume_spike_score'].values,
            expected_volume_spike.values
        ), "volume_spike_score calculation incorrect"
        
        print("✅ Stage 2 passed: 6 features engineered correctly")
        return df_features
    
    def test_stage_3_ml_model_training_and_loading(self, temp_csv_file, temp_model_dir):
        """
        Stage 3: Feature Engineering → ML Model Training/Loading
        
        Validates:
        - Model trains successfully on engineered features
        - Model can be saved and loaded
        - Model has correct configuration
        """
        print("\n=== Stage 3: ML Model Training and Loading ===")
        
        # Load and engineer features
        df = load_dataset(temp_csv_file)
        df_features = engineer_features(df)
        
        # Train model
        model = train_model(df_features)
        
        # Validate model
        assert model is not None, "Model should not be None"
        assert hasattr(model, 'predict'), "Model should have predict method"
        assert hasattr(model, 'decision_function'), "Model should have decision_function method"
        assert hasattr(model, 'estimators_'), "Model should be fitted"
        
        # Validate model configuration
        assert model.n_estimators == 100, "Should have 100 estimators"
        assert model.contamination == 0.1, "Should have 0.1 contamination"
        assert model.random_state == 42, "Should have random_state=42"
        
        # Save model
        model_path = os.path.join(temp_model_dir, 'test_model.pkl')
        save_model(model, model_path)
        assert os.path.exists(model_path), "Model file should exist"
        
        # Load model
        loaded_model = load_model(model_path)
        assert loaded_model is not None, "Loaded model should not be None"
        assert hasattr(loaded_model, 'estimators_'), "Loaded model should be fitted"
        
        print("✅ Stage 3 passed: Model trained, saved, and loaded")
        return loaded_model
    
    def test_stage_4_fraud_detection_scoring(self, temp_csv_file, temp_model_dir):
        """
        Stage 4: ML Model → Fraud Detection (scoring + classification)
        
        Validates:
        - Transactions are scored correctly
        - Risk categories are assigned
        - Risk scores align with categories
        """
        print("\n=== Stage 4: Fraud Detection Scoring and Classification ===")
        
        # Load, engineer, and train
        df = load_dataset(temp_csv_file)
        df_features = engineer_features(df)
        model = train_model(df_features)
        
        # Score transactions
        df_scored = score_transactions(df_features, model)
        
        # Validate scoring
        assert 'risk_score' in df_scored.columns, "Should have risk_score column"
        assert len(df_scored) == len(df_features), "Should preserve all transactions"
        assert not df_scored['risk_score'].isna().any(), "Risk scores should not be NaN"
        
        # Classify risk
        df_classified = classify_risk(df_scored)
        
        # Validate classification
        assert 'risk_category' in df_classified.columns, "Should have risk_category column"
        assert not df_classified['risk_category'].isna().any(), "Risk categories should not be NaN"
        
        # Validate risk categories
        valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
        assert df_classified['risk_category'].isin(valid_categories).all(), \
            "All categories should be valid"
        
        # Validate risk score consistency with categories
        for idx, row in df_classified.iterrows():
            score = row['risk_score']
            category = row['risk_category']
            
            if category == 'SAFE':
                assert score < -0.2, f"SAFE category should have score < -0.2, got {score}"
            elif category == 'SUSPICIOUS':
                assert -0.2 <= score < 0.2, \
                    f"SUSPICIOUS category should have -0.2 <= score < 0.2, got {score}"
            elif category == 'FRAUD':
                assert score >= 0.2, f"FRAUD category should have score >= 0.2, got {score}"
        
        print("✅ Stage 4 passed: Transactions scored and classified")
        return df_classified
    
    def test_stage_5_data_integrity_throughout_pipeline(self, temp_csv_file):
        """
        Stage 5: Data Integrity Validation
        
        Validates:
        - Transaction count preserved throughout pipeline
        - Transaction IDs preserved
        - No data corruption
        """
        print("\n=== Stage 5: Data Integrity Throughout Pipeline ===")
        
        # Stage 1: Load
        df_loaded = load_dataset(temp_csv_file)
        original_count = len(df_loaded)
        original_ids = df_loaded['transaction_id'].tolist()
        
        # Stage 2: Engineer features
        df_features = engineer_features(df_loaded)
        assert len(df_features) == original_count, "Feature engineering should preserve count"
        assert df_features['transaction_id'].tolist() == original_ids, \
            "Feature engineering should preserve IDs"
        
        # Stage 3: Train and score
        model = train_model(df_features)
        df_scored = score_transactions(df_features, model)
        assert len(df_scored) == original_count, "Scoring should preserve count"
        assert df_scored['transaction_id'].tolist() == original_ids, \
            "Scoring should preserve IDs"
        
        # Stage 4: Classify
        df_final = classify_risk(df_scored)
        assert len(df_final) == original_count, "Classification should preserve count"
        assert df_final['transaction_id'].tolist() == original_ids, \
            "Classification should preserve IDs"
        
        # Validate all original columns still exist
        for col in df_loaded.columns:
            assert col in df_final.columns, f"Original column {col} should be preserved"
        
        print("✅ Stage 5 passed: Data integrity maintained throughout pipeline")
    
    def test_stage_6_api_data_format(self, temp_csv_file):
        """
        Stage 6: API Data Format Validation
        
        Validates:
        - Data can be converted to API-friendly format
        - All required fields are present
        - Data types are JSON-serializable
        """
        print("\n=== Stage 6: API Data Format Validation ===")
        
        # Run through pipeline
        df = load_dataset(temp_csv_file)
        df_features = engineer_features(df)
        model = train_model(df_features)
        df_scored = score_transactions(df_features, model)
        df_final = classify_risk(df_scored)
        
        # Convert to API format (list of dicts)
        transactions = df_final.to_dict('records')
        
        # Validate API format
        assert isinstance(transactions, list), "Should be list of transactions"
        assert len(transactions) == len(df_final), "Should have all transactions"
        
        # Validate each transaction
        for txn in transactions:
            assert isinstance(txn, dict), "Each transaction should be a dict"
            
            # Required fields for API
            required_fields = [
                'transaction_id', 'risk_score', 'risk_category',
                'price_anomaly_score', 'route_risk_score', 'company_network_risk',
                'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
            ]
            
            for field in required_fields:
                assert field in txn, f"Transaction should have {field}"
            
            # Validate data types are JSON-serializable
            assert isinstance(txn['transaction_id'], str), "transaction_id should be string"
            assert isinstance(txn['risk_score'], (int, float)), "risk_score should be numeric"
            assert isinstance(txn['risk_category'], str), "risk_category should be string"
        
        print("✅ Stage 6 passed: Data properly formatted for API")
    
    def test_complete_data_flow_end_to_end(self, temp_csv_file):
        """
        Complete End-to-End Data Flow Test
        
        Validates the entire pipeline:
        CSV → Load → Validate → Engineer → Train → Score → Classify → API Format
        """
        print("\n=== Complete End-to-End Data Flow Test ===")
        
        # Stage 1: CSV Loading
        print("Stage 1: Loading CSV...")
        df_raw = load_dataset(temp_csv_file)
        assert len(df_raw) > 0, "Should load data"
        assert validate_schema(df_raw), "Schema should be valid"
        
        # Stage 2: Feature Engineering
        print("Stage 2: Engineering features...")
        df_features = engineer_features(df_raw)
        expected_features = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        for feature in expected_features:
            assert feature in df_features.columns, f"Missing feature: {feature}"
        
        # Stage 3: ML Model Training
        print("Stage 3: Training ML model...")
        model = train_model(df_features)
        assert model is not None, "Model should be trained"
        
        # Stage 4: Fraud Detection
        print("Stage 4: Scoring and classifying...")
        df_scored = score_transactions(df_features, model)
        df_final = classify_risk(df_scored)
        
        assert 'risk_score' in df_final.columns, "Should have risk scores"
        assert 'risk_category' in df_final.columns, "Should have risk categories"
        
        # Stage 5: API Format
        print("Stage 5: Converting to API format...")
        transactions = df_final.to_dict('records')
        assert len(transactions) == len(df_raw), "Should preserve all transactions"
        
        # Final validation
        print("\nFinal Validation:")
        print(f"  Transactions processed: {len(df_final)}")
        print(f"  Features generated: {len(expected_features)}")
        print(f"  Risk categories: {df_final['risk_category'].value_counts().to_dict()}")
        
        # Validate data flow completeness
        assert len(df_final) == len(df_raw), "Data count preserved"
        assert all(col in df_final.columns for col in df_raw.columns), "Original columns preserved"
        assert all(feat in df_final.columns for feat in expected_features), "Features added"
        assert 'risk_score' in df_final.columns, "Risk scores added"
        assert 'risk_category' in df_final.columns, "Risk categories added"
        
        print("\n✅ Complete end-to-end data flow test passed!")
        print("=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
