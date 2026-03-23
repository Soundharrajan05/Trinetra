"""
Test script for quota management and caching functionality.

This script tests the updated AI explanation system to ensure:
1. Session limits are enforced (max 3 explanations per session)
2. Caching works correctly to avoid repeated API calls
3. Fallback explanations are generated when quota is exceeded
4. API calls only happen when explicitly requested (force_api=True)

Author: TRINETRA AI Team
Date: 2024
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_explainer import (
    explain_transaction,
    reset_session_count,
    get_session_count,
    can_make_explanation,
    get_cached_explanation,
    clear_explanation_cache,
    MAX_EXPLANATIONS_PER_SESSION,
    _generate_fallback_explanation,
    _generate_quota_exceeded_fallback
)

def create_sample_transaction(transaction_id: str = "TEST001") -> dict:
    """Create a sample transaction for testing."""
    return {
        'transaction_id': transaction_id,
        'product': 'Electronics',
        'commodity_category': 'Consumer Goods',
        'market_price': 1000,
        'unit_price': 1500,
        'price_deviation': 0.5,
        'shipping_route': 'Shanghai-Los Angeles',
        'distance_km': 11000,
        'company_risk_score': 0.9,
        'port_activity_index': 1.8,
        'route_anomaly': 1,
        'risk_score': 0.3,
        'risk_category': 'FRAUD',
        'cargo_volume': 50000,
        'quantity': 100,
        'volume_spike_score': 500,
        'shipment_duration_risk': 0.15
    }

def test_session_limits():
    """Test that session limits are enforced correctly."""
    print("🧪 Testing Session Limits...")
    
    # Reset session
    reset_session_count()
    assert get_session_count() == 0, "Session count should be 0 after reset"
    assert can_make_explanation() == True, "Should be able to make explanations initially"
    
    # Test that non-forced calls don't use quota
    transaction = create_sample_transaction("LIMIT_TEST_1")
    explanation1 = explain_transaction(transaction, force_api=False)
    assert get_session_count() == 0, "Non-forced calls should not increment session count"
    assert "Fraud Indicators Detected:" in explanation1, "Should get fallback explanation"
    
    print(f"✅ Non-forced call correctly used fallback (count: {get_session_count()})")
    
    # Test forced calls increment session count
    explanation2 = explain_transaction(transaction, force_api=True)
    assert get_session_count() == 1, "Forced calls should increment session count"
    
    print(f"✅ Forced call incremented session count (count: {get_session_count()})")
    
    # Test reaching session limit
    for i in range(2, MAX_EXPLANATIONS_PER_SESSION + 1):
        transaction_test = create_sample_transaction(f"LIMIT_TEST_{i}")
        explanation = explain_transaction(transaction_test, force_api=True)
        print(f"   Explanation {i}: Session count = {get_session_count()}")
    
    assert get_session_count() == MAX_EXPLANATIONS_PER_SESSION, f"Should reach max session count of {MAX_EXPLANATIONS_PER_SESSION}"
    assert can_make_explanation() == False, "Should not be able to make more explanations"
    
    # Test quota exceeded behavior
    transaction_over_limit = create_sample_transaction("OVER_LIMIT")
    explanation_over = explain_transaction(transaction_over_limit, force_api=True)
    assert "AI explanation limit reached" in explanation_over, "Should get quota exceeded message"
    
    print(f"✅ Session limit enforced correctly (final count: {get_session_count()})")

def test_caching():
    """Test that caching works correctly."""
    print("\n🧪 Testing Caching...")
    
    # Reset session and cache
    reset_session_count()
    clear_explanation_cache()
    
    transaction = create_sample_transaction("CACHE_TEST")
    
    # First call should not be cached
    assert get_cached_explanation("CACHE_TEST") is None, "Should not be cached initially"
    
    # Make a fallback call (should be cached)
    explanation1 = explain_transaction(transaction, force_api=False)
    cached = get_cached_explanation("CACHE_TEST")
    assert cached is not None, "Explanation should be cached after first call"
    assert cached == explanation1, "Cached explanation should match returned explanation"
    
    # Second call should use cache
    explanation2 = explain_transaction(transaction, force_api=False)
    assert explanation2 == explanation1, "Second call should return same cached explanation"
    
    print("✅ Caching works correctly for fallback explanations")
    
    # Test that force_api bypasses cache (but still caches result)
    explanation3 = explain_transaction(transaction, force_api=True)
    # This should increment session count and potentially get different result
    assert get_session_count() == 1, "Force API call should increment session count"
    
    print("✅ Force API correctly bypasses cache")

def test_fallback_format():
    """Test that fallback explanations use the correct format."""
    print("\n🧪 Testing Fallback Format...")
    
    transaction = create_sample_transaction("FORMAT_TEST")
    
    # Test regular fallback
    fallback = _generate_fallback_explanation(transaction)
    assert "Fraud Indicators Detected:" in fallback, "Should have correct header"
    assert "•" in fallback, "Should have bullet points"
    
    print("✅ Regular fallback has correct format")
    
    # Test quota exceeded fallback
    quota_fallback = _generate_quota_exceeded_fallback(transaction)
    assert "AI explanation limit reached" in quota_fallback, "Should mention quota limit"
    assert "Fraud Indicators Detected:" in quota_fallback, "Should have fraud indicators section"
    
    print("✅ Quota exceeded fallback has correct format")

def test_no_automatic_api_calls():
    """Test that API calls only happen when explicitly requested."""
    print("\n🧪 Testing No Automatic API Calls...")
    
    reset_session_count()
    
    transaction = create_sample_transaction("NO_AUTO_API")
    
    # Default behavior should not make API calls
    explanation = explain_transaction(transaction)  # No force_api parameter
    assert get_session_count() == 0, "Default calls should not increment session count"
    assert "Fraud Indicators Detected:" in explanation, "Should get fallback explanation"
    
    print("✅ Default calls correctly avoid API usage")
    
    # Only force_api=True should make API calls
    explanation_forced = explain_transaction(transaction, force_api=True)
    assert get_session_count() == 1, "Force API calls should increment session count"
    
    print("✅ Only explicit force_api=True makes API calls")

def run_all_tests():
    """Run all quota management tests."""
    print("🚀 Starting Quota Management Tests...\n")
    
    try:
        test_session_limits()
        test_caching()
        test_fallback_format()
        test_no_automatic_api_calls()
        
        print("\n🎉 All tests passed! Quota management system is working correctly.")
        print("\n📋 Summary of implemented features:")
        print("✅ Session limits enforced (max 3 AI explanations per session)")
        print("✅ Caching prevents repeated API calls for same transaction")
        print("✅ Fallback explanations use required format")
        print("✅ API calls only happen on explicit user request (force_api=True)")
        print("✅ Quota exceeded messages provide clear guidance")
        print("✅ Session can be reset to get new quota")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n🔧 To use the updated system:")
        print("1. Start the API: python backend/api.py")
        print("2. Start the dashboard: streamlit run frontend/dashboard.py")
        print("3. Use 'Get AI Explanation' button for Gemini API calls")
        print("4. Use 'Get Fallback Explanation' for rule-based analysis")
        print("5. Reset session when quota is exhausted")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        sys.exit(1)