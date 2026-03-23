"""
Test script for alert dismissal functionality.

This script tests the alert dismissal and restoration features.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_alert_dismissal():
    """Test alert dismissal functionality."""
    print("=" * 60)
    print("Testing Alert Dismissal Functionality")
    print("=" * 60)
    
    # 1. Get active alerts
    print("\n1. Getting active alerts...")
    response = requests.get(f"{API_BASE_URL}/alerts/active")
    if response.status_code == 200:
        data = response.json()
        active_alerts = data.get("data", {}).get("summaries", [])
        print(f"   ✓ Found {len(active_alerts)} active alerts")
        
        if active_alerts:
            # Get first alert for testing
            test_alert = active_alerts[0]
            transaction_id = test_alert.get("transaction_id")
            print(f"   Testing with transaction: {transaction_id}")
            
            # 2. Dismiss the alert
            print(f"\n2. Dismissing alert {transaction_id}...")
            dismiss_response = requests.post(
                f"{API_BASE_URL}/alerts/dismiss/{transaction_id}",
                json={"dismissed_by": "test_user"}
            )
            if dismiss_response.status_code == 200:
                print(f"   ✓ Alert dismissed successfully")
            else:
                print(f"   ✗ Failed to dismiss alert: {dismiss_response.text}")
                return
            
            # 3. Verify it's in dismissed list
            print(f"\n3. Verifying alert is dismissed...")
            dismissed_response = requests.get(f"{API_BASE_URL}/alerts/dismissed")
            if dismissed_response.status_code == 200:
                dismissed_data = dismissed_response.json()
                dismissed_alerts = dismissed_data.get("data", {}).get("summaries", [])
                dismissed_ids = [a.get("transaction_id") for a in dismissed_alerts]
                
                if transaction_id in dismissed_ids:
                    print(f"   ✓ Alert found in dismissed list")
                else:
                    print(f"   ✗ Alert NOT found in dismissed list")
                    return
            
            # 4. Verify it's NOT in active list
            print(f"\n4. Verifying alert is not in active list...")
            active_response = requests.get(f"{API_BASE_URL}/alerts/active")
            if active_response.status_code == 200:
                active_data = active_response.json()
                active_alerts_new = active_data.get("data", {}).get("summaries", [])
                active_ids = [a.get("transaction_id") for a in active_alerts_new]
                
                if transaction_id not in active_ids:
                    print(f"   ✓ Alert correctly removed from active list")
                else:
                    print(f"   ✗ Alert still in active list")
                    return
            
            # 5. Restore the alert
            print(f"\n5. Restoring alert {transaction_id}...")
            restore_response = requests.post(
                f"{API_BASE_URL}/alerts/undismiss/{transaction_id}"
            )
            if restore_response.status_code == 200:
                print(f"   ✓ Alert restored successfully")
            else:
                print(f"   ✗ Failed to restore alert: {restore_response.text}")
                return
            
            # 6. Verify it's back in active list
            print(f"\n6. Verifying alert is back in active list...")
            active_response = requests.get(f"{API_BASE_URL}/alerts/active")
            if active_response.status_code == 200:
                active_data = active_response.json()
                active_alerts_final = active_data.get("data", {}).get("summaries", [])
                active_ids = [a.get("transaction_id") for a in active_alerts_final]
                
                if transaction_id in active_ids:
                    print(f"   ✓ Alert successfully restored to active list")
                else:
                    print(f"   ✗ Alert NOT found in active list after restore")
                    return
            
            print("\n" + "=" * 60)
            print("✓ All tests passed! Alert dismissal functionality works correctly.")
            print("=" * 60)
        else:
            print("   No active alerts to test with")
    else:
        print(f"   ✗ Failed to get active alerts: {response.text}")

def test_alert_statistics():
    """Test alert statistics endpoint."""
    print("\n\nTesting Alert Statistics...")
    print("-" * 60)
    
    response = requests.get(f"{API_BASE_URL}/alerts/statistics")
    if response.status_code == 200:
        data = response.json()
        stats = data.get("data", {})
        
        print(f"Total Alerts: {stats.get('total_alerts', 0)}")
        print(f"Total Summaries: {stats.get('total_summaries', 0)}")
        print(f"Active Alerts: {stats.get('active_count', 0)}")
        print(f"Dismissed Alerts: {stats.get('dismissed_count', 0)}")
        print(f"\nPriority Breakdown:")
        for priority, count in stats.get('priority_counts', {}).items():
            print(f"  {priority}: {count}")
        print(f"\nAlert Type Breakdown:")
        for alert_type, count in stats.get('alert_type_counts', {}).items():
            print(f"  {alert_type}: {count}")
        
        print("✓ Statistics retrieved successfully")
    else:
        print(f"✗ Failed to get statistics: {response.text}")

if __name__ == "__main__":
    try:
        test_alert_dismissal()
        test_alert_statistics()
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to API. Please ensure the backend is running:")
        print("  python backend/api.py")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
