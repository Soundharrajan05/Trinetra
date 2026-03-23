#!/usr/bin/env python3
"""
End-to-End Dataset Processing Test for TRINETRA AI

This script validates the complete data processing pipeline:
1. Load dataset
2. Feature engineering
3. Model training/loading
4. Fraud detection scoring
5. Risk classification
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from backend.data_loader import load_dataset
from backend.feature_engineering import engineer_features
from backend.model import train_model, save_model, load_model
from backend.fraud_detection import score_transactions, classify_risk

def test_full_pipeline():
    """Test the complete data processing pipeline."""
    print("\n" + "="*70)
    print("TRINETRA AI - END-TO-END DATASET PROCESSING TEST")
    print("="*70)
    
    dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    model_path = "models/test_isolation_forest.pkl"
    
    # Step 1: Load dataset
    print("\n[STEP 1] Loading dataset...")
    try:
        df = load_dataset(dataset_path)
        print(f"✓ Dataset loaded: {df.shape}")
        print(f"  - Rows: {df.shape[0]}")
        print(f"  - Columns: {df.shape[1]}")
    except Exception as e:
        print(f"✗ Failed to load dataset: {e}")
        return False
    
    # Step 2: Feature engineering
    print("\n[STEP 2] Engineering features...")
    try:
        df_features = engineer_features(df)
        print(f"✓ Features engineered: {df_features.shape}")
        
        # Check for new feature columns
        expected_features = [
            'price_anomaly_score',
            'route_risk_score',
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        
        missing_features = [f for f in expected_features if f not in df_features.columns]
        if missing_features:
            print(f"✗ Missing features: {missing_features}")
            return False
        
        print(f"  - All expected features present:")
        for feature in expected_features:
            non_null = df_features[feature].notna().sum()
            print(f"    • {feature}: {non_null}/{len(df_features)} non-null values")
        
    except Exception as e:
        print(f"✗ Failed to engineer features: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Train model
    print("\n[STEP 3] Training ML model...")
    try:
        model = train_model(df_features)
        print(f"✓ Model trained successfully")
        print(f"  - Model type: {type(model).__name__}")
        print(f"  - N estimators: {model.n_estimators}")
        print(f"  - Contamination: {model.contamination}")
        
        # Save model
        save_model(model, model_path)
        print(f"✓ Model saved to: {model_path}")
        
    except Exception as e:
        print(f"✗ Failed to train model: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Load model
    print("\n[STEP 4] Loading trained model...")
    try:
        loaded_model = load_model(model_path)
        print(f"✓ Model loaded successfully")
        print(f"  - Model type: {type(loaded_model).__name__}")
        
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return False
    
    # Step 5: Score transactions
    print("\n[STEP 5] Scoring transactions...")
    try:
        df_scored = score_transactions(df_features, loaded_model)
        print(f"✓ Transactions scored: {df_scored.shape}")
        
        # Check for risk_score column
        if 'risk_score' not in df_scored.columns:
            print(f"✗ risk_score column not found")
            return False
        
        risk_scores = df_scored['risk_score']
        print(f"  - Risk scores generated:")
        print(f"    • Mean: {risk_scores.mean():.4f}")
        print(f"    • Std: {risk_scores.std():.4f}")
        print(f"    • Min: {risk_scores.min():.4f}")
        print(f"    • Max: {risk_scores.max():.4f}")
        
    except Exception as e:
        print(f"✗ Failed to score transactions: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 6: Classify risk
    print("\n[STEP 6] Classifying risk levels...")
    try:
        df_classified = classify_risk(df_scored)
        print(f"✓ Risk levels classified: {df_classified.shape}")
        
        # Check for risk_category column
        if 'risk_category' not in df_classified.columns:
            print(f"✗ risk_category column not found")
            return False
        
        # Count risk categories
        category_counts = df_classified['risk_category'].value_counts()
        print(f"  - Risk category distribution:")
        for category, count in category_counts.items():
            percentage = (count / len(df_classified)) * 100
            print(f"    • {category}: {count} ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"✗ Failed to classify risk: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 7: Validate final output
    print("\n[STEP 7] Validating final output...")
    try:
        # Check all expected columns are present
        required_final_columns = [
            'transaction_id', 'date', 'product', 'fraud_label',
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score',
            'risk_score', 'risk_category'
        ]
        
        missing_columns = [col for col in required_final_columns if col not in df_classified.columns]
        if missing_columns:
            print(f"✗ Missing final columns: {missing_columns}")
            return False
        
        print(f"✓ All required columns present")
        
        # Check data integrity
        if df_classified['transaction_id'].isnull().any():
            print(f"✗ Found null transaction IDs")
            return False
        
        if df_classified['risk_score'].isnull().any():
            print(f"✗ Found null risk scores")
            return False
        
        if df_classified['risk_category'].isnull().any():
            print(f"✗ Found null risk categories")
            return False
        
        print(f"✓ Data integrity validated")
        
        # Sample output
        print(f"\n  Sample processed transactions:")
        sample_cols = ['transaction_id', 'product', 'fraud_label', 'risk_score', 'risk_category']
        print(df_classified[sample_cols].head(5).to_string(index=False))
        
    except Exception as e:
        print(f"✗ Failed to validate final output: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Cleanup
    print("\n[CLEANUP] Removing test model...")
    try:
        if os.path.exists(model_path):
            os.remove(model_path)
            print(f"✓ Test model removed")
    except Exception as e:
        print(f"⚠ Warning: Could not remove test model: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("✓ END-TO-END PIPELINE TEST PASSED")
    print("="*70)
    print("\nThe system successfully:")
    print("  1. Loaded the CSV dataset (1000 rows, 32 columns)")
    print("  2. Engineered 6 fraud detection features")
    print("  3. Trained an IsolationForest model")
    print("  4. Saved and loaded the model")
    print("  5. Scored all transactions with risk scores")
    print("  6. Classified transactions into risk categories")
    print("  7. Validated data integrity throughout the pipeline")
    print("\n✓ Dataset is ready for the TRINETRA AI system!")
    print("="*70)
    
    return True

if __name__ == "__main__":
    try:
        success = test_full_pipeline()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
