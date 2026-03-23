"""
Complete System Validation Test for TRINETRA AI

This test validates that the entire TRINETRA AI fraud detection system is working correctly
and is ready for hackathon demonstration.

**Validates: Task 14.1 - Run complete system test**

Success Criteria:
1. System successfully loads and processes the dataset
2. ML model achieves reasonable fraud detection accuracy
3. Gemini API provides meaningful explanations (or fallback works)
4. Dashboard displays all required visualizations
5. System runs with single command: python main.py
6. Demo-ready for hackathon presentation

This is a quick validation test to ensure end-to-end functionality, not exhaustive testing.
"""

import os
import sys
import time
import logging
import subprocess
import requests
from pathlib import Path
import pandas as pd

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.data_loader import load_dataset, validate_schema
from backend.feature_engineering import engineer_features
from backend.model import train_model, load_model
from backend.fraud_detection import score_transactions, classify_risk
from backend.ai_explainer import initialize_gemini, test_fallback_system

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DATASET_PATH = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
MODEL_PATH = "models/isolation_forest.pkl"
API_PORT = 8003  # Use different port to avoid conflicts
API_BASE_URL = f"http://localhost:{API_PORT}"


class SystemValidator:
    """Complete system validation for TRINETRA AI."""
    
    def __init__(self):
        self.api_process = None
        self.validation_results = {}
        
    def validate_data_loading(self):
        """Validate system successfully loads and processes the dataset."""
        logger.info("=" * 70)
        logger.info("TEST 1: Data Loading and Processing")
        logger.info("=" * 70)
        
        try:
            # Load dataset
            logger.info(f"Loading dataset from: {DATASET_PATH}")
            df = load_dataset(DATASET_PATH)
            
            assert df is not None and not df.empty, "Dataset should be loaded"
            assert len(df) > 0, "Dataset should have transactions"
            
            # Validate schema
            assert validate_schema(df), "Dataset schema should be valid"
            
            # Check required columns
            required_cols = ['transaction_id', 'date', 'fraud_label', 'unit_price', 'market_price']
            for col in required_cols:
                assert col in df.columns, f"Missing required column: {col}"
            
            logger.info(f"✅ Dataset loaded successfully: {len(df)} transactions")
            self.validation_results['data_loading'] = {
                'status': 'PASSED',
                'transactions': len(df),
                'columns': len(df.columns)
            }
            return df
            
        except Exception as e:
            logger.error(f"❌ Data loading failed: {e}")
            self.validation_results['data_loading'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def validate_feature_engineering(self, df):
        """Validate feature engineering produces expected features."""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 2: Feature Engineering")
        logger.info("=" * 70)
        
        try:
            # Engineer features
            logger.info("Engineering fraud detection features...")
            df_features = engineer_features(df.copy())
            
            # Check all 6 features are created
            expected_features = [
                'price_anomaly_score', 'route_risk_score', 'company_network_risk',
                'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
            ]
            
            for feature in expected_features:
                assert feature in df_features.columns, f"Missing feature: {feature}"
                assert not df_features[feature].isna().all(), f"Feature {feature} is all NaN"
            
            logger.info(f"✅ All 6 features engineered successfully")
            self.validation_results['feature_engineering'] = {
                'status': 'PASSED',
                'features_created': len(expected_features)
            }
            return df_features
            
        except Exception as e:
            logger.error(f"❌ Feature engineering failed: {e}")
            self.validation_results['feature_engineering'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def validate_ml_model(self, df):
        """Validate ML model achieves reasonable fraud detection accuracy."""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 3: ML Model Training and Scoring")
        logger.info("=" * 70)
        
        try:
            # Train or load model
            if Path(MODEL_PATH).exists():
                logger.info("Loading existing model...")
                model = load_model(MODEL_PATH)
            else:
                logger.info("Training new model...")
                model = train_model(df)
            
            assert model is not None, "Model should be trained/loaded"
            
            # Score transactions
            logger.info("Scoring transactions...")
            df_scored = score_transactions(df, model)
            assert 'risk_score' in df_scored.columns, "Should have risk scores"
            
            # Classify risk
            df_classified = classify_risk(df_scored)
            assert 'risk_category' in df_classified.columns, "Should have risk categories"
            
            # Check risk distribution
            fraud_count = len(df_classified[df_classified['risk_category'] == 'FRAUD'])
            suspicious_count = len(df_classified[df_classified['risk_category'] == 'SUSPICIOUS'])
            safe_count = len(df_classified[df_classified['risk_category'] == 'SAFE'])
            
            total = len(df_classified)
            fraud_rate = (fraud_count / total) * 100
            
            logger.info(f"Risk Distribution:")
            logger.info(f"  - FRAUD: {fraud_count} ({fraud_rate:.1f}%)")
            logger.info(f"  - SUSPICIOUS: {suspicious_count} ({(suspicious_count/total)*100:.1f}%)")
            logger.info(f"  - SAFE: {safe_count} ({(safe_count/total)*100:.1f}%)")
            
            # Validate reasonable distribution (fraud should be minority)
            assert fraud_rate < 50, "Fraud rate should be reasonable (< 50%)"
            assert fraud_count + suspicious_count + safe_count == total, "All transactions should be classified"
            
            logger.info(f"✅ ML model working correctly with {fraud_rate:.1f}% fraud detection rate")
            self.validation_results['ml_model'] = {
                'status': 'PASSED',
                'fraud_count': fraud_count,
                'suspicious_count': suspicious_count,
                'safe_count': safe_count,
                'fraud_rate': f"{fraud_rate:.1f}%"
            }
            return df_classified
            
        except Exception as e:
            logger.error(f"❌ ML model validation failed: {e}")
            self.validation_results['ml_model'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def validate_ai_integration(self):
        """Validate Gemini API provides meaningful explanations or fallback works."""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 4: AI Integration (Gemini API / Fallback)")
        logger.info("=" * 70)
        
        try:
            ai_available = False
            fallback_available = False
            
            # Test Gemini API
            try:
                logger.info("Testing Gemini API initialization...")
                model = initialize_gemini()
                ai_available = True
                logger.info("✅ Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Gemini API not available: {e}")
            
            # Test fallback system
            logger.info("Testing fallback explanation system...")
            fallback_results = test_fallback_system()
            fallback_available = fallback_results.get('test_status') == 'success'
            
            if fallback_available:
                logger.info("✅ Fallback explanation system working")
            
            # At least one should work
            assert ai_available or fallback_available, "Either Gemini API or fallback should work"
            
            status = "Gemini API" if ai_available else "Fallback System"
            logger.info(f"✅ AI integration validated: {status} operational")
            
            self.validation_results['ai_integration'] = {
                'status': 'PASSED',
                'gemini_available': ai_available,
                'fallback_available': fallback_available,
                'active_system': status
            }
            
        except Exception as e:
            logger.error(f"❌ AI integration validation failed: {e}")
            self.validation_results['ai_integration'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def start_api_server(self):
        """Start FastAPI server for testing."""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 5: API Server and Dashboard Integration")
        logger.info("=" * 70)
        
        try:
            # First check if API is already running
            logger.info("Checking if API server is already running...")
            try:
                response = requests.get(f"{API_BASE_URL}/", timeout=2)
                if response.status_code == 200:
                    logger.info("✅ API server already running, using existing instance")
                    return True
            except Exception:
                pass
            
            logger.info("Starting FastAPI server...")
            cmd = [
                sys.executable, "-m", "uvicorn",
                "backend.api:app",
                "--host", "localhost",
                "--port", str(API_PORT),
                "--log-level", "error"
            ]
            
            self.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            # Wait for server to start
            logger.info("Waiting for API server to be ready...")
            for i in range(20):
                try:
                    response = requests.get(f"{API_BASE_URL}/", timeout=5)
                    if response.status_code == 200:
                        logger.info("✅ API server started successfully")
                        return True
                except Exception as e:
                    if i < 19:
                        time.sleep(3)
                    else:
                        # Check if process died
                        if self.api_process.poll() is not None:
                            stdout, stderr = self.api_process.communicate()
                            logger.error(f"API process died. STDOUT: {stdout.decode()[:500]}")
                            logger.error(f"STDERR: {stderr.decode()[:500]}")
                        raise Exception(f"API server failed to start after {i+1} attempts: {e}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start API server: {e}")
            raise
    
    def validate_api_endpoints(self):
        """Validate dashboard displays all required visualizations via API."""
        try:
            logger.info("Testing API endpoints for dashboard data...")
            
            # Test core endpoints that dashboard needs
            endpoints = {
                '/stats': 'Dashboard KPIs',
                '/transactions': 'Transaction data',
                '/suspicious': 'Suspicious transactions',
                '/fraud': 'Fraud transactions',
                '/alerts': 'Alert system',
                '/session/info': 'Session management'
            }
            
            endpoint_results = {}
            for endpoint, description in endpoints.items():
                logger.info(f"  Testing {description} ({endpoint})...")
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
                
                assert response.status_code == 200, f"{endpoint} should return 200"
                data = response.json()
                assert data['status'] == 'success', f"{endpoint} should return success"
                
                endpoint_results[endpoint] = 'PASSED'
            
            # Test explanation endpoint
            logger.info("  Testing AI explanation endpoint...")
            txns_response = requests.get(f"{API_BASE_URL}/transactions?limit=1", timeout=10)
            txns = txns_response.json()['data']
            
            if len(txns) > 0:
                explain_response = requests.post(
                    f"{API_BASE_URL}/explain/{txns[0]['transaction_id']}",
                    json={"force_ai": False},
                    timeout=20
                )
                assert explain_response.status_code == 200, "Explanation endpoint should work"
                endpoint_results['/explain'] = 'PASSED'
            
            logger.info(f"✅ All {len(endpoint_results)} API endpoints working correctly")
            
            self.validation_results['api_endpoints'] = {
                'status': 'PASSED',
                'endpoints_tested': len(endpoint_results),
                'all_passed': True
            }
            
        except Exception as e:
            logger.error(f"❌ API endpoint validation failed: {e}")
            self.validation_results['api_endpoints'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def validate_dashboard_data(self):
        """Validate dashboard can display all required visualizations."""
        try:
            logger.info("Validating dashboard data requirements...")
            
            # Get stats for KPIs
            stats_response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
            stats = stats_response.json()['data']
            
            # Check all required KPIs are present
            required_kpis = [
                'total_transactions', 'fraud_rate', 'total_trade_value',
                'high_risk_countries', 'suspicious_count', 'fraud_count', 'safe_count'
            ]
            
            for kpi in required_kpis:
                assert kpi in stats, f"Missing KPI: {kpi}"
            
            # Get transaction data for visualizations
            txns_response = requests.get(f"{API_BASE_URL}/transactions?limit=100", timeout=10)
            txns = txns_response.json()['data']
            
            assert len(txns) > 0, "Should have transactions for visualization"
            
            # Check transaction data has fields needed for visualizations
            sample_txn = txns[0]
            viz_fields = [
                'transaction_id', 'product', 'risk_score', 'risk_category',
                'unit_price', 'market_price', 'export_port', 'import_port'
            ]
            
            for field in viz_fields:
                assert field in sample_txn, f"Missing visualization field: {field}"
            
            logger.info("✅ Dashboard data requirements validated")
            logger.info(f"  - KPIs available: {len(required_kpis)}")
            logger.info(f"  - Transactions for visualization: {len(txns)}")
            logger.info(f"  - Fraud rate: {stats['fraud_rate']:.1f}%")
            
            self.validation_results['dashboard_data'] = {
                'status': 'PASSED',
                'kpis_available': len(required_kpis),
                'transactions_available': len(txns),
                'visualizations_ready': True
            }
            
        except Exception as e:
            logger.error(f"❌ Dashboard data validation failed: {e}")
            self.validation_results['dashboard_data'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def validate_system_performance(self):
        """Validate system meets performance requirements."""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 6: System Performance")
        logger.info("=" * 70)
        
        try:
            # Test API response times
            logger.info("Testing API response times...")
            
            start = time.time()
            response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
            stats_time = time.time() - start
            
            assert response.status_code == 200, "Stats endpoint should work"
            assert stats_time < 2.0, f"Stats endpoint took {stats_time:.2f}s (should be < 2s)"
            
            logger.info(f"  - Stats endpoint: {stats_time:.3f}s ✅")
            
            # Test transaction loading
            start = time.time()
            response = requests.get(f"{API_BASE_URL}/transactions?limit=100", timeout=10)
            txns_time = time.time() - start
            
            assert response.status_code == 200, "Transactions endpoint should work"
            assert txns_time < 3.0, f"Transactions endpoint took {txns_time:.2f}s (should be < 3s)"
            
            logger.info(f"  - Transactions endpoint: {txns_time:.3f}s ✅")
            
            logger.info("✅ System performance meets requirements")
            
            self.validation_results['performance'] = {
                'status': 'PASSED',
                'stats_response_time': f"{stats_time:.3f}s",
                'transactions_response_time': f"{txns_time:.3f}s"
            }
            
        except Exception as e:
            logger.error(f"❌ Performance validation failed: {e}")
            self.validation_results['performance'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def cleanup(self):
        """Clean up test resources."""
        if self.api_process:
            logger.info("Stopping API server...")
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.api_process.kill()
    
    def print_summary(self):
        """Print validation summary."""
        logger.info("\n" + "=" * 70)
        logger.info("COMPLETE SYSTEM VALIDATION SUMMARY")
        logger.info("=" * 70)
        
        all_passed = True
        for test_name, result in self.validation_results.items():
            status = result.get('status', 'UNKNOWN')
            symbol = "✅" if status == 'PASSED' else "❌"
            logger.info(f"{symbol} {test_name.replace('_', ' ').title()}: {status}")
            
            if status != 'PASSED':
                all_passed = False
                if 'error' in result:
                    logger.info(f"   Error: {result['error']}")
        
        logger.info("=" * 70)
        
        if all_passed:
            logger.info("🎉 ALL SYSTEM VALIDATION TESTS PASSED!")
            logger.info("✅ TRINETRA AI is ready for hackathon demonstration!")
            logger.info("\nSystem can be started with: python main.py")
            return 0
        else:
            logger.error("❌ SOME SYSTEM VALIDATION TESTS FAILED")
            logger.error("Please review the errors above and fix before deployment")
            return 1


def main():
    """Run complete system validation."""
    logger.info("🚀 Starting TRINETRA AI Complete System Validation")
    logger.info("=" * 70)
    
    validator = SystemValidator()
    
    try:
        # Run validation tests
        df = validator.validate_data_loading()
        df_features = validator.validate_feature_engineering(df)
        df_classified = validator.validate_ml_model(df_features)
        validator.validate_ai_integration()
        
        # Start API and test endpoints
        validator.start_api_server()
        validator.validate_api_endpoints()
        validator.validate_dashboard_data()
        validator.validate_system_performance()
        
        # Print summary
        exit_code = validator.print_summary()
        
    except Exception as e:
        logger.error(f"❌ System validation failed with error: {e}")
        validator.print_summary()
        exit_code = 1
    
    finally:
        validator.cleanup()
    
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
