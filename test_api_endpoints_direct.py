#!/usr/bin/env python3
"""
Direct API Endpoint Testing for TRINETRA AI
Tests API endpoints by importing and calling them directly
"""

import sys
import os
import logging
import json
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_test_environment():
    """Set up the test environment with processed data."""
    logger.info("Setting up test environment...")
    
    try:
        # Add backend to path
        sys.path.append('backend')
        
        # Import required modules
        import data_loader
        import feature_engineering
        import model
        import fraud_detection
        import api
        
        # Load and process data
        df = data_loader.load_dataset("data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
        df = feature_engineering.engineer_features(df)
        
        # Load model and score transactions
        ml_model = model.load_model("models/isolation_forest.pkl")
        df = fraud_detection.score_transactions(df, ml_model)
        df = fraud_detection.classify_risk(df)
        
        # Set the processed data in the API module
        api.df_processed = df
        
        logger.info(f"✅ Test environment ready with {len(df)} transactions")
        return df, api.app
        
    except Exception as e:
        logger.error(f"❌ Failed to setup test environment: {e}")
        return None, None

def test_api_endpoints_direct(app, df):
    """Test API endpoints by calling them directly."""
    logger.info("Testing API endpoints directly...")
    
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    test_results = {}
    
    # Test endpoints
    endpoints = [
        ("/stats", "GET", "Dashboard statistics"),
        ("/transactions", "GET", "All transactions"),
        ("/suspicious", "GET", "Suspicious transactions"),
        ("/fraud", "GET", "Fraud transactions"),
        ("/session/info", "GET", "Session information"),
    ]
    
    for endpoint, method, description in endpoints:
        try:
            logger.info(f"Testing {endpoint}...")
            
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            success = response.status_code == 200
            test_results[endpoint] = success
            
            if success:
                logger.info(f"✅ {endpoint} - {description}: OK")
                
                # Validate response structure
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'status' in data:
                        logger.info(f"   Response status: {data.get('status')}")
                        if 'data' in data:
                            response_data = data['data']
                            if isinstance(response_data, list):
                                logger.info(f"   Data count: {len(response_data)}")
                            elif isinstance(response_data, dict):
                                logger.info(f"   Data keys: {list(response_data.keys())}")
                    else:
                        logger.warning(f"⚠️  {endpoint}: Unexpected response format")
                        
                except json.JSONDecodeError:
                    logger.warning(f"⚠️  {endpoint}: Invalid JSON response")
            else:
                logger.error(f"❌ {endpoint} - {description}: Failed ({response.status_code})")
                logger.error(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            logger.error(f"❌ {endpoint} - {description}: Exception - {e}")
            test_results[endpoint] = False
    
    return test_results

def test_interactive_endpoints(app, df):
    """Test interactive endpoints that require parameters."""
    logger.info("Testing interactive endpoints...")
    
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    test_results = {}
    
    try:
        # Get a sample transaction ID
        sample_transaction = df.iloc[0]
        transaction_id = sample_transaction['transaction_id']
        
        # Test explanation endpoint
        logger.info(f"Testing explanation for transaction {transaction_id}...")
        response = client.post(f"/explain/{transaction_id}")
        
        explanation_success = response.status_code == 200
        test_results["/explain"] = explanation_success
        
        if explanation_success:
            logger.info("✅ Explanation endpoint: OK")
            data = response.json()
            if 'data' in data and 'explanation' in data['data']:
                explanation = data['data']['explanation']
                logger.info(f"   Explanation length: {len(explanation)} characters")
            else:
                logger.warning("⚠️  No explanation content in response")
        else:
            logger.error(f"❌ Explanation endpoint: Failed ({response.status_code})")
        
        # Test query endpoint
        logger.info("Testing natural language query...")
        query_data = {"query": "How many transactions are there?"}
        response = client.post("/query", json=query_data)
        
        query_success = response.status_code == 200
        test_results["/query"] = query_success
        
        if query_success:
            logger.info("✅ Query endpoint: OK")
            data = response.json()
            if 'data' in data and 'response' in data['data']:
                query_response = data['data']['response']
                logger.info(f"   Query response length: {len(query_response)} characters")
            else:
                logger.warning("⚠️  No query response content")
        else:
            logger.error(f"❌ Query endpoint: Failed ({response.status_code})")
        
    except Exception as e:
        logger.error(f"❌ Interactive endpoints test failed: {e}")
        test_results["/explain"] = False
        test_results["/query"] = False
    
    return test_results

def test_data_compatibility(df):
    """Test that data structure is compatible with dashboard requirements."""
    logger.info("Testing data compatibility with dashboard...")
    
    try:
        # Check required columns for dashboard
        required_columns = [
            'transaction_id', 'risk_score', 'risk_category',
            'product', 'unit_price', 'market_price', 'price_deviation',
            'exporter_country', 'importer_country', 'shipping_route'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"❌ Missing required columns: {missing_columns}")
            return False
        
        logger.info("✅ All required columns present")
        
        # Check data types and ranges
        if df['risk_score'].dtype not in ['float64', 'float32']:
            logger.warning("⚠️  Risk score should be numeric")
        
        risk_categories = df['risk_category'].unique()
        expected_categories = ['SAFE', 'SUSPICIOUS', 'FRAUD']
        unexpected_categories = [cat for cat in risk_categories if cat not in expected_categories]
        if unexpected_categories:
            logger.warning(f"⚠️  Unexpected risk categories: {unexpected_categories}")
        
        logger.info(f"✅ Risk categories: {list(risk_categories)}")
        logger.info(f"✅ Risk score range: {df['risk_score'].min():.3f} to {df['risk_score'].max():.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Data compatibility test failed: {e}")
        return False

def main():
    """Run direct API endpoint testing."""
    logger.info("🔍 Starting Direct API Endpoint Testing")
    logger.info("=" * 60)
    
    # Setup test environment
    df, app = setup_test_environment()
    if df is None or app is None:
        logger.error("❌ Failed to setup test environment")
        return False
    
    # Run tests
    test_results = []
    
    # Test 1: Basic API endpoints
    basic_results = test_api_endpoints_direct(app, df)
    basic_passed = all(basic_results.values())
    test_results.append(("Basic API Endpoints", basic_passed))
    
    # Test 2: Interactive endpoints
    interactive_results = test_interactive_endpoints(app, df)
    interactive_passed = all(interactive_results.values())
    test_results.append(("Interactive Endpoints", interactive_passed))
    
    # Test 3: Data compatibility
    data_compatible = test_data_compatibility(df)
    test_results.append(("Data Compatibility", data_compatible))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 DIRECT API TEST RESULTS:")
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    # Detailed results
    logger.info("\n📋 DETAILED ENDPOINT RESULTS:")
    all_endpoint_results = {**basic_results, **interactive_results}
    for endpoint, passed in all_endpoint_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {endpoint}: {status}")
    
    logger.info("=" * 60)
    
    if all_passed:
        logger.info("🎉 DIRECT API TESTING: SUCCESS")
        logger.info("✅ All API endpoints are functional")
        logger.info("✅ Data structure is compatible with dashboard")
        logger.info("✅ Interactive features are working")
        logger.info("\n💡 API is ready for dashboard integration!")
    else:
        logger.error("❌ DIRECT API TESTING: SOME ISSUES FOUND")
        logger.error("See detailed results above")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)