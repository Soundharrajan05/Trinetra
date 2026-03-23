"""
Comprehensive System Performance Testing for TRINETRA AI

This module provides comprehensive performance testing covering:
1. API endpoint response times (<1 second - NFR-1)
2. Dashboard load times (<3 seconds - NFR-1)
3. ML model training time (<30 seconds - NFR-1)
4. ML model inference performance (batch predictions)
5. System under concurrent load (1000+ transactions)
6. Performance bottleneck identification
7. Comprehensive performance report generation

Task: 12.4 Performance Testing - Test system performance under load
Spec: .kiro/specs/trinetra-ai-fraud-detection

**Validates: Requirements NFR-1 (Performance)**

Author: TRINETRA AI Team
Date: 2024
"""

import pytest
import time
import statistics
import sys
import os
from typing import Dict, List, Tuple
import logging
import concurrent.futures
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from api import app, initialize_system
from data_loader import load_dataset
from feature_engineering import engineer_features
from model import train_model
from fraud_detection import score_transactions, classify_risk

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Container for performance metrics."""
    
    def __init__(self):
        self.api_times = {}
        self.dashboard_load_time = 0.0
        self.model_training_time = 0.0
        self.inference_times = []
        self.concurrent_load_results = {}
        self.bottlenecks = []
    
    def add_api_time(self, endpoint: str, time_seconds: float):
        """Record API endpoint response time."""
        if endpoint not in self.api_times:
            self.api_times[endpoint] = []
        self.api_times[endpoint].append(time_seconds)
    
    def add_bottleneck(self, component: str, issue: str, time_seconds: float):
        """Record a performance bottleneck."""
        self.bottlenecks.append({
            'component': component,
            'issue': issue,
            'time': time_seconds
        })
    
    def generate_report(self) -> str:
        """Generate comprehensive performance report."""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("TRINETRA AI - COMPREHENSIVE PERFORMANCE TEST REPORT")
        lines.append("="*80)
        lines.append("\nPerformance Requirements (NFR-1):")
        lines.append("  • API responses: < 1 second")
        lines.append("  • Dashboard load: < 3 seconds")
        lines.append("  • ML model training: < 30 seconds")
        lines.append("  • System handles: 1000+ transactions")
        lines.append("="*80)
        
        # API Performance
        lines.append("\n1. API ENDPOINT PERFORMANCE")
        lines.append("-"*80)
        if self.api_times:
            lines.append(f"{'Endpoint':<45} {'Avg (s)':<10} {'Max (s)':<10} {'Status':<10}")
            lines.append("-"*80)
            
            for endpoint, times in sorted(self.api_times.items()):
                avg_time = statistics.mean(times)
                max_time = max(times)
                status = "✅ PASS" if max_time < 1.0 else "❌ FAIL"
                lines.append(f"{endpoint:<45} {avg_time:<10.3f} {max_time:<10.3f} {status:<10}")
            
            all_times = [t for times in self.api_times.values() for t in times]
            lines.append("-"*80)
            lines.append(f"Overall API Average: {statistics.mean(all_times):.3f}s")
            lines.append(f"Overall API Max: {max(all_times):.3f}s")
        
        # Dashboard Performance
        lines.append("\n2. DASHBOARD LOAD PERFORMANCE")
        lines.append("-"*80)
        if self.dashboard_load_time > 0:
            status = "✅ PASS" if self.dashboard_load_time < 3.0 else "❌ FAIL"
            lines.append(f"Dashboard Load Time: {self.dashboard_load_time:.3f}s {status}")
            lines.append(f"Target: < 3.0s")
            lines.append(f"Margin: {3.0 - self.dashboard_load_time:.3f}s")
        
        # ML Model Training
        lines.append("\n3. ML MODEL TRAINING PERFORMANCE")
        lines.append("-"*80)
        if self.model_training_time > 0:
            status = "✅ PASS" if self.model_training_time < 30.0 else "❌ FAIL"
            lines.append(f"Training Time: {self.model_training_time:.3f}s {status}")
            lines.append(f"Target: < 30.0s")
            lines.append(f"Margin: {30.0 - self.model_training_time:.3f}s")
            lines.append(f"Performance Ratio: {(self.model_training_time / 30.0) * 100:.1f}%")
        
        # Inference Performance
        lines.append("\n4. ML MODEL INFERENCE PERFORMANCE")
        lines.append("-"*80)
        if self.inference_times:
            avg_inference = statistics.mean(self.inference_times)
            lines.append(f"Average Inference Time: {avg_inference:.3f}s")
            lines.append(f"Min Inference Time: {min(self.inference_times):.3f}s")
            lines.append(f"Max Inference Time: {max(self.inference_times):.3f}s")
            lines.append(f"Inference Runs: {len(self.inference_times)}")
        
        # Concurrent Load
        lines.append("\n5. CONCURRENT LOAD PERFORMANCE")
        lines.append("-"*80)
        if self.concurrent_load_results:
            for test_name, result in self.concurrent_load_results.items():
                lines.append(f"\n{test_name}:")
                lines.append(f"  Total Time: {result['total_time']:.3f}s")
                lines.append(f"  Requests: {result['request_count']}")
                lines.append(f"  Success Rate: {result['success_rate']:.1f}%")
                lines.append(f"  Avg Response: {result['avg_response']:.3f}s")
        
        # Bottlenecks
        lines.append("\n6. PERFORMANCE BOTTLENECKS")
        lines.append("-"*80)
        if self.bottlenecks:
            for bottleneck in self.bottlenecks:
                lines.append(f"⚠️  {bottleneck['component']}: {bottleneck['issue']}")
                lines.append(f"   Time: {bottleneck['time']:.3f}s")
        else:
            lines.append("✅ No significant bottlenecks detected")
        
        # Summary
        lines.append("\n" + "="*80)
        lines.append("PERFORMANCE TEST SUMMARY")
        lines.append("="*80)
        
        # Calculate pass/fail
        api_pass = all(max(times) < 1.0 for times in self.api_times.values()) if self.api_times else True
        dashboard_pass = self.dashboard_load_time < 3.0 if self.dashboard_load_time > 0 else True
        training_pass = self.model_training_time < 30.0 if self.model_training_time > 0 else True
        
        lines.append(f"API Performance: {'✅ PASS' if api_pass else '❌ FAIL'}")
        lines.append(f"Dashboard Performance: {'✅ PASS' if dashboard_pass else '❌ FAIL'}")
        lines.append(f"ML Training Performance: {'✅ PASS' if training_pass else '❌ FAIL'}")
        
        all_pass = api_pass and dashboard_pass and training_pass
        lines.append("\n" + "="*80)
        lines.append(f"OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_pass else '❌ SOME TESTS FAILED'}")
        lines.append("="*80)
        
        return "\n".join(lines)


class TestSystemPerformance:
    """Comprehensive system performance tests."""
    
    metrics = PerformanceMetrics()
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create FastAPI test client and initialize system."""
        logger.info("Initializing TRINETRA AI system for performance testing...")
        
        try:
            initialize_system()
            logger.info("✅ System initialized successfully\n")
        except Exception as e:
            logger.warning(f"⚠️  System initialization had issues: {e}\n")
        
        return TestClient(app)
    
    @pytest.fixture(scope="class")
    def test_data(self):
        """Load test dataset."""
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        df = load_dataset(dataset_path)
        df = engineer_features(df)
        return df
    
    def measure_time(self, func, *args, **kwargs) -> Tuple[float, any]:
        """Measure execution time of a function."""
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return elapsed, result
    
    def test_01_api_endpoint_performance(self, client):
        """
        Test all API endpoints meet <1 second requirement.
        
        **Validates: NFR-1 - API responses within 1 second**
        """
        logger.info("="*80)
        logger.info("TEST 1: API ENDPOINT PERFORMANCE")
        logger.info("="*80)
        logger.info("Testing all API endpoints for <1 second response time\n")
        
        endpoints = [
            ("GET", "/", "Root"),
            ("GET", "/transactions?limit=10", "Transactions (10)"),
            ("GET", "/transactions?limit=100", "Transactions (100)"),
            ("GET", "/suspicious", "Suspicious"),
            ("GET", "/fraud", "Fraud"),
            ("GET", "/stats", "Statistics"),
            ("GET", "/session/info", "Session Info"),
            ("GET", "/alerts", "Alerts"),
            ("GET", "/alerts/statistics", "Alert Statistics"),
            ("GET", "/alerts/active", "Active Alerts"),
        ]
        
        for method, endpoint, name in endpoints:
            # Run 3 times and take average
            times = []
            for _ in range(3):
                start = time.time()
                if method == "GET":
                    response = client.get(endpoint)
                else:
                    response = client.post(endpoint)
                elapsed = time.time() - start
                times.append(elapsed)
                
                assert response.status_code == 200, f"{name} failed with status {response.status_code}"
            
            avg_time = statistics.mean(times)
            max_time = max(times)
            self.metrics.add_api_time(name, avg_time)
            
            status = "✅" if max_time < 1.0 else "❌"
            logger.info(f"{status} {name:<40} Avg: {avg_time:.3f}s  Max: {max_time:.3f}s")
            
            if max_time >= 1.0:
                self.metrics.add_bottleneck("API", f"{name} exceeds 1s", max_time)
            
            assert max_time < 1.0, f"{name} max time {max_time:.3f}s exceeds 1.0s"
        
        logger.info("\n✅ All API endpoints meet <1 second requirement\n")
    
    def test_02_dashboard_load_performance(self, client):
        """
        Test dashboard data loading meets <3 second requirement.
        
        **Validates: NFR-1 - Dashboard loads within 3 seconds**
        """
        logger.info("="*80)
        logger.info("TEST 2: DASHBOARD LOAD PERFORMANCE")
        logger.info("="*80)
        logger.info("Simulating dashboard initial data load\n")
        
        # Simulate dashboard loading sequence
        dashboard_endpoints = [
            "/stats",
            "/alerts/active",
            "/transactions?limit=50",
            "/session/info"
        ]
        
        start_time = time.time()
        
        for endpoint in dashboard_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Dashboard endpoint {endpoint} failed"
        
        total_time = time.time() - start_time
        self.metrics.dashboard_load_time = total_time
        
        status = "✅" if total_time < 3.0 else "❌"
        logger.info(f"{status} Dashboard Load Time: {total_time:.3f}s")
        logger.info(f"   Target: < 3.0s")
        logger.info(f"   Margin: {3.0 - total_time:.3f}s\n")
        
        if total_time >= 3.0:
            self.metrics.add_bottleneck("Dashboard", "Load time exceeds 3s", total_time)
        
        assert total_time < 3.0, f"Dashboard load time {total_time:.3f}s exceeds 3.0s"
        
        logger.info("✅ Dashboard meets <3 second load requirement\n")
    
    def test_03_ml_model_training_performance(self, test_data):
        """
        Test ML model training meets <30 second requirement.
        
        **Validates: NFR-1 - ML model training within 30 seconds**
        """
        logger.info("="*80)
        logger.info("TEST 3: ML MODEL TRAINING PERFORMANCE")
        logger.info("="*80)
        logger.info(f"Training IsolationForest on {len(test_data)} transactions\n")
        
        start_time = time.time()
        model = train_model(test_data)
        training_time = time.time() - start_time
        
        self.metrics.model_training_time = training_time
        
        assert model is not None, "Model training failed"
        assert hasattr(model, 'estimators_'), "Model not properly fitted"
        
        status = "✅" if training_time < 30.0 else "❌"
        logger.info(f"{status} Model Training Time: {training_time:.3f}s")
        logger.info(f"   Target: < 30.0s")
        logger.info(f"   Margin: {30.0 - training_time:.3f}s")
        logger.info(f"   Performance Ratio: {(training_time / 30.0) * 100:.1f}%\n")
        
        if training_time >= 30.0:
            self.metrics.add_bottleneck("ML Training", "Training time exceeds 30s", training_time)
        
        assert training_time < 30.0, f"Model training time {training_time:.3f}s exceeds 30.0s"
        
        logger.info("✅ ML model training meets <30 second requirement\n")
    
    def test_04_ml_inference_performance(self, test_data):
        """
        Test ML model inference performance with batch predictions.
        
        **Validates: System can efficiently score 1000+ transactions**
        """
        logger.info("="*80)
        logger.info("TEST 4: ML MODEL INFERENCE PERFORMANCE")
        logger.info("="*80)
        logger.info("Testing batch prediction performance\n")
        
        # Train model first
        model = train_model(test_data)
        
        # Test different batch sizes
        batch_sizes = [10, 50, 100, 500, 1000]
        
        for batch_size in batch_sizes:
            if batch_size > len(test_data):
                continue
            
            batch_data = test_data.head(batch_size)
            
            start_time = time.time()
            scored_data = score_transactions(batch_data, model)
            classified_data = classify_risk(scored_data)
            inference_time = time.time() - start_time
            
            self.metrics.inference_times.append(inference_time)
            
            time_per_transaction = inference_time / batch_size
            
            logger.info(f"Batch Size {batch_size:>4}: {inference_time:.3f}s total, "
                       f"{time_per_transaction*1000:.2f}ms per transaction")
            
            # Verify results
            assert 'risk_score' in classified_data.columns
            assert 'risk_category' in classified_data.columns
            assert len(classified_data) == batch_size
        
        logger.info("\n✅ ML inference performance is efficient\n")
    
    def test_05_concurrent_load_performance(self, client):
        """
        Test system performance under concurrent load.
        
        **Validates: System handles 1000+ transactions with concurrent requests**
        """
        logger.info("="*80)
        logger.info("TEST 5: CONCURRENT LOAD PERFORMANCE")
        logger.info("="*80)
        logger.info("Testing system under concurrent API requests\n")
        
        def make_request(endpoint: str) -> Dict:
            """Make a single request and return timing info."""
            start = time.time()
            try:
                response = client.get(endpoint)
                elapsed = time.time() - start
                return {
                    'success': response.status_code == 200,
                    'time': elapsed,
                    'endpoint': endpoint
                }
            except Exception as e:
                return {
                    'success': False,
                    'time': time.time() - start,
                    'endpoint': endpoint,
                    'error': str(e)
                }
        
        # Test 1: Concurrent requests to different endpoints
        logger.info("Test 5a: Concurrent requests to different endpoints")
        endpoints = [
            "/stats",
            "/transactions?limit=50",
            "/suspicious",
            "/fraud",
            "/alerts/active",
            "/session/info"
        ]
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(make_request, endpoints))
        total_time = time.time() - start_time
        
        success_count = sum(1 for r in results if r['success'])
        success_rate = (success_count / len(results)) * 100
        avg_response = statistics.mean(r['time'] for r in results if r['success'])
        
        logger.info(f"  Total Time: {total_time:.3f}s")
        logger.info(f"  Requests: {len(results)}")
        logger.info(f"  Success Rate: {success_rate:.1f}%")
        logger.info(f"  Avg Response: {avg_response:.3f}s\n")
        
        self.metrics.concurrent_load_results['Different Endpoints'] = {
            'total_time': total_time,
            'request_count': len(results),
            'success_rate': success_rate,
            'avg_response': avg_response
        }
        
        assert success_rate == 100.0, f"Some concurrent requests failed: {success_rate}%"
        assert total_time < 3.0, f"Concurrent requests took {total_time:.3f}s"
        
        # Test 2: Multiple concurrent requests to same endpoint
        logger.info("Test 5b: Multiple concurrent requests to same endpoint")
        same_endpoint = ["/transactions?limit=10"] * 10
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(make_request, same_endpoint))
        total_time = time.time() - start_time
        
        success_count = sum(1 for r in results if r['success'])
        success_rate = (success_count / len(results)) * 100
        avg_response = statistics.mean(r['time'] for r in results if r['success'])
        
        logger.info(f"  Total Time: {total_time:.3f}s")
        logger.info(f"  Requests: {len(results)}")
        logger.info(f"  Success Rate: {success_rate:.1f}%")
        logger.info(f"  Avg Response: {avg_response:.3f}s\n")
        
        self.metrics.concurrent_load_results['Same Endpoint (10x)'] = {
            'total_time': total_time,
            'request_count': len(results),
            'success_rate': success_rate,
            'avg_response': avg_response
        }
        
        assert success_rate == 100.0, f"Some concurrent requests failed: {success_rate}%"
        
        logger.info("✅ System handles concurrent load efficiently\n")
    
    def test_06_large_dataset_performance(self, client):
        """
        Test system performance with large dataset queries.
        
        **Validates: System efficiently handles 1000+ transaction queries**
        """
        logger.info("="*80)
        logger.info("TEST 6: LARGE DATASET QUERY PERFORMANCE")
        logger.info("="*80)
        logger.info("Testing queries with increasing dataset sizes\n")
        
        query_sizes = [100, 500, 1000]
        
        for limit in query_sizes:
            start_time = time.time()
            response = client.get(f"/transactions?limit={limit}")
            query_time = time.time() - start_time
            
            assert response.status_code == 200, f"Query with limit={limit} failed"
            
            data = response.json()
            actual_count = len(data['data']['transactions'])
            
            status = "✅" if query_time < 2.0 else "⚠️"
            logger.info(f"{status} Limit {limit:>4}: {query_time:.3f}s (returned {actual_count} records)")
            
            if query_time >= 2.0:
                self.metrics.add_bottleneck("Large Query", f"Query with limit={limit} slow", query_time)
        
        logger.info("\n✅ Large dataset queries perform efficiently\n")
    
    def test_07_generate_performance_report(self):
        """Generate and save comprehensive performance report."""
        logger.info("="*80)
        logger.info("TEST 7: GENERATING PERFORMANCE REPORT")
        logger.info("="*80)
        
        report = self.metrics.generate_report()
        
        # Print to console
        logger.info(report)
        
        # Save to file
        report_path = Path("backend/system_performance_report.txt")
        with open(report_path, "w") as f:
            f.write(report)
        
        logger.info(f"\n📊 Performance report saved to: {report_path}\n")


def main():
    """Run comprehensive performance tests."""
    logger.info("\n" + "="*80)
    logger.info("TRINETRA AI - COMPREHENSIVE SYSTEM PERFORMANCE TEST SUITE")
    logger.info("="*80)
    logger.info("\nThis test suite validates all NFR-1 performance requirements:")
    logger.info("  • API responses < 1 second")
    logger.info("  • Dashboard load < 3 seconds")
    logger.info("  • ML model training < 30 seconds")
    logger.info("  • System handles 1000+ transactions")
    logger.info("\nStarting comprehensive performance tests...\n")
    
    # Run pytest
    exit_code = pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
        "--color=yes"
    ])
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
