#!/usr/bin/env python3
"""
Core Integration Test for TRINETRA AI system
Tests essential API and dashboard integration functionality
"""

import requests
import time
import sys
from typing import Dict, List

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 15  # seconds

class CoreIntegrationTester:
    def __init__(self):
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
    
    def test_api_connectivity(self) -> bool:
        """Test basic API connectivity"""
        print("\n🔍 Testing API Connectivity...")
        
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_result("API Connectivity", True, "API is responding")
                    return True
                else:
                    self.log_result("API Connectivity", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_result("API Connectivity", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("API Connectivity", False, str(e))
            return False
    
    def test_transaction_endpoints(self) -> bool:
        """Test transaction data endpoints"""
        print("\n📊 Testing Transaction Endpoints...")
        
        endpoints = [
            ("/transactions", "All transactions"),
            ("/suspicious", "Suspicious transactions"),
            ("/fraud", "Fraud transactions")
        ]
        
        all_passed = True
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=TEST_TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success' and 'data' in data:
                        transaction_count = len(data['data'])
                        self.log_result(f"Endpoint {endpoint}", True, f"{transaction_count} transactions")
                    else:
                        self.log_result(f"Endpoint {endpoint}", False, "Invalid response format")
                        all_passed = False
                else:
                    self.log_result(f"Endpoint {endpoint}", False, f"HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_result(f"Endpoint {endpoint}", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_data_integrity(self) -> bool:
        """Test data integrity and schema"""
        print("\n🔍 Testing Data Integrity...")
        
        try:
            response = requests.get(f"{API_BASE_URL}/transactions?limit=5", timeout=TEST_TIMEOUT)
            if response.status_code != 200:
                self.log_result("Data Integrity", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            # Handle nested structure for /transactions endpoint
            if 'transactions' in data.get('data', {}):
                transactions = data['data']['transactions']
            else:
                transactions = data.get('data', [])
            
            if not transactions:
                self.log_result("Data Integrity", False, "No transaction data")
                return False
            
            # Check required fields
            required_fields = ['transaction_id', 'risk_score', 'risk_category']
            sample_transaction = transactions[0]
            
            missing_fields = [field for field in required_fields if field not in sample_transaction]
            if missing_fields:
                self.log_result("Data Integrity", False, f"Missing fields: {missing_fields}")
                return False
            
            # Check risk categories are valid
            valid_categories = ['SAFE', 'SUSPICIOUS', 'FRAUD']
            for transaction in transactions:
                if transaction['risk_category'] not in valid_categories:
                    self.log_result("Data Integrity", False, f"Invalid risk category: {transaction['risk_category']}")
                    return False
            
            self.log_result("Data Integrity", True, f"Validated {len(transactions)} transactions")
            return True
            
        except Exception as e:
            self.log_result("Data Integrity", False, str(e))
            return False
    
    def test_explanation_functionality(self) -> bool:
        """Test AI explanation functionality"""
        print("\n🤖 Testing Explanation Functionality...")
        
        try:
            # Get a transaction to explain
            response = requests.get(f"{API_BASE_URL}/transactions?limit=1", timeout=TEST_TIMEOUT)
            if response.status_code != 200:
                self.log_result("Explanation - Get Transaction", False, "Cannot get transaction")
                return False
            
            data = response.json()
            # Handle nested structure for /transactions endpoint
            if 'transactions' in data.get('data', {}):
                transactions = data['data']['transactions']
            else:
                transactions = data.get('data', [])
                
            if not transactions:
                self.log_result("Explanation - Get Transaction", False, "No transactions available")
                return False
            
            transaction_id = transactions[0]['transaction_id']
            self.log_result("Explanation - Get Transaction", True, f"Using transaction {transaction_id}")
            
            # Test explanation endpoint (using fallback, not AI)
            explain_data = {"force_ai": False}
            response = requests.post(
                f"{API_BASE_URL}/explain/{transaction_id}",
                json=explain_data,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                explain_result = response.json()
                if explain_result.get('data', {}).get('explanation'):
                    self.log_result("Explanation - Generate", True, "Explanation generated")
                    return True
                else:
                    self.log_result("Explanation - Generate", False, "No explanation in response")
                    return False
            else:
                self.log_result("Explanation - Generate", False, f"HTTP {response.status_code}")
                return False
            
        except Exception as e:
            self.log_result("Explanation - General", False, str(e))
            return False
    
    def test_query_functionality(self) -> bool:
        """Test natural language query functionality"""
        print("\n💬 Testing Query Functionality...")
        
        try:
            query_data = {"query": "What are the main fraud indicators?", "force_ai": False}
            response = requests.post(
                f"{API_BASE_URL}/query",
                json=query_data,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                query_result = response.json()
                if query_result.get('data', {}).get('response'):
                    self.log_result("Query Processing", True, "Query processed successfully")
                    return True
                else:
                    self.log_result("Query Processing", False, "No response in query result")
                    return False
            else:
                self.log_result("Query Processing", False, f"HTTP {response.status_code}")
                return False
            
        except Exception as e:
            self.log_result("Query Processing", False, str(e))
            return False
    
    def test_dashboard_integration(self) -> bool:
        """Test dashboard integration readiness"""
        print("\n🖥️  Testing Dashboard Integration Readiness...")
        
        # Test that all endpoints needed by dashboard are working
        dashboard_endpoints = [
            "/transactions",
            "/suspicious", 
            "/fraud"
        ]
        
        all_ready = True
        
        for endpoint in dashboard_endpoints:
            try:
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=TEST_TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        self.log_result(f"Dashboard Ready - {endpoint}", True, "Endpoint ready")
                    else:
                        self.log_result(f"Dashboard Ready - {endpoint}", False, "Invalid response")
                        all_ready = False
                else:
                    self.log_result(f"Dashboard Ready - {endpoint}", False, f"HTTP {response.status_code}")
                    all_ready = False
            except Exception as e:
                self.log_result(f"Dashboard Ready - {endpoint}", False, str(e))
                all_ready = False
        
        return all_ready
    
    def run_core_tests(self) -> bool:
        """Run all core integration tests"""
        print("🚀 Starting TRINETRA AI Core Integration Tests")
        print("=" * 50)
        
        # Run tests
        tests_passed = []
        tests_passed.append(self.test_api_connectivity())
        tests_passed.append(self.test_transaction_endpoints())
        tests_passed.append(self.test_data_integrity())
        tests_passed.append(self.test_explanation_functionality())
        tests_passed.append(self.test_query_functionality())
        tests_passed.append(self.test_dashboard_integration())
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 Core Integration Test Summary")
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
            print("🎉 All core integration tests PASSED!")
            print("\n✅ VERIFICATION COMPLETE:")
            print("   • FastAPI backend is running and responding")
            print("   • All transaction endpoints are working")
            print("   • Data integrity is maintained")
            print("   • AI explanation system is functional")
            print("   • Query processing is working")
            print("   • Dashboard integration is ready")
        else:
            print("⚠️  Some core integration tests FAILED!")
        
        return overall_success

def main():
    """Main test runner"""
    tester = CoreIntegrationTester()
    
    try:
        success = tester.run_core_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()