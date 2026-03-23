"""
Test script for alert count indicators functionality.

This script tests the alert statistics endpoint and verifies that
alert count indicators are properly calculated and returned.

Author: TRINETRA AI Team
Date: 2024
"""

import requests
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"


def test_alert_statistics_endpoint():
    """Test the /alerts/statistics endpoint."""
    print("=" * 60)
    print("Testing Alert Count Indicators")
    print("=" * 60)
    
    try:
        # Test alert statistics endpoint
        print("\n1. Testing /alerts/statistics endpoint...")
        response = requests.get(f"{API_BASE_URL}/alerts/statistics")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success":
                stats = data.get("data", {})
                
                print("\n   ✅ Alert Statistics Retrieved Successfully!")
                print(f"\n   📊 Total Alerts: {stats.get('total_alerts', 0)}")
                print(f"   📋 Total Summaries: {stats.get('total_summaries', 0)}")
                print(f"   🔢 Transactions with Alerts: {stats.get('total_transactions', 0)}")
                
                # Display priority counts
                priority_counts = stats.get('priority_counts', {})
                print("\n   🚨 Priority Distribution:")
                for priority, count in priority_counts.items():
                    icon = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "⚡", "LOW": "ℹ️"}.get(priority, "•")
                    print(f"      {icon} {priority}: {count}")
                
                # Display alert type counts
                alert_type_counts = stats.get('alert_type_counts', {})
                print("\n   📊 Alert Type Breakdown:")
                for alert_type, count in alert_type_counts.items():
                    icon = {
                        "PRICE_ANOMALY": "💰",
                        "ROUTE_ANOMALY": "🛣️",
                        "HIGH_RISK_COMPANY": "🏢",
                        "PORT_CONGESTION": "⚓"
                    }.get(alert_type, "⚠️")
                    display_name = alert_type.replace("_", " ").title()
                    print(f"      {icon} {display_name}: {count}")
                
                return True
            else:
                print(f"   ❌ API returned error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Request failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Please ensure the backend is running.")
        print("   Run: python backend/api.py")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False


def test_alert_summaries_with_counts():
    """Test alert summaries to verify count data."""
    print("\n" + "=" * 60)
    print("Testing Alert Summaries for Count Verification")
    print("=" * 60)
    
    try:
        print("\n2. Testing /alerts/summaries endpoint...")
        response = requests.get(f"{API_BASE_URL}/alerts/summaries")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success":
                summaries_data = data.get("data", {})
                summaries = summaries_data.get("summaries", [])
                count = summaries_data.get("count", 0)
                
                print(f"\n   ✅ Retrieved {count} alert summaries")
                
                if summaries:
                    # Analyze first few summaries
                    print("\n   📋 Sample Alert Summaries:")
                    for i, summary in enumerate(summaries[:3], 1):
                        transaction_id = summary.get("transaction_id", "UNKNOWN")
                        priority = summary.get("priority", "UNKNOWN")
                        alert_count = summary.get("alert_count", 0)
                        alerts = summary.get("alerts", [])
                        
                        print(f"\n      {i}. Transaction: {transaction_id}")
                        print(f"         Priority: {priority}")
                        print(f"         Alert Count: {alert_count}")
                        print(f"         Alert Types: {', '.join([a.get('alert_type', 'UNKNOWN') for a in alerts])}")
                
                return True
            else:
                print(f"   ❌ API returned error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Request failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False


def test_high_priority_alerts():
    """Test high priority alerts filtering."""
    print("\n" + "=" * 60)
    print("Testing High Priority Alert Filtering")
    print("=" * 60)
    
    try:
        print("\n3. Testing /alerts/summaries?min_priority=HIGH endpoint...")
        response = requests.get(f"{API_BASE_URL}/alerts/summaries?min_priority=HIGH")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success":
                summaries_data = data.get("data", {})
                summaries = summaries_data.get("summaries", [])
                count = summaries_data.get("count", 0)
                
                print(f"\n   ✅ Retrieved {count} high-priority alert summaries")
                
                # Count by priority
                priority_breakdown = {}
                for summary in summaries:
                    priority = summary.get("priority", "UNKNOWN")
                    priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
                
                print("\n   🚨 High Priority Alert Distribution:")
                for priority, count in sorted(priority_breakdown.items(), 
                                             key=lambda x: {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(x[0], 0), 
                                             reverse=True):
                    icon = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "⚡", "LOW": "ℹ️"}.get(priority, "•")
                    print(f"      {icon} {priority}: {count}")
                
                return True
            else:
                print(f"   ❌ API returned error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Request failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n🛡️ TRINETRA AI - Alert Count Indicators Test")
    print("=" * 60)
    print("This test verifies the alert count indicators functionality")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Alert Statistics", test_alert_statistics_endpoint()))
    results.append(("Alert Summaries", test_alert_summaries_with_counts()))
    results.append(("High Priority Filtering", test_high_priority_alerts()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Alert count indicators are working correctly.")
        print("\n💡 Next Steps:")
        print("   1. Start the dashboard: streamlit run frontend/dashboard.py")
        print("   2. Navigate to the Fraud Alerts section")
        print("   3. Verify that alert count indicators are displayed")
        print("   4. Check that counts match the statistics shown above")
    else:
        print("\n⚠️ Some tests failed. Please check the API server and try again.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
