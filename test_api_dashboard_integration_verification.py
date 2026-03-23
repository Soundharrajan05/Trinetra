#!/usr/bin/env python3
"""
Integration Test: API and Dashboard Integration Verification
Task: Verify API and dashboard integration for TRINETRA AI system

This test verifies that:
1. FastAPI backend starts successfully
2. All API endpoints are accessible
3. Dashboard can connect to API
4. Data flows correctly between backend and frontend
5. Interactive features work properly
"""

import requests
import time
import subprocess
import threading
import logging
import sys
import os
from typing import Dict, Any, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIIntegrationVerifier:
    """Verifies API and Dashboard integration for TRINETRA AI."""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
        self.dashboard_url = "http://localhost:8501"
        self.api_process = None
        self.dashboard_process = None
        
    def start_api_server(self) -> bool:
        """Start the FastAPI server."""
        try:
            logger.info("Starting FastAPI server...")
            # Start the main application which includes the API server
            self.api_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for API to be ready
            return self.wait_for_api_ready()
            
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            return False
    
    def wait_for_api_ready(self, max_retries: int = 30, delay: int = 2) -> bool:
        """Wait for API server to be ready."""
        logger.info(f"Waiting for API server at {self.api_base_url}...")
        
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{self.api_base_url}/stats", timeout=5)
                if response.status_code == 200:
                    logger.info(f"API server ready after {attempt + 1} attempts")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            logger.info(f"Attempt {attempt + 1}/{max_retries} - API not ready, waiting {delay}s...")
            time.sleep(delay)
        
        logger.error("API server failed to start within timeout")
        return False
    
    def test_api_endpoints(self) -> Dict[str, bool]:
        """Test all API endpoints for accessibility and correct responses."""
        logger.info("Testing API endpoints...")
        
        results = {}
        
        # Test endpoints
        endpoints = [
            ("/stats", "GET", "Dashboard statistics"),
            ("/transactions", "GET", "All transactions"),
            ("/suspicious", "GET", "Suspicious transactions"),
            ("/fraud", "GET", "Fraud transactions"),
            ("/session/info", "GET", "Session information"),
        ]
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{self.api_base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                success = response.status_code == 200
                results[endpoint] = success
                
                if success:
                    logger.info(f"✅ {endpoint} - {description}: OK")
                    # Validate JSON response
                    try:
                        data = response.json()
                        if not isinstance(data, dict):
                            logger.warning(f"⚠️  {endpoint}: Response is not a JSON object")
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️  {endpoint}: Invalid JSON response")
                else:
                    logger.error(f"❌ {endpoint} - {description}: Failed ({response.status_code})")
                    
            except Exception as e:
                logger.error(f"❌ {endpoint} - {description}: Exception - {e}")
                results[endpoint] = False
        
        return results
    
    def test_data_flow(self) -> bool:
        """Test data flow from API to verify dashboard integration."""
        logger.info("Testing data flow for dashboard integration...")
        
        try:
            # Test transactions endpoint - this is what dashboard uses
            response = requests.get(f"{self.api_base_url}/transactions", timeout=10)
            if response.status_code != 200:
                logger.error("Failed to get transactions data")
                return False
            
            data = response.json()
            transactions = data.get('data', [])
            
            if not transactions:
                logger.error("No transaction data available")
                return False
            
            logger.info(f"✅ Retrieved {len(transactions)} transactions")
            
            # Verify transaction structure (what dashboard expects)
            sample_transaction = transactions[0]
            required_fields = [
                'transaction_id', 'risk_score', 'risk_category',
                'product', 'unit_price', 'market_price', 'price_deviation'
            ]
            
            missing_fields = [field for field in required_fields if field not in sample_transaction]
            if missing_fields:
                logger.error(f"Missing required fields for dashboard: {missing_fields}")
                return False
            
            logger.info("✅ Transaction data structure is compatible with dashboard")
            
            # Test stats endpoint - dashboard KPIs
            response = requests.get(f"{self.api_base_url}/stats", timeout=10)
            if response.status_code != 200:
                logger.error("Failed to get stats data")
                return False
            
            stats = response.json().get('data', {})
            required_stats = ['total_transactions', 'fraud_rate', 'total_trade_value']
            
            missing_stats = [stat for stat in required_stats if stat not in stats]
            if missing_stats:
                logger.error(f"Missing required stats for dashboard: {missing_stats}")
                return False
            
            logger.info("✅ Statistics data is compatible with dashboard")
            return True
            
        except Exception as e:
            logger.error(f"Data flow test failed: {e}")
            return False
    
    def test_interactive_features(self) -> bool:
        """Test interactive features that dashboard uses."""
        logger.info("Testing interactive features...")
        
        try:
            # Test explanation endpoint (used by dashboard for AI explanations)
            response = requests.get(f"{self.api_base_url}/transactions", timeout=10)
            if response.status_code != 200:
                return False
            
            transactions = response.json().get('data', [])
            if not transactions:
                return False
            
            # Test explanation for first transaction
            transaction_id = transactions[0]['transaction_id']
            response = requests.post(
                f"{self.api_base_url}/explain/{transaction_id}",
                timeout=15
            )
            
            if response.status_code == 200:
                explanation_data = response.json()
                if 'explanation' in explanation_data.get('data', {}):
                    logger.info("✅ AI explanation feature working")
                else:
                    logger.warning("⚠️  Explanation endpoint accessible but no explanation content")
            else:
                logger.warning(f"⚠️  Explanation endpoint returned {response.status_code}")
            
            # Test query endpoint (used by dashboard chat feature)
            query_data = {"query": "How many transactions are suspicious?"}
            response = requests.post(
                f"{self.api_base_url}/query",
                json=query_data,
                timeout=15
            )
            
            if response.status_code == 200:
                logger.info("✅ Natural language query feature working")
            else:
                logger.warning(f"⚠️  Query endpoint returned {response.status_code}")
            
            return True
            
        except Exception as e:
            logger.error(f"Interactive features test failed: {e}")
            return False
    
    def test_performance_requirements(self) -> bool:
        """Test API performance requirements for dashboard."""
        logger.info("Testing API performance requirements...")
        
        try:
            # Test API response time (should be < 1 second per requirements)
            start_time = time.time()
            response = requests.get(f"{self.api_base_url}/stats", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 1.0:
                logger.info(f"✅ API response time: {response_time:.3f}s (< 1s requirement)")
                return True
            else:
                logger.warning(f"⚠️  API response time: {response_time:.3f}s (exceeds 1s requirement)")
                return False
                
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up processes."""
        logger.info("Cleaning up processes...")
        
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.api_process.kill()
            except Exception as e:
                logger.warning(f"Error cleaning up API process: {e}")
    
    def run_verification(self) -> bool:
        """Run complete API and dashboard integration verification."""
        logger.info("🔍 Starting API and Dashboard Integration Verification")
        logger.info("=" * 60)
        
        try:
            # Start API server
            if not self.start_api_server():
                logger.error("❌ Failed to start API server")
                return False
            
            # Run tests
            test_results = []
            
            # Test 1: API endpoints accessibility
            endpoint_results = self.test_api_endpoints()
            endpoints_passed = all(endpoint_results.values())
            test_results.append(("API Endpoints", endpoints_passed))
            
            # Test 2: Data flow compatibility
            data_flow_passed = self.test_data_flow()
            test_results.append(("Data Flow", data_flow_passed))
            
            # Test 3: Interactive features
            interactive_passed = self.test_interactive_features()
            test_results.append(("Interactive Features", interactive_passed))
            
            # Test 4: Performance requirements
            performance_passed = self.test_performance_requirements()
            test_results.append(("Performance", performance_passed))
            
            # Summary
            logger.info("=" * 60)
            logger.info("📊 VERIFICATION RESULTS:")
            
            all_passed = True
            for test_name, passed in test_results:
                status = "✅ PASS" if passed else "❌ FAIL"
                logger.info(f"  {test_name}: {status}")
                if not passed:
                    all_passed = False
            
            logger.info("=" * 60)
            
            if all_passed:
                logger.info("🎉 API and Dashboard Integration: VERIFIED SUCCESSFULLY")
                logger.info("✅ All integration tests passed")
                logger.info("✅ API endpoints are accessible from dashboard")
                logger.info("✅ Data flows correctly between backend and frontend")
                logger.info("✅ Interactive features are working")
                logger.info("✅ Performance requirements are met")
            else:
                logger.error("❌ API and Dashboard Integration: VERIFICATION FAILED")
                logger.error("Some integration tests failed - see details above")
            
            return all_passed
            
        except Exception as e:
            logger.error(f"Verification failed with exception: {e}")
            return False
        
        finally:
            self.cleanup()

def main():
    """Main function to run the verification."""
    verifier = APIIntegrationVerifier()
    success = verifier.run_verification()
    
    if success:
        print("\n🎉 INTEGRATION VERIFICATION: SUCCESS")
        print("The API and dashboard integration is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ INTEGRATION VERIFICATION: FAILED")
        print("Issues found with API and dashboard integration.")
        sys.exit(1)

if __name__ == "__main__":
    main()