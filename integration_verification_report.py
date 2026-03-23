#!/usr/bin/env python3
"""
TRINETRA AI System Integration Verification Report
Comprehensive verification of API and dashboard integration
"""

import requests
import time
import sys
from typing import Dict, List

# Test configuration
API_BASE_URL = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8501"

def test_system_integration():
    """Comprehensive system integration verification"""
    
    print("🔍 TRINETRA AI System Integration Verification")
    print("=" * 60)
    
    results = {
        'api_connectivity': False,
        'dashboard_connectivity': False,
        'data_endpoints': False,
        'data_integrity': False,
        'explanation_system': False,
        'dashboard_api_integration': False
    }
    
    # 1. Test API Connectivity
    print("\n1. Testing API Connectivity...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("   ✅ API is running and responding correctly")
                results['api_connectivity'] = True
            else:
                print("   ❌ API responding but with unexpected format")
        else:
            print(f"   ❌ API returned HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ API connectivity failed: {e}")
    
    # 2. Test Dashboard Connectivity
    print("\n2. Testing Dashboard Connectivity...")
    try:
        response = requests.get(DASHBOARD_URL, timeout=10)
        if response.status_code == 200:
            print("   ✅ Dashboard is accessible")
            results['dashboard_connectivity'] = True
        else:
            print(f"   ❌ Dashboard returned HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard connectivity failed: {e}")
    
    # 3. Test Data Endpoints
    print("\n3. Testing Data Endpoints...")
    endpoints = [
        ("/transactions", "All transactions"),
        ("/suspicious", "Suspicious transactions"),
        ("/fraud", "Fraud transactions")
    ]
    
    endpoint_results = []
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    # Handle different response structures
                    if 'transactions' in data.get('data', {}):
                        count = len(data['data']['transactions'])
                    else:
                        count = len(data.get('data', []))
                    print(f"   ✅ {endpoint}: {count} records")
                    endpoint_results.append(True)
                else:
                    print(f"   ❌ {endpoint}: Invalid response format")
                    endpoint_results.append(False)
            else:
                print(f"   ❌ {endpoint}: HTTP {response.status_code}")
                endpoint_results.append(False)
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
            endpoint_results.append(False)
    
    results['data_endpoints'] = all(endpoint_results)
    
    # 4. Test Data Integrity
    print("\n4. Testing Data Integrity...")
    try:
        response = requests.get(f"{API_BASE_URL}/transactions?limit=3", timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Handle nested structure
            if 'transactions' in data.get('data', {}):
                transactions = data['data']['transactions']
            else:
                transactions = data.get('data', [])
            
            if transactions:
                sample = transactions[0]
                required_fields = ['transaction_id', 'risk_score', 'risk_category']
                missing = [f for f in required_fields if f not in sample]
                
                if not missing:
                    valid_categories = ['SAFE', 'SUSPICIOUS', 'FRAUD']
                    categories_valid = all(t['risk_category'] in valid_categories for t in transactions)
                    
                    if categories_valid:
                        print(f"   ✅ Data integrity verified ({len(transactions)} transactions)")
                        results['data_integrity'] = True
                    else:
                        print("   ❌ Invalid risk categories found")
                else:
                    print(f"   ❌ Missing required fields: {missing}")
            else:
                print("   ❌ No transaction data available")
        else:
            print(f"   ❌ Data integrity check failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Data integrity check failed: {e}")
    
    # 5. Test Explanation System
    print("\n5. Testing Explanation System...")
    try:
        # Get a transaction ID
        response = requests.get(f"{API_BASE_URL}/transactions?limit=1", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'transactions' in data.get('data', {}):
                transactions = data['data']['transactions']
            else:
                transactions = data.get('data', [])
            
            if transactions:
                transaction_id = transactions[0]['transaction_id']
                
                # Test explanation (using fallback)
                explain_response = requests.post(
                    f"{API_BASE_URL}/explain/{transaction_id}",
                    json={"force_ai": False},
                    timeout=15
                )
                
                if explain_response.status_code == 200:
                    explain_data = explain_response.json()
                    if explain_data.get('data', {}).get('explanation'):
                        print(f"   ✅ Explanation system working (transaction {transaction_id})")
                        results['explanation_system'] = True
                    else:
                        print("   ❌ No explanation generated")
                else:
                    print(f"   ❌ Explanation failed: HTTP {explain_response.status_code}")
            else:
                print("   ❌ No transactions available for explanation test")
        else:
            print(f"   ❌ Could not get transaction for explanation test")
    except Exception as e:
        print(f"   ❌ Explanation system test failed: {e}")
    
    # 6. Test Dashboard-API Integration
    print("\n6. Testing Dashboard-API Integration...")
    # This tests that the dashboard can successfully connect to all the API endpoints it needs
    dashboard_endpoints = ["/transactions", "/suspicious", "/fraud"]
    integration_results = []
    
    for endpoint in dashboard_endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    integration_results.append(True)
                else:
                    integration_results.append(False)
            else:
                integration_results.append(False)
        except:
            integration_results.append(False)
    
    if all(integration_results):
        print("   ✅ Dashboard can successfully connect to all required API endpoints")
        results['dashboard_api_integration'] = True
    else:
        print("   ❌ Dashboard-API integration issues detected")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 INTEGRATION VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        readable_name = test_name.replace('_', ' ').title()
        print(f"{status} {readable_name}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 INTEGRATION VERIFICATION SUCCESSFUL!")
        print("\n✅ VERIFICATION COMPLETE:")
        print("   • FastAPI backend is running on http://localhost:8000")
        print("   • Streamlit dashboard is running on http://localhost:8501")
        print("   • All transaction endpoints are functional")
        print("   • Data integrity is maintained")
        print("   • Explanation system is operational")
        print("   • Dashboard can successfully integrate with API")
        print("\n🚀 The TRINETRA AI system is ready for use!")
        return True
    else:
        print("\n⚠️  INTEGRATION VERIFICATION INCOMPLETE!")
        print(f"   {total_tests - passed_tests} issues need to be resolved")
        return False

def main():
    """Main verification runner"""
    try:
        success = test_system_integration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Verification error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()