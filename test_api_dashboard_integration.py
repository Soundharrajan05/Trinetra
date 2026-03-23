"""
TRINETRA AI - API and Dashboard Integration Tests

This module tests the integration between the FastAPI backend and Streamlit dashboard
to ensure all endpoints work correctly and data flows properly between components.

Test Coverage:
1. API endpoint connectivity and response validation
2. Dashboard component data integration
3. Interactive features (explanations, queries)
4. Error handling between frontend and backend
5. Session management and quota system
6. Alert system integration

Author: TRINETRA AI Team
Date: 2024
"""

import requests
import json
import time
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test Configuration
API_BASE_URL = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8501"
TEST_TIMEOUT = 10

class APIIntegrationTester:
    """Test class for API and Dashboard integration testing."""
    
    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.dashboard_url = DASHBOARD_URL
        self.test_results = []
        self.session = requests.Session()
        
    def log_test_result(self, test_name: str, passed: bool, message: str = "", details: Dict = None):
        """Log test result with details."""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "details": details or {},
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name} - {message}")
        
        if details:
            logger.debug(f"Details: {json.dumps(details, indent=2)}")
    
    def make_api_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Make API request with error handling."""
        try:
            url = f"{self.api_base_url}{endpoint}"
            
            if method == "GET":
                response = self.session.get(url, timeout=TEST_TIMEOUT)
            elif method == "POST":
                response = self.session.post(url, json=data or {}, timeout=TEST_TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError as e:
            return {"status": "error", "message": f"Connection failed: {str(e)}"}
        except requests.exceptions.HTTPError as e:
            return {"status": "error", "message": f"HTTP Error {e.response.status_code}: {e.response.text}"}
        except requests.exceptions.Timeout as e:
            return {"status": "error", "message": f"Request timeout: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
    
    def test_api_connectivity(self):
        """Test basic API connectivity and root endpoint."""
        logger.info("🔍 Testing API connectivity...")
        
        response = self.make_api_request("/")
        
        if response.get("status") == "success":
            data = response.get("data", {})
            expected_fields = ["name", "version", "description"]
            
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                self.log_test_result(
                    "API Root Endpoint",
                    True,
                    "API root endpoint responding correctly",
                    {"response_data": data}
                )
            else:
                self.log_test_result(
                    "API Root Endpoint",
                    False,
                    f"Missing fields in response: {missing_fields}",
                    {"response": response}
                )
        else:
            self.log_test_result(
                "API Root Endpoint",
                False,
                f"API not responding: {response.get('message', 'Unknown error')}",
                {"response": response}
            )
    
    def test_transactions_endpoint(self):
        """Test /transactions endpoint with pagination."""
        logger.info("🔍 Testing transactions endpoint...")
        
        # Test basic transactions endpoint
        response = self.make_api_request("/transactions?limit=10")
        
        if response.get("status") == "success":
            data = response.get("data", {})
            
            # Validate response structure
            required_fields = ["transactions", "pagination"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test_result(
                    "Transactions Endpoint Structure",
                    False,
                    f"Missing fields: {missing_fields}",
                    {"response": response}
                )
                return
            
            transactions = data.get("transactions", [])
            pagination = data.get("pagination", {})
            
            # Validate transactions data
            if not transactions:
                self.log_test_result(
                    "Transactions Data",
                    False,
                    "No transactions returned",
                    {"response": response}
                )
                return
            
            # Check first transaction structure
            first_transaction = transactions[0]
            expected_transaction_fields = [
                "transaction_id", "risk_score", "risk_category"
            ]
            
            missing_transaction_fields = [
                field for field in expected_transaction_fields 
                if field not in first_transaction
            ]
            
            if missing_transaction_fields:
                self.log_test_result(
                    "Transaction Data Structure",
                    False,
                    f"Missing transaction fields: {missing_transaction_fields}",
                    {"first_transaction": first_transaction}
                )
            else:
                self.log_test_result(
                    "Transactions Endpoint",
                    True,
                    f"Retrieved {len(transactions)} transactions with correct structure",
                    {
                        "transaction_count": len(transactions),
                        "pagination": pagination,
                        "sample_transaction": first_transaction
                    }
                )
        else:
            self.log_test_result(
                "Transactions Endpoint",
                False,
                f"Failed to retrieve transactions: {response.get('message', 'Unknown error')}",
                {"response": response}
            )
    
    def test_suspicious_and_fraud_endpoints(self):
        """Test /suspicious and /fraud endpoints."""
        logger.info("🔍 Testing suspicious and fraud endpoints...")
        
        # Test suspicious endpoint
        suspicious_response = self.make_api_request("/suspicious")
        
        if suspicious_response.get("status") == "success":
            suspicious_data = suspicious_response.get("data", [])
            
            # Validate all returned transactions are SUSPICIOUS
            if suspicious_data:
                non_suspicious = [
                    t for t in suspicious_data 
                    if t.get("risk_category") != "SUSPICIOUS"
                ]
                
                if non_suspicious:
                    self.log_test_result(
                        "Suspicious Endpoint Filtering",
                        False,
                        f"Found {len(non_suspicious)} non-suspicious transactions",
                        {"non_suspicious_count": len(non_suspicious)}
                    )
                else:
                    self.log_test_result(
                        "Suspicious Endpoint",
                        True,
                        f"Retrieved {len(suspicious_data)} suspicious transactions",
                        {"suspicious_count": len(suspicious_data)}
                    )
            else:
                self.log_test_result(
                    "Suspicious Endpoint",
                    True,
                    "No suspicious transactions found (valid result)",
                    {"suspicious_count": 0}
                )
        else:
            self.log_test_result(
                "Suspicious Endpoint",
                False,
                f"Failed to retrieve suspicious transactions: {suspicious_response.get('message')}",
                {"response": suspicious_response}
            )
        
        # Test fraud endpoint
        fraud_response = self.make_api_request("/fraud")
        
        if fraud_response.get("status") == "success":
            fraud_data = fraud_response.get("data", [])
            
            # Validate all returned transactions are FRAUD
            if fraud_data:
                non_fraud = [
                    t for t in fraud_data 
                    if t.get("risk_category") != "FRAUD"
                ]
                
                if non_fraud:
                    self.log_test_result(
                        "Fraud Endpoint Filtering",
                        False,
                        f"Found {len(non_fraud)} non-fraud transactions",
                        {"non_fraud_count": len(non_fraud)}
                    )
                else:
                    self.log_test_result(
                        "Fraud Endpoint",
                        True,
                        f"Retrieved {len(fraud_data)} fraud transactions",
                        {"fraud_count": len(fraud_data)}
                    )
            else:
                self.log_test_result(
                    "Fraud Endpoint",
                    True,
                    "No fraud transactions found (valid result)",
                    {"fraud_count": 0}
                )
        else:
            self.log_test_result(
                "Fraud Endpoint",
                False,
                f"Failed to retrieve fraud transactions: {fraud_response.get('message')}",
                {"response": fraud_response}
            )
    
    def test_stats_endpoint(self):
        """Test /stats endpoint for dashboard KPIs."""
        logger.info("🔍 Testing stats endpoint...")
        
        response = self.make_api_request("/stats")
        
        if response.get("status") == "success":
            stats = response.get("data", {})
            
            # Expected KPI fields
            expected_kpi_fields = [
                "total_transactions", "fraud_cases", "suspicious_cases",
                "fraud_rate", "total_trade_value", "avg_risk_score"
            ]
            
            missing_fields = [field for field in expected_kpi_fields if field not in stats]
            
            if missing_fields:
                self.log_test_result(
                    "Stats Endpoint Structure",
                    False,
                    f"Missing KPI fields: {missing_fields}",
                    {"stats": stats}
                )
            else:
                # Validate data types and ranges
                validation_errors = []
                
                if not isinstance(stats.get("total_transactions"), int) or stats.get("total_transactions") < 0:
                    validation_errors.append("total_transactions should be non-negative integer")
                
                if not isinstance(stats.get("fraud_rate"), (int, float)) or not (0 <= stats.get("fraud_rate") <= 100):
                    validation_errors.append("fraud_rate should be between 0 and 100")
                
                if not isinstance(stats.get("avg_risk_score"), (int, float)):
                    validation_errors.append("avg_risk_score should be numeric")
                
                if validation_errors:
                    self.log_test_result(
                        "Stats Data Validation",
                        False,
                        f"Data validation errors: {validation_errors}",
                        {"stats": stats}
                    )
                else:
                    self.log_test_result(
                        "Stats Endpoint",
                        True,
                        "Stats endpoint returning valid KPI data",
                        {"stats": stats}
                    )
        else:
            self.log_test_result(
                "Stats Endpoint",
                False,
                f"Failed to retrieve stats: {response.get('message', 'Unknown error')}",
                {"response": response}
            )
    
    def test_explanation_endpoint(self):
        """Test transaction explanation endpoint with quota management."""
        logger.info("🔍 Testing explanation endpoint...")
        
        # First, get a transaction ID to test with
        transactions_response = self.make_api_request("/transactions?limit=5")
        
        if transactions_response.get("status") != "success":
            self.log_test_result(
                "Explanation Endpoint Setup",
                False,
                "Could not retrieve transactions for explanation testing",
                {"response": transactions_response}
            )
            return
        
        transactions = transactions_response.get("data", {}).get("transactions", [])
        if not transactions:
            self.log_test_result(
                "Explanation Endpoint Setup",
                False,
                "No transactions available for explanation testing",
                {}
            )
            return
        
        test_transaction_id = transactions[0].get("transaction_id")
        
        # Test fallback explanation (force_ai=False)
        fallback_response = self.make_api_request(
            f"/explain/{test_transaction_id}",
            method="POST",
            data={"force_ai": False}
        )
        
        if fallback_response.get("status") == "success":
            data = fallback_response.get("data", {})
            required_fields = ["transaction_id", "explanation", "explanation_type"]
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test_result(
                    "Explanation Response Structure",
                    False,
                    f"Missing fields in explanation response: {missing_fields}",
                    {"response": fallback_response}
                )
            else:
                explanation_type = data.get("explanation_type")
                explanation = data.get("explanation", "")
                
                if explanation and len(explanation) > 10:  # Basic validation
                    self.log_test_result(
                        "Fallback Explanation",
                        True,
                        f"Generated {explanation_type} explanation successfully",
                        {
                            "transaction_id": test_transaction_id,
                            "explanation_type": explanation_type,
                            "explanation_length": len(explanation)
                        }
                    )
                else:
                    self.log_test_result(
                        "Fallback Explanation Quality",
                        False,
                        "Explanation too short or empty",
                        {"explanation": explanation}
                    )
        else:
            self.log_test_result(
                "Explanation Endpoint",
                False,
                f"Failed to generate explanation: {fallback_response.get('message')}",
                {"response": fallback_response}
            )
        
        # Test AI explanation (force_ai=True) - this may hit quota limits
        ai_response = self.make_api_request(
            f"/explain/{test_transaction_id}",
            method="POST",
            data={"force_ai": True}
        )
        
        if ai_response.get("status") == "success":
            data = ai_response.get("data", {})
            explanation_type = data.get("explanation_type")
            session_info = data.get("session_info", {})
            
            self.log_test_result(
                "AI Explanation Request",
                True,
                f"AI explanation request processed (type: {explanation_type})",
                {
                    "explanation_type": explanation_type,
                    "session_info": session_info
                }
            )
        else:
            self.log_test_result(
                "AI Explanation Request",
                False,
                f"AI explanation request failed: {ai_response.get('message')}",
                {"response": ai_response}
            )
    
    def test_query_endpoint(self):
        """Test natural language query endpoint."""
        logger.info("🔍 Testing query endpoint...")
        
        test_queries = [
            "What are the main fraud patterns?",
            "How many transactions are suspicious?",
            "What should I investigate next?"
        ]
        
        for query in test_queries:
            response = self.make_api_request(
                "/query",
                method="POST",
                data={"query": query}
            )
            
            if response.get("status") == "success":
                data = response.get("data", {})
                required_fields = ["query", "answer", "context_summary"]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result(
                        f"Query Response Structure ({query[:30]}...)",
                        False,
                        f"Missing fields: {missing_fields}",
                        {"response": response}
                    )
                else:
                    answer = data.get("answer", "")
                    if answer and len(answer) > 10:
                        self.log_test_result(
                            f"Query Processing ({query[:30]}...)",
                            True,
                            "Query processed successfully",
                            {
                                "query": query,
                                "answer_length": len(answer),
                                "context": data.get("context_summary")
                            }
                        )
                    else:
                        self.log_test_result(
                            f"Query Answer Quality ({query[:30]}...)",
                            False,
                            "Answer too short or empty",
                            {"answer": answer}
                        )
            else:
                self.log_test_result(
                    f"Query Endpoint ({query[:30]}...)",
                    False,
                    f"Query failed: {response.get('message')}",
                    {"response": response}
                )
    
    def test_session_management(self):
        """Test session management endpoints."""
        logger.info("🔍 Testing session management...")
        
        # Test session info endpoint
        session_info_response = self.make_api_request("/session/info")
        
        if session_info_response.get("status") == "success":
            session_data = session_info_response.get("data", {})
            required_fields = ["current_count", "max_count", "remaining", "can_make_explanation"]
            
            missing_fields = [field for field in required_fields if field not in session_data]
            
            if missing_fields:
                self.log_test_result(
                    "Session Info Structure",
                    False,
                    f"Missing session info fields: {missing_fields}",
                    {"response": session_info_response}
                )
            else:
                self.log_test_result(
                    "Session Info Endpoint",
                    True,
                    "Session info retrieved successfully",
                    {"session_data": session_data}
                )
        else:
            self.log_test_result(
                "Session Info Endpoint",
                False,
                f"Failed to retrieve session info: {session_info_response.get('message')}",
                {"response": session_info_response}
            )
        
        # Test session reset endpoint
        reset_response = self.make_api_request("/session/reset", method="POST")
        
        if reset_response.get("status") == "success":
            reset_data = reset_response.get("data", {})
            
            if "session_count" in reset_data and "max_count" in reset_data:
                self.log_test_result(
                    "Session Reset Endpoint",
                    True,
                    "Session reset successfully",
                    {"reset_data": reset_data}
                )
            else:
                self.log_test_result(
                    "Session Reset Response",
                    False,
                    "Session reset response missing required fields",
                    {"response": reset_response}
                )
        else:
            self.log_test_result(
                "Session Reset Endpoint",
                False,
                f"Failed to reset session: {reset_response.get('message')}",
                {"response": reset_response}
            )
    
    def test_alert_system_integration(self):
        """Test alert system endpoints."""
        logger.info("🔍 Testing alert system integration...")
        
        # Test active alerts endpoint
        active_alerts_response = self.make_api_request("/alerts/active")
        
        if active_alerts_response.get("status") == "success":
            data = active_alerts_response.get("data", {})
            
            if "summaries" in data and "count" in data:
                summaries = data.get("summaries", [])
                count = data.get("count", 0)
                
                self.log_test_result(
                    "Active Alerts Endpoint",
                    True,
                    f"Retrieved {count} active alerts",
                    {"alert_count": count, "has_summaries": len(summaries) > 0}
                )
                
                # Test alert structure if alerts exist
                if summaries:
                    first_alert = summaries[0]
                    expected_alert_fields = ["transaction_id", "priority", "risk_category"]
                    
                    missing_alert_fields = [
                        field for field in expected_alert_fields 
                        if field not in first_alert
                    ]
                    
                    if missing_alert_fields:
                        self.log_test_result(
                            "Alert Structure",
                            False,
                            f"Missing alert fields: {missing_alert_fields}",
                            {"first_alert": first_alert}
                        )
                    else:
                        self.log_test_result(
                            "Alert Structure",
                            True,
                            "Alert summaries have correct structure",
                            {"sample_alert": first_alert}
                        )
            else:
                self.log_test_result(
                    "Active Alerts Response Structure",
                    False,
                    "Missing required fields in active alerts response",
                    {"response": active_alerts_response}
                )
        else:
            self.log_test_result(
                "Active Alerts Endpoint",
                False,
                f"Failed to retrieve active alerts: {active_alerts_response.get('message')}",
                {"response": active_alerts_response}
            )
        
        # Test alert statistics endpoint
        stats_response = self.make_api_request("/alerts/statistics")
        
        if stats_response.get("status") == "success":
            stats_data = stats_response.get("data", {})
            
            expected_stats_fields = ["total_count", "active_count", "dismissed_count"]
            missing_stats_fields = [
                field for field in expected_stats_fields 
                if field not in stats_data
            ]
            
            if missing_stats_fields:
                self.log_test_result(
                    "Alert Statistics Structure",
                    False,
                    f"Missing alert statistics fields: {missing_stats_fields}",
                    {"response": stats_response}
                )
            else:
                self.log_test_result(
                    "Alert Statistics Endpoint",
                    True,
                    "Alert statistics retrieved successfully",
                    {"stats": stats_data}
                )
        else:
            self.log_test_result(
                "Alert Statistics Endpoint",
                False,
                f"Failed to retrieve alert statistics: {stats_response.get('message')}",
                {"response": stats_response}
            )
    
    def test_dashboard_connectivity(self):
        """Test dashboard connectivity (basic HTTP check)."""
        logger.info("🔍 Testing dashboard connectivity...")
        
        try:
            response = requests.get(self.dashboard_url, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                # Check if response contains Streamlit indicators
                content = response.text.lower()
                streamlit_indicators = ["streamlit", "st-", "data-testid"]
                
                has_streamlit_content = any(indicator in content for indicator in streamlit_indicators)
                
                if has_streamlit_content:
                    self.log_test_result(
                        "Dashboard Connectivity",
                        True,
                        "Dashboard is accessible and serving Streamlit content",
                        {"status_code": response.status_code, "content_length": len(content)}
                    )
                else:
                    self.log_test_result(
                        "Dashboard Content",
                        False,
                        "Dashboard accessible but may not be serving Streamlit content",
                        {"status_code": response.status_code, "content_preview": content[:200]}
                    )
            else:
                self.log_test_result(
                    "Dashboard Connectivity",
                    False,
                    f"Dashboard returned status code {response.status_code}",
                    {"status_code": response.status_code}
                )
                
        except requests.exceptions.ConnectionError:
            self.log_test_result(
                "Dashboard Connectivity",
                False,
                "Cannot connect to dashboard - service may not be running",
                {"dashboard_url": self.dashboard_url}
            )
        except requests.exceptions.Timeout:
            self.log_test_result(
                "Dashboard Connectivity",
                False,
                "Dashboard connection timed out",
                {"timeout": TEST_TIMEOUT}
            )
        except Exception as e:
            self.log_test_result(
                "Dashboard Connectivity",
                False,
                f"Unexpected error connecting to dashboard: {str(e)}",
                {"error": str(e)}
            )
    
    def test_error_handling(self):
        """Test error handling for invalid requests."""
        logger.info("🔍 Testing error handling...")
        
        # Test invalid transaction ID
        invalid_explain_response = self.make_api_request(
            "/explain/INVALID_TRANSACTION_ID",
            method="POST",
            data={"force_ai": False}
        )
        
        # Should return 404 or appropriate error
        if invalid_explain_response.get("status") == "error":
            self.log_test_result(
                "Invalid Transaction ID Handling",
                True,
                "API correctly handles invalid transaction ID",
                {"response": invalid_explain_response}
            )
        else:
            self.log_test_result(
                "Invalid Transaction ID Handling",
                False,
                "API should return error for invalid transaction ID",
                {"response": invalid_explain_response}
            )
        
        # Test invalid endpoint
        invalid_endpoint_response = self.make_api_request("/nonexistent-endpoint")
        
        if invalid_endpoint_response.get("status") == "error":
            self.log_test_result(
                "Invalid Endpoint Handling",
                True,
                "API correctly handles invalid endpoints",
                {"response": invalid_endpoint_response}
            )
        else:
            self.log_test_result(
                "Invalid Endpoint Handling",
                False,
                "API should return error for invalid endpoints",
                {"response": invalid_endpoint_response}
            )
    
    def run_all_tests(self):
        """Run all integration tests."""
        logger.info("🚀 Starting TRINETRA AI API-Dashboard Integration Tests")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all test methods
        test_methods = [
            self.test_api_connectivity,
            self.test_transactions_endpoint,
            self.test_suspicious_and_fraud_endpoints,
            self.test_stats_endpoint,
            self.test_explanation_endpoint,
            self.test_query_endpoint,
            self.test_session_management,
            self.test_alert_system_integration,
            self.test_dashboard_connectivity,
            self.test_error_handling
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"Test method {test_method.__name__} failed with exception: {str(e)}")
                self.log_test_result(
                    test_method.__name__,
                    False,
                    f"Test failed with exception: {str(e)}",
                    {"exception": str(e)}
                )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate test summary
        self.generate_test_summary(duration)
    
    def generate_test_summary(self, duration: float):
        """Generate and display test summary."""
        logger.info("=" * 60)
        logger.info("🏁 TRINETRA AI Integration Test Summary")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["passed"]])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"📊 Test Results:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   ✅ Passed: {passed_tests}")
        logger.info(f"   ❌ Failed: {failed_tests}")
        logger.info(f"   📈 Success Rate: {success_rate:.1f}%")
        logger.info(f"   ⏱️ Duration: {duration:.2f} seconds")
        
        if failed_tests > 0:
            logger.info("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    logger.info(f"   - {result['test_name']}: {result['message']}")
        
        logger.info("\n" + "=" * 60)
        
        # Return summary for external use
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "duration": duration,
            "detailed_results": self.test_results
        }


def main():
    """Main function to run integration tests."""
    tester = APIIntegrationTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    if summary["failed_tests"] == 0:
        logger.info("🎉 All integration tests passed!")
        exit(0)
    else:
        logger.error(f"💥 {summary['failed_tests']} tests failed!")
        exit(1)


if __name__ == "__main__":
    main()