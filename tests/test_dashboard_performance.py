#!/usr/bin/env python3
"""
Performance Tests for TRINETRA AI Dashboard Load Times

This module tests the dashboard load time performance requirement:
- NFR-1: Dashboard loads within 3 seconds

**Validates: Requirements NFR-1 (Performance)**

Author: TRINETRA AI Team
Date: 2024
"""

import time
import sys
import subprocess
import requests
from pathlib import Path
import pytest
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"  # Use 127.0.0.1 instead of localhost for better performance on Windows
DASHBOARD_URL = "http://localhost:8501"
MAX_LOAD_TIME = 3.0  # seconds (NFR-1 requirement)
API_STARTUP_TIMEOUT = 30  # seconds to wait for API to start
DASHBOARD_STARTUP_TIMEOUT = 30  # seconds to wait for dashboard to start


class TestDashboardPerformance:
    """Test dashboard load time performance requirements."""
    
    @pytest.fixture(scope="class", autouse=True)
    def check_api_server(self):
        """Check if API server is running, skip tests if not."""
        logger.info("Checking if FastAPI server is running...")
        
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ FastAPI server is running and ready")
                yield
            else:
                pytest.skip("FastAPI server is not responding correctly")
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ FastAPI server is not running: {e}")
            logger.info("\nTo run these tests, please start the system first:")
            logger.info("  python main.py")
            logger.info("\nOr start just the API server:")
            logger.info("  python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000")
            pytest.skip("FastAPI server is not running. Please start the system first.")
    
    def test_api_endpoint_response_times(self):
        """
        Test that all API endpoints respond within acceptable time limits.
        
        **Validates: NFR-1 Performance - API responses within 1 second**
        """
        logger.info("\n" + "="*60)
        logger.info("Testing API Endpoint Response Times")
        logger.info("="*60)
        
        endpoints = [
            ("/", "Root endpoint"),
            ("/transactions?limit=50", "Transactions endpoint"),
            ("/suspicious", "Suspicious transactions"),
            ("/fraud", "Fraud transactions"),
            ("/stats", "Statistics endpoint"),
            ("/alerts/active", "Active alerts"),
            ("/session/info", "Session info")
        ]
        
        results = []
        all_passed = True
        
        for endpoint, description in endpoints:
            url = f"{API_BASE_URL}{endpoint}"
            
            # Measure response time
            start_time = time.time()
            try:
                response = requests.get(url, timeout=5)
                response_time = time.time() - start_time
                
                # Check if response is successful
                if response.status_code == 200:
                    status = "✅ PASS" if response_time < 1.0 else "⚠️ SLOW"
                    if response_time >= 1.0:
                        all_passed = False
                else:
                    status = "❌ FAIL"
                    all_passed = False
                
                results.append({
                    "endpoint": endpoint,
                    "description": description,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "status": status
                })
                
                logger.info(f"{status} {description}: {response_time:.3f}s (Status: {response.status_code})")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ FAIL {description}: {str(e)}")
                all_passed = False
                results.append({
                    "endpoint": endpoint,
                    "description": description,
                    "response_time": None,
                    "status_code": None,
                    "status": "❌ FAIL",
                    "error": str(e)
                })
        
        # Summary
        logger.info("\n" + "-"*60)
        logger.info("API Performance Summary:")
        logger.info("-"*60)
        
        successful_requests = [r for r in results if r.get("response_time") is not None]
        if successful_requests:
            avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
            max_response_time = max(r["response_time"] for r in successful_requests)
            min_response_time = min(r["response_time"] for r in successful_requests)
            
            logger.info(f"Average Response Time: {avg_response_time:.3f}s")
            logger.info(f"Max Response Time: {max_response_time:.3f}s")
            logger.info(f"Min Response Time: {min_response_time:.3f}s")
            logger.info(f"Endpoints Tested: {len(endpoints)}")
            logger.info(f"Successful: {len(successful_requests)}")
            logger.info(f"Failed: {len(endpoints) - len(successful_requests)}")
        
        # Assert all endpoints respond within 1 second
        assert all_passed, "Some API endpoints exceeded 1 second response time or failed"
    
    def test_dashboard_data_loading_performance(self):
        """
        Test the time it takes to load all dashboard data from API.
        
        This simulates the dashboard's initial data loading process.
        
        **Validates: NFR-1 Performance - Dashboard data loads within 3 seconds**
        """
        logger.info("\n" + "="*60)
        logger.info("Testing Dashboard Data Loading Performance")
        logger.info("="*60)
        
        # Simulate dashboard data loading sequence
        data_loading_steps = [
            ("/stats", "Load KPI statistics"),
            ("/alerts/active", "Load active alerts"),
            ("/transactions?limit=50", "Load transaction table"),
            ("/session/info", "Load session info")
        ]
        
        total_start_time = time.time()
        step_times = []
        
        for endpoint, description in data_loading_steps:
            url = f"{API_BASE_URL}{endpoint}"
            
            step_start = time.time()
            try:
                response = requests.get(url, timeout=5)
                step_time = time.time() - step_start
                step_times.append(step_time)
                
                logger.info(f"  {description}: {step_time:.3f}s (Status: {response.status_code})")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"  ❌ {description}: Failed - {str(e)}")
                pytest.fail(f"Data loading step failed: {description}")
        
        total_load_time = time.time() - total_start_time
        
        # Summary
        logger.info("\n" + "-"*60)
        logger.info("Dashboard Data Loading Summary:")
        logger.info("-"*60)
        logger.info(f"Total Load Time: {total_load_time:.3f}s")
        logger.info(f"Average Step Time: {sum(step_times)/len(step_times):.3f}s")
        logger.info(f"Slowest Step: {max(step_times):.3f}s")
        logger.info(f"Fastest Step: {min(step_times):.3f}s")
        logger.info(f"Target: < {MAX_LOAD_TIME}s")
        
        if total_load_time < MAX_LOAD_TIME:
            logger.info(f"✅ PASS: Dashboard data loads in {total_load_time:.3f}s (under {MAX_LOAD_TIME}s)")
        else:
            logger.warning(f"⚠️ FAIL: Dashboard data loads in {total_load_time:.3f}s (exceeds {MAX_LOAD_TIME}s)")
        
        # Assert total load time is under 3 seconds
        assert total_load_time < MAX_LOAD_TIME, \
            f"Dashboard data loading took {total_load_time:.3f}s, exceeds {MAX_LOAD_TIME}s requirement"
    
    def test_concurrent_api_requests_performance(self):
        """
        Test API performance under concurrent requests (simulating multiple dashboard sections loading).
        
        **Validates: NFR-1 Performance - System handles concurrent requests efficiently**
        """
        logger.info("\n" + "="*60)
        logger.info("Testing Concurrent API Requests Performance")
        logger.info("="*60)
        
        import concurrent.futures
        
        # Endpoints to test concurrently
        endpoints = [
            "/stats",
            "/alerts/active",
            "/transactions?limit=50",
            "/suspicious",
            "/session/info"
        ]
        
        def fetch_endpoint(endpoint):
            """Fetch a single endpoint and return timing info."""
            url = f"{API_BASE_URL}{endpoint}"
            start_time = time.time()
            try:
                response = requests.get(url, timeout=5)
                elapsed = time.time() - start_time
                return {
                    "endpoint": endpoint,
                    "success": response.status_code == 200,
                    "time": elapsed,
                    "status_code": response.status_code
                }
            except requests.exceptions.RequestException as e:
                elapsed = time.time() - start_time
                return {
                    "endpoint": endpoint,
                    "success": False,
                    "time": elapsed,
                    "error": str(e)
                }
        
        # Execute concurrent requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(fetch_endpoint, endpoints))
        total_time = time.time() - start_time
        
        # Analyze results
        logger.info("\nConcurrent Request Results:")
        for result in results:
            status = "✅" if result["success"] else "❌"
            logger.info(f"  {status} {result['endpoint']}: {result['time']:.3f}s")
        
        successful_requests = [r for r in results if r["success"]]
        avg_time = sum(r["time"] for r in successful_requests) / len(successful_requests) if successful_requests else 0
        
        logger.info("\n" + "-"*60)
        logger.info("Concurrent Request Summary:")
        logger.info("-"*60)
        logger.info(f"Total Concurrent Execution Time: {total_time:.3f}s")
        logger.info(f"Average Individual Request Time: {avg_time:.3f}s")
        logger.info(f"Successful Requests: {len(successful_requests)}/{len(endpoints)}")
        logger.info(f"Target: < {MAX_LOAD_TIME}s")
        
        if total_time < MAX_LOAD_TIME:
            logger.info(f"✅ PASS: Concurrent requests completed in {total_time:.3f}s")
        else:
            logger.warning(f"⚠️ FAIL: Concurrent requests took {total_time:.3f}s (exceeds {MAX_LOAD_TIME}s)")
        
        # Assert all requests succeeded
        assert len(successful_requests) == len(endpoints), \
            f"Some concurrent requests failed: {len(endpoints) - len(successful_requests)} failures"
        
        # Assert total time is reasonable (should be faster than sequential)
        assert total_time < MAX_LOAD_TIME, \
            f"Concurrent requests took {total_time:.3f}s, exceeds {MAX_LOAD_TIME}s requirement"
    
    def test_large_dataset_query_performance(self):
        """
        Test API performance with larger dataset queries.
        
        **Validates: NFR-1 Performance - System handles larger queries efficiently**
        """
        logger.info("\n" + "="*60)
        logger.info("Testing Large Dataset Query Performance")
        logger.info("="*60)
        
        query_sizes = [50, 100, 200, 500]
        results = []
        
        for limit in query_sizes:
            url = f"{API_BASE_URL}/transactions?limit={limit}"
            
            start_time = time.time()
            try:
                response = requests.get(url, timeout=10)
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    actual_count = len(data.get("data", {}).get("transactions", []))
                    
                    status = "✅" if elapsed < 2.0 else "⚠️"
                    logger.info(f"  {status} Limit {limit}: {elapsed:.3f}s (returned {actual_count} records)")
                    
                    results.append({
                        "limit": limit,
                        "time": elapsed,
                        "count": actual_count,
                        "success": True
                    })
                else:
                    logger.error(f"  ❌ Limit {limit}: Failed with status {response.status_code}")
                    results.append({
                        "limit": limit,
                        "time": elapsed,
                        "success": False
                    })
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"  ❌ Limit {limit}: {str(e)}")
                results.append({
                    "limit": limit,
                    "success": False,
                    "error": str(e)
                })
        
        # Summary
        successful_results = [r for r in results if r["success"]]
        if successful_results:
            logger.info("\n" + "-"*60)
            logger.info("Large Dataset Query Summary:")
            logger.info("-"*60)
            logger.info(f"Queries Tested: {len(query_sizes)}")
            logger.info(f"Successful: {len(successful_results)}")
            logger.info(f"Average Time: {sum(r['time'] for r in successful_results)/len(successful_results):.3f}s")
            logger.info(f"Max Time: {max(r['time'] for r in successful_results):.3f}s")
        
        # Assert all queries succeeded and were reasonably fast
        assert len(successful_results) == len(query_sizes), "Some large dataset queries failed"
        assert all(r["time"] < 2.0 for r in successful_results), \
            "Some large dataset queries exceeded 2 second threshold"


def main():
    """Run performance tests and generate report."""
    logger.info("\n" + "="*70)
    logger.info("TRINETRA AI - Dashboard Performance Test Suite")
    logger.info("="*70)
    logger.info("\nTesting NFR-1: Dashboard loads within 3 seconds")
    logger.info("\nStarting performance tests...\n")
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s",  # Show print statements
        "--color=yes"
    ])
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
