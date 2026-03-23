#!/usr/bin/env python3
"""Quick API speed test"""
import requests
import time

API_BASE_URL = "http://127.0.0.1:8000"

# Test multiple endpoints
endpoints = [
    "/",
    "/stats",
    "/session/info",
    "/alerts/active",
    "/transactions?limit=10"
]

print("Testing API response times...")
print("="*60)

for endpoint in endpoints:
    url = f"{API_BASE_URL}{endpoint}"
    
    # Warm up
    try:
        requests.get(url, timeout=5)
    except:
        pass
    
    # Measure
    times = []
    for i in range(3):
        start = time.time()
        try:
            r = requests.get(url, timeout=5)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"{endpoint:30s} {elapsed:.3f}s (Status: {r.status_code})")
        except Exception as e:
            print(f"{endpoint:30s} ERROR: {e}")
    
    if times:
        avg = sum(times) / len(times)
        print(f"  Average: {avg:.3f}s")
    print()
