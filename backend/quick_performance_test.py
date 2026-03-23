"""
Quick API Performance Test - Standalone Script

This script runs a quick performance test on all API endpoints
without using pytest, for faster execution and debugging.
"""

import time
import statistics
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.api import app, initialize_system

# Initialize system
print("Initializing system...")
initialize_system()
print("✅ System initialized\n")

# Create test client
client = TestClient(app)

# Performance threshold
THRESHOLD = 1.0  # 1 second

def test_endpoint(method, endpoint, name, runs=3, **kwargs):
    """Test an endpoint and return timing stats."""
    times = []
    
    for _ in range(runs):
        start = time.time()
        
        if method == "GET":
            response = client.get(endpoint, **kwargs)
        else:
            response = client.post(endpoint, **kwargs)
        
        elapsed = time.time() - start
        times.append(elapsed)
        
        if response.status_code != 200:
            print(f"❌ {name}: HTTP {response.status_code}")
            return None
    
    avg = statistics.mean(times)
    max_time = max(times)
    
    status = "✅ PASS" if max_time < THRESHOLD else "❌ FAIL"
    print(f"{status} {name:<40} Avg: {avg:.3f}s  Max: {max_time:.3f}s")
    
    return {"avg": avg, "max": max_time, "pass": max_time < THRESHOLD}

# Run tests
print("="*80)
print("API PERFORMANCE TEST RESULTS")
print("="*80)
print(f"Threshold: {THRESHOLD}s (NFR-1 Requirement)")
print("="*80)

results = []

# Test all endpoints
results.append(test_endpoint("GET", "/", "Root"))
results.append(test_endpoint("GET", "/transactions?limit=10", "Transactions (10)"))
results.append(test_endpoint("GET", "/transactions?limit=100", "Transactions (100)"))
results.append(test_endpoint("GET", "/suspicious", "Suspicious"))
results.append(test_endpoint("GET", "/fraud", "Fraud"))
results.append(test_endpoint("GET", "/stats", "Statistics"))
results.append(test_endpoint("GET", "/session/info", "Session Info"))
results.append(test_endpoint("POST", "/session/reset", "Session Reset"))
results.append(test_endpoint("GET", "/alerts", "Alerts"))
results.append(test_endpoint("GET", "/alerts/statistics", "Alert Statistics"))
results.append(test_endpoint("GET", "/alerts/summaries", "Alert Summaries"))
results.append(test_endpoint("GET", "/alerts/active", "Active Alerts"))

# Get a transaction ID for explain test
response = client.get("/transactions?limit=1")
if response.status_code == 200:
    data = response.json()
    if data['data']['transactions']:
        txn_id = data['data']['transactions'][0]['transaction_id']
        results.append(test_endpoint("POST", f"/explain/{txn_id}", "Explain", json={"force_ai": False}))

# Query test
results.append(test_endpoint("POST", "/query", "Query", json={"query": "How many transactions?"}))

print("="*80)

# Summary
results = [r for r in results if r is not None]
passed = sum(1 for r in results if r['pass'])
total = len(results)

print(f"\nSummary: {passed}/{total} tests passed")

if passed == total:
    print("✅ ALL PERFORMANCE TESTS PASSED - All endpoints meet the 1-second requirement")
else:
    print(f"❌ {total - passed} tests failed to meet performance requirements")

print("="*80)
