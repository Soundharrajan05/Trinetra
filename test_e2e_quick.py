#!/usr/bin/env python3
"""
Quick End-to-End Functionality Test for TRINETRA AI
Validates core system functionality efficiently.

**Validates: System Integration Tests (section 10.2) - Task: Validate end-to-end functionality**

This test validates:
1. Complete data pipeline from CSV loading through fraud detection
2. API integration working properly
3. All components working together seamlessly
"""

import sys
import os
import time
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_data_pipeline():
    """Test the complete data pipeline."""
    print("📊 Testing Data Pipeline...")
    
    try:
        # Test data loading
        from data_loader import load_dataset, validate_schema
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        
        if not os.path.exists(dataset_path):
            print("❌ Dataset not found")
            return False
        
        df = load_dataset(dataset_path)
        if df is None or df.empty:
            print("❌ Failed to load dataset")
            return False
        
        print(f"✅ Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Test feature engineering
        from feature_engineering import engineer_features
        df_engineered = engineer_features(df)
        
        if len(df_engineered.columns) <= len(df.columns):
            print("❌ Feature engineering failed")
            return False
        
        print(f"✅ Feature engineering: {len(df_engineered.columns)} columns (added {len(df_engineered.columns) - len(df.columns)} features)")
        
        # Test ML model
        from fraud_detection import load_fraud_detector, score_transactions, classify_risk
        model = load_fraud_detector()
        
        if model is None:
            print("❌ Failed to load ML model")
            return False
        
        print("✅ ML model loaded successfully")
        
        # Test scoring
        df_scored = score_transactions(df_engineered, model)
        df_classified = classify_risk(df_scored)
        
        if 'risk_score' not in df_classified.columns or 'risk_category' not in df_classified.columns:
            print("❌ Transaction scoring failed")
            return False
        
        risk_categories = df_classified['risk_category'].value_counts()
        print(f"✅ Transaction scoring: {dict(risk_categories)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data pipeline error: {e}")
        return False

def test_api_integration():
    """Test API integration using TestClient."""
    print("\n🔌 Testing API Integration...")
    
    try:
        from fastapi.testclient import TestClient
        from api import app, initialize_system
        
        # Initialize system
        initialize_system()
        client = TestClient(app)
        
        # Test key endpoints
        endpoints = [
            ("/", "Root"),
            ("/stats", "Statistics"),
            ("/transactions?limit=5", "Transactions"),
            ("/alerts", "Alerts"),
            ("/session/info", "Session")
        ]
        
        all_passed = True
        for endpoint, name in endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"✅ {name} endpoint: HTTP {response.status_code}")
            else:
                print(f"❌ {name} endpoint: HTTP {response.status_code}")
                all_passed = False
        
        # Test AI explanation
        transactions_response = client.get("/transactions?limit=1")
        if transactions_response.status_code == 200:
            transactions = transactions_response.json()['data']['transactions']
            if transactions:
                transaction_id = transactions[0]['transaction_id']
                explain_response = client.post(f"/explain/{transaction_id}", json={"force_ai": False})
                if explain_response.status_code == 200:
                    print("✅ AI explanation endpoint working")
                else:
                    print(f"❌ AI explanation failed: HTTP {explain_response.status_code}")
                    all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ API integration error: {e}")
        return False

def test_system_performance():
    """Test basic performance requirements."""
    print("\n⚡ Testing Performance...")
    
    try:
        from fastapi.testclient import TestClient
        from api import app
        
        client = TestClient(app)
        
        # Test response times
        start_time = time.time()
        response = client.get("/stats")
        duration = time.time() - start_time
        
        if response.status_code == 200 and duration < 1.0:
            print(f"✅ API response time: {duration:.3f}s < 1.0s")
            return True
        else:
            print(f"❌ API too slow: {duration:.3f}s >= 1.0s")
            return False
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def main():
    """Run the quick end-to-end test."""
    print("🔍 TRINETRA AI - Quick End-to-End Functionality Test")
    print("=" * 55)
    
    start_time = time.time()
    
    # Run tests
    tests = [
        ("Data Pipeline", test_data_pipeline),
        ("API Integration", test_api_integration),
        ("Performance", test_system_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    total_duration = time.time() - start_time
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n" + "=" * 55)
    print("📋 TEST SUMMARY")
    print("=" * 55)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total:.1%})")
    print(f"Total time: {total_duration:.2f}s")
    
    if passed == total:
        print("\n🎉 END-TO-END FUNCTIONALITY TEST PASSED!")
        print("✅ Complete data pipeline from CSV loading through fraud detection")
        print("✅ API integration working properly")
        print("✅ All components working together seamlessly")
        print("✅ Performance requirements met")
        return True
    else:
        print("\n❌ END-TO-END FUNCTIONALITY TEST FAILED!")
        print(f"❌ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)