"""
TRINETRA AI - Local Deployment Test
Tests the complete local deployment process to ensure all components work correctly.

Test Coverage:
1. System can be deployed with `python main.py`
2. All components start correctly (FastAPI backend, Streamlit dashboard)
3. Data loading and ML model initialization
4. Dashboard accessibility and functionality
5. Gemini API integration
6. End-to-end functionality

Author: TRINETRA AI Team
Date: 2024
"""

import os
import sys
import time
import subprocess
import requests
import pytest
from pathlib import Path
import pandas as pd
import signal

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Test configuration
DATASET_PATH = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
MODEL_PATH = "models/isolation_forest.pkl"
API_HOST = "localhost"
API_PORT = 8000
DASHBOARD_PORT = 8501
STARTUP_TIMEOUT = 30  # seconds
API_TIMEOUT = 5  # seconds


class TestLocalDeployment:
    """Test suite for local deployment process"""
    
    @pytest.fixture(scope="class")
    def deployment_process(self):
        """Start the main.py process and yield it for tests"""
        print("\n🚀 Starting TRINETRA AI deployment process...")
        
        # Start main.py as subprocess
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Wait for services to start
        print("⏳ Waiting for services to start...")
        time.sleep(STARTUP_TIMEOUT)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            pytest.fail(f"Deployment process failed to start:\nSTDOUT: {stdout}\nSTDERR: {stderr}")
        
        yield process
        
        # Cleanup: terminate the process
        print("\n🛑 Shutting down deployment process...")
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        print("✅ Deployment process terminated")
    
    def test_dataset_exists(self):
        """Test 1: Verify dataset file exists"""
        print("\n📊 Test 1: Checking dataset existence...")
        assert Path(DATASET_PATH).exists(), f"Dataset not found at {DATASET_PATH}"
        print("✅ Dataset file exists")
    
    def test_dataset_loading(self):
        """Test 2: Verify dataset can be loaded and has correct structure"""
        print("\n📊 Test 2: Testing dataset loading...")
        
        from data_loader import load_dataset, validate_schema
        
        df = load_dataset(DATASET_PATH)
        assert df is not None, "Dataset loading returned None"
        assert not df.empty, "Dataset is empty"
        assert len(df) > 0, "Dataset has no rows"
        
        # Validate schema
        assert validate_schema(df), "Dataset schema validation failed"
        
        print(f"✅ Dataset loaded successfully: {len(df)} rows, {len(df.columns)} columns")
    
    def test_feature_engineering(self):
        """Test 3: Verify feature engineering works correctly"""
        print("\n🔧 Test 3: Testing feature engineering...")
        
        from data_loader import load_dataset
        from feature_engineering import engineer_features
        
        df = load_dataset(DATASET_PATH)
        df_engineered = engineer_features(df)
        
        # Check that new features were added
        expected_features = [
            'price_anomaly_score',
            'route_risk_score',
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        
        for feature in expected_features:
            assert feature in df_engineered.columns, f"Feature {feature} not found"
        
        print(f"✅ Feature engineering completed: {len(expected_features)} features added")
    
    def test_model_initialization(self):
        """Test 4: Verify ML model can be loaded or trained"""
        print("\n🤖 Test 4: Testing ML model initialization...")
        
        from model import load_model, train_model, save_model
        from data_loader import load_dataset
        from feature_engineering import engineer_features
        
        # Check if model exists
        if Path(MODEL_PATH).exists():
            model = load_model(MODEL_PATH)
            assert model is not None, "Model loading failed"
            print("✅ Existing model loaded successfully")
        else:
            # Train new model
            df = load_dataset(DATASET_PATH)
            df_engineered = engineer_features(df)
            model = train_model(df_engineered)
            assert model is not None, "Model training failed"
            
            # Save model
            Path(MODEL_PATH).parent.mkdir(exist_ok=True)
            save_model(model, MODEL_PATH)
            print("✅ New model trained and saved successfully")
    
    def test_fraud_detection(self):
        """Test 5: Verify fraud detection scoring works"""
        print("\n🔍 Test 5: Testing fraud detection...")
        
        from data_loader import load_dataset
        from feature_engineering import engineer_features
        from model import load_model
        from fraud_detection import score_transactions, classify_risk
        
        df = load_dataset(DATASET_PATH)
        df_engineered = engineer_features(df)
        model = load_model(MODEL_PATH)
        
        df_scored = score_transactions(df_engineered, model)
        assert 'risk_score' in df_scored.columns, "risk_score column not found"
        
        df_classified = classify_risk(df_scored)
        assert 'risk_category' in df_classified.columns, "risk_category column not found"
        
        # Check that all categories are valid
        valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
        actual_categories = set(df_classified['risk_category'].unique())
        assert actual_categories.issubset(valid_categories), f"Invalid categories found: {actual_categories - valid_categories}"
        
        fraud_count = len(df_classified[df_classified['risk_category'] == 'FRAUD'])
        suspicious_count = len(df_classified[df_classified['risk_category'] == 'SUSPICIOUS'])
        safe_count = len(df_classified[df_classified['risk_category'] == 'SAFE'])
        
        print(f"✅ Fraud detection completed: {fraud_count} fraud, {suspicious_count} suspicious, {safe_count} safe")
    
    def test_fastapi_server_running(self, deployment_process):
        """Test 6: Verify FastAPI server is running and accessible"""
        print("\n🌐 Test 6: Testing FastAPI server...")
        
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"http://{API_HOST}:{API_PORT}/", timeout=API_TIMEOUT)
                if response.status_code == 200:
                    print(f"✅ FastAPI server is running on http://{API_HOST}:{API_PORT}")
                    return
            except requests.exceptions.RequestException:
                if i < max_retries - 1:
                    print(f"⏳ Waiting for API server... ({i+1}/{max_retries})")
                    time.sleep(2)
                else:
                    pytest.fail("FastAPI server is not responding")
    
    def test_api_endpoints(self, deployment_process):
        """Test 7: Verify all API endpoints are working"""
        print("\n🔌 Test 7: Testing API endpoints...")
        
        base_url = f"http://{API_HOST}:{API_PORT}"
        
        # Test /transactions endpoint
        response = requests.get(f"{base_url}/transactions", timeout=API_TIMEOUT)
        assert response.status_code == 200, f"/transactions endpoint failed: {response.status_code}"
        transactions = response.json()
        assert isinstance(transactions, list), "/transactions should return a list"
        assert len(transactions) > 0, "/transactions returned empty list"
        print(f"  ✅ /transactions: {len(transactions)} transactions")
        
        # Test /suspicious endpoint
        response = requests.get(f"{base_url}/suspicious", timeout=API_TIMEOUT)
        assert response.status_code == 200, f"/suspicious endpoint failed: {response.status_code}"
        suspicious = response.json()
        assert isinstance(suspicious, list), "/suspicious should return a list"
        print(f"  ✅ /suspicious: {len(suspicious)} suspicious transactions")
        
        # Test /fraud endpoint
        response = requests.get(f"{base_url}/fraud", timeout=API_TIMEOUT)
        assert response.status_code == 200, f"/fraud endpoint failed: {response.status_code}"
        fraud = response.json()
        assert isinstance(fraud, list), "/fraud should return a list"
        print(f"  ✅ /fraud: {len(fraud)} fraud transactions")
        
        # Test /stats endpoint
        response = requests.get(f"{base_url}/stats", timeout=API_TIMEOUT)
        assert response.status_code == 200, f"/stats endpoint failed: {response.status_code}"
        stats = response.json()
        assert isinstance(stats, dict), "/stats should return a dict"
        print(f"  ✅ /stats: {stats}")
        
        print("✅ All API endpoints working correctly")
    
    def test_streamlit_dashboard_running(self, deployment_process):
        """Test 8: Verify Streamlit dashboard is running and accessible"""
        print("\n📱 Test 8: Testing Streamlit dashboard...")
        
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"http://{API_HOST}:{DASHBOARD_PORT}/", timeout=API_TIMEOUT)
                if response.status_code == 200:
                    print(f"✅ Streamlit dashboard is running on http://{API_HOST}:{DASHBOARD_PORT}")
                    return
            except requests.exceptions.RequestException:
                if i < max_retries - 1:
                    print(f"⏳ Waiting for dashboard... ({i+1}/{max_retries})")
                    time.sleep(2)
                else:
                    pytest.fail("Streamlit dashboard is not responding")
    
    def test_gemini_api_integration(self):
        """Test 9: Verify Gemini API integration (with fallback)"""
        print("\n🧠 Test 9: Testing Gemini API integration...")
        
        from ai_explainer import initialize_gemini, test_fallback_system
        
        # Test Gemini initialization (may fail if API key invalid)
        try:
            model = initialize_gemini()
            print("  ✅ Gemini API initialized successfully")
        except Exception as e:
            print(f"  ⚠️ Gemini API initialization failed: {e}")
            print("  ℹ️ This is expected if API key is invalid - fallback will be used")
        
        # Test fallback system
        fallback_results = test_fallback_system()
        assert fallback_results.get('test_status') == 'success', "Fallback system test failed"
        print("  ✅ Fallback explanation system working")
        
        print("✅ AI integration test completed")
    
    def test_end_to_end_workflow(self, deployment_process):
        """Test 10: Verify complete end-to-end workflow"""
        print("\n🔄 Test 10: Testing end-to-end workflow...")
        
        base_url = f"http://{API_HOST}:{API_PORT}"
        
        # 1. Get all transactions
        response = requests.get(f"{base_url}/transactions", timeout=API_TIMEOUT)
        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) > 0
        print(f"  ✅ Step 1: Retrieved {len(transactions)} transactions")
        
        # 2. Get suspicious transactions
        response = requests.get(f"{base_url}/suspicious", timeout=API_TIMEOUT)
        assert response.status_code == 200
        suspicious = response.json()
        print(f"  ✅ Step 2: Retrieved {len(suspicious)} suspicious transactions")
        
        # 3. Get fraud transactions
        response = requests.get(f"{base_url}/fraud", timeout=API_TIMEOUT)
        assert response.status_code == 200
        fraud = response.json()
        print(f"  ✅ Step 3: Retrieved {len(fraud)} fraud transactions")
        
        # 4. Test explanation endpoint (if there are suspicious transactions)
        if len(suspicious) > 0:
            transaction_id = suspicious[0].get('transaction_id')
            if transaction_id:
                try:
                    response = requests.post(
                        f"{base_url}/explain/{transaction_id}",
                        timeout=15  # Longer timeout for AI
                    )
                    if response.status_code == 200:
                        explanation = response.json()
                        assert 'explanation' in explanation or 'message' in explanation
                        print(f"  ✅ Step 4: Generated explanation for transaction {transaction_id}")
                    else:
                        print(f"  ⚠️ Step 4: Explanation endpoint returned {response.status_code}")
                except Exception as e:
                    print(f"  ⚠️ Step 4: Explanation failed (expected if Gemini API unavailable): {e}")
        
        # 5. Verify dashboard is accessible
        response = requests.get(f"http://{API_HOST}:{DASHBOARD_PORT}/", timeout=API_TIMEOUT)
        assert response.status_code == 200
        print(f"  ✅ Step 5: Dashboard is accessible")
        
        print("✅ End-to-end workflow completed successfully")


def test_deployment_without_fixture():
    """
    Standalone test that can be run without starting the full deployment.
    Tests individual components in isolation.
    """
    print("\n🔬 Running standalone component tests...")
    
    test = TestLocalDeployment()
    
    # Run tests that don't require the deployment process
    test.test_dataset_exists()
    test.test_dataset_loading()
    test.test_feature_engineering()
    test.test_model_initialization()
    test.test_fraud_detection()
    test.test_gemini_api_integration()
    
    print("\n✅ All standalone component tests passed!")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  🧪 TRINETRA AI - Local Deployment Test Suite              ║
    ║                                                              ║
    ║  This test suite verifies the complete deployment process   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run pytest with verbose output
    pytest.main([__file__, "-v", "-s"])
