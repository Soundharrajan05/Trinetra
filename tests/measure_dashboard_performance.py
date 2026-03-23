#!/usr/bin/env python3
"""
Dashboard Performance Measurement Script

This script measures the actual dashboard load time by simulating
the data loading sequence that occurs when the dashboard initializes.

**Validates: NFR-1 Performance - Dashboard loads within 3 seconds**

Usage:
    python tests/measure_dashboard_performance.py

Requirements:
    - API server must be running on http://localhost:8000
    - Run: python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000

Author: TRINETRA AI Team
Date: 2024
"""

import time
import requests
import sys
from typing import Dict, List, Tuple

# Configuration
API_BASE_URL = "http://localhost:8000"
MAX_LOAD_TIME = 3.0  # seconds (NFR-1 requirement)


def measure_endpoint(endpoint: str, description: str, timeout: int = 10) -> Tuple[bool, float, str]:
    """
    Measure the response time of a single endpoint.
    
    Returns:
        (success, response_time, message)
    """
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            return (True, elapsed, f"Success")
        else:
            return (False, elapsed, f"HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        return (False, timeout, "Timeout")
    except requests.exceptions.RequestException as e:
        return (False, 0, f"Error: {str(e)}")


def test_dashboard_load_sequence():
    """
    Simulate the dashboard's initial load sequence and measure total time.
    
    The dashboard loads data in this sequence:
    1. Session info (for quota display)
    2. Statistics (for KPI metrics)
    3. Active alerts (for alert banners)
    4. Transactions (for table display)
    """
    print("="*70)
    print("TRINETRA AI - Dashboard Load Time Performance Test")
    print("="*70)
    print(f"\nRequirement: NFR-1 - Dashboard loads within {MAX_LOAD_TIME} seconds")
    print(f"API Base URL: {API_BASE_URL}\n")
    
    # Check if API is available
    print("Step 1: Checking API availability...")
    success, elapsed, message = measure_endpoint("/", "Root endpoint", timeout=5)
    
    if not success:
        print(f"❌ FAIL: API server is not responding ({message})")
        print("\nPlease start the API server first:")
        print("  python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000")
        return False
    
    print(f"✅ API server is running ({elapsed:.3f}s)\n")
    
    # Define dashboard load sequence
    load_sequence = [
        ("/session/info", "Session Info (quota management)"),
        ("/stats", "Statistics (KPI metrics)"),
        ("/alerts/active", "Active Alerts (alert banners)"),
        ("/transactions?limit=50", "Transactions (table data)")
    ]
    
    print("Step 2: Measuring dashboard data loading sequence...")
    print("-"*70)
    
    total_start_time = time.time()
    results = []
    all_success = True
    
    for endpoint, description in load_sequence:
        success, elapsed, message = measure_endpoint(endpoint, description, timeout=10)
        results.append((endpoint, description, success, elapsed, message))
        
        status_icon = "✅" if success else "❌"
        status_text = "PASS" if success and elapsed < 1.0 else ("SLOW" if success else "FAIL")
        
        print(f"  {status_icon} {description:40s} {elapsed:6.3f}s  [{status_text}]")
        
        if not success:
            all_success = False
    
    total_load_time = time.time() - total_start_time
    
    # Calculate statistics
    successful_requests = [r for r in results if r[2]]
    if successful_requests:
        avg_time = sum(r[3] for r in successful_requests) / len(successful_requests)
        max_time = max(r[3] for r in successful_requests)
        min_time = min(r[3] for r in successful_requests)
    else:
        avg_time = max_time = min_time = 0
    
    # Print summary
    print("\n" + "="*70)
    print("PERFORMANCE TEST RESULTS")
    print("="*70)
    print(f"\nTotal Dashboard Load Time:    {total_load_time:.3f} seconds")
    print(f"Average Endpoint Response:    {avg_time:.3f} seconds")
    print(f"Slowest Endpoint:             {max_time:.3f} seconds")
    print(f"Fastest Endpoint:             {min_time:.3f} seconds")
    print(f"Successful Requests:          {len(successful_requests)}/{len(load_sequence)}")
    print(f"\nPerformance Requirement:      < {MAX_LOAD_TIME} seconds")
    
    # Determine pass/fail
    if not all_success:
        print(f"\n❌ FAIL: Some endpoints failed to respond")
        print("\nFailed Endpoints:")
        for endpoint, desc, success, elapsed, message in results:
            if not success:
                print(f"  - {desc}: {message}")
        return False
    
    if total_load_time < MAX_LOAD_TIME:
        print(f"\n✅ PASS: Dashboard loads in {total_load_time:.3f}s (under {MAX_LOAD_TIME}s requirement)")
        print("\nPerformance Status: EXCELLENT")
        return True
    else:
        print(f"\n⚠️ FAIL: Dashboard loads in {total_load_time:.3f}s (exceeds {MAX_LOAD_TIME}s requirement)")
        print(f"\nPerformance Gap: {total_load_time - MAX_LOAD_TIME:.3f}s over target")
        print("\nRecommended Optimizations:")
        print("  1. Implement API response caching")
        print("  2. Add lazy loading for non-critical data")
        print("  3. Optimize database queries")
        print("  4. Use async data loading in dashboard")
        print("  5. Reduce initial data payload size")
        return False


def test_individual_endpoint_performance():
    """Test individual endpoint performance for bottleneck identification."""
    print("\n" + "="*70)
    print("INDIVIDUAL ENDPOINT PERFORMANCE ANALYSIS")
    print("="*70)
    
    endpoints = [
        ("/", "Root"),
        ("/transactions?limit=10", "Transactions (10)"),
        ("/transactions?limit=50", "Transactions (50)"),
        ("/transactions?limit=100", "Transactions (100)"),
        ("/suspicious", "Suspicious Transactions"),
        ("/fraud", "Fraud Transactions"),
        ("/stats", "Statistics"),
        ("/alerts/active", "Active Alerts"),
        ("/alerts/dismissed", "Dismissed Alerts"),
        ("/session/info", "Session Info")
    ]
    
    print("\nMeasuring response times for all endpoints...\n")
    
    results = []
    for endpoint, description in endpoints:
        success, elapsed, message = measure_endpoint(endpoint, description, timeout=10)
        results.append((endpoint, description, success, elapsed, message))
        
        if success:
            status = "✅" if elapsed < 1.0 else "⚠️"
            print(f"  {status} {description:30s} {elapsed:6.3f}s")
        else:
            print(f"  ❌ {description:30s} FAILED ({message})")
    
    # Identify bottlenecks
    successful_results = [(e, d, t) for e, d, s, t, m in results if s]
    if successful_results:
        successful_results.sort(key=lambda x: x[2], reverse=True)
        
        print("\n" + "-"*70)
        print("BOTTLENECK ANALYSIS")
        print("-"*70)
        print("\nSlowest Endpoints:")
        for i, (endpoint, desc, elapsed) in enumerate(successful_results[:3], 1):
            print(f"  {i}. {desc:30s} {elapsed:.3f}s")
        
        print("\nFastest Endpoints:")
        for i, (endpoint, desc, elapsed) in enumerate(reversed(successful_results[-3:]), 1):
            print(f"  {i}. {desc:30s} {elapsed:.3f}s")


def main():
    """Main entry point for performance testing."""
    try:
        # Test dashboard load sequence
        dashboard_pass = test_dashboard_load_sequence()
        
        # Test individual endpoints
        test_individual_endpoint_performance()
        
        # Final summary
        print("\n" + "="*70)
        print("FINAL SUMMARY")
        print("="*70)
        
        if dashboard_pass:
            print("\n✅ Dashboard Performance: PASS")
            print("   The dashboard meets the NFR-1 requirement (<3 seconds)")
            return 0
        else:
            print("\n❌ Dashboard Performance: FAIL")
            print("   The dashboard does not meet the NFR-1 requirement (<3 seconds)")
            print("   Performance optimization is required")
            return 1
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
