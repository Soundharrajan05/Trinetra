"""
Simple End-to-End Functionality Validation for TRINETRA AI System

This test validates the core end-to-end functionality without complex server setup.
Tests the complete data pipeline and core system components.

**Validates: Task 10.2 - Validate end-to-end functionality**
"""

import pytest
import pandas as pd
import os
import sys
import logging

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all system components
from backend.data_loader import load_dataset, validate_schema, get_dataset_stats
from backend.feature_engineering import engineer_features
from backend.model import train_model, save_model, load_model
from backend.fraud_detection import score_transactions, classify_risk
from backend.ai_explainer import initialize_gemini, test_fallback_system

# Configure logging without Unicode characters
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestSimpleEndToEndValidation:
    """Simple end-to-end validation test for TRINETRA AI system."""
    
    DATASET_PATH = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    
    def test_01_complete_data_pipeline_validation(self):
        """Test complete data pipeline from raw data to final output."""
        logger.info("Testing complete data pipeline validation...")
        
        # Check if dataset exists
        if not os.path.exists(self.DATASET_PATH):
            pytest.skip("Dataset not available for end-to-end validation")
        
        # Step 1: Load and validate dataset
        logger.info("Step 1: Loading dataset...")
        df_raw = load_dataset(self.DATASET_PATH)
        assert len(df_raw) > 0, "Dataset should be loaded successfully"
        assert 'transaction_id' in df_raw.columns, "Should have transaction IDs"
        assert 'date' in df_raw.columns, "Should have date column"
        assert 'fraud_label' in df_raw.columns, "Should have fraud labels"
        
        # Validate schema
        assert validate_schema(df_raw), "Dataset schema should be valid"
        
        # Step 2: Engineer features
        logger.info("Step 2: Engineering features...")
        df_features = engineer_features(df_raw.copy())
        
        # Validate feature engineering
        expected_features = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        
        for feature in expected_features:
            assert feature in df_features.columns, f"Missing engineered feature: {feature}"
            assert not df_features[feature].isna().all(), f"Feature {feature} should not be all NaN"
        
        # Step 3: Train ML model
        logger.info("Step 3: Training ML model...")
        model = train_model(df_features)
        assert model is not None, "Model should be trained successfully"
        
        # Step 4: Score transactions
        logger.info("Step 4: Scoring transactions...")
        df_scored = score_transactions(df_features, model)
        assert 'risk_score' in df_scored.columns, "Should have ML risk scores"
        assert not df_scored['risk_score'].isna().any(), "Risk scores should not have NaN values"
        
        # Step 5: Classify risk
        logger.info("Step 5: Classifying risk...")
        df_final = classify_risk(df_scored)
        assert 'risk_category' in df_final.columns, "Should have risk categories"
        
        valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
        actual_categories = set(df_final['risk_category'].unique())
        assert actual_categories.issubset(valid_categories), f"Invalid categories: {actual_categories - valid_categories}"
        
        # Validate data consistency
        assert len(df_final) == len(df_raw), "Should preserve all transactions"
        
        # Generate pipeline statistics
        stats = {
            'total_transactions': len(df_final),
            'fraud_count': len(df_final[df_final['risk_category'] == 'FRAUD']),
            'suspicious_count': len(df_final[df_final['risk_category'] == 'SUSPICIOUS']),
            'safe_count': len(df_final[df_final['risk_category'] == 'SAFE']),
            'features_engineered': len(expected_features)
        }
        
        logger.info(f"Data pipeline validation passed: {stats}")
        
        # Validate mathematical consistency
        total_classified = stats['fraud_count'] + stats['suspicious_count'] + stats['safe_count']
        assert total_classified == stats['total_transactions'], "Category counts should sum to total"
        
        return stats