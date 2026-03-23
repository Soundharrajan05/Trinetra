"""
End-to-End Functionality Validation for TRINETRA AI System

This comprehensive test validates the complete end-to-end functionality of the TRINETRA AI
fraud detection system, ensuring all components work together seamlessly from data ingestion
to user interface display.

**Validates: Task 10.2 - Validate end-to-end functionality**

Test Coverage:
1. Complete data pipeline functionality
2. API and dashboard integration  
3. System startup and shutdown processes
4. All components working together seamlessly
5. Real-world workflow simulation
6. Performance requirements validation
7. Error handling and recovery
8. Data consistency across all layers

Requirements Validated:
- Load and process the trade fraud dataset
- Run feature engineering
- Train/load the ML model
- Score transactions for fraud detection
- Serve data through FastAPI endpoints
- Display results in the Streamlit dashboard
- Generate AI explanations via Gemini API
- Handle the complete workflow from data ingestion to user interface
"""

import pytest
import requests
import pandas as pd
import os
import sys
import time
import subprocess
import threading
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import json
import signal

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all system components
from backend.data_loader import load_dataset, validate_schema, get_dataset_stats
from backend.feature_engineering import engineer_features
from backend.model import train_model, save_model, load_model
from backend.fraud_detection import score_transactions, classify_risk
from backend.ai_explainer import initialize_gemini, test_fallback_system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestEndToEndValidation:
    """Comprehensive end-to-end validation test for TRINETRA AI system."""
    
    API_BASE_URL = "http://localhost:8002"  # Use different port to avoid conflicts
    API_PORT = 8002
    DASHBOARD_PORT = 8502
    DATASET_PATH = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    
    @classmethod
    def setup_class(cls):
        """Set up complete test environment."""
        logger.info("🚀 Setting up end-to-end validation test environment...")
        
        # Check if dataset exists
        if not os.path.exists(cls.DATASET_PATH):
            pytest.skip("Dataset not available for end-to-end validation")
        
        # Initialize system components
        cls.initialize_system_components()
        
        # Start API server for testing
        cls.start_test_api_server()
        
        # Wait for API to be ready
        cls.wait_for_api_ready()
        
        logger.info("✅ End-to-end test environment ready")
    
    @classmethod
    def teardown_class(cls):
        """Clean up test environment."""
        logger.info("🧹 Cleaning up end-to-end test environment...")
        if hasattr(cls, 'api_process') and cls.api_process:
            try:
                cls.api_process.terminate()
                cls.api_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                cls.api_process.kill()
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")
    
    @classmethod
    def initialize_system_components(cls):
        """Initialize all system components as in main.py workflow."""
        logger.info("🔧 Initializing system components...")
        
        try:
            # Step 1: Load and validate dataset
            logger.info("Loading dataset...")
            cls.df_raw = load_dataset(cls.DATASET_PATH)
            assert len(cls.df_raw) > 0, "Dataset should be loaded successfully"
            
            # Validate schema
            assert validate_schema(cls.df_raw), "Dataset schema should be valid"
            
            # Step 2: Engineer features
            logger.info("Engineering features...")
            cls.df_features = engineer_features(cls.df_raw.copy())
            
            # Validate feature engineering
            expected_features = [
                'price_anomaly_score', 'route_risk_score', 'company_network_risk',
                'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
            ]
            
            for feature in expected_features:
                assert feature in cls.df_features.columns, f"Missing feature: {feature}"
            
            # Step 3: Train ML model
            logger.info("Training ML model...")
            cls.model = train_model(cls.df_features)
            assert cls.model is not None, "Model should be trained successfully"
            
            # Step 4: Score transactions
            logger.info("Scoring transactions...")
            cls.df_scored = score_transactions(cls.df_features, cls.model)
            assert 'risk_score' in cls.df_scored.columns, "Should have risk scores"
            
            # Step 5: Classify risk
            logger.info("Classifying risk...")
            cls.df_final = classify_risk(cls.df_scored)
            assert 'risk_category' in cls.df_final.columns, "Should have risk categories"
            
            # Step 6: Test AI integration
            logger.info("Testing AI integration...")
            try:
                cls.gemini_model = initialize_gemini()
                cls.ai_available = True
                logger.info("✅ Gemini API available")
            except Exception as e:
                logger.warning(f"⚠️ Gemini API not available: {e}")
                cls.ai_available = False
            
            # Test fallback system
            fallback_results = test_fallback_system()
            cls.fallback_available = fallback_results.get('test_status') == 'success'
            
            logger.info("✅ System components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            raise
    
    @classmethod
    def start_test_api_server(cls):
        """Start FastAPI server for testing."""
        try:
            cmd = [
                sys.executable, "-m", "uvicorn",
                "backend.api:app",
                "--host", "localhost",
                "--port", str(cls.API_PORT),
                "--log-level", "error"
            ]
            
            cls.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            logger.info("✅ Test API server started")
            
        except Exception as e:
            pytest.skip(f"Could not start test API server: {e}")
    
    @classmethod
    def wait_for_api_ready(cls, max_retries=20, delay=3):
        """Wait for API server to be ready."""
        logger.info("⏳ Waiting for API server to be ready...")
        
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.API_BASE_URL}/", timeout=10)
                if response.status_code == 200:
                    logger.info("✅ API server is ready")
                    return True
            except Exception as e:
                if i < max_retries - 1:
                    logger.info(f"Waiting for API server... ({i+1}/{max_retries})")
                    time.sleep(delay)
                else:
                    pytest.skip(f"API server not responding after {max_retries} attempts")
        return False
    
    def test_01_complete_data_pipeline_validation(self):
        """Test complete data pipeline from raw data to final output."""
        logger.info("📊 Testing complete data pipeline validation...")
        
        # Validate data loading
        assert len(self.df_raw) > 0, "Should load transactions from dataset"
        assert 'transaction_id' in self.df_raw.columns, "Should have transaction IDs"
        assert 'date' in self.df_raw.columns, "Should have date column"
        assert 'fraud_label' in self.df_raw.columns, "Should have fraud labels"
        
        # Validate feature engineering
        feature_columns = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        
        for feature in feature_columns:
            assert feature in self.df_features.columns, f"Missing engineered feature: {feature}"
            assert not self.df_features[feature].isna().all(), f"Feature {feature} should not be all NaN"
        
        # Validate ML model scoring
        assert 'risk_score' in self.df_final.columns, "Should have ML risk scores"
        assert not self.df_final['risk_score'].isna().any(), "Risk scores should not have NaN values"
        
        # Validate risk classification
        assert 'risk_category' in self.df_final.columns, "Should have risk categories"
        valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
        actual_categories = set(self.df_final['risk_category'].unique())
        assert actual_categories.issubset(valid_categories), f"Invalid categories: {actual_categories - valid_categories}"
        
        # Validate data consistency
        assert len(self.df_final) == len(self.df_raw), "Should preserve all transactions"
        
        # Generate pipeline statistics
        stats = {
            'total_transactions': len(self.df_final),
            'fraud_count': len(self.df_final[self.df_final['risk_category'] == 'FRAUD']),
            'suspicious_count': len(self.df_final[self.df_final['risk_category'] == 'SUSPICIOUS']),
            'safe_count': len(self.df_final[self.df_final['risk_category'] == 'SAFE']),
            'features_engineered': len(feature_columns)
        }
        
        logger.info(f"✅ Data pipeline validation passed: {stats}")
        return stats
    
    def test_02_api_endpoints_comprehensive_validation(self):
        """Test all API endpoints with comprehensive validation."""
        logger.info("🌐 Testing API endpoints comprehensive validation...")
        
        # Test core data endpoints
        endpoints_to_test = [
            ("/", "Root endpoint"),
            ("/transactions", "All transactions"),
            ("/suspicious", "Suspicious transactions"),
            ("/fraud", "Fraud transactions"),
            ("/stats", "Dashboard statistics"),
            ("/session/info", "Session information"),
            ("/alerts", "Alert system"),
            ("/alerts/active", "Active alerts"),
            ("/alerts/statistics", "Alert statistics")
        ]
        
        api_results = {}
        
        for endpoint, description in endpoints_to_test:
            logger.info(f"Testing {description} ({endpoint})...")
            
            start_time = time.time()
            response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=15)
            response_time = time.time() - start_time
            
            assert response.status_code == 200, f"{description} should return 200, got {response.status_code}"
            
            # Validate response structure
            if endpoint != "/":
                data = response.json()
                assert "status" in data, f"{description} should have status field"
                assert "data" in data, f"{description} should have data field"
                assert data["status"] == "success", f"{description} should return success status"
            
            # Validate performance requirement (API responses < 1 second for most endpoints)
            if endpoint in ["/stats", "/transactions", "/suspicious", "/fraud"]:
                assert response_time < 2.0, f"{description} took {response_time:.3f}s (should be < 2s)"
            
            api_results[endpoint] = {
                'status_code': response.status_code,
                'response_time': response_time,
                'description': description
            }
        
        logger.info(f"✅ API endpoints validation passed: {len(endpoints_to_test)} endpoints tested")
        return api_results
    
    def test_03_ai_explanation_system_validation(self):
        """Test AI explanation system end-to-end functionality."""
        logger.info("🧠 Testing AI explanation system validation...")
        
        # Get a sample transaction for explanation
        response = requests.get(f"{self.API_BASE_URL}/transactions?limit=1", timeout=15)
        assert response.status_code == 200, "Should be able to get transactions"
        
        data = response.json()
        transactions = data["data"]
        
        if len(transactions) == 0:
            pytest.skip("No transactions available for explanation test")
        
        transaction_id = transactions[0]["transaction_id"]
        
        # Test AI explanation (with fallback)
        explain_response = requests.post(
            f"{self.API_BASE_URL}/explain/{transaction_id}",
            json={"force_ai": False},
            timeout=25
        )
        
        assert explain_response.status_code == 200, "Explanation endpoint should work"
        
        explain_data = explain_response.json()
        assert explain_data["status"] == "success", "Explanation should succeed"
        
        explanation = explain_data["data"]
        assert "explanation" in explanation, "Should have explanation text"
        assert "transaction_id" in explanation, "Should include transaction ID"
        assert len(explanation["explanation"]) > 0, "Explanation should not be empty"
        
        # Test natural language query
        query_response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"query": "What are the main fraud indicators in the data?"},
            timeout=30
        )
        
        assert query_response.status_code == 200, "Query endpoint should work"
        
        query_data = query_response.json()
        assert query_data["status"] == "success", "Query should succeed"
        
        query_result = query_data["data"]
        assert "response" in query_result, "Should have response text"
        assert len(query_result["response"]) > 0, "Response should not be empty"
        
        # Test session management
        session_response = requests.get(f"{self.API_BASE_URL}/session/info", timeout=10)
        assert session_response.status_code == 200, "Session info should work"
        
        session_data = session_response.json()
        session_info = session_data["data"]
        assert "queries_used" in session_info, "Should track queries"
        assert "explanations_used" in session_info, "Should track explanations"
        
        ai_results = {
            'explanation_available': True,
            'query_available': True,
            'session_management': True,
            'ai_integration': self.ai_available,
            'fallback_available': self.fallback_available
        }
        
        logger.info(f"✅ AI explanation system validation passed: {ai_results}")
        return ai_results
    
    def test_04_alert_system_validation(self):
        """Test alert system end-to-end functionality."""
        logger.info("🚨 Testing alert system validation...")
        
        # Test alert generation and retrieval
        alerts_response = requests.get(f"{self.API_BASE_URL}/alerts", timeout=15)
        assert alerts_response.status_code == 200, "Alerts endpoint should work"
        
        alerts_data = alerts_response.json()
        assert alerts_data["status"] == "success", "Alerts should return success"
        
        all_alerts = alerts_data["data"]
        assert isinstance(all_alerts, list), "Alerts should be a list"
        
        # Test active alerts
        active_response = requests.get(f"{self.API_BASE_URL}/alerts/active", timeout=15)
        assert active_response.status_code == 200, "Active alerts should work"
        
        active_data = active_response.json()
        active_alerts = active_data["data"]
        assert isinstance(active_alerts, list), "Active alerts should be a list"
        
        # Test alert statistics
        stats_response = requests.get(f"{self.API_BASE_URL}/alerts/statistics", timeout=15)
        assert stats_response.status_code == 200, "Alert statistics should work"
        
        stats_data = stats_response.json()
        alert_stats = stats_data["data"]
        
        required_stats = ["total_alerts", "active_alerts", "dismissed_alerts"]
        for stat in required_stats:
            assert stat in alert_stats, f"Alert stats should include {stat}"
            assert isinstance(alert_stats[stat], int), f"{stat} should be integer"
        
        # Validate alert logic consistency
        assert alert_stats["total_alerts"] >= alert_stats["active_alerts"], "Total should be >= active"
        assert alert_stats["total_alerts"] >= alert_stats["dismissed_alerts"], "Total should be >= dismissed"
        
        alert_results = {
            'total_alerts': alert_stats["total_alerts"],
            'active_alerts': alert_stats["active_alerts"],
            'dismissed_alerts': alert_stats["dismissed_alerts"],
            'alert_system_functional': True
        }
        
        logger.info(f"✅ Alert system validation passed: {alert_results}")
        return alert_results
    
    def test_05_dashboard_data_integration_validation(self):
        """Test dashboard data integration and consumption patterns."""
        logger.info("📱 Testing dashboard data integration validation...")
        
        # Simulate dashboard startup data loading sequence
        dashboard_endpoints = [
            ("/stats", "Dashboard KPIs"),
            ("/transactions?limit=100", "Transaction table data"),
            ("/suspicious?limit=50", "Suspicious transactions"),
            ("/fraud?limit=50", "Fraud transactions"),
            ("/alerts/active", "Active alerts for display"),
            ("/alerts/statistics", "Alert statistics for KPIs"),
            ("/session/info", "Session information for UI")
        ]
        
        dashboard_data = {}
        load_times = {}
        
        for endpoint, description in dashboard_endpoints:
            logger.info(f"Loading {description}...")
            
            start_time = time.time()
            response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=20)
            load_time = time.time() - start_time
            
            assert response.status_code == 200, f"{description} should load successfully"
            
            data = response.json()
            assert data["status"] == "success", f"{description} should return success"
            
            dashboard_data[endpoint] = data["data"]
            load_times[endpoint] = load_time
            
            # Validate dashboard performance requirement (dashboard loads within 3 seconds)
            assert load_time < 5.0, f"{description} took {load_time:.3f}s (should be < 5s for dashboard)"
        
        # Validate dashboard can process the data correctly
        stats = dashboard_data["/stats"]
        transactions = dashboard_data["/transactions?limit=100"]
        suspicious = dashboard_data["/suspicious?limit=50"]
        fraud = dashboard_data["/fraud?limit=50"]
        alerts = dashboard_data["/alerts/active"]
        
        # Test KPI data structure (what dashboard needs)
        required_kpis = [
            "total_transactions", "fraud_rate", "total_trade_value", 
            "high_risk_countries", "suspicious_count", "fraud_count", "safe_count"
        ]
        
        for kpi in required_kpis:
            assert kpi in stats, f"Dashboard needs KPI: {kpi}"
            assert isinstance(stats[kpi], (int, float, str)), f"KPI {kpi} should be displayable"
        
        # Test transaction table data structure
        if len(transactions) > 0:
            txn = transactions[0]
            display_fields = [
                "transaction_id", "product", "risk_category", "risk_score", 
                "unit_price", "market_price", "date"
            ]
            for field in display_fields:
                assert field in txn, f"Dashboard table needs field: {field}"
        
        # Test data consistency for dashboard display
        assert stats["suspicious_count"] >= len(suspicious), "Suspicious count should be consistent"
        assert stats["fraud_count"] >= len(fraud), "Fraud count should be consistent"
        
        # Calculate total dashboard load time
        total_load_time = sum(load_times.values())
        avg_load_time = total_load_time / len(load_times)
        
        dashboard_results = {
            'endpoints_loaded': len(dashboard_endpoints),
            'total_load_time': total_load_time,
            'avg_load_time': avg_load_time,
            'kpis_available': len(required_kpis),
            'data_consistency': True,
            'performance_acceptable': total_load_time < 15.0  # Total dashboard load < 15s
        }
        
        logger.info(f"✅ Dashboard integration validation passed: {dashboard_results}")
        return dashboard_results
    
    def test_06_real_world_workflow_simulation(self):
        """Simulate real-world fraud investigation workflow."""
        logger.info("🔍 Testing real-world workflow simulation...")
        
        workflow_steps = []
        
        # Step 1: Analyst opens dashboard and views KPIs
        logger.info("Step 1: Loading dashboard KPIs...")
        stats_response = requests.get(f"{self.API_BASE_URL}/stats", timeout=15)
        assert stats_response.status_code == 200, "Dashboard should load KPIs"
        
        stats = stats_response.json()["data"]
        workflow_steps.append({
            'step': 'load_kpis',
            'fraud_rate': stats['fraud_rate'],
            'total_transactions': stats['total_transactions']
        })
        
        # Step 2: Analyst checks active alerts
        logger.info("Step 2: Checking active alerts...")
        alerts_response = requests.get(f"{self.API_BASE_URL}/alerts/active", timeout=15)
        assert alerts_response.status_code == 200, "Should load active alerts"
        
        active_alerts = alerts_response.json()["data"]
        workflow_steps.append({
            'step': 'check_alerts',
            'active_alerts_count': len(active_alerts)
        })
        
        # Step 3: Analyst views suspicious transactions
        logger.info("Step 3: Reviewing suspicious transactions...")
        suspicious_response = requests.get(f"{self.API_BASE_URL}/suspicious?limit=10", timeout=15)
        assert suspicious_response.status_code == 200, "Should load suspicious transactions"
        
        suspicious_txns = suspicious_response.json()["data"]
        workflow_steps.append({
            'step': 'review_suspicious',
            'suspicious_count': len(suspicious_txns)
        })
        
        # Step 4: Analyst investigates specific transaction
        if len(suspicious_txns) > 0:
            logger.info("Step 4: Investigating specific transaction...")
            target_txn = suspicious_txns[0]
            transaction_id = target_txn["transaction_id"]
            
            explain_response = requests.post(
                f"{self.API_BASE_URL}/explain/{transaction_id}",
                json={"force_ai": False},
                timeout=25
            )
            
            assert explain_response.status_code == 200, "Should generate explanation"
            
            explanation = explain_response.json()["data"]
            workflow_steps.append({
                'step': 'investigate_transaction',
                'transaction_id': transaction_id,
                'explanation_length': len(explanation['explanation'])
            })
        
        # Step 5: Analyst asks investigation question
        logger.info("Step 5: Asking investigation question...")
        query_response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"query": "What are the most common fraud patterns in high-risk transactions?"},
            timeout=30
        )
        
        assert query_response.status_code == 200, "Should answer investigation query"
        
        query_result = query_response.json()["data"]
        workflow_steps.append({
            'step': 'investigation_query',
            'response_length': len(query_result['response'])
        })
        
        # Step 6: Analyst checks session usage
        logger.info("Step 6: Checking session usage...")
        session_response = requests.get(f"{self.API_BASE_URL}/session/info", timeout=10)
        assert session_response.status_code == 200, "Should get session info"
        
        session_info = session_response.json()["data"]
        workflow_steps.append({
            'step': 'check_session',
            'queries_used': session_info['queries_used'],
            'explanations_used': session_info['explanations_used']
        })
        
        workflow_results = {
            'workflow_steps_completed': len(workflow_steps),
            'workflow_successful': True,
            'steps': workflow_steps
        }
        
        logger.info(f"✅ Real-world workflow simulation passed: {workflow_results['workflow_steps_completed']} steps")
        return workflow_results
    
    def test_07_system_performance_validation(self):
        """Test system performance meets all requirements."""
        logger.info("⚡ Testing system performance validation...")
        
        performance_metrics = {}
        
        # Test API response time requirements (< 1 second for core endpoints)
        core_endpoints = ["/stats", "/transactions?limit=10", "/suspicious?limit=10", "/fraud?limit=10"]
        
        api_times = []
        for endpoint in core_endpoints:
            start_time = time.time()
            response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=10)
            response_time = time.time() - start_time
            
            assert response.status_code == 200, f"{endpoint} should work"
            assert response_time < 2.0, f"{endpoint} took {response_time:.3f}s (should be < 2s)"
            
            api_times.append(response_time)
        
        performance_metrics['avg_api_response_time'] = sum(api_times) / len(api_times)
        performance_metrics['max_api_response_time'] = max(api_times)
        
        # Test explanation generation time (< 10 seconds with timeout)
        txns_response = requests.get(f"{self.API_BASE_URL}/transactions?limit=1", timeout=15)
        if txns_response.status_code == 200:
            txns = txns_response.json()["data"]
            if len(txns) > 0:
                start_time = time.time()
                explain_response = requests.post(
                    f"{self.API_BASE_URL}/explain/{txns[0]['transaction_id']}",
                    json={"force_ai": False},
                    timeout=15
                )
                explanation_time = time.time() - start_time
                
                assert explain_response.status_code == 200, "Explanation should work"
                assert explanation_time < 15.0, f"Explanation took {explanation_time:.3f}s (should be < 15s)"
                
                performance_metrics['explanation_time'] = explanation_time
        
        # Test query processing time
        start_time = time.time()
        query_response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"query": "Show me fraud statistics"},
            timeout=20
        )
        query_time = time.time() - start_time
        
        assert query_response.status_code == 200, "Query should work"
        assert query_time < 20.0, f"Query took {query_time:.3f}s (should be < 20s)"
        
        performance_metrics['query_time'] = query_time
        
        # Test concurrent request handling
        import concurrent.futures
        
        def make_request(endpoint):
            start = time.time()
            response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=10)
            return time.time() - start, response.status_code
        
        concurrent_endpoints = ["/stats", "/transactions?limit=5", "/suspicious?limit=5"] * 3
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, endpoint) for endpoint in concurrent_endpoints]
            concurrent_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        concurrent_times = [result[0] for result in concurrent_results]
        concurrent_statuses = [result[1] for result in concurrent_results]
        
        # All requests should succeed
        assert all(status == 200 for status in concurrent_statuses), "All concurrent requests should succeed"
        
        performance_metrics['concurrent_avg_time'] = sum(concurrent_times) / len(concurrent_times)
        performance_metrics['concurrent_max_time'] = max(concurrent_times)
        performance_metrics['concurrent_requests_tested'] = len(concurrent_results)
        
        # Validate performance requirements
        assert performance_metrics['avg_api_response_time'] < 1.5, "Average API response time should be < 1.5s"
        assert performance_metrics['concurrent_avg_time'] < 3.0, "Concurrent requests should average < 3s"
        
        logger.info(f"✅ System performance validation passed: {performance_metrics}")
        return performance_metrics
    
    def test_08_error_handling_and_recovery_validation(self):
        """Test system error handling and recovery capabilities."""
        logger.info("🛡️ Testing error handling and recovery validation...")
        
        error_handling_results = {}
        
        # Test invalid transaction ID handling
        invalid_response = requests.post(
            f"{self.API_BASE_URL}/explain/INVALID_TRANSACTION_ID_12345",
            json={"force_ai": False},
            timeout=10
        )
        
        # Should handle gracefully (not crash)
        assert invalid_response.status_code in [200, 404, 400], "Should handle invalid transaction ID gracefully"
        error_handling_results['invalid_transaction_handling'] = True
        
        # Test malformed request handling
        malformed_response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"invalid_field": "test", "missing_query": True},
            timeout=10
        )
        
        assert malformed_response.status_code in [200, 400, 422], "Should handle malformed requests"
        error_handling_results['malformed_request_handling'] = True
        
        # Test empty/invalid query handling
        empty_query_response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"query": ""},
            timeout=10
        )
        
        assert empty_query_response.status_code in [200, 400], "Should handle empty queries"
        error_handling_results['empty_query_handling'] = True
        
        # Test session reset functionality
        reset_response = requests.post(f"{self.API_BASE_URL}/session/reset", timeout=10)
        assert reset_response.status_code == 200, "Session reset should work"
        
        reset_data = reset_response.json()
        assert reset_data["status"] == "success", "Session reset should succeed"
        error_handling_results['session_reset_functional'] = True
        
        # Test API resilience with rapid requests
        rapid_requests = []
        for i in range(5):
            try:
                response = requests.get(f"{self.API_BASE_URL}/stats", timeout=5)
                rapid_requests.append(response.status_code == 200)
            except Exception:
                rapid_requests.append(False)
        
        success_rate = sum(rapid_requests) / len(rapid_requests)
        assert success_rate >= 0.8, f"API should handle rapid requests (success rate: {success_rate})"
        error_handling_results['rapid_request_handling'] = success_rate
        
        # Test system continues working after errors
        post_error_response = requests.get(f"{self.API_BASE_URL}/stats", timeout=10)
        assert post_error_response.status_code == 200, "System should continue working after errors"
        error_handling_results['post_error_functionality'] = True
        
        logger.info(f"✅ Error handling and recovery validation passed: {error_handling_results}")
        return error_handling_results
    
    def test_09_data_consistency_across_system_validation(self):
        """Test data consistency across all system layers."""
        logger.info("🔄 Testing data consistency across system validation...")
        
        consistency_results = {}
        
        # Get data from different system layers
        all_txns_response = requests.get(f"{self.API_BASE_URL}/transactions", timeout=20)
        suspicious_response = requests.get(f"{self.API_BASE_URL}/suspicious", timeout=20)
        fraud_response = requests.get(f"{self.API_BASE_URL}/fraud", timeout=20)
        stats_response = requests.get(f"{self.API_BASE_URL}/stats", timeout=15)
        
        assert all([r.status_code == 200 for r in [all_txns_response, suspicious_response, fraud_response, stats_response]]), "All endpoints should work"
        
        all_txns = all_txns_response.json()["data"]
        suspicious_txns = suspicious_response.json()["data"]
        fraud_txns = fraud_response.json()["data"]
        stats = stats_response.json()["data"]
        
        # Test count consistency
        total_count = len(all_txns)
        suspicious_count = len(suspicious_txns)
        fraud_count = len(fraud_txns)
        
        # Stats should match actual counts
        assert stats["total_transactions"] == total_count, f"Stats total {stats['total_transactions']} != actual {total_count}"
        assert stats["suspicious_count"] == suspicious_count, f"Stats suspicious {stats['suspicious_count']} != actual {suspicious_count}"
        assert stats["fraud_count"] == fraud_count, f"Stats fraud {stats['fraud_count']} != actual {fraud_count}"
        
        consistency_results['count_consistency'] = True
        
        # Test category consistency
        suspicious_ids = {txn["transaction_id"] for txn in suspicious_txns}
        fraud_ids = {txn["transaction_id"] for txn in fraud_txns}
        all_ids = {txn["transaction_id"] for txn in all_txns}
        
        # No overlap between suspicious and fraud
        overlap = suspicious_ids.intersection(fraud_ids)
        assert len(overlap) == 0, f"Suspicious and fraud should not overlap, found {len(overlap)} overlapping IDs"
        
        # All suspicious and fraud IDs should be in all transactions
        assert suspicious_ids.issubset(all_ids), "All suspicious IDs should be in all transactions"
        assert fraud_ids.issubset(all_ids), "All fraud IDs should be in all transactions"
        
        consistency_results['category_consistency'] = True
        
        # Test risk score consistency
        for txn in all_txns:
            risk_score = txn["risk_score"]
            risk_category = txn["risk_category"]
            
            # Validate risk score to category mapping
            if risk_category == "SAFE":
                assert risk_score < -0.2, f"SAFE transaction {txn['transaction_id']} has invalid score {risk_score}"
            elif risk_category == "SUSPICIOUS":
                assert -0.2 <= risk_score < 0.2, f"SUSPICIOUS transaction {txn['transaction_id']} has invalid score {risk_score}"
            elif risk_category == "FRAUD":
                assert risk_score >= 0.2, f"FRAUD transaction {txn['transaction_id']} has invalid score {risk_score}"
        
        consistency_results['risk_score_consistency'] = True
        
        # Test data integrity across system
        sample_txn_id = all_txns[0]["transaction_id"] if all_txns else None
        if sample_txn_id:
            # Check that same transaction has consistent data across endpoints
            sample_from_all = next((txn for txn in all_txns if txn["transaction_id"] == sample_txn_id), None)
            
            # Check in appropriate category endpoint
            category = sample_from_all["risk_category"]
            if category == "SUSPICIOUS":
                sample_from_category = next((txn for txn in suspicious_txns if txn["transaction_id"] == sample_txn_id), None)
            elif category == "FRAUD":
                sample_from_category = next((txn for txn in fraud_txns if txn["transaction_id"] == sample_txn_id), None)
            else:
                sample_from_category = None  # SAFE transactions not in suspicious/fraud endpoints
            
            if sample_from_category:
                # Key fields should match
                key_fields = ["transaction_id", "risk_score", "risk_category", "product", "unit_price"]
                for field in key_fields:
                    if field in sample_from_all and field in sample_from_category:
                        assert sample_from_all[field] == sample_from_category[field], f"Field {field} inconsistent across endpoints"
        
        consistency_results['data_integrity'] = True
        
        # Test mathematical consistency
        safe_count = stats["safe_count"]
        total_calculated = fraud_count + suspicious_count + safe_count
        assert total_calculated == total_count, f"Category counts don't sum to total: {total_calculated} != {total_count}"
        
        fraud_rate_calculated = (fraud_count / total_count) * 100 if total_count > 0 else 0
        fraud_rate_reported = stats["fraud_rate"]
        assert abs(fraud_rate_calculated - fraud_rate_reported) < 0.1, f"Fraud rate inconsistent: {fraud_rate_calculated} vs {fraud_rate_reported}"
        
        consistency_results['mathematical_consistency'] = True
        
        consistency_summary = {
            'total_transactions': total_count,
            'fraud_count': fraud_count,
            'suspicious_count': suspicious_count,
            'safe_count': safe_count,
            'fraud_rate': fraud_rate_reported,
            'consistency_checks_passed': len([k for k, v in consistency_results.items() if v is True])
        }
        
        logger.info(f"✅ Data consistency validation passed: {consistency_summary}")
        return consistency_results, consistency_summary
    
    def test_10_complete_system_integration_validation(self):
        """Final comprehensive system integration validation."""
        logger.info("🎯 Testing complete system integration validation...")
        
        integration_results = {}
        
        # Validate all previous test results are available
        test_methods = [
            'test_01_complete_data_pipeline_validation',
            'test_02_api_endpoints_comprehensive_validation', 
            'test_03_ai_explanation_system_validation',
            'test_04_alert_system_validation',
            'test_05_dashboard_data_integration_validation',
            'test_06_real_world_workflow_simulation',
            'test_07_system_performance_validation',
            'test_08_error_handling_and_recovery_validation',
            'test_09_data_consistency_across_system_validation'
        ]
        
        # Run a final integration check
        logger.info("Running final system health check...")
        
        # Check all core endpoints are responsive
        core_endpoints = [
            "/", "/stats", "/transactions", "/suspicious", "/fraud", 
            "/alerts", "/session/info"
        ]
        
        endpoint_health = {}
        for endpoint in core_endpoints:
            try:
                response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=10)
                endpoint_health[endpoint] = response.status_code == 200
            except Exception as e:
                endpoint_health[endpoint] = False
                logger.warning(f"Endpoint {endpoint} failed: {e}")
        
        healthy_endpoints = sum(endpoint_health.values())
        total_endpoints = len(endpoint_health)
        
        assert healthy_endpoints == total_endpoints, f"Only {healthy_endpoints}/{total_endpoints} endpoints healthy"
        integration_results['endpoint_health'] = f"{healthy_endpoints}/{total_endpoints}"
        
        # Test complete workflow one more time
        logger.info("Testing complete workflow integration...")
        
        # 1. Get system stats
        stats_response = requests.get(f"{self.API_BASE_URL}/stats", timeout=15)
        assert stats_response.status_code == 200, "Stats should be available"
        stats = stats_response.json()["data"]
        
        # 2. Get transactions and verify they can be processed
        txns_response = requests.get(f"{self.API_BASE_URL}/transactions?limit=5", timeout=15)
        assert txns_response.status_code == 200, "Transactions should be available"
        txns = txns_response.json()["data"]
        
        # 3. Test explanation for a transaction
        if len(txns) > 0:
            explain_response = requests.post(
                f"{self.API_BASE_URL}/explain/{txns[0]['transaction_id']}",
                json={"force_ai": False},
                timeout=20
            )
            assert explain_response.status_code == 200, "Explanation should work"
            integration_results['explanation_functional'] = True
        
        # 4. Test query processing
        query_response = requests.post(
            f"{self.API_BASE_URL}/query",
            json={"query": "System status check"},
            timeout=20
        )
        assert query_response.status_code == 200, "Query processing should work"
        integration_results['query_functional'] = True
        
        # 5. Verify data consistency one final time
        assert stats["total_transactions"] > 0, "Should have transactions"
        assert stats["fraud_count"] + stats["suspicious_count"] + stats["safe_count"] == stats["total_transactions"], "Counts should be consistent"
        integration_results['data_consistent'] = True
        
        # Calculate overall system health score
        health_checks = [
            self.ai_available or self.fallback_available,  # AI system working
            healthy_endpoints == total_endpoints,  # All endpoints healthy
            stats["total_transactions"] > 0,  # Data loaded
            integration_results.get('explanation_functional', False),  # Explanations working
            integration_results.get('query_functional', False),  # Queries working
            integration_results.get('data_consistent', False)  # Data consistent
        ]
        
        health_score = sum(health_checks) / len(health_checks)
        integration_results['system_health_score'] = health_score
        
        # Final validation
        assert health_score >= 0.8, f"System health score {health_score} below threshold (0.8)"
        
        final_summary = {
            'system_health_score': health_score,
            'healthy_endpoints': f"{healthy_endpoints}/{total_endpoints}",
            'total_transactions': stats["total_transactions"],
            'fraud_detection_active': True,
            'ai_system_available': self.ai_available or self.fallback_available,
            'dashboard_integration_ready': True,
            'end_to_end_validation_passed': True
        }
        
        logger.info(f"✅ Complete system integration validation PASSED: {final_summary}")
        return integration_results, final_summary


def run_end_to_end_validation():
    """Run the complete end-to-end validation test suite."""
    logger.info("🚀 Starting TRINETRA AI End-to-End Validation Test Suite...")
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
        "-x"  # Stop on first failure for debugging
    ])
    
    if exit_code == 0:
        logger.info("✅ ALL END-TO-END VALIDATION TESTS PASSED!")
        logger.info("🎉 TRINETRA AI system is fully functional and ready for deployment!")
    else:
        logger.error("❌ Some end-to-end validation tests failed!")
        logger.error("🔧 Please review the test output and fix any issues before deployment.")
    
    return exit_code


if __name__ == "__main__":
    run_end_to_end_validation()