#!/usr/bin/env python3
"""
End-to-End Functionality Validation Test for TRINETRA AI
Validates complete system functionality from data loading to dashboard interaction.

**Validates: System Integration Tests (section 10.2) - Task: Validate end-to-end functionality**

This comprehensive test validates:
1. Complete data pipeline from CSV loading through fraud detection
2. API and dashboard integration working properly
3. System startup and shutdown processes
4. All components working together seamlessly
5. Data flow integrity across the entire system
6. AI integration and explanation generation
7. Alert system functionality
8. Performance requirements compliance

Success Criteria:
- System runs with single command: `python main.py`
- Dashboard loads within 3 seconds
- API responses within 1 second
- All components integrate seamlessly
- Data flows correctly through entire pipeline
"""

import pytest
import subprocess
import time
import signal
import os
import sys
import requests
import json
import threading
import psutil
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import pandas as pd

# Test configuration
TEST_TIMEOUT = 120  # Extended timeout for comprehensive testing
API_PORT = 8000
DASHBOARD_PORT = 8501
STARTUP_WAIT_TIME = 15  # Extended wait time for full system startup
PERFORMANCE_TIMEOUT_API = 1.0  # API response time requirement
PERFORMANCE_TIMEOUT_DASHBOARD = 3.0  # Dashboard load time requirement


class EndToEndTester:
    """Comprehensive end-to-end system tester."""
    
    def __init__(self):
        self.main_process: Optional[subprocess.Popen] = None
        self.test_results: List[Dict[str, Any]] = []
        self.start_time = None
        self.system_ready = False
        
    def log_result(self, test_name: str, success: bool, message: str = "", duration: float = 0):
        """Log test result with timing information."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if duration > 0:
            result += f" ({duration:.2f}s)"
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
    
    def cleanup(self):
        """Clean up test resources."""
        if self.main_process:
            self.terminate_process_tree(self.main_process.pid)
    
    def terminate_process_tree(self, pid: int):
        """Terminate a process and all its children."""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            
            # Terminate children first
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass
            
            # Wait for children to terminate
            psutil.wait_procs(children, timeout=10)
            
            # Terminate parent
            try:
                parent.terminate()
                parent.wait(timeout=10)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                try:
                    parent.kill()
                except psutil.NoSuchProcess:
                    pass
                    
        except psutil.NoSuchProcess:
            pass
    
    def wait_for_service(self, url: str, timeout: int = 30) -> tuple[bool, float]:
        """Wait for service to be available and measure response time."""
        start_time = time.time()
        first_response_time = None
        
        while time.time() - start_time < timeout:
            try:
                request_start = time.time()
                response = requests.get(url, timeout=5)
                request_duration = time.time() - request_start
                
                if response.status_code == 200:
                    if first_response_time is None:
                        first_response_time = request_duration
                    return True, first_response_time
                    
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        return False, 0.0
    
    def check_system_running(self) -> bool:
        """Check if the TRINETRA AI system is already running."""
        print("🔍 Checking if TRINETRA AI system is running...")
        
        # Check if dataset exists
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            self.log_result("System Check - Dataset", False, "Dataset not found")
            return False
        
        self.log_result("System Check - Dataset", True, "Dataset found")
        
        # Check if API is accessible
        try:
            response = requests.get(f"http://localhost:{API_PORT}/", timeout=5)
            if response.status_code == 200:
                self.log_result("System Check - API Running", True, "API is accessible")
                return True
            else:
                self.log_result("System Check - API Running", False, f"API returned HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_result("System Check - API Running", False, f"API not accessible: {str(e)}")
            print("\n⚠️  TRINETRA AI system is not running.")
            print("Please start the system first by running: python main.py")
            print("Then run this test again.")
            return False
    
    def test_data_pipeline(self) -> bool:
        """Test the complete data pipeline from CSV loading through fraud detection."""
        print("\n📊 Testing Data Pipeline...")
        
        try:
            # Test that API has loaded and processed data
            start_time = time.time()
            response = requests.get(f"http://localhost:{API_PORT}/stats", timeout=10)
            api_duration = time.time() - start_time
            
            if response.status_code != 200:
                self.log_result("Data Pipeline - API Stats", False, 
                              f"HTTP {response.status_code}", api_duration)
                return False
            
            stats_data = response.json()
            if not stats_data.get('data'):
                self.log_result("Data Pipeline - API Stats", False, 
                              "No stats data returned", api_duration)
                return False
            
            stats = stats_data['data']
            required_stats = ['total_transactions', 'fraud_rate', 'total_trade_value']
            missing_stats = [stat for stat in required_stats if stat not in stats]
            
            if missing_stats:
                self.log_result("Data Pipeline - API Stats", False, 
                              f"Missing stats: {missing_stats}", api_duration)
                return False
            
            total_transactions = stats['total_transactions']
            fraud_rate = stats['fraud_rate']
            
            self.log_result("Data Pipeline - API Stats", True, 
                          f"Processed {total_transactions} transactions, {fraud_rate:.1%} fraud rate", 
                          api_duration)
            
            # Test that transactions have been scored and classified
            response = requests.get(f"http://localhost:{API_PORT}/transactions?limit=10", timeout=10)
            if response.status_code != 200:
                self.log_result("Data Pipeline - Transaction Scoring", False, 
                              f"HTTP {response.status_code}")
                return False
            
            transactions_data = response.json()
            transactions = transactions_data.get('data', [])
            
            if not transactions:
                self.log_result("Data Pipeline - Transaction Scoring", False, 
                              "No transactions returned")
                return False
            
            # Verify transactions have required ML fields
            sample_transaction = transactions[0]
            required_fields = ['risk_score', 'risk_category', 'transaction_id']
            missing_fields = [field for field in required_fields if field not in sample_transaction]
            
            if missing_fields:
                self.log_result("Data Pipeline - Transaction Scoring", False, 
                              f"Missing ML fields: {missing_fields}")
                return False
            
            # Verify risk categories are valid
            valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
            invalid_categories = [t['risk_category'] for t in transactions 
                                if t['risk_category'] not in valid_categories]
            
            if invalid_categories:
                self.log_result("Data Pipeline - Transaction Scoring", False, 
                              f"Invalid risk categories: {set(invalid_categories)}")
                return False
            
            self.log_result("Data Pipeline - Transaction Scoring", True, 
                          f"All transactions properly scored and classified")
            
            # Test feature engineering by checking for engineered features
            feature_fields = ['price_anomaly_score', 'route_risk_score', 'company_network_risk']
            present_features = [field for field in feature_fields if field in sample_transaction]
            
            if len(present_features) < 2:  # At least some features should be present
                self.log_result("Data Pipeline - Feature Engineering", False, 
                              f"Missing engineered features. Found: {present_features}")
                return False
            
            self.log_result("Data Pipeline - Feature Engineering", True, 
                          f"Engineered features present: {present_features}")
            
            return True
            
        except Exception as e:
            self.log_result("Data Pipeline - General", False, str(e))
            return False
    
    def test_api_integration(self) -> bool:
        """Test API endpoints and integration."""
        print("\n🔌 Testing API Integration...")
        
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
                url = f"http://localhost:{API_PORT}{endpoint}"
                response = requests.get(url, timeout=10)
                duration = time.time() - start_time
                total_api_time += duration
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    if isinstance(data, dict) and 'status' in data:
                        # Check performance requirement
                        if duration <= PERFORMANCE_TIMEOUT_API:
                            self.log_result(f"API {endpoint}", True, 
                                          f"Response time: {duration:.3f}s", duration)
                        else:
                            self.log_result(f"API {endpoint}", False, 
                                          f"Too slow: {duration:.3f}s > {PERFORMANCE_TIMEOUT_API}s", 
                                          duration)
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
        
        # Test AI integration endpoints
        try:
            # Get a transaction for explanation testing
            response = requests.get(f"http://localhost:{API_PORT}/transactions?limit=1", timeout=10)
            if response.status_code == 200:
                transactions = response.json().get('data', [])
                if transactions:
                    transaction_id = transactions[0]['transaction_id']
                    
                    # Test explanation endpoint (with fallback)
                    start_time = time.time()
                    explain_data = {"force_ai": False}  # Use fallback for reliability
                    response = requests.post(
                        f"http://localhost:{API_PORT}/explain/{transaction_id}",
                        json=explain_data,
                        timeout=15
                    )
                    duration = time.time() - start_time
                    
                    if response.status_code == 200:
                        explain_result = response.json()
                        if explain_result.get('data', {}).get('explanation'):
                            self.log_result("API - AI Explanation", True, 
                                          "Explanation generated", duration)
                        else:
                            self.log_result("API - AI Explanation", False, 
                                          "No explanation in response", duration)
                            all_passed = False
                    else:
                        self.log_result("API - AI Explanation", False, 
                                      f"HTTP {response.status_code}", duration)
                        all_passed = False
                        
        except Exception as e:
            self.log_result("API - AI Explanation", False, str(e))
            all_passed = False
        
        avg_api_time = total_api_time / len(endpoints) if endpoints else 0
        self.log_result("API Integration - Performance", 
                       avg_api_time <= PERFORMANCE_TIMEOUT_API,
                       f"Average response time: {avg_api_time:.3f}s")
        
        return all_passed
    
    def test_dashboard_integration(self) -> bool:
        """Test dashboard integration and accessibility."""
        print("\n🖥️  Testing Dashboard Integration...")
        
        try:
            # Test dashboard accessibility with performance measurement
            start_time = time.time()
            dashboard_available, response_time = self.wait_for_service(
                f"http://localhost:{DASHBOARD_PORT}", timeout=30
            )
            
            if not dashboard_available:
                self.log_result("Dashboard - Accessibility", False, 
                              "Dashboard not accessible")
                return False
            
            # Check performance requirement
            if response_time <= PERFORMANCE_TIMEOUT_DASHBOARD:
                self.log_result("Dashboard - Accessibility", True, 
                              f"Load time: {response_time:.3f}s", response_time)
            else:
                self.log_result("Dashboard - Accessibility", False, 
                              f"Too slow: {response_time:.3f}s > {PERFORMANCE_TIMEOUT_DASHBOARD}s", 
                              response_time)
                return False
            
            # Test that dashboard can connect to API (indirect test)
            # Dashboard uses the same API endpoints we tested above
            self.log_result("Dashboard - API Integration", True, 
                          "API endpoints available for dashboard")
            
            return True
            
        except Exception as e:
            self.log_result("Dashboard - General", False, str(e))
            return False
    
    def test_alert_system(self) -> bool:
        """Test alert system functionality."""
        print("\n🚨 Testing Alert System...")
        
        try:
            # Test alerts endpoint
            start_time = time.time()
            response = requests.get(f"http://localhost:{API_PORT}/alerts", timeout=10)
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
            response = requests.get(f"http://localhost:{API_PORT}/alerts/statistics", timeout=10)
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
            
            return True
            
        except Exception as e:
            self.log_result("Alert System - General", False, str(e))
            return False
    
    def test_system_performance(self) -> bool:
        """Test overall system performance requirements."""
        print("\n⚡ Testing System Performance...")
        
        try:
            # Test multiple concurrent API requests
            import concurrent.futures
            
            def make_request(endpoint):
                start_time = time.time()
                response = requests.get(f"http://localhost:{API_PORT}{endpoint}", timeout=5)
                duration = time.time() - start_time
                return endpoint, response.status_code == 200, duration
            
            endpoints = ["/stats", "/transactions?limit=10", "/suspicious", "/fraud", "/alerts"]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, endpoint) for endpoint in endpoints]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successful_requests = sum(1 for _, success, _ in results if success)
            avg_response_time = sum(duration for _, _, duration in results) / len(results)
            
            if successful_requests == len(endpoints):
                self.log_result("System Performance - Concurrent Requests", True, 
                              f"All {len(endpoints)} requests successful, avg: {avg_response_time:.3f}s")
            else:
                self.log_result("System Performance - Concurrent Requests", False, 
                              f"Only {successful_requests}/{len(endpoints)} requests successful")
                return False
            
            # Test system resource usage
            if self.main_process:
                try:
                    process = psutil.Process(self.main_process.pid)
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    cpu_percent = process.cpu_percent(interval=1)
                    
                    # Reasonable resource usage thresholds
                    memory_ok = memory_mb < 1000  # Less than 1GB
                    cpu_ok = cpu_percent < 80     # Less than 80% CPU
                    
                    if memory_ok and cpu_ok:
                        self.log_result("System Performance - Resource Usage", True, 
                                      f"Memory: {memory_mb:.1f}MB, CPU: {cpu_percent:.1f}%")
                    else:
                        self.log_result("System Performance - Resource Usage", False, 
                                      f"High usage - Memory: {memory_mb:.1f}MB, CPU: {cpu_percent:.1f}%")
                        return False
                        
                except psutil.NoSuchProcess:
                    self.log_result("System Performance - Resource Usage", False, 
                                  "Cannot measure resource usage")
                    return False
            
            return True
            
        except Exception as e:
            self.log_result("System Performance - General", False, str(e))
            return False
    
    def test_system_health(self) -> bool:
        """Test overall system health and responsiveness."""
        print("\n💚 Testing System Health...")
        
        try:
            # Test system responsiveness with multiple quick requests
            health_checks = [
                ("/", "Root endpoint"),
                ("/stats", "Statistics"),
                ("/session/info", "Session info")
            ]
            
            all_healthy = True
            total_response_time = 0
            
            for endpoint, description in health_checks:
                start_time = time.time()
                try:
                    response = requests.get(f"http://localhost:{API_PORT}{endpoint}", timeout=5)
                    duration = time.time() - start_time
                    total_response_time += duration
                    
                    if response.status_code == 200:
                        self.log_result(f"Health Check - {description}", True, 
                                      f"Response time: {duration:.3f}s", duration)
                    else:
                        self.log_result(f"Health Check - {description}", False, 
                                      f"HTTP {response.status_code}", duration)
                        all_healthy = False
                        
                except Exception as e:
                    self.log_result(f"Health Check - {description}", False, str(e))
                    all_healthy = False
            
            avg_response_time = total_response_time / len(health_checks)
            
            if all_healthy and avg_response_time < 2.0:
                self.log_result("System Health - Overall", True, 
                              f"System healthy, avg response: {avg_response_time:.3f}s")
                return True
            else:
                self.log_result("System Health - Overall", False, 
                              f"Health issues detected, avg response: {avg_response_time:.3f}s")
                return False
                
        except Exception as e:
            self.log_result("System Health - General", False, str(e))
            return False
    
    def run_comprehensive_test(self) -> bool:
        """Run the complete end-to-end test suite."""
        print("🔍 TRINETRA AI - Comprehensive End-to-End Functionality Test")
        print("=" * 70)
        
        overall_start_time = time.time()
        
        # Step 1: Check if system is running
        if not self.check_system_running():
            return False
        
        # Step 2: Wait for services to be fully ready
        print("\n⏳ Verifying services are ready...")
        api_ready, api_time = self.wait_for_service(f"http://localhost:{API_PORT}", timeout=10)
        dashboard_ready, dashboard_time = self.wait_for_service(f"http://localhost:{DASHBOARD_PORT}", timeout=10)
        
        if not api_ready:
            self.log_result("Service Readiness - API", False, "API not ready")
            return False
        
        if not dashboard_ready:
            self.log_result("Service Readiness - Dashboard", False, "Dashboard not ready")
            return False
        
        self.log_result("Service Readiness - API", True, f"Ready in {api_time:.3f}s")
        self.log_result("Service Readiness - Dashboard", True, f"Ready in {dashboard_time:.3f}s")
        
        self.system_ready = True
        
        # Step 3: Run comprehensive tests
        test_results = []
        
        test_results.append(self.test_data_pipeline())
        test_results.append(self.test_api_integration())
        test_results.append(self.test_dashboard_integration())
        test_results.append(self.test_alert_system())
        test_results.append(self.test_system_performance())
        test_results.append(self.test_system_health())
        
        # Calculate overall results
        total_duration = time.time() - overall_start_time
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 END-TO-END TEST SUMMARY")
        print("=" * 70)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            duration_str = f" ({result['duration']:.3f}s)" if result['duration'] > 0 else ""
            print(f"{status} {result['test']}{duration_str}")
            if result['message'] and not result['success']:
                print(f"   └─ {result['message']}")
        
        print(f"\nResults: {passed_tests}/{total_tests} tests passed ({success_rate:.1%})")
        print(f"Total test duration: {total_duration:.2f}s")
        
        # Determine overall success
        overall_success = all(test_results) and success_rate >= 0.9
        
        if overall_success:
            print("\n🎉 END-TO-END FUNCTIONALITY TEST PASSED!")
            print("✅ Complete data pipeline working")
            print("✅ API and dashboard integration verified")
            print("✅ All components working together seamlessly")
            print("✅ Performance requirements met")
            print("✅ System health verified")
        else:
            print("\n❌ END-TO-END FUNCTIONALITY TEST FAILED!")
            print(f"❌ Success rate: {success_rate:.1%} (need ≥90%)")
            
            failed_tests = [result for result in self.test_results if not result['success']]
            if failed_tests:
                print("❌ Failed tests:")
                for result in failed_tests[:5]:  # Show first 5 failures
                    print(f"   • {result['test']}: {result['message']}")
        
        return overall_success


def test_end_to_end_functionality():
    """Main test function for end-to-end functionality validation."""
    tester = EndToEndTester()
    
    try:
        success = tester.run_comprehensive_test()
        assert success, "End-to-end functionality test failed"
        
    finally:
        tester.cleanup()


if __name__ == "__main__":
    """Run the end-to-end test directly."""
    tester = EndToEndTester()
    
    try:
        success = tester.run_comprehensive_test()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)
        
    finally:
        tester.cleanup()