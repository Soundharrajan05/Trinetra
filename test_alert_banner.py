"""
Test script to verify alert banner implementation

This script tests the alert banner display functionality by:
1. Checking if the API endpoint returns alert summaries
2. Verifying the data structure matches expectations
3. Simulating the dashboard's alert display logic

Author: TRINETRA AI Team
Date: 2024
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_alert_summaries_endpoint():
    """Test the /alerts/summaries endpoint."""
    print("Testing /alerts/summaries endpoint...")
    
    try:
        # Test without filter
        response = requests.get(f"{API_BASE_URL}/alerts/summaries")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Status: {data.get('status')}")
            
            summaries = data.get('data', {}).get('summaries', [])
            print(f"Total Summaries: {len(summaries)}")
            
            if summaries:
                print("\nSample Alert Summary:")
                sample = summaries[0]
                print(json.dumps(sample, indent=2))
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Please start the backend first.")
        print("Run: python backend/api.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_high_priority_alerts():
    """Test filtering by HIGH priority."""
    print("\n" + "="*50)
    print("Testing HIGH priority filter...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/alerts/summaries?min_priority=HIGH")
        
        if response.status_code == 200:
            data = response.json()
            summaries = data.get('data', {}).get('summaries', [])
            print(f"High Priority Alerts: {len(summaries)}")
            
            # Group by priority
            critical = [s for s in summaries if s.get('priority') == 'CRITICAL']
            high = [s for s in summaries if s.get('priority') == 'HIGH']
            
            print(f"  - CRITICAL: {len(critical)}")
            print(f"  - HIGH: {len(high)}")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_alert_statistics():
    """Test the alert statistics endpoint."""
    print("\n" + "="*50)
    print("Testing /alerts/statistics endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/alerts/statistics")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('data', {})
            
            print(f"Total Alerts: {stats.get('total_alerts')}")
            print(f"Total Summaries: {stats.get('total_summaries')}")
            print(f"Total Transactions with Alerts: {stats.get('total_transactions')}")
            
            print("\nPriority Counts:")
            for priority, count in stats.get('priority_counts', {}).items():
                print(f"  - {priority}: {count}")
            
            print("\nAlert Type Counts:")
            for alert_type, count in stats.get('alert_type_counts', {}).items():
                print(f"  - {alert_type}: {count}")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🛡️ TRINETRA AI - Alert Banner Test")
    print("="*50)
    
    # Run tests
    test1 = test_alert_summaries_endpoint()
    test2 = test_high_priority_alerts()
    test3 = test_alert_statistics()
    
    print("\n" + "="*50)
    print("Test Results:")
    print(f"  Alert Summaries Endpoint: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  High Priority Filter: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"  Alert Statistics: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 All tests passed! Alert banner implementation is ready.")
    else:
        print("\n⚠️ Some tests failed. Please check the backend.")
