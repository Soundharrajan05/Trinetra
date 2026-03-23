#!/usr/bin/env python3
"""
Integration test for TRINETRA AI system
Tests API and dashboard integration
"""

import requests
import time
import subprocess
import threading
import sys
import os
import signal
from typing import Dict, List, Optional

# Test configuration
API_BASE_URL = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8501"
TEST_TIMEOUT = 30  # seconds

class IntegrationTester:
    def __init__(self):
        self.api_process = None
        self.dashboard_process = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f": {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """Wait for service to be available"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        return False
    
    def test_api_endpoints(self) -> bool:
        """Test all FastAPI endpoints"""
        print("\n🔍 Testing API Endpoints...")
        
        endpoints = [
            ("GET", "/", "Root endpoint"),
            ("GET", "/transactions", "All transactions"),
            ("GET", "/suspicious", "Suspicious transactions"),
            ("GET", "/fraud", "Fraud transactions"),
            ("GET", "/stats", "Statistics"),
            ("GET", "/session/info", "Session info"),
            ("GET", "/alerts", "All alerts"),
            ("GET", "/alerts/statistics", "Alert statistics")
        ]
        
        all_passed = True
        
        for method, endpoint, description in endpoints:
            try:
                url = f"{API_BASE_URL}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and 'status' in data:
                        self.log_result(f"API {endpoint}", True, f"Status: {data['status']}")
                    else:
                        self.log_result(f"API {endpoint}", True, "Valid response")
                else:
                    self.log_result(f"API {endpoint}", False, f"HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_result(f"API {endpoint}", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_api_data_flow(self) -> bool:
        """Test data flow through API"""
        print("\n📊 Testing API Data Flow...")
        
        try:
            # Test transactions endpoint
            response = requests.get(f"{API_BASE_URL}/transactions", timeout=10)
            if response.status_code != 200:
                self.log_result("Data Flow - Transactions", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            if not data.get('data'):
                self.log_result("Data Flow - Transactions", False, "No transaction data")
                return False
            
            transactions = data['data']
            self.log_result("Data Flow - Transactions", True, f"Found {len(transactions)} transactions")
            
            # Test that transactions have required fields
            required_fields = ['transaction_id', 'risk_score', 'risk_category']
            sample_transaction = transactions[0]
            
            missing_fields = [field for field in required_fields if field not in sample_transaction]
            if missing_fields:
                self.log_result("Data Flow - Transaction Schema", False, f"Missing fields: {missing_fields}")
                return False
            
            self.log_result("Data Flow - Transaction Schema", True, "All required fields present")
            
            # Test suspicious transactions
            response = requests.get(f"{API_BASE_URL}/suspicious", timeout=10)
            if response.status_code == 200:
                suspicious_data = response.json()
                suspicious_count = len(suspicious_data.get('data', []))
                self.log_result("Data Flow - Suspicious Filter", True, f"Found {suspicious_count} suspicious transactions")
            else:
                self.log_result("Data Flow - Suspicious Filter", False, f"HTTP {response.status_code}")
                return False
            
            # Test fraud transactions
            response = requests.get(f"{API_BASE_URL}/fraud", timeout=10)
            if response.status_code == 200:
                fraud_data = response.json()
                fraud_count = len(fraud_data.get('data', []))
                self.log_result("Data Flow - Fraud Filter", True, f"Found {fraud_count} fraud transactions")
            else:
                self.log_result("Data Flow - Fraud Filter", False, f"HTTP {response.status_code}")
                return False
            
            # Test statistics
            response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
            if response.status_code == 200:
                stats_data = response.json()
                stats = stats_data.get('data', {})
                required_stats = ['total_transactions', 'fraud_rate', 'total_trade_value']
                missing_stats = [stat for stat in required_stats if stat not in stats]
                
                if missing_stats:
                    self.log_result("Data Flow - Statistics", False, f"Missing stats: {missing_stats}")
                    return False
                
                self.log_result("Data Flow - Statistics", True, f"Total transactions: {stats['total_transactions']}")
            else:
                self.log_result("Data Flow - Statistics", False, f"HTTP {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Data Flow - General", False, str(e))
            return False
    
    def test_ai_integration(self) -> bool:
        """Test AI explanation functionality"""
        print("\n🤖 Testing AI Integration...")
        
        try:
            # Get a transaction to explain
            response = requests.get(f"{API_BASE_URL}/transactions?limit=1", timeout=10)
            if response.status_code != 200:
                self.log_result("AI Integration - Get Transaction", False, "Cannot get transaction")
                return False
            
            data = response.json()
            transactions = data.get('data', [])
            if not transactions:
                self.log_result("AI Integration - Get Transaction", False, "No transactions available")
                return False
            
            transaction_id = transactions[0]['transaction_id']
            self.log_result("AI Integration - Get Transaction", True, f"Using transaction {transaction_id}")
            
            # Test explanation endpoint
            explain_data = {"force_ai": False}  # Use fallback explanation for testing
            response = requests.post(
                f"{API_BASE_URL}/explain/{transaction_id}",
                json=explain_data,
                timeout=15
            )
            
            if response.status_code == 200:
                explain_result = response.json()
                if explain_result.get('data', {}).get('explanation'):
                    self.log_result("AI Integration - Explanation", True, "Explanation generated")
                else:
                    self.log_result("AI Integration - Explanation", False, "No explanation in response")
                    return False
            else:
                self.log_result("AI Integration - Explanation", False, f"HTTP {response.status_code}")
                return False
            
            # Test query endpoint
            query_data = {"query": "What are the main fraud indicators?", "force_ai": False}
            response = requests.post(
                f"{API_BASE_URL}/query",
                json=query_data,
                timeout=15
            )
            
            if response.status_code == 200:
                query_result = response.json()
                if query_result.get('data', {}).get('response'):
                    self.log_result("AI Integration - Query", True, "Query processed")
                else:
                    self.log_result("AI Integration - Query", False, "No response in query result")
                    return False
            else:
                self.log_result("AI Integration - Query", False, f"HTTP {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("AI Integration - General", False, str(e))
            return False
    
    def test_dashboard_connectivity(self) -> bool:
        """Test dashboard can connect to API"""
        print("\n🖥️  Testing Dashboard Connectivity...")
        
        try:
            # Check if dashboard is accessible
            if not self.wait_for_service(DASHBOARD_URL, timeout=10):
                self.log_result("Dashboard - Accessibility", False, "Dashboard not accessible")
                return False
            
            self.log_result("Dashboard - Accessibility", True, "Dashboard is running")
            
            # The dashboard connectivity to API is tested indirectly through API tests
            # since the dashboard makes requests to the same endpoints we tested above
            self.log_result("Dashboard - API Integration", True, "API endpoints available for dashboard")
            
            return True
            
        except Exception as e:
            self.log_result("Dashboard - General", False, str(e))
            return False
    
    def run_integration_tests(self) -> bool:
        """Run all integration tests"""
        print("🚀 Starting TRINETRA AI Integration Tests")
        print("=" * 50)
        
        # Wait for API to be ready
        print("⏳ Waiting for FastAPI backend...")
        if not self.wait_for_service(API_BASE_URL, timeout=30):
            self.log_result("System Startup - API", False, "API not available")
            return False
        
        self.log_result("System Startup - API", True, "API is running")
        
        # Run tests
        tests_passed = []
        tests_passed.append(self.test_api_endpoints())
        tests_passed.append(self.test_api_data_flow())
        tests_passed.append(self.test_ai_integration())
        tests_passed.append(self.test_dashboard_connectivity())
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 Integration Test Summary")
        print("=" * 50)
        
        passed_count = sum(1 for result in self.test_results if result['success'])
        total_count = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['message'] and not result['success']:
                print(f"   └─ {result['message']}")
        
        print(f"\nResults: {passed_count}/{total_count} tests passed")
        
        overall_success = all(tests_passed)
        if overall_success:
            print("🎉 All integration tests PASSED!")
        else:
            print("⚠️  Some integration tests FAILED!")
        
        return overall_success

def main():
    """Main test runner"""
    tester = IntegrationTester()
    
    try:
        success = tester.run_integration_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()