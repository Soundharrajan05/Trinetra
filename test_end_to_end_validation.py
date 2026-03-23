#!/usr/bin/env python3
"""
End-to-End Validation Test for TRINETRA AI
Validates complete system functionality using the existing API architecture.

**Validates: System Integration Tests (section 10.2) - Task: Validate end-to-end functionality**

This test validates:
1. Complete data pipeline from CSV loading through fraud detection
2. API integration and all endpoints working properly
3. Data flow integrity across the entire system
4. AI integration and explanation generation
5. Alert system functionality
6. Performance requirements compliance

Success Criteria:
- All API endpoints respond correctly
- Data pipeline processes transactions successfully
- Feature engineering and ML scoring work
- Alert system generates appropriate alerts
- Performance requirements are met
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add backend directory to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import test client and API
from fastapi.testclient import TestClient
from api import app

class EndToEndValidator:
    """Comprehensive end-to-end system validator."""
    
    def __init__(self):
        # Initialize the system before creating the test client
        try:
            from api import initialize_system
            initialize_system()
            print("✅ System initialized successfully")
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            raise
        
        self.client = TestClient(app)
        self.test_results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
    def log_result(self, test_name: str, success: bool, message: str = "", duration: float = 0):
        """Log test result with timing information."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if duration > 0:
            result += f" ({duration:.3f}s)"
        if message:
            result += f": {message}"
        print(result)
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
    
    def validate_data_pipeline(self) -> bool:
        """Validate the complete data pipeline from CSV loading through fraud detection."""
        print("\n📊 Validating Data Pipeline...")
        
        try:
            # Test that system initializes and loads data
            start_time = time.time()
            response = self.client.get("/stats")
            duration = time.time() - start_time
            
            if response.status_code != 200:
                self.log_result("Data Pipeline - System Initialization", False, 
                              f"HTTP {response.status_code}", duration)
                return False
            
            stats_data = response.json()
            if not stats_data.get('data'):
                self.log_result("Data Pipeline - System Initialization", False, 
                              "No stats data returned", duration)
                return False
            
            stats = stats_data['data']
            required_stats = ['total_transactions', 'fraud_rate', 'total_trade_value']
            missing_stats = [stat for stat in required_stats if stat not in stats]
            
            if missing_stats:
                self.log_result("Data Pipeline - System Initialization", False, 
                              f"Missing stats: {missing_stats}", duration)
                return False
            
            total_transactions = stats['total_transactions']
            fraud_rate = stats['fraud_rate']
            
            if total_transactions == 0:
                self.log_result("Data Pipeline - Data Loading", False, 
                              "No transactions loaded", duration)
                return False
            
            self.log_result("Data Pipeline - Data Loading", True, 
                          f"Loaded {total_transactions} transactions", duration)
            
            # Test feature engineering by checking transactions have ML features
            response = self.client.get("/transactions?limit=5")
            if response.status_code != 200:
                self.log_result("Data Pipeline - Feature Engineering", False, 
                              f"HTTP {response.status_code}")
                return False
            
            transactions_data = response.json()
            transactions = transactions_data.get('data', [])
            
            if not transactions:
                self.log_result("Data Pipeline - Feature Engineering", False, 
                              "No transactions returned")
                return False
            
            # Verify transactions have required ML fields
            sample_transaction = transactions[0]
            required_fields = ['risk_score', 'risk_category', 'transaction_id']
            missing_fields = [field for field in required_fields if field not in sample_transaction]
            
            if missing_fields:
                self.log_result("Data Pipeline - Feature Engineering", False, 
                              f"Missing ML fields: {missing_fields}")
                return False
            
            # Check for engineered features
            feature_fields = ['price_anomaly_score', 'route_risk_score', 'company_network_risk']
            present_features = [field for field in feature_fields if field in sample_transaction]
            
            if len(present_features) < 2:
                self.log_result("Data Pipeline - Feature Engineering", False, 
                              f"Missing engineered features. Found: {present_features}")
                return False
            
            self.log_result("Data Pipeline - Feature Engineering", True, 
                          f"Features present: {present_features}")
            
            # Test ML model scoring
            valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
            invalid_categories = [t['risk_category'] for t in transactions 
                                if t['risk_category'] not in valid_categories]
            
            if invalid_categories:
                self.log_result("Data Pipeline - ML Scoring", False, 
                              f"Invalid risk categories: {set(invalid_categories)}")
                return False
            
            # Check risk score ranges
            risk_scores = [t['risk_score'] for t in transactions if 'risk_score' in t]
            if not risk_scores:
                self.log_result("Data Pipeline - ML Scoring", False, 
                              "No risk scores found")
                return False
            
            min_score, max_score = min(risk_scores), max(risk_scores)
            if min_score < -1.0 or max_score > 1.0:
                self.log_result("Data Pipeline - ML Scoring", False, 
                              f"Risk scores out of range: {min_score:.3f} to {max_score:.3f}")
                return False
            
            self.log_result("Data Pipeline - ML Scoring", True, 
                          f"Risk scores in valid range: {min_score:.3f} to {max_score:.3f}")
            
            return True
            
        except Exception as e:
            self.log_result("Data Pipeline - General", False, str(e))
            return False
    
    def validate_api_integration(self) -> bool:
        """Validate all API endpoints and integration."""
        print("\n🔌 Validating API Integration...")
        
        # Test all critical endpoints
        endpoints = [
            ("GET", "/", "Root endpoint"),
            ("GET", "/transactions", "All transactions"),
            ("GET", "/suspicious", "Suspicious transactions"),
            ("GET", "/fraud", "Fraud transactions"),
            ("GET", "/stats", "Statistics"),
            ("GET", "/alerts", "Alerts"),
            ("GET", "/session/info", "Session info")
        ]
        
        all_passed = True
        total_api_time = 0
        
        for method, endpoint, description in endpoints:
            try:
                start_time = time.time()
                response = self.client.get(endpoint)
                duration = time.time() - start_time
                total_api_time += duration
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    if isinstance(data, dict) and 'status' in data:
                        # Check performance requirement (API should respond within 1 second)
                        if duration <= 1.0:
                            self.log_result(f"API {endpoint}", True, 
                                          f"Response time: {duration:.3f}s", duration)
                        else:
                            self.log_result(f"API {endpoint}", False, 
                                          f"Too slow: {duration:.3f}s > 1.0s", duration)
                            all_passed = False
                    else:
                        self.log_result(f"API {endpoint}", False, 
                                      "Invalid response structure", duration)
                        all_passed = False
                else:
                    self.log_result(f"API {endpoint}", False, 
                                  f"HTTP {response.status_code}", duration)
                    all_passed = False
                    
            except Exception as e:
                self.log_result(f"API {endpoint}", False, str(e))
                all_passed = False
        
        avg_api_time = total_api_time / len(endpoints) if endpoints else 0
        self.log_result("API Integration - Performance", 
                       avg_api_time <= 1.0,
                       f"Average response time: {avg_api_time:.3f}s")
        
        return all_passed
    
    def validate_ai_integration(self) -> bool:
        """Validate AI explanation functionality."""
        print("\n🤖 Validating AI Integration...")
        
        try:
            # Get a transaction for explanation testing
            response = self.client.get("/transactions?limit=1")
            if response.status_code != 200:
                self.log_result("AI Integration - Get Transaction", False, 
                              "Cannot get transaction")
                return False
            
            transactions = response.json().get('data', [])
            if not transactions:
                self.log_result("AI Integration - Get Transaction", False, 
                              "No transactions available")
                return False
            
            transaction_id = transactions[0]['transaction_id']
            self.log_result("AI Integration - Get Transaction", True, 
                          f"Using transaction {transaction_id}")
            
            # Test explanation endpoint (with fallback for reliability)
            start_time = time.time()
            explain_data = {"force_ai": False}  # Use fallback for reliability
            response = self.client.post(f"/explain/{transaction_id}", json=explain_data)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                explain_result = response.json()
                if explain_result.get('data', {}).get('explanation'):
                    self.log_result("AI Integration - Explanation", True, 
                                  "Explanation generated", duration)
                else:
                    self.log_result("AI Integration - Explanation", False, 
                                  "No explanation in response", duration)
                    return False
            else:
                self.log_result("AI Integration - Explanation", False, 
                              f"HTTP {response.status_code}", duration)
                return False
            
            # Test query endpoint
            query_data = {"query": "What are the main fraud indicators?", "force_ai": False}
            response = self.client.post("/query", json=query_data)
            
            if response.status_code == 200:
                query_result = response.json()
                if query_result.get('data', {}).get('response'):
                    self.log_result("AI Integration - Query", True, "Query processed")
                else:
                    self.log_result("AI Integration - Query", False, 
                                  "No response in query result")
                    return False
            else:
                self.log_result("AI Integration - Query", False, 
                              f"HTTP {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("AI Integration - General", False, str(e))
            return False
    
    def validate_alert_system(self) -> bool:
        """Validate alert system functionality."""
        print("\n🚨 Validating Alert System...")
        
        try:
            # Test alerts endpoint
            start_time = time.time()
            response = self.client.get("/alerts")
            duration = time.time() - start_time
            
            if response.status_code != 200:
                self.log_result("Alert System - Alerts Endpoint", False, 
                              f"HTTP {response.status_code}", duration)
                return False
            
            alerts_data = response.json()
            alerts = alerts_data.get('data', [])
            
            self.log_result("Alert System - Alerts Endpoint", True, 
                          f"Found {len(alerts)} alerts", duration)
            
            # Test alert statistics
            response = self.client.get("/alerts/statistics")
            if response.status_code == 200:
                stats_data = response.json()
                stats = stats_data.get('data', {})
                
                required_stats = ['total_alerts', 'alert_types']
                missing_stats = [stat for stat in required_stats if stat not in stats]
                
                if missing_stats:
                    self.log_result("Alert System - Statistics", False, 
                                  f"Missing alert stats: {missing_stats}")
                    return False
                
                self.log_result("Alert System - Statistics", True, 
                              f"Total alerts: {stats['total_alerts']}")
            else:
                self.log_result("Alert System - Statistics", False, 
                              f"HTTP {response.status_code}")
                return False
            
            # Validate alert structure if alerts exist
            if alerts:
                sample_alert = alerts[0]
                required_alert_fields = ['transaction_id', 'alert_type']
                missing_alert_fields = [field for field in required_alert_fields 
                                      if field not in sample_alert]
                
                if missing_alert_fields:
                    self.log_result("Alert System - Alert Structure", False, 
                                  f"Missing alert fields: {missing_alert_fields}")
                    return False
                
                self.log_result("Alert System - Alert Structure", True, 
                              "Alert structure valid")
            
            return True
            
        except Exception as e:
            self.log_result("Alert System - General", False, str(e))
            return False
    
    def validate_data_consistency(self) -> bool:
        """Validate data consistency across different endpoints."""
        print("\n🔍 Validating Data Consistency...")
        
        try:
            # Get stats
            stats_response = self.client.get("/stats")
            if stats_response.status_code != 200:
                self.log_result("Data Consistency - Stats", False, "Cannot get stats")
                return False
            
            stats = stats_response.json()['data']
            total_from_stats = stats['total_transactions']
            
            # Get all transactions
            transactions_response = self.client.get("/transactions")
            if transactions_response.status_code != 200:
                self.log_result("Data Consistency - Transactions", False, 
                              "Cannot get transactions")
                return False
            
            transactions = transactions_response.json()['data']
            total_from_transactions = len(transactions)
            
            if total_from_stats != total_from_transactions:
                self.log_result("Data Consistency - Transaction Count", False, 
                              f"Mismatch: stats={total_from_stats}, actual={total_from_transactions}")
                return False
            
            self.log_result("Data Consistency - Transaction Count", True, 
                          f"Consistent: {total_from_stats} transactions")
            
            # Check suspicious transactions
            suspicious_response = self.client.get("/suspicious")
            if suspicious_response.status_code == 200:
                suspicious_transactions = suspicious_response.json()['data']
                suspicious_count = len(suspicious_transactions)
                
                # Verify all suspicious transactions are actually suspicious
                non_suspicious = [t for t in suspicious_transactions 
                                if t.get('risk_category') != 'SUSPICIOUS']
                
                if non_suspicious:
                    self.log_result("Data Consistency - Suspicious Filter", False, 
                                  f"Found {len(non_suspicious)} non-suspicious in suspicious list")
                    return False
                
                self.log_result("Data Consistency - Suspicious Filter", True, 
                              f"All {suspicious_count} transactions are suspicious")
            
            # Check fraud transactions
            fraud_response = self.client.get("/fraud")
            if fraud_response.status_code == 200:
                fraud_transactions = fraud_response.json()['data']
                fraud_count = len(fraud_transactions)
                
                # Verify all fraud transactions are actually fraud
                non_fraud = [t for t in fraud_transactions 
                           if t.get('risk_category') != 'FRAUD']
                
                if non_fraud:
                    self.log_result("Data Consistency - Fraud Filter", False, 
                                  f"Found {len(non_fraud)} non-fraud in fraud list")
                    return False
                
                self.log_result("Data Consistency - Fraud Filter", True, 
                              f"All {fraud_count} transactions are fraud")
            
            return True
            
        except Exception as e:
            self.log_result("Data Consistency - General", False, str(e))
            return False
    
    def validate_performance_requirements(self) -> bool:
        """Validate system performance requirements."""
        print("\n⚡ Validating Performance Requirements...")
        
        try:
            # Test multiple concurrent requests
            import concurrent.futures
            
            def make_request(endpoint):
                start_time = time.time()
                response = self.client.get(endpoint)
                duration = time.time() - start_time
                return endpoint, response.status_code == 200, duration
            
            endpoints = ["/stats", "/transactions?limit=10", "/suspicious", "/fraud", "/alerts"]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, endpoint) for endpoint in endpoints]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successful_requests = sum(1 for _, success, _ in results if success)
            avg_response_time = sum(duration for _, _, duration in results) / len(results)
            
            if successful_requests == len(endpoints):
                self.log_result("Performance - Concurrent Requests", True, 
                              f"All {len(endpoints)} requests successful, avg: {avg_response_time:.3f}s")
            else:
                self.log_result("Performance - Concurrent Requests", False, 
                              f"Only {successful_requests}/{len(endpoints)} requests successful")
                return False
            
            # Test response time requirements
            if avg_response_time <= 1.0:
                self.log_result("Performance - Response Time", True, 
                              f"Average response time: {avg_response_time:.3f}s ≤ 1.0s")
            else:
                self.log_result("Performance - Response Time", False, 
                              f"Too slow: {avg_response_time:.3f}s > 1.0s")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Performance - General", False, str(e))
            return False
    
    def run_validation(self) -> bool:
        """Run the complete end-to-end validation suite."""
        print("🔍 TRINETRA AI - End-to-End Functionality Validation")
        print("=" * 65)
        
        # Initialize system (this happens automatically when TestClient is created)
        print("🚀 Initializing system...")
        
        # Run validation tests
        validation_results = []
        
        validation_results.append(self.validate_data_pipeline())
        validation_results.append(self.validate_api_integration())
        validation_results.append(self.validate_ai_integration())
        validation_results.append(self.validate_alert_system())
        validation_results.append(self.validate_data_consistency())
        validation_results.append(self.validate_performance_requirements())
        
        # Calculate results
        total_duration = time.time() - self.start_time
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        # Summary
        print("\n" + "=" * 65)
        print("📋 END-TO-END VALIDATION SUMMARY")
        print("=" * 65)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            duration_str = f" ({result['duration']:.3f}s)" if result['duration'] > 0 else ""
            print(f"{status} {result['test']}{duration_str}")
            if result['message'] and not result['success']:
                print(f"   └─ {result['message']}")
        
        print(f"\nResults: {passed_tests}/{total_tests} tests passed ({success_rate:.1%})")
        print(f"Total validation time: {total_duration:.2f}s")
        
        # Determine overall success
        overall_success = all(validation_results) and success_rate >= 0.9
        
        if overall_success:
            print("\n🎉 END-TO-END FUNCTIONALITY VALIDATION PASSED!")
            print("✅ Complete data pipeline from CSV loading through fraud detection")
            print("✅ API integration and all endpoints working properly")
            print("✅ Data flow integrity across the entire system")
            print("✅ AI integration and explanation generation")
            print("✅ Alert system functionality")
            print("✅ Performance requirements compliance")
            print("✅ All components working together seamlessly")
        else:
            print("\n❌ END-TO-END FUNCTIONALITY VALIDATION FAILED!")
            print(f"❌ Success rate: {success_rate:.1%} (need ≥90%)")
            
            failed_tests = [result for result in self.test_results if not result['success']]
            if failed_tests:
                print("❌ Failed validations:")
                for result in failed_tests[:5]:  # Show first 5 failures
                    print(f"   • {result['test']}: {result['message']}")
        
        return overall_success


def test_end_to_end_validation():
    """Main test function for pytest."""
    validator = EndToEndValidator()
    success = validator.run_validation()
    assert success, "End-to-end functionality validation failed"


if __name__ == "__main__":
    """Run the validation directly."""
    validator = EndToEndValidator()
    
    try:
        success = validator.run_validation()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Validation interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n💥 Validation error: {e}")
        sys.exit(1)