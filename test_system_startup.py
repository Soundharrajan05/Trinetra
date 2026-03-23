#!/usr/bin/env python3
"""
TRINETRA AI System Startup Test
Tests the main application startup process without running the servers.
"""

import os
import sys
import logging
from pathlib import Path

# Add backend directory to Python path for imports
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_system_startup():
    """Test the complete system startup process."""
    
    print("🔍 TRINETRA AI System Startup Test")
    print("=" * 50)
    
    try:
        # Import all required modules
        print("1. Testing module imports...")
        from data_loader import load_dataset, validate_schema, get_dataset_stats
        from feature_engineering import engineer_features
        from model import train_model, save_model, load_model
        from fraud_detection import score_transactions, classify_risk
        from ai_explainer import initialize_gemini, test_fallback_system
        print("   ✅ All modules imported successfully")
        
        # Test dataset loading
        print("\n2. Testing dataset loading...")
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not Path(dataset_path).exists():
            print(f"   ❌ Dataset not found: {dataset_path}")
            return False
            
        df = load_dataset(dataset_path)
        if df is None or df.empty:
            print("   ❌ Failed to load dataset")
            return False
            
        print(f"   ✅ Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Test schema validation
        if not validate_schema(df):
            print("   ❌ Schema validation failed")
            return False
        print("   ✅ Schema validation passed")
        
        # Test feature engineering
        print("\n3. Testing feature engineering...")
        df_engineered = engineer_features(df)
        new_features = [col for col in df_engineered.columns if col not in df.columns]
        print(f"   ✅ Feature engineering completed: {len(new_features)} new features")
        
        # Test model loading
        print("\n4. Testing ML model...")
        model_path = "models/isolation_forest.pkl"
        if not Path(model_path).exists():
            print(f"   ❌ Model not found: {model_path}")
            return False
            
        model = load_model(model_path)
        print("   ✅ Model loaded successfully")
        
        # Test fraud detection
        print("\n5. Testing fraud detection...")
        df_scored = score_transactions(df_engineered, model)
        df_classified = classify_risk(df_scored)
        
        risk_counts = df_classified['risk_category'].value_counts().to_dict()
        print(f"   ✅ Fraud detection completed: {risk_counts}")
        
        # Test AI integration
        print("\n6. Testing AI integration...")
        try:
            gemini_model = initialize_gemini()
            print("   ✅ Gemini API initialized")
        except Exception as e:
            print(f"   ⚠️  Gemini API failed (expected): {e}")
        
        fallback_result = test_fallback_system()
        if fallback_result.get('test_status') == 'success':
            print("   ✅ Fallback system working")
        else:
            print("   ❌ Fallback system failed")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 SYSTEM STARTUP TEST PASSED!")
        print("All components are ready for deployment.")
        print("\nTo start the full system, run: python main.py")
        return True
        
    except Exception as e:
        print(f"\n❌ System startup test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system_startup()
    sys.exit(0 if success else 1)