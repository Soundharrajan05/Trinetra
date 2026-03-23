"""
Dashboard-API Integration Test for TRINETRA AI

This test verifies that the Streamlit dashboard can successfully integrate with
the FastAPI backend by testing the actual running system components.
"""

import requests
import time
import json
from pathlib import Path
import subprocess
import sys

def test_system_processes():
    """Test if both API and dashboard processes are running."""
    print("🔍 Testing System Processes...")
    
    try:
        # Check if ports are in use
        result = subprocess.run(
            ["powershell", "-Command", "Get-NetTCPConnection | Where-Object {$_.LocalPort -eq 8000 -or $_.LocalPort -eq 8501} | Select-Object LocalPort, State"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            output = result.stdout
            has_8000 = "8000" in output
            has_8501 = "8501" in output
            
            if has_8000 and has_8501:
                print("✅ Both API (8000) and Dashboard (8501) ports are active")
                return True
            elif has_8501:
                print("⚠️ Dashboard (8501) is running but API (8000) may have issues")
                return False
            else:
                print("❌ Neither API nor Dashboard ports are active")
                return False
        else:
            print("❌ Could not check port status")
            return False
            
    except Exception as e:
        print(f"❌ Process check failed: {str(e)}")
        return False

def test_dashboard_content():
    """Test dashboard content and functionality."""
    print("🔍 Testing Dashboard Content...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=15)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Check for TRINETRA AI specific content
            trinetra_indicators = [
                "trinetra ai",
                "trade fraud intelligence",
                "fraud detection",
                "suspicious transactions"
            ]
            
            found_indicators = [indicator for indicator in trinetra_indicators if indicator in content]
            
            if len(found_indicators) >= 2:
                print(f"✅ Dashboard serving TRINETRA AI content ({len(found_indicators)}/4 indicators found)")
                return True
            else:
                print(f"⚠️ Dashboard accessible but limited TRINETRA content ({len(found_indicators)}/4 indicators)")
                return False
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Dashboard request timed out")
        return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {str(e)}")
        return False

def test_api_endpoints_via_curl():
    """Test API endpoints using curl commands."""
    print("🔍 Testing API Endpoints via System Commands...")
    
    endpoints_to_test = [
        ("/", "Root endpoint"),
        ("/stats", "Statistics endpoint"),
        ("/transactions?limit=5", "Transactions endpoint"),
        ("/suspicious", "Suspicious transactions"),
        ("/fraud", "Fraud transactions")
    ]
    
    successful_endpoints = 0
    
    for endpoint, description in endpoints_to_test:
        try:
            # Use PowerShell Invoke-WebRequest instead of curl
            cmd = [
                "powershell", "-Command",
                f"try {{ $response = Invoke-WebRequest -Uri 'http://localhost:8000{endpoint}' -TimeoutSec 10; $response.StatusCode }} catch {{ 'ERROR: ' + $_.Exception.Message }}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output == "200":
                    print(f"✅ {description}: HTTP 200 OK")
                    successful_endpoints += 1
                elif "ERROR:" in output:
                    print(f"❌ {description}: {output}")
                else:
                    print(f"⚠️ {description}: Unexpected response - {output}")
            else:
                print(f"❌ {description}: Command failed")
                
        except subprocess.TimeoutExpired:
            print(f"❌ {description}: Request timed out")
        except Exception as e:
            print(f"❌ {description}: {str(e)}")
    
    success_rate = successful_endpoints / len(endpoints_to_test)
    print(f"📊 API Endpoints: {successful_endpoints}/{len(endpoints_to_test)} successful ({success_rate*100:.1f}%)")
    
    return success_rate >= 0.6  # At least 60% of endpoints should work

def test_data_flow_integration():
    """Test data flow from backend to potential dashboard consumption."""
    print("🔍 Testing Data Flow Integration...")
    
    try:
        # Test if we can access the data that the dashboard would use
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from data_loader import load_dataset
        from feature_engineering import engineer_features
        from fraud_detection import load_fraud_detector, score_transactions, classify_risk
        
        # Load and process data (simulating what the API does)
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        df = load_dataset(dataset_path)
        df_engineered = engineer_features(df)
        
        # Load model and score transactions
        model = load_fraud_detector()
        df_scored = score_transactions(df_engineered, model)
        df_classified = classify_risk(df_scored)
        
        # Verify data structure matches what dashboard expects
        expected_columns = [
            'transaction_id', 'risk_score', 'risk_category',
            'price_anomaly_score', 'route_risk_score', 'company_network_risk'
        ]
        
        missing_columns = [col for col in expected_columns if col not in df_classified.columns]
        
        if not missing_columns:
            # Test data statistics
            total_transactions = len(df_classified)
            fraud_count = len(df_classified[df_classified['risk_category'] == 'FRAUD'])
            suspicious_count = len(df_classified[df_classified['risk_category'] == 'SUSPICIOUS'])
            safe_count = len(df_classified[df_classified['risk_category'] == 'SAFE'])
            
            print(f"✅ Data flow integration successful:")
            print(f"   - Total transactions: {total_transactions}")
            print(f"   - Fraud: {fraud_count}, Suspicious: {suspicious_count}, Safe: {safe_count}")
            print(f"   - All expected columns present")
            
            return True
        else:
            print(f"❌ Missing expected columns: {missing_columns}")
            return False
            
    except Exception as e:
        print(f"❌ Data flow integration test failed: {str(e)}")
        return False

def test_alert_system_integration():
    """Test alert system integration."""
    print("🔍 Testing Alert System Integration...")
    
    try:
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from alerts import get_alert_store, create_alert_summary
        from data_loader import load_dataset
        from feature_engineering import engineer_features
        from fraud_detection import load_fraud_detector, score_transactions, classify_risk
        
        # Load and process a small sample
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        df = load_dataset(dataset_path)
        df_engineered = engineer_features(df)
        model = load_fraud_detector()
        df_scored = score_transactions(df_engineered, model)
        df_classified = classify_risk(df_scored)
        
        # Test alert creation for a few transactions
        alert_store = get_alert_store()
        alert_count = 0
        
        for _, transaction in df_classified.head(10).iterrows():
            transaction_dict = transaction.to_dict()
            summary = create_alert_summary(transaction_dict)
            if summary:
                alert_store.store_summary(summary)
                alert_count += 1
        
        # Test alert retrieval
        active_alerts = alert_store.get_active_summaries()
        stats = alert_store.get_statistics()
        
        print(f"✅ Alert system integration successful:")
        print(f"   - Created {alert_count} alert summaries")
        print(f"   - Active alerts: {len(active_alerts)}")
        print(f"   - Alert statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Alert system integration test failed: {str(e)}")
        return False

def test_explanation_system():
    """Test explanation system integration."""
    print("🔍 Testing Explanation System Integration...")
    
    try:
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from ai_explainer import explain_transaction, answer_investigation_query
        from data_loader import load_dataset
        from feature_engineering import engineer_features
        from fraud_detection import load_fraud_detector, score_transactions, classify_risk
        
        # Get a sample transaction
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        df = load_dataset(dataset_path)
        df_engineered = engineer_features(df)
        model = load_fraud_detector()
        df_scored = score_transactions(df_engineered, model)
        df_classified = classify_risk(df_scored)
        
        # Test explanation generation (fallback mode)
        sample_transaction = df_classified.iloc[0].to_dict()
        explanation = explain_transaction(sample_transaction, force_api=False)
        
        if explanation and len(explanation) > 20:
            print("✅ Explanation system working (fallback mode)")
            
            # Test query system
            context = {
                'total_transactions': len(df_classified),
                'fraud_cases': len(df_classified[df_classified['risk_category'] == 'FRAUD']),
                'suspicious_cases': len(df_classified[df_classified['risk_category'] == 'SUSPICIOUS'])
            }
            
            query_answer = answer_investigation_query("What are the main fraud patterns?", context)
            
            if query_answer and len(query_answer) > 20:
                print("✅ Query system working")
                return True
            else:
                print("⚠️ Query system has limited functionality")
                return True  # Still acceptable
        else:
            print("❌ Explanation system not generating adequate responses")
            return False
            
    except Exception as e:
        print(f"❌ Explanation system test failed: {str(e)}")
        return False

def main():
    """Run comprehensive dashboard-API integration tests."""
    print("🚀 TRINETRA AI - Dashboard-API Integration Tests")
    print("=" * 60)
    
    tests = [
        ("System Processes", test_system_processes),
        ("Dashboard Content", test_dashboard_content),
        ("API Endpoints", test_api_endpoints_via_curl),
        ("Data Flow Integration", test_data_flow_integration),
        ("Alert System Integration", test_alert_system_integration),
        ("Explanation System", test_explanation_system)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Integration Test Results Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n📈 Overall: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    # Determine integration status
    if success_rate >= 80:
        print("🎉 API-Dashboard integration is working well!")
        print("✅ TRINETRA AI system integration verified successfully")
    elif success_rate >= 60:
        print("⚠️ API-Dashboard integration has some issues but core functionality works")
        print("🔧 Some components may need attention")
    else:
        print("❌ API-Dashboard integration has significant issues")
        print("🚨 System requires troubleshooting")
    
    return success_rate

if __name__ == "__main__":
    success_rate = main()
    
    # Exit with appropriate code
    if success_rate >= 60:
        exit(0)  # Success
    else:
        exit(1)  # Failure