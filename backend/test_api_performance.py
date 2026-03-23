"""
API Performance Testing for TRINETRA AI

This module tests API response times to ensure all endpoints meet the
NFR-1 requirement: API responses within 1 second.

Task: 12.4 Performance Testing - Test API response times (<1 second)

Author: TRINETRA AI Team
Date: 2024
"""

import pytest
import time
import statistics
from typing import Dict, Tuple
import logging
from fastapi.testclient import TestClient
from backend.api import app
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAPIPerformance:
    """Test API response times meet performance requirements."""
    
    PERFORMANCE_THRESHOLD = 1.0  # NFR-1: API responses within 1 second
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create FastAPI test client and initialize system."""
        logger.info("✅ Creating FastAPI test client")
        
        # Initialize the system before creating the client
        from backend.api import initialize_system
        try:
            initialize_system()
            logger.info("✅ System initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️  System initialization had issues: {e}")
            # Continue anyway - some tests may still work
        
        return TestClient(app)
    
    def measure_response_time(self, client: TestClient, method: str, endpoint: str, **kwargs) -> Tuple[float, any]:
        """
        Measure response time for an API endpoint.
        
        Args:
            client: FastAPI TestClient
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Tuple of (response_time, response_object)
        """
        start_time = time.time()
        
        if method.upper() == "GET":
            response = client.get(endpoint, **kwargs)
        elif method.upper() == "POST":
            response = client.post(endpoint, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        return response_time, response
    
    def run_multiple_measurements(self, client: TestClient, method: str, endpoint: str, runs: int = 5, **kwargs) -> Dict:
        """
        Run multiple measurements and calculate statistics.
        
        Args:
            client: FastAPI TestClient
            method: HTTP method
            endpoint: API endpoint
            runs: Number of test runs
            **kwargs: Additional arguments for requests
            
        Returns:
            Dictionary with timing statistics
        """
        times = []
        
        for i in range(runs):
            response_time, response = self.measure_response_time(client, method, endpoint, **kwargs)
            
            # Verify response is successful
            assert response.status_code == 200, f"Request failed with status {response.status_code}"
            
            times.append(response_time)
        
        return {
            'min': min(times),
            'max': max(times),
            'avg': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'all_times': times
        }
    
    def test_01_root_endpoint_performance(self, client):
        """Test root endpoint (/) response time."""
        logger.info("Testing root endpoint performance...")
        
        stats = self.run_multiple_measurements(client, "GET", "/", runs=3)
        
        logger.info(f"Root endpoint - Avg: {stats['avg']:.3f}s, Min: {stats['min']:.3f}s, Max: {stats['max']:.3f}s")
        
        # All measurements should be under threshold
        assert stats['max'] < self.PERFORMANCE_THRESHOLD, \
            f"Root endpoint max response time {stats['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
        
        # Average should be well under threshold
        assert stats['avg'] < self.PERFORMANCE_THRESHOLD * 0.5, \
            f"Root endpoint avg response time {stats['avg']:.3f}s should be < {self.PERFORMANCE_THRESHOLD * 0.5}s"
    
    def test_02_transactions_endpoint_performance(self, client):
        """Test /transactions endpoint response time with different limits."""
        logger.info("Testing /transactions endpoint performance...")
        
        # Test with small limit
        stats_small = self.run_multiple_measurements(client, "GET", "/transactions?limit=10&offset=0", runs=3)
        logger.info(f"/transactions (limit=10) - Avg: {stats_small['avg']:.3f}s, Max: {stats_small['max']:.3f}s")
        
        assert stats_small['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/transactions (limit=10) max time {stats_small['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
        
        # Test with medium limit
        stats_medium = self.run_multiple_measurements(client, "GET", "/transactions?limit=100&offset=0", runs=3)
        logger.info(f"/transactions (limit=100) - Avg: {stats_medium['avg']:.3f}s, Max: {stats_medium['max']:.3f}s")
        
        assert stats_medium['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/transactions (limit=100) max time {stats_medium['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
        
        # Test with large limit
        stats_large = self.run_multiple_measurements(client, "GET", "/transactions?limit=1000&offset=0", runs=2)
        logger.info(f"/transactions (limit=1000) - Avg: {stats_large['avg']:.3f}s, Max: {stats_large['max']:.3f}s")
        
        assert stats_large['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/transactions (limit=1000) max time {stats_large['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
    
    def test_03_suspicious_endpoint_performance(self, client):
        """Test /suspicious endpoint response time."""
        logger.info("Testing /suspicious endpoint performance...")
        
        stats = self.run_multiple_measurements(client, "GET", "/suspicious", runs=3)
        
        logger.info(f"/suspicious - Avg: {stats['avg']:.3f}s, Min: {stats['min']:.3f}s, Max: {stats['max']:.3f}s")
        
        assert stats['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/suspicious max response time {stats['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
    
    def test_04_fraud_endpoint_performance(self, client):
        """Test /fraud endpoint response time."""
        logger.info("Testing /fraud endpoint performance...")
        
        stats = self.run_multiple_measurements(client, "GET", "/fraud", runs=3)
        
        logger.info(f"/fraud - Avg: {stats['avg']:.3f}s, Min: {stats['min']:.3f}s, Max: {stats['max']:.3f}s")
        
        assert stats['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/fraud max response time {stats['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
    
    def test_05_stats_endpoint_performance(self, client):
        """Test /stats endpoint response time."""
        logger.info("Testing /stats endpoint performance...")
        
        stats = self.run_multiple_measurements(client, "GET", "/stats", runs=3)
        
        logger.info(f"/stats - Avg: {stats['avg']:.3f}s, Min: {stats['min']:.3f}s, Max: {stats['max']:.3f}s")
        
        assert stats['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/stats max response time {stats['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
    
    def test_06_explain_endpoint_performance(self, client):
        """Test /explain/{transaction_id} endpoint response time."""
        logger.info("Testing /explain endpoint performance...")
        
        # First, get a valid transaction ID
        response = client.get("/transactions?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        transactions = data['data']['transactions']
        
        if not transactions:
            pytest.skip("No transactions available for testing")
        
        transaction_id = transactions[0]['transaction_id']
        
        # Test with force_ai=False (uses fallback, should be fast)
        stats = self.run_multiple_measurements(
            client,
            "POST",
            f"/explain/{transaction_id}",
            runs=3,
            json={"force_ai": False}
        )
        
        logger.info(f"/explain (fallback) - Avg: {stats['avg']:.3f}s, Min: {stats['min']:.3f}s, Max: {stats['max']:.3f}s")
        
        assert stats['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/explain max response time {stats['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
    
    def test_07_query_endpoint_performance(self, client):
        """Test /query endpoint response time."""
        logger.info("Testing /query endpoint performance...")
        
        test_queries = [
            "What is the total number of transactions?",
            "How many fraud cases are there?"
        ]
        
        all_times = []
        
        for query in test_queries:
            stats = self.run_multiple_measurements(
                client,
                "POST",
                "/query",
                runs=2,
                json={"query": query}
            )
            
            logger.info(f"/query ('{query[:30]}...') - Avg: {stats['avg']:.3f}s, Max: {stats['max']:.3f}s")
            
            all_times.extend(stats['all_times'])
            
            assert stats['max'] < self.PERFORMANCE_THRESHOLD, \
                f"/query max response time {stats['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
        
        # Check overall average
        overall_avg = statistics.mean(all_times)
        logger.info(f"/query overall average: {overall_avg:.3f}s")
        
        assert overall_avg < self.PERFORMANCE_THRESHOLD, \
            f"/query overall avg {overall_avg:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
    
    def test_08_session_endpoints_performance(self, client):
        """Test session management endpoints response time."""
        logger.info("Testing session endpoints performance...")
        
        # Test /session/info
        stats_info = self.run_multiple_measurements(client, "GET", "/session/info", runs=3)
        logger.info(f"/session/info - Avg: {stats_info['avg']:.3f}s, Max: {stats_info['max']:.3f}s")
        
        assert stats_info['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/session/info max time {stats_info['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
        
        # Test /session/reset
        stats_reset = self.run_multiple_measurements(client, "POST", "/session/reset", runs=3)
        logger.info(f"/session/reset - Avg: {stats_reset['avg']:.3f}s, Max: {stats_reset['max']:.3f}s")
        
        assert stats_reset['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/session/reset max time {stats_reset['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
    
    def test_09_alert_endpoints_performance(self, client):
        """Test alert-related endpoints response time."""
        logger.info("Testing alert endpoints performance...")
        
        # Test /alerts
        stats_alerts = self.run_multiple_measurements(client, "GET", "/alerts", runs=3)
        logger.info(f"/alerts - Avg: {stats_alerts['avg']:.3f}s, Max: {stats_alerts['max']:.3f}s")
        
        assert stats_alerts['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/alerts max time {stats_alerts['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
        
        # Test /alerts/statistics
        stats_alert_stats = self.run_multiple_measurements(client, "GET", "/alerts/statistics", runs=3)
        logger.info(f"/alerts/statistics - Avg: {stats_alert_stats['avg']:.3f}s, Max: {stats_alert_stats['max']:.3f}s")
        
        assert stats_alert_stats['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/alerts/statistics max time {stats_alert_stats['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
        
        # Test /alerts/summaries
        stats_summaries = self.run_multiple_measurements(client, "GET", "/alerts/summaries", runs=3)
        logger.info(f"/alerts/summaries - Avg: {stats_summaries['avg']:.3f}s, Max: {stats_summaries['max']:.3f}s")
        
        assert stats_summaries['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/alerts/summaries max time {stats_summaries['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
        
        # Test /alerts/active
        stats_active = self.run_multiple_measurements(client, "GET", "/alerts/active", runs=3)
        logger.info(f"/alerts/active - Avg: {stats_active['avg']:.3f}s, Max: {stats_active['max']:.3f}s")
        
        assert stats_active['max'] < self.PERFORMANCE_THRESHOLD, \
            f"/alerts/active max time {stats_active['max']:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
    
    def test_10_concurrent_requests_performance(self, client):
        """Test API performance under concurrent load."""
        logger.info("Testing concurrent requests performance...")
        
        def make_request(endpoint: str) -> float:
            """Make a single request and return response time."""
            response_time, response = self.measure_response_time(client, "GET", endpoint)
            assert response.status_code == 200
            return response_time
        
        # Test concurrent requests to different endpoints
        endpoints = [
            "/stats",
            "/transactions?limit=10",
            "/suspicious",
            "/fraud",
            "/session/info"
        ]
        
        # Run 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, endpoint) for endpoint in endpoints]
            
            # Collect results
            response_times = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze concurrent performance
        max_time = max(response_times)
        avg_time = statistics.mean(response_times)
        
        logger.info(f"Concurrent requests - Count: {len(response_times)}, Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")
        
        # Under concurrent load, allow slightly higher threshold (1.5x)
        concurrent_threshold = self.PERFORMANCE_THRESHOLD * 1.5
        
        assert max_time < concurrent_threshold, \
            f"Concurrent max time {max_time:.3f}s exceeds {concurrent_threshold}s"
        
        assert avg_time < self.PERFORMANCE_THRESHOLD, \
            f"Concurrent avg time {avg_time:.3f}s exceeds {self.PERFORMANCE_THRESHOLD}s"
    
    def test_11_generate_performance_report(self, client):
        """Generate comprehensive performance report for all endpoints."""
        logger.info("Generating comprehensive performance report...")
        
        # Define all endpoints to test
        test_cases = [
            ("GET", "/", "Root"),
            ("GET", "/transactions?limit=10", "Transactions (10)"),
            ("GET", "/transactions?limit=100", "Transactions (100)"),
            ("GET", "/suspicious", "Suspicious"),
            ("GET", "/fraud", "Fraud"),
            ("GET", "/stats", "Statistics"),
            ("GET", "/session/info", "Session Info"),
            ("GET", "/alerts", "Alerts"),
            ("GET", "/alerts/statistics", "Alert Statistics"),
            ("GET", "/alerts/summaries", "Alert Summaries"),
            ("GET", "/alerts/active", "Active Alerts"),
        ]
        
        report = []
        report.append("\n" + "="*80)
        report.append("API PERFORMANCE TEST REPORT")
        report.append("="*80)
        report.append(f"Performance Threshold: {self.PERFORMANCE_THRESHOLD}s (NFR-1 Requirement)")
        report.append("="*80)
        report.append(f"{'Endpoint':<40} {'Avg (s)':<10} {'Max (s)':<10} {'Status':<10}")
        report.append("-"*80)
        
        all_passed = True
        
        for method, endpoint, name in test_cases:
            try:
                stats = self.run_multiple_measurements(client, method, endpoint, runs=3)
                
                status = "✅ PASS" if stats['max'] < self.PERFORMANCE_THRESHOLD else "❌ FAIL"
                if stats['max'] >= self.PERFORMANCE_THRESHOLD:
                    all_passed = False
                
                report.append(f"{name:<40} {stats['avg']:<10.3f} {stats['max']:<10.3f} {status:<10}")
                
            except Exception as e:
                report.append(f"{name:<40} {'ERROR':<10} {'ERROR':<10} {'❌ ERROR':<10}")
                logger.error(f"Error testing {name}: {e}")
                all_passed = False
        
        report.append("="*80)
        report.append(f"Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        report.append("="*80)
        
        # Print report
        for line in report:
            logger.info(line)
        
        # Save report to file
        report_path = "backend/api_performance_report.txt"
        with open(report_path, "w") as f:
            f.write("\n".join(report))
        
        logger.info(f"\n📊 Performance report saved to: {report_path}")
        
        assert all_passed, "Some endpoints failed to meet performance requirements"


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s", "--tb=short"])
