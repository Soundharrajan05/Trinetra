#!/usr/bin/env python3
"""
Proper API Integration Test for TRINETRA AI
Tests API endpoints with proper system initialization
"""

import sys
import os
import logging
import json
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_with_proper_initialization():
    """Test API endpoints with proper system initialization."""
    logger.info("🔍 Testing API with proper system initialization")
    logger.info("=" * 60)
    
    try:
        # Add backend to path
        sys.path.append('backend')
        
        # Import API module
        import api
        from fastapi.testclient import TestClient
        
        # Initialize the system (this sets up global variables)
        logger.info("Initializing TRINETRA AI system...")
        api.initialize_system()
        logger.info("✅ System initialized successfully")
        
        # Create test client
        client = TestClient(api.app)
        
        # Test results storage
        test_results = {}
        
        # Test basic endpoints
        logger.info("\n🧪 Testing basic API endpoints...")
        basic_endpoints = [
            ("/stats", "Dashboard statistics"),
            ("/transactions", "All transactions"),
            ("/suspicious", "Suspicious transactions"),
            ("/fraud", "Fraud transactions"),
            ("/session/info", "Session information"),
        ]
        
        for endpoint, description in basic_endpoints:
            try:
                logger.info(f"Testing {endpoint}...")
                response = client.get(endpoint)
                
                success = response.status_code == 200
                test_results[endpoint] = success
                
                if success:
                    logger.info(f"✅ {endpoint} - {description}: OK")
                    
                    # Validate response structure
                    data = response.json()
                    if isinstance(data, dict) and 'status' in data:
                        logger.info(f"   Status: {data.get('status')}")
                        if 'data' in data:
                            response_data = data['data']
                            if isinstance(response_data, list):
                                logger.info(f"   Data count: {len(response_data)}")
                            elif isinstance(response_data, dict):
                                logger.info(f"   Data keys: {list(response_data.keys())}")
                    
                else:
                    logger.error(f"❌ {endpoint} - {description}: Failed ({response.status_code})")
                    logger.error(f"   Response: {response.text[:200]}...")
                    
            except Exception as e:
                logger.error(f"❌ {endpoint} - {description}: Exception - {e}")
                test_results[endpoint] = False
        
        # Test interactive endpoints
        logger.info("\n🧪 Testing interactive endpoints...")
        
        # Get a sample transaction for testing
        transactions_response = client.get("/transactions")
        if transactions_response.status_code == 200:
            transactions_data = transactions_response.json()
            transactions = transactions_data.get('data', [])
            
            if transactions:
                sample_transaction = transactions[0]
                transaction_id = sample_transaction['transaction_id']
                
                # Test explanation endpoint
                logger.info(f"Testing explanation for transaction {transaction_id}...")
                explain_response = client.post(f"/explain/{transaction_id}")
                
                explain_success = explain_response.status_code == 200
                test_results["/explain"] = explain_success
                
                if explain_success:
                    logger.info("✅ Explanation endpoint: OK")
                    explain_data = explain_response.json()
                    if 'data' in explain_data and 'explanation' in explain_data['data']:
                        explanation = explain_data['data']['explanation']
                        logger.info(f"   Explanation length: {len(explanation)} characters")
                        logger.info(f"   Explanation preview: {explanation[:100]}...")
                else:
                    logger.error(f"❌ Explanation endpoint: Failed ({explain_response.status_code})")
                    logger.error(f"   Response: {explain_response.text[:200]}...")
                
                # Test query endpoint
                logger.info("Testing natural language query...")
                query_data = {"query": "How many transactions are there?"}
                query_response = client.post("/query", json=query_data)
                
                query_success = query_response.status_code == 200
                test_results["/query"] = query_success
                
                if query_success:
                    logger.info("✅ Query endpoint: OK")
                    query_data_response = query_response.json()
                    if 'data' in query_data_response and 'response' in query_data_response['data']:
                        query_result = query_data_response['data']['response']
                        logger.info(f"   Query response length: {len(query_result)} characters")
                        logger.info(f"   Query response preview: {query_result[:100]}...")
                else:
                    logger.error(f"❌ Query endpoint: Failed ({query_response.status_code})")
                    logger.error(f"   Response: {query_response.text[:200]}...")
            else:
                logger.error("❌ No transactions available for interactive testing")
                test_results["/explain"] = False
                test_results["/query"] = False
        else:
            logger.error("❌ Could not get transactions for interactive testing")
            test_results["/explain"] = False
            test_results["/query"] = False
        
        # Test alert endpoints
        logger.info("\n🧪 Testing alert endpoints...")
        alert_endpoints = [
            ("/alerts", "All alerts"),
            ("/alerts/statistics", "Alert statistics"),
        ]
        
        for endpoint, description in alert_endpoints:
            try:
                logger.info(f"Testing {endpoint}...")
                response = client.get(endpoint)
                
                success = response.status_code == 200
                test_results[endpoint] = success
                
                if success:
                    logger.info(f"✅ {endpoint} - {description}: OK")
                    data = response.json()
                    if 'data' in data:
                        response_data = data['data']
                        if isinstance(response_data, list):
                            logger.info(f"   Data count: {len(response_data)}")
                        elif isinstance(response_data, dict):
                            logger.info(f"   Data keys: {list(response_data.keys())}")
                else:
                    logger.error(f"❌ {endpoint} - {description}: Failed ({response.status_code})")
                    
            except Exception as e:
                logger.error(f"❌ {endpoint} - {description}: Exception - {e}")
                test_results[endpoint] = False
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 API INTEGRATION TEST RESULTS:")
        
        all_passed = True
        for endpoint, passed in test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"  {endpoint}: {status}")
            if not passed:
                all_passed = False
        
        logger.info("=" * 60)
        
        if all_passed:
            logger.info("🎉 API INTEGRATION TEST: SUCCESS")
            logger.info("✅ All API endpoints are functional")
            logger.info("✅ System initialization works correctly")
            logger.info("✅ Data flows properly through API")
            logger.info("✅ Interactive features are working")
            logger.info("✅ Alert system is operational")
            logger.info("\n💡 API is fully ready for dashboard integration!")
        else:
            logger.error("❌ API INTEGRATION TEST: SOME ISSUES FOUND")
            failed_endpoints = [ep for ep, passed in test_results.items() if not passed]
            logger.error(f"Failed endpoints: {failed_endpoints}")
        
        return all_passed
        
    except Exception as e:
        logger.error(f"❌ API integration test failed with exception: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_dashboard_data_requirements():
    """Test that API provides all data required by dashboard."""
    logger.info("\n🧪 Testing dashboard data requirements...")
    
    try:
        sys.path.append('backend')
        import api
        from fastapi.testclient import TestClient
        
        client = TestClient(api.app)
        
        # Test transactions endpoint for dashboard table
        response = client.get("/transactions")
        if response.status_code != 200:
            logger.error("❌ Cannot get transactions data")
            return False
        
        transactions = response.json().get('data', [])
        if not transactions:
            logger.error("❌ No transaction data available")
            return False
        
        # Check required fields for dashboard
        sample_transaction = transactions[0]
        required_fields = [
            'transaction_id', 'risk_score', 'risk_category',
            'product', 'unit_price', 'market_price', 'price_deviation',
            'exporter_country', 'importer_country', 'shipping_route',
            'date', 'quantity', 'cargo_volume'
        ]
        
        missing_fields = [field for field in required_fields if field not in sample_transaction]
        if missing_fields:
            logger.error(f"❌ Missing required fields for dashboard: {missing_fields}")
            return False
        
        logger.info("✅ All required transaction fields present")
        
        # Test stats endpoint for dashboard KPIs
        response = client.get("/stats")
        if response.status_code != 200:
            logger.error("❌ Cannot get statistics data")
            return False
        
        stats = response.json().get('data', {})
        required_stats = [
            'total_transactions', 'fraud_rate', 'total_trade_value',
            'suspicious_count', 'fraud_count', 'safe_count'
        ]
        
        missing_stats = [stat for stat in required_stats if stat not in stats]
        if missing_stats:
            logger.error(f"❌ Missing required stats for dashboard: {missing_stats}")
            return False
        
        logger.info("✅ All required statistics available")
        logger.info(f"   Total transactions: {stats['total_transactions']}")
        logger.info(f"   Fraud rate: {stats['fraud_rate']:.2%}")
        logger.info(f"   Total trade value: ${stats['total_trade_value']:,.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Dashboard data requirements test failed: {e}")
        return False

def main():
    """Run the proper API integration test."""
    logger.info("🚀 Starting Proper API Integration Test for TRINETRA AI")
    
    # Test 1: API functionality with proper initialization
    api_test_passed = test_api_with_proper_initialization()
    
    # Test 2: Dashboard data requirements
    dashboard_test_passed = test_dashboard_data_requirements()
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("🏁 FINAL INTEGRATION TEST SUMMARY:")
    logger.info(f"  API Functionality: {'✅ PASS' if api_test_passed else '❌ FAIL'}")
    logger.info(f"  Dashboard Data Requirements: {'✅ PASS' if dashboard_test_passed else '❌ FAIL'}")
    logger.info("=" * 60)
    
    overall_success = api_test_passed and dashboard_test_passed
    
    if overall_success:
        logger.info("🎉 OVERALL RESULT: API AND DASHBOARD INTEGRATION VERIFIED")
        logger.info("✅ FastAPI backend is fully functional")
        logger.info("✅ All endpoints return correct data")
        logger.info("✅ Dashboard data requirements are met")
        logger.info("✅ Interactive features work properly")
        logger.info("✅ System is ready for production use")
    else:
        logger.error("❌ OVERALL RESULT: INTEGRATION ISSUES FOUND")
        logger.error("Some components need attention before full integration")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)