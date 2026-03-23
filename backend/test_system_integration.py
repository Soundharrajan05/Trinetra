"""
System Integration Test for Complete TRINETRA AI Pipeline

This test validates that the complete system integration works as expected,
testing the actual main.py workflow components in isolation.

**Validates: System Integration Requirements from Task 10.2**
"""

import pytest
import pandas as pd
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path to import main components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import main application components
from backend.data_loader import load_dataset
from backend.feature_engineering import engineer_features
from backend.model import train_model, save_model, load_model
from backend.fraud_detection import score_transactions, classify_risk


class TestSystemIntegration:
    """Integration test for the complete TRINETRA AI system."""
    
    def test_main_workflow_components(self):
        """Test the main workflow components work together as in main.py."""
        
        # Check if real dataset exists
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Real dataset not available for system integration test")
        
        print("🔄 Testing complete system integration workflow...")
        
        # Step 1: Load dataset (as in main.py)
        print("Step 1: Loading dataset...")
        df_raw = load_dataset(dataset_path)
        assert len(df_raw) > 0, "Dataset should be loaded successfully"
        print(f"✅ Loaded {len(df_raw)} transactions")
        
        # Step 2: Engineer features (as in main.py)
        print("Step 2: Engineering features...")
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
        
        print(f"✅ Engineered {len(expected_features)} features")
        
        # Step 3: Train ML model (as in main.py)
        print("Step 3: Training ML model...")
        model = train_model(df_features)
        assert model is not None, "Model should be trained successfully"
        print("✅ ML model trained successfully")
        
        # Step 4: Score transactions (as in main.py)
        print("Step 4: Scoring transactions...")
        df_scored = score_transactions(df_features, model)
        assert 'risk_score' in df_scored.columns, "Should have risk scores"
        print(f"✅ Scored {len(df_scored)} transactions")
        
        # Step 5: Classify risk (as in main.py)
        print("Step 5: Classifying risk...")
        df_final = classify_risk(df_scored)
        assert 'risk_category' in df_final.columns, "Should have risk categories"
        
        # Validate risk categories
        valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
        actual_categories = set(df_final['risk_category'].unique())
        assert actual_categories.issubset(valid_categories), f"Invalid categories found: {actual_categories - valid_categories}"
        
        print(f"✅ Classified {len(df_final)} transactions into risk categories")
        
        # Step 6: Validate final output structure
        print("Step 6: Validating final output...")
        
        # Check that all original data is preserved
        assert len(df_final) == len(df_raw), "Should preserve all transactions"
        assert 'transaction_id' in df_final.columns, "Should preserve transaction IDs"
        
        # Check that all engineered features are present
        for feature in expected_features:
            assert feature in df_final.columns, f"Final output should have {feature}"
        
        # Check that ML outputs are present
        assert 'risk_score' in df_final.columns, "Final output should have risk scores"
        assert 'risk_category' in df_final.columns, "Final output should have risk categories"
        
        print("✅ Final output structure validated")
        
        # Step 7: Generate summary statistics
        print("Step 7: Generating summary statistics...")
        
        category_counts = df_final['risk_category'].value_counts()
        risk_score_stats = df_final['risk_score'].describe()
        
        print(f"Risk Category Distribution:")
        for category, count in category_counts.items():
            percentage = (count / len(df_final)) * 100
            print(f"  {category}: {count} ({percentage:.1f}%)")
        
        print(f"Risk Score Statistics:")
        print(f"  Mean: {risk_score_stats['mean']:.4f}")
        print(f"  Std:  {risk_score_stats['std']:.4f}")
        print(f"  Min:  {risk_score_stats['min']:.4f}")
        print(f"  Max:  {risk_score_stats['max']:.4f}")
        
        print("✅ System integration test completed successfully!")
        
        return {
            'total_transactions': len(df_final),
            'risk_categories': category_counts.to_dict(),
            'risk_score_stats': risk_score_stats.to_dict(),
            'features_engineered': len(expected_features)
        }
    
    def test_model_persistence_integration(self):
        """Test model persistence works in the system integration context."""
        
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Real dataset not available for model persistence test")
        
        print("🔄 Testing model persistence integration...")
        
        # Create temporary directory for model
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = os.path.join(temp_dir, 'test_integration_model.pkl')
            
            # Load and prepare data
            df_raw = load_dataset(dataset_path)
            df_features = engineer_features(df_raw.copy())
            
            # Train and save model
            print("Training and saving model...")
            model = train_model(df_features)
            save_model(model, model_path)
            assert os.path.exists(model_path), "Model file should be saved"
            
            # Load model and test
            print("Loading and testing saved model...")
            loaded_model = load_model(model_path)
            
            # Test that loaded model produces same results
            original_scores = score_transactions(df_features, model)
            loaded_scores = score_transactions(df_features, loaded_model)
            
            # Compare risk scores (should be identical)
            score_diff = abs(original_scores['risk_score'] - loaded_scores['risk_score']).max()
            assert score_diff < 1e-10, f"Loaded model should produce identical scores, max diff: {score_diff}"
            
            print("✅ Model persistence integration test passed!")
    
    def test_data_quality_integration(self):
        """Test that the system handles data quality issues appropriately."""
        
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Real dataset not available for data quality test")
        
        print("🔄 Testing data quality integration...")
        
        # Load dataset
        df_raw = load_dataset(dataset_path)
        
        # Check for data quality issues that the system should handle
        print("Checking data quality metrics...")
        
        # Check for missing values
        missing_counts = df_raw.isnull().sum()
        total_missing = missing_counts.sum()
        print(f"Total missing values: {total_missing}")
        
        # Check for duplicate transaction IDs
        duplicate_ids = df_raw['transaction_id'].duplicated().sum()
        print(f"Duplicate transaction IDs: {duplicate_ids}")
        
        # Check date range
        date_range = df_raw['date'].max() - df_raw['date'].min()
        print(f"Date range: {date_range.days} days")
        
        # The system should handle these gracefully
        df_features = engineer_features(df_raw.copy())
        model = train_model(df_features)
        df_final = classify_risk(score_transactions(df_features, model))
        
        # Verify no NaN values in critical outputs
        assert not df_final['risk_score'].isna().any(), "Risk scores should not have NaN values"
        assert not df_final['risk_category'].isna().any(), "Risk categories should not have NaN values"
        
        print("✅ Data quality integration test passed!")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])