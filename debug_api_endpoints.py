#!/usr/bin/env python3
"""
Debug API Endpoints for Dashboard Integration

Quick test to identify which endpoints are working and which are causing issues.
"""

import sys
import os
import time
from fastapi.testclient import TestClient

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.api import app, initialize_system
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_endpoint(client, endpoint, method="GET", json_data=None, timeout=5):
    """Test a single endpoint with timeout."""
    print(f"Testing {method} {endpoint}...")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = client.get(endpoint, timeout=timeout)
        elif method == "POST":
            response = client.post(endpoint, json=json_data, timeout=timeout)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"  Status: {response.status_code}")
        print(f"  Duration: {duration:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Response keys: {list(data.keys())}")
            print("  ✅ SUCCESS")
        else:
            print(f"  ❌ FAILED - Status {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Error: {response.text[:200]}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"  ❌ EXCEPTION: {e}")
        return False


def main():
    print("🔍 Debugging API Endpoints for Dashboard Integration")
    print("=" * 60)
    
    # Initialize system
    print("Initializing system...")
    try:
        initialize_system()
        print("✅ System initialized")
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return
    
    # Create test client
    client = TestClient(app)
    
    # Test endpoints one by one
    endpoints = [
        ("GET", "/", None),
        ("GET", "/stats", None),
        ("GET", "/transactions?limit=5", None),
        ("GET", "/suspicious", None),
        ("GET", "/fraud", None),
        ("GET", "/session/info", None),
        ("POST", "/session/reset", None),
    ]
    
    results = {}
    
    for method, endpoint, json_data in endpoints:
        print(f"\n{'-' * 40}")
        success = test_endpoint(client, endpoint, method, json_data, timeout=10)
        results[endpoint] = success
    
    print(f"\n{'=' * 60}")
    print("📊 Summary:")
    for endpoint, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {endpoint}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nOverall: {passed}/{total} endpoints working ({passed/total*100:.1f}%)")


if __name__ == "__main__":
    main()