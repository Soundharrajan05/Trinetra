#!/usr/bin/env python3
"""
Simple test to verify backend works in TEST_MODE without external dependencies.
"""

import os
import sys
import time

# Set TEST_MODE before importing any modules
os.environ["TEST_MODE"] = "true"

# Add backend to path
sys.path.insert(0, "backend")

def test_ai_explainer():
    """Test AI explainer in TEST_MODE."""
    print("Testing AI explainer in TEST_MODE...")
    
    from ai_explainer import explain_transaction, answer_investigation_query
    
    # Test transaction explanation
    sample_transaction = {
        'transaction_id': 'TEST001',
        'product': 'Electronics',
        'price_deviation': 0.5,
        'risk_category': 'SUSPICIOUS'
    }
    
    result = explain_transaction(sample_transaction)
    print(f"✅ Explanation result: {result}")
    assert isinstance(result, str), "Should return string"
    assert "test mode" in result.lower(), "Should indicate test mode"
    
    # Test investigation query
    context = {'total_transactions': 100, 'fraud_cases': 10}
    query_result = answer_investigation_query("What is the fraud rate?", context)
    print(f"✅ Query result: {query_result}")
    assert isinstance(query_result, str), "Should return string"
    assert "test mode" in query_result.lower(), "Should indicate test mode"

def test_data_pipeline():
    """Test data pipeline components."""
    print("Testing data pipeline...")
    
    from data_loader import load_dataset
    from feature_engineering import engineer_features
    from fraud_detection import load_fraud_detector, score_transactions, classify_risk
    
    # Load dataset
    dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    if not os.path.exists(dataset_path):
        print("⚠️ Dataset not found, skipping data pipeline test")
        return
    
    df = load_dataset(dataset_path)
    print(f"✅ Loaded {len(df)} transactions")
    
    # Engineer features
    df_features = engineer_features(df)
    print(f"✅ Engineered features: {df_features.shape}")
    
    # Load model and score
    model = load_fraud_detector()
    df_scored = score_transactions(df_features, model)
    df_classified = classify_risk(df_scored)
    print(f"✅ Classified transactions: {df_classified['risk_category'].value_counts().to_dict()}")

def test_api_initialization():
    """Test API initialization without starting server."""
    print("Testing API initialization...")
    
    from api import initialize_system
    
    try:
        # This should work without starting the server
        initialize_system()
        print("✅ API system initialized successfully")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        raise

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing TRINETRA AI Backend in TEST_MODE")
    print("=" * 60)
    
    try:
        test_ai_explainer()
        print()
        
        test_data_pipeline()
        print()
        
        test_api_initialization()
        print()
        
        print("=" * 60)
        print("✅ All backend tests passed in TEST_MODE!")
        print("Backend is ready for integration testing.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()