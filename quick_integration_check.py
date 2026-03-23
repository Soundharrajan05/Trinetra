#!/usr/bin/env python3
"""
Quick Integration Check for TRINETRA AI
Verifies that API and dashboard components can be imported and initialized
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_backend_imports():
    """Test that all backend modules can be imported."""
    logger.info("Testing backend module imports...")
    
    try:
        # Test core backend imports
        sys.path.append('backend')
        
        import data_loader
        logger.info("✅ data_loader module imported successfully")
        
        import feature_engineering
        logger.info("✅ feature_engineering module imported successfully")
        
        import model
        logger.info("✅ model module imported successfully")
        
        import fraud_detection
        logger.info("✅ fraud_detection module imported successfully")
        
        import ai_explainer
        logger.info("✅ ai_explainer module imported successfully")
        
        import api
        logger.info("✅ api module imported successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Backend import failed: {e}")
        return False

def test_frontend_imports():
    """Test that frontend modules can be imported."""
    logger.info("Testing frontend module imports...")
    
    try:
        sys.path.append('frontend')
        
        import dashboard
        logger.info("✅ dashboard module imported successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Frontend import failed: {e}")
        return False

def test_data_pipeline():
    """Test the data processing pipeline."""
    logger.info("Testing data processing pipeline...")
    
    try:
        sys.path.append('backend')
        import data_loader
        import feature_engineering
        
        # Load dataset
        df = data_loader.load_dataset("data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
        logger.info(f"✅ Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Test feature engineering
        df_features = feature_engineering.engineer_features(df)
        logger.info(f"✅ Features engineered: {len(df_features.columns)} total columns")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Data pipeline test failed: {e}")
        return False

def test_api_initialization():
    """Test API initialization without starting server."""
    logger.info("Testing API initialization...")
    
    try:
        sys.path.append('backend')
        import api
        
        # Check if FastAPI app can be created
        app = api.app
        logger.info("✅ FastAPI app initialized successfully")
        
        # Check routes
        routes = [route.path for route in app.routes]
        expected_routes = ['/transactions', '/suspicious', '/fraud', '/stats', '/explain', '/query']
        
        missing_routes = [route for route in expected_routes if not any(route in r for r in routes)]
        if missing_routes:
            logger.warning(f"⚠️  Missing routes: {missing_routes}")
        else:
            logger.info("✅ All expected API routes are defined")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ API initialization test failed: {e}")
        return False

def test_ml_model():
    """Test ML model loading and prediction."""
    logger.info("Testing ML model...")
    
    try:
        sys.path.append('backend')
        import model
        import fraud_detection
        
        # Check if model file exists
        model_path = "models/isolation_forest.pkl"
        if not os.path.exists(model_path):
            logger.warning(f"⚠️  Model file not found: {model_path}")
            return False
        
        # Load model
        ml_model = model.load_model(model_path)
        logger.info("✅ ML model loaded successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ML model test failed: {e}")
        return False

def main():
    """Run all integration checks."""
    logger.info("🔍 Starting Quick Integration Check for TRINETRA AI")
    logger.info("=" * 60)
    
    tests = [
        ("Backend Imports", test_backend_imports),
        ("Frontend Imports", test_frontend_imports),
        ("Data Pipeline", test_data_pipeline),
        ("API Initialization", test_api_initialization),
        ("ML Model", test_ml_model),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 INTEGRATION CHECK RESULTS:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    logger.info("=" * 60)
    
    if all_passed:
        logger.info("🎉 QUICK INTEGRATION CHECK: ALL COMPONENTS READY")
        logger.info("✅ Backend modules can be imported and initialized")
        logger.info("✅ Frontend modules are accessible")
        logger.info("✅ Data pipeline is functional")
        logger.info("✅ API can be initialized")
        logger.info("✅ ML model is available")
        logger.info("\n💡 System components are ready for integration!")
        return True
    else:
        logger.error("❌ QUICK INTEGRATION CHECK: SOME COMPONENTS FAILED")
        logger.error("Issues found with system components - see details above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)