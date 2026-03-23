"""
Fast Performance Under Load Test - Standalone Script

This script runs performance tests quickly without pytest overhead.
All tests complete within 30 seconds and validate NFR-1 requirements.

Task: 14.2 Demo Preparation - Test system performance under load
Spec: .kiro/specs/trinetra-ai-fraud-detection

**Validates: Requirements NFR-1 (Performance)**

Author: TRINETRA AI Team
Date: 2024
"""

import time
import statistics
import sys
import os
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.api import app, initialize_system
from backend.data_loader import load_dataset
from backend.feature_engineering import engineer_features
from backend.model import train_model, load_model
from backend.fraud_detection import score_transactions, classify_risk


def print_header(title):
    """Print formatted header."""
    print("\n" + "="*70)
    print(title)
    print("="*70)


def test_api_performance(client):
    """Test API endpoint response times."""
    print_header("TEST 1: API RESPONSE TIMES (<1 second requirement)")
    
    endpoints = [
        ("/stats", "Statistics"),
        ("/transactions?limit=50", "Transactions"),
        ("/suspicious", "Suspicious"),
        ("/fraud", "Fraud"),
        ("/alerts/active", "Active Alerts"),
    ]
    
    all_pass = True
    for endpoint, name in endpoints:
        times = []
        for _ in range(3):
            start = time.time()
            response = client.get(endpoint)
            elapsed = time.time() - start
            times.append(elapsed)
            
            if response.status_code != 200:
                print(f"❌ {name}: HTTP {response.status_code}")
                all_pass = False
                continue
        
        avg = statistics.mean(times)
        max_time = max(times)
        status = "✅" if max_time < 1.0 else "❌"
        
        if max_time >= 1.0:
            all_pass = False
        
        print(f"{status} {name:<25} Avg: {avg:.3f}s  Max: {max_time:.3f}s")
    
    if all_pass:
        print("\n✅ All API endpoints meet <1 second requirement")
    else:
        print("\n❌ Some endpoints failed to meet requirement")
    
    return all_pass


def test_dashboard_load(client):
    """Test dashboard load time."""
    print_header("TEST 2: DASHBOARD LOAD TIME (<3 second requirement)")
    
    dashboard_endpoints = [
        "/stats",
        "/alerts/active",
        "/transactions?limit=50",
    ]
    
    start_time = time.time()
    for endpoint in dashboard_endpoints:
        response = client.get(endpoint)
        if response.status_code != 200:
            print(f"❌ Dashboard endpoint {endpoint} failed")
            return False
    
    total_time = time.time() - start_time
    status = "✅" if total_time < 3.0 else "❌"
    
    print(f"{status} Dashboard Load Time: {total_time:.3f}s")
    print(f"   Target: < 3.0s")
    print(f"   Margin: {3.0 - total_time:.3f}s")
    
    if total_time < 3.0:
        print("\n✅ Dashboard meets <3 second load requirement")
        return True
    else:
        print("\n❌ Dashboard exceeds 3 second requirement")
        return False


def test_ml_training(test_data):
    """Test ML model training time."""
    print_header("TEST 3: ML MODEL TRAINING TIME (<30 second requirement)")
    print(f"Training on {len(test_data)} transactions...")
    
    start_time = time.time()
    model = train_model(test_data)
    training_time = time.time() - start_time
    
    status = "✅" if training_time < 30.0 else "❌"
    
    print(f"{status} Training Time: {training_time:.3f}s")
    print(f"   Target: < 30.0s")
    print(f"   Margin: {30.0 - training_time:.3f}s")
    print(f"   Performance: {(training_time / 30.0) * 100:.1f}% of limit")
    
    if training_time < 30.0:
        print("\n✅ ML training meets <30 second requirement")
        return True, model
    else:
        print("\n❌ ML training exceeds 30 second requirement")
        return False, model


def test_ml_inference(test_data, model):
    """Test ML inference performance."""
    print_header("TEST 4: ML INFERENCE PERFORMANCE (1000+ transactions)")
    
    batch_sizes = [100, 500, 1000]
    all_pass = True
    
    for batch_size in batch_sizes:
        if batch_size > len(test_data):
            continue
        
        batch = test_data.head(batch_size)
        
        start = time.time()
        scored = score_transactions(batch, model)
        classified = classify_risk(scored)
        elapsed = time.time() - start
        
        per_txn = (elapsed / batch_size) * 1000  # ms per transaction
        
        print(f"Batch {batch_size:>4}: {elapsed:.3f}s total, {per_txn:.2f}ms per transaction")
        
        if 'risk_score' not in classified.columns or 'risk_category' not in classified.columns:
            all_pass = False
    
    if all_pass:
        print("\n✅ ML inference handles 1000+ transactions efficiently")
    else:
        print("\n❌ ML inference had issues")
    
    return all_pass


def test_concurrent_load(client):
    """Test concurrent request handling."""
    print_header("TEST 5: CONCURRENT LOAD PERFORMANCE")
    
    def make_request(endpoint):
        start = time.time()
        try:
            response = client.get(endpoint)
            return {
                'success': response.status_code == 200,
                'time': time.time() - start
            }
        except:
            return {'success': False, 'time': time.time() - start}
    
    endpoints = [
        "/stats",
        "/transactions?limit=20",
        "/suspicious",
        "/fraud",
        "/alerts/active"
    ]
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(make_request, endpoints))
    total_time = time.time() - start_time
    
    success_count = sum(1 for r in results if r['success'])
    success_rate = (success_count / len(results)) * 100
    avg_response = statistics.mean(r['time'] for r in results if r['success'])
    
    print(f"Concurrent Requests: {len(results)}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Total Time: {total_time:.3f}s")
    print(f"Avg Response: {avg_response:.3f}s")
    
    if success_rate == 100.0 and total_time < 3.0:
        print("\n✅ System handles concurrent load efficiently")
        return True
    else:
        print("\n❌ Concurrent load test had issues")
        return False


def test_large_queries(client):
    """Test large dataset queries."""
    print_header("TEST 6: LARGE DATASET QUERY PERFORMANCE")
    
    query_sizes = [100, 500, 1000]
    all_pass = True
    
    for limit in query_sizes:
        start = time.time()
        response = client.get(f"/transactions?limit={limit}")
        elapsed = time.time() - start
        
        if response.status_code != 200:
            print(f"❌ Query with limit={limit} failed")
            all_pass = False
            continue
        
        data = response.json()
        count = len(data['data']['transactions'])
        
        status = "✅" if elapsed < 2.0 else "⚠️"
        print(f"{status} Limit {limit:>4}: {elapsed:.3f}s ({count} records)")
        
        if elapsed >= 2.0:
            all_pass = False
    
    if all_pass:
        print("\n✅ Large dataset queries perform efficiently")
    else:
        print("\n⚠️  Some large queries were slow")
    
    return all_pass


def generate_report(results):
    """Generate final performance report."""
    print_header("PERFORMANCE TEST SUMMARY")
    
    print("\nTRINETRA AI - Performance Under Load Test Results")
    print("="*70)
    print("\nNFR-1 Performance Requirements:")
    print(f"  {'✅' if results['api'] else '❌'} API responses < 1 second")
    print(f"  {'✅' if results['dashboard'] else '❌'} Dashboard load < 3 seconds")
    print(f"  {'✅' if results['training'] else '❌'} ML model training < 30 seconds")
    print(f"  {'✅' if results['inference'] else '❌'} System handles 1000+ transactions")
    print(f"  {'✅' if results['concurrent'] else '❌'} Concurrent load handling")
    print(f"  {'✅' if results['queries'] else '❌'} Large query performance")
    
    all_pass = all(results.values())
    
    print("\n" + "="*70)
    if all_pass:
        print("OVERALL RESULT: ✅ ALL PERFORMANCE TESTS PASSED")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"OVERALL RESULT: ❌ FAILED TESTS: {', '.join(failed)}")
    print("="*70)
    
    if all_pass:
        print("\nSystem is ready for demo and meets all performance requirements.")
    else:
        print("\nSome performance requirements were not met.")
    
    print("="*70)
    
    # Save report
    report_lines = [
        "TRINETRA AI - Performance Under Load Test Results",
        "="*70,
        "",
        "NFR-1 Performance Requirements:",
        f"  {'✅' if results['api'] else '❌'} API responses < 1 second",
        f"  {'✅' if results['dashboard'] else '❌'} Dashboard load < 3 seconds",
        f"  {'✅' if results['training'] else '❌'} ML model training < 30 seconds",
        f"  {'✅' if results['inference'] else '❌'} System handles 1000+ transactions",
        f"  {'✅' if results['concurrent'] else '❌'} Concurrent load handling",
        f"  {'✅' if results['queries'] else '❌'} Large query performance",
        "",
        "="*70,
        f"OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_pass else '❌ SOME TESTS FAILED'}",
        "="*70,
    ]
    
    with open("backend/performance_under_load_report.txt", "w") as f:
        f.write("\n".join(report_lines))
    
    print("\n📊 Report saved to: backend/performance_under_load_report.txt")
    
    return all_pass


def main():
    """Run all performance tests."""
    print("\n" + "="*70)
    print("TRINETRA AI - PERFORMANCE UNDER LOAD TEST SUITE")
    print("="*70)
    print("\nValidating NFR-1 performance requirements:")
    print("  • API responses < 1 second")
    print("  • Dashboard load < 3 seconds")
    print("  • ML model training < 30 seconds")
    print("  • System handles 1000+ transactions")
    print("\nStarting tests...")
    
    # Initialize system
    print("\nInitializing system...")
    try:
        initialize_system()
        print("✅ System initialized successfully")
    except Exception as e:
        print(f"⚠️  System initialization warning: {e}")
    
    # Create test client
    client = TestClient(app)
    
    # Load test data
    print("Loading test data...")
    dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    test_data = load_dataset(dataset_path)
    test_data = engineer_features(test_data)
    print(f"✅ Loaded {len(test_data)} transactions")
    
    # Run tests
    results = {}
    
    results['api'] = test_api_performance(client)
    results['dashboard'] = test_dashboard_load(client)
    results['training'], model = test_ml_training(test_data)
    results['inference'] = test_ml_inference(test_data, model)
    results['concurrent'] = test_concurrent_load(client)
    results['queries'] = test_large_queries(client)
    
    # Generate report
    all_pass = generate_report(results)
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
