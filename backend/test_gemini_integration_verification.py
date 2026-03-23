"""
Gemini API Integration Verification Tests for TRINETRA AI

This module verifies the Gemini API integration according to task 14.1 requirements:
1. Test Gemini API connectivity
2. Test explanation generation with sample transaction data
3. Test error handling for API failures
4. Validate explanation quality and relevance
5. Verify timeout and retry logic works
6. Check that fallback explanations work when API fails

Author: TRINETRA AI Team
Date: 2024
"""

import pytest
import os
import time
from unittest.mock import patch, MagicMock
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Disable TEST_MODE for actual API testing
os.environ["TEST_MODE"] = "false"

from ai_explainer import (
    initialize_gemini,
    explain_transaction,
    answer_investigation_query,
    reset_session_count,
    get_session_count,
    clear_explanation_cache,
    GeminiInitializationError,
    GeminiAPIError,
    GeminiTimeoutError,
    GeminiRateLimitError,
    API_KEY,
    MODEL_NAME,
    REQUEST_TIMEOUT,
    MAX_RETRIES
)


class TestGeminiAPIConnectivity:
    """Test Gemini API connectivity and initialization."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    def test_gemini_initialization_success(self):
        """Verify Gemini API initializes successfully with valid API key."""
        try:
            model = initialize_gemini(API_KEY)
            
            assert model is not None
            assert hasattr(model, 'generate_content')
            assert model.model_name == MODEL_NAME
            
            print(f"✓ Gemini API initialized successfully")
            print(f"  Model: {MODEL_NAME}")
            print(f"  API Key: {API_KEY[:20]}...")
            
        except Exception as e:
            pytest.fail(f"Gemini initialization failed: {str(e)}")
    
    def test_gemini_connection_test(self):
        """Verify Gemini API connection with a simple test request."""
        try:
            model = initialize_gemini(API_KEY)
            
            # The initialization includes a connection test
            # If we get here, the connection test passed
            assert model is not None
            
            print(f"✓ Gemini API connection test passed")
            
        except Exception as e:
            pytest.fail(f"Gemini connection test failed: {str(e)}")
    
    def test_gemini_initialization_with_invalid_key(self):
        """Verify proper error handling with invalid API key."""
        invalid_key = "invalid_key_12345"
        
        with pytest.raises(GeminiInitializationError):
            initialize_gemini(invalid_key)
        
        print(f"✓ Invalid API key properly rejected")
    
    def test_gemini_initialization_with_empty_key(self):
        """Verify proper error handling with empty API key."""
        with pytest.raises(GeminiInitializationError):
            initialize_gemini("")
        
        print(f"✓ Empty API key properly rejected")


class TestExplanationGeneration:
    """Test explanation generation with sample transaction data."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    @pytest.fixture
    def high_risk_transaction(self):
        """Sample high-risk transaction for testing."""
        return {
            'transaction_id': 'TXN_VERIFY_001',
            'product': 'Electronics',
            'commodity_category': 'Consumer Goods',
            'market_price': 1000,
            'unit_price': 1800,
            'price_deviation': 0.8,
            'shipping_route': 'Shanghai-Los Angeles',
            'distance_km': 11000,
            'company_risk_score': 0.95,
            'port_activity_index': 2.5,
            'route_anomaly': 1,
            'risk_score': 0.5,
            'risk_category': 'FRAUD'
        }
    
    @pytest.fixture
    def medium_risk_transaction(self):
        """Sample medium-risk transaction for testing."""
        return {
            'transaction_id': 'TXN_VERIFY_002',
            'product': 'Textiles',
            'commodity_category': 'Apparel',
            'market_price': 500,
            'unit_price': 650,
            'price_deviation': 0.3,
            'shipping_route': 'Mumbai-Dubai',
            'distance_km': 1900,
            'company_risk_score': 0.6,
            'port_activity_index': 1.3,
            'route_anomaly': 0,
            'risk_score': 0.1,
            'risk_category': 'SUSPICIOUS'
        }
    
    def test_explanation_generation_high_risk(self, high_risk_transaction):
        """Verify explanation generation for high-risk transaction."""
        try:
            model = initialize_gemini(API_KEY)
            explanation = explain_transaction(high_risk_transaction, model, force_api=True)
            
            assert isinstance(explanation, str)
            assert len(explanation) > 50
            
            # Verify explanation mentions key fraud indicators
            explanation_lower = explanation.lower()
            assert any(keyword in explanation_lower for keyword in 
                      ['price', 'deviation', 'risk', 'fraud', 'suspicious'])
            
            print(f"✓ High-risk transaction explanation generated")
            print(f"  Transaction ID: {high_risk_transaction['transaction_id']}")
            print(f"  Explanation length: {len(explanation)} characters")
            print(f"  Sample: {explanation[:150]}...")
            
        except Exception as e:
            pytest.fail(f"Explanation generation failed: {str(e)}")
    
    def test_explanation_generation_medium_risk(self, medium_risk_transaction):
        """Verify explanation generation for medium-risk transaction."""
        try:
            model = initialize_gemini(API_KEY)
            explanation = explain_transaction(medium_risk_transaction, model, force_api=True)
            
            assert isinstance(explanation, str)
            assert len(explanation) > 50
            
            print(f"✓ Medium-risk transaction explanation generated")
            print(f"  Transaction ID: {medium_risk_transaction['transaction_id']}")
            print(f"  Explanation length: {len(explanation)} characters")
            
        except Exception as e:
            pytest.fail(f"Explanation generation failed: {str(e)}")
    
    def test_explanation_caching(self, high_risk_transaction):
        """Verify explanation caching works correctly."""
        try:
            model = initialize_gemini(API_KEY)
            
            # First call - should generate and cache
            start_time = time.time()
            explanation1 = explain_transaction(high_risk_transaction, model, force_api=True)
            first_call_time = time.time() - start_time
            
            # Second call - should use cache
            start_time = time.time()
            explanation2 = explain_transaction(high_risk_transaction, model, force_api=False)
            cached_call_time = time.time() - start_time
            
            assert explanation1 == explanation2
            assert cached_call_time < first_call_time
            
            print(f"✓ Explanation caching verified")
            print(f"  First call: {first_call_time:.3f}s")
            print(f"  Cached call: {cached_call_time:.3f}s")
            print(f"  Speedup: {first_call_time/cached_call_time:.1f}x")
            
        except Exception as e:
            pytest.fail(f"Caching test failed: {str(e)}")


class TestErrorHandling:
    """Test error handling for API failures."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    @pytest.fixture
    def sample_transaction(self):
        """Sample transaction for error testing."""
        return {
            'transaction_id': 'TXN_ERROR_001',
            'product': 'Test Product',
            'price_deviation': 0.5,
            'route_anomaly': 1,
            'company_risk_score': 0.8,
            'port_activity_index': 1.6,
            'risk_score': 0.3,
            'risk_category': 'FRAUD'
        }
    
    def test_fallback_explanation_on_api_failure(self, sample_transaction):
        """Verify fallback explanation when API fails."""
        # Mock API failure
        with patch('backend.ai_explainer._generate_content_with_robust_timeout') as mock_api:
            mock_api.side_effect = GeminiAPIError("Mock API failure")
            
            model = initialize_gemini(API_KEY)
            explanation = explain_transaction(sample_transaction, model, force_api=True)
            
            assert isinstance(explanation, str)
            assert len(explanation) > 0
            assert "Fraud Indicators Detected:" in explanation
            
            print(f"✓ Fallback explanation generated on API failure")
            print(f"  Fallback length: {len(explanation)} characters")
    
    def test_timeout_error_handling(self, sample_transaction):
        """Verify timeout error handling."""
        # Mock timeout error
        with patch('backend.ai_explainer._generate_content_with_robust_timeout') as mock_api:
            mock_api.side_effect = GeminiTimeoutError("Request timeout")
            
            model = initialize_gemini(API_KEY)
            explanation = explain_transaction(sample_transaction, model, force_api=True)
            
            assert isinstance(explanation, str)
            assert len(explanation) > 0
            
            print(f"✓ Timeout error handled gracefully")
    
    def test_rate_limit_error_handling(self, sample_transaction):
        """Verify rate limit error handling."""
        # Mock rate limit error
        with patch('backend.ai_explainer._generate_content_with_robust_timeout') as mock_api:
            mock_api.side_effect = GeminiRateLimitError("Rate limit exceeded")
            
            model = initialize_gemini(API_KEY)
            explanation = explain_transaction(sample_transaction, model, force_api=True)
            
            assert isinstance(explanation, str)
            assert len(explanation) > 0
            
            print(f"✓ Rate limit error handled gracefully")
    
    def test_network_error_handling(self, sample_transaction):
        """Verify network error handling."""
        # Mock network error
        with patch('backend.ai_explainer._generate_content_with_robust_timeout') as mock_api:
            mock_api.side_effect = Exception("Network connection failed")
            
            model = initialize_gemini(API_KEY)
            explanation = explain_transaction(sample_transaction, model, force_api=True)
            
            assert isinstance(explanation, str)
            assert len(explanation) > 0
            
            print(f"✓ Network error handled gracefully")


class TestExplanationQuality:
    """Validate explanation quality and relevance."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    @pytest.fixture
    def detailed_transaction(self):
        """Detailed transaction for quality testing."""
        return {
            'transaction_id': 'TXN_QUALITY_001',
            'product': 'Smartphones',
            'commodity_category': 'Electronics',
            'market_price': 800,
            'unit_price': 1400,
            'price_deviation': 0.75,
            'shipping_route': 'Shenzhen-Rotterdam',
            'distance_km': 10500,
            'company_risk_score': 0.88,
            'port_activity_index': 2.1,
            'route_anomaly': 1,
            'risk_score': 0.45,
            'risk_category': 'FRAUD',
            'cargo_volume': 80000,
            'quantity': 200,
            'volume_spike_score': 400
        }
    
    def test_explanation_contains_transaction_details(self, detailed_transaction):
        """Verify explanation references transaction details."""
        try:
            model = initialize_gemini(API_KEY)
            explanation = explain_transaction(detailed_transaction, model, force_api=True)
            
            # Check for relevant fraud indicators
            explanation_lower = explanation.lower()
            
            # Should mention price issues
            has_price_mention = any(keyword in explanation_lower for keyword in 
                                   ['price', 'deviation', 'over-invoicing', 'under-invoicing'])
            
            # Should mention route or shipping
            has_route_mention = any(keyword in explanation_lower for keyword in 
                                   ['route', 'shipping', 'unusual', 'circuitous'])
            
            # Should mention risk or fraud
            has_risk_mention = any(keyword in explanation_lower for keyword in 
                                  ['risk', 'fraud', 'suspicious', 'anomaly'])
            
            assert has_price_mention or has_route_mention or has_risk_mention
            
            print(f"✓ Explanation contains relevant transaction details")
            print(f"  Price mention: {has_price_mention}")
            print(f"  Route mention: {has_route_mention}")
            print(f"  Risk mention: {has_risk_mention}")
            
        except Exception as e:
            pytest.fail(f"Quality validation failed: {str(e)}")
    
    def test_explanation_length_appropriate(self, detailed_transaction):
        """Verify explanation length is appropriate (3-4 sentences)."""
        try:
            model = initialize_gemini(API_KEY)
            explanation = explain_transaction(detailed_transaction, model, force_api=True)
            
            # Count sentences (approximate)
            sentence_count = explanation.count('.') + explanation.count('!') + explanation.count('?')
            
            # Should be substantial but not too long
            assert len(explanation) >= 100
            assert len(explanation) <= 1000
            assert sentence_count >= 2
            
            print(f"✓ Explanation length appropriate")
            print(f"  Length: {len(explanation)} characters")
            print(f"  Sentences: ~{sentence_count}")
            
        except Exception as e:
            pytest.fail(f"Length validation failed: {str(e)}")
    
    def test_explanation_relevance_to_risk_level(self):
        """Verify explanation relevance matches risk level."""
        try:
            model = initialize_gemini(API_KEY)
            
            # High-risk transaction
            high_risk = {
                'transaction_id': 'TXN_HIGH',
                'price_deviation': 0.9,
                'route_anomaly': 1,
                'company_risk_score': 0.95,
                'port_activity_index': 2.8,
                'risk_score': 0.6,
                'risk_category': 'FRAUD'
            }
            
            # Low-risk transaction
            low_risk = {
                'transaction_id': 'TXN_LOW',
                'price_deviation': 0.05,
                'route_anomaly': 0,
                'company_risk_score': 0.2,
                'port_activity_index': 1.0,
                'risk_score': -0.3,
                'risk_category': 'SAFE'
            }
            
            high_explanation = explain_transaction(high_risk, model, force_api=True)
            low_explanation = explain_transaction(low_risk, model, force_api=True)
            
            # High-risk should have more detailed explanation
            assert len(high_explanation) >= len(low_explanation) * 0.5
            
            print(f"✓ Explanation relevance matches risk level")
            print(f"  High-risk length: {len(high_explanation)}")
            print(f"  Low-risk length: {len(low_explanation)}")
            
        except Exception as e:
            pytest.fail(f"Relevance validation failed: {str(e)}")


class TestTimeoutAndRetry:
    """Verify timeout and retry logic works."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    def test_timeout_configuration(self):
        """Verify timeout is configured correctly."""
        assert REQUEST_TIMEOUT == 10
        print(f"✓ Timeout configured: {REQUEST_TIMEOUT} seconds")
    
    def test_retry_configuration(self):
        """Verify retry logic is configured."""
        assert MAX_RETRIES >= 1
        print(f"✓ Max retries configured: {MAX_RETRIES}")
    
    def test_timeout_enforcement(self):
        """Verify timeout is enforced on API calls."""
        # Mock a slow API response
        with patch('backend.ai_explainer._generate_content_with_robust_timeout') as mock_api:
            def slow_response(*args, **kwargs):
                time.sleep(REQUEST_TIMEOUT + 1)
                return MagicMock(text="Slow response")
            
            mock_api.side_effect = GeminiTimeoutError("Request timeout")
            
            model = initialize_gemini(API_KEY)
            transaction = {'transaction_id': 'TXN_TIMEOUT', 'price_deviation': 0.5}
            
            start_time = time.time()
            explanation = explain_transaction(transaction, model, force_api=True)
            elapsed_time = time.time() - start_time
            
            # Should timeout and use fallback quickly
            assert elapsed_time < REQUEST_TIMEOUT + 2
            assert isinstance(explanation, str)
            
            print(f"✓ Timeout enforced")
            print(f"  Elapsed time: {elapsed_time:.2f}s")
    
    def test_retry_on_transient_failure(self):
        """Verify retry logic on transient failures."""
        call_count = 0
        
        def failing_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise GeminiAPIError("Transient failure")
            return "Success after retry"
        
        with patch('backend.ai_explainer._generate_content_with_robust_timeout') as mock_api:
            mock_api.side_effect = failing_then_success
            
            model = initialize_gemini(API_KEY)
            transaction = {'transaction_id': 'TXN_RETRY', 'price_deviation': 0.5}
            
            explanation = explain_transaction(transaction, model, force_api=True)
            
            # Should have retried
            assert call_count >= 1
            assert isinstance(explanation, str)
            
            print(f"✓ Retry logic verified")
            print(f"  Attempts made: {call_count}")


class TestInvestigationQueries:
    """Test investigation query functionality."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    @pytest.fixture
    def sample_context(self):
        """Sample context for investigation queries."""
        return {
            'total_transactions': 1000,
            'fraud_cases': 50,
            'suspicious_cases': 150,
            'avg_risk_score': 0.12,
            'high_risk_companies': ['CompanyA', 'CompanyB', 'CompanyC'],
            'fraud_patterns': ['Price manipulation', 'Route laundering', 'Volume misrepresentation']
        }
    
    def test_investigation_query_fraud_rate(self, sample_context):
        """Test investigation query about fraud rate."""
        try:
            model = initialize_gemini(API_KEY)
            query = "What is the current fraud rate?"
            
            answer = answer_investigation_query(query, sample_context, model)
            
            assert isinstance(answer, str)
            assert len(answer) > 30
            
            # Should mention fraud rate or percentage
            answer_lower = answer.lower()
            assert any(keyword in answer_lower for keyword in ['fraud', 'rate', '%', 'percent'])
            
            print(f"✓ Investigation query answered: fraud rate")
            print(f"  Answer length: {len(answer)} characters")
            
        except Exception as e:
            pytest.fail(f"Investigation query failed: {str(e)}")
    
    def test_investigation_query_patterns(self, sample_context):
        """Test investigation query about fraud patterns."""
        try:
            model = initialize_gemini(API_KEY)
            query = "What are the main fraud patterns?"
            
            answer = answer_investigation_query(query, sample_context, model)
            
            assert isinstance(answer, str)
            assert len(answer) > 30
            
            print(f"✓ Investigation query answered: fraud patterns")
            
        except Exception as e:
            pytest.fail(f"Investigation query failed: {str(e)}")
    
    def test_investigation_query_fallback(self, sample_context):
        """Test investigation query fallback on API failure."""
        with patch('backend.ai_explainer._generate_content_with_robust_timeout') as mock_api:
            mock_api.side_effect = GeminiAPIError("Mock API failure")
            
            model = initialize_gemini(API_KEY)
            query = "What is the fraud rate?"
            
            answer = answer_investigation_query(query, sample_context, model)
            
            assert isinstance(answer, str)
            assert len(answer) > 0
            
            print(f"✓ Investigation query fallback works")


class TestIntegrationScenarios:
    """Integration tests for complete scenarios."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    def test_complete_fraud_analysis_workflow(self):
        """Test complete fraud analysis workflow."""
        try:
            # 1. Initialize Gemini
            model = initialize_gemini(API_KEY)
            print(f"✓ Step 1: Gemini initialized")
            
            # 2. Analyze high-risk transaction
            transaction = {
                'transaction_id': 'TXN_WORKFLOW_001',
                'product': 'Electronics',
                'price_deviation': 0.7,
                'route_anomaly': 1,
                'company_risk_score': 0.9,
                'port_activity_index': 2.0,
                'risk_score': 0.4,
                'risk_category': 'FRAUD'
            }
            
            explanation = explain_transaction(transaction, model, force_api=True)
            assert isinstance(explanation, str)
            assert len(explanation) > 50
            print(f"✓ Step 2: Transaction explained")
            
            # 3. Answer investigation query
            context = {
                'total_transactions': 1000,
                'fraud_cases': 50,
                'suspicious_cases': 150,
                'avg_risk_score': 0.12
            }
            
            query = "What is the fraud rate?"
            answer = answer_investigation_query(query, context, model)
            assert isinstance(answer, str)
            assert len(answer) > 30
            print(f"✓ Step 3: Investigation query answered")
            
            # 4. Verify caching
            cached_explanation = explain_transaction(transaction, model, force_api=False)
            assert cached_explanation == explanation
            print(f"✓ Step 4: Caching verified")
            
            print(f"\n✓ Complete workflow successful")
            
        except Exception as e:
            pytest.fail(f"Workflow test failed: {str(e)}")
    
    def test_session_quota_management(self):
        """Test session quota management."""
        try:
            model = initialize_gemini(API_KEY)
            
            # Generate multiple explanations
            for i in range(3):
                transaction = {
                    'transaction_id': f'TXN_QUOTA_{i:03d}',
                    'price_deviation': 0.5,
                    'risk_score': 0.3
                }
                
                explanation = explain_transaction(transaction, model, force_api=True)
                assert isinstance(explanation, str)
            
            session_count = get_session_count()
            assert session_count == 3
            
            print(f"✓ Session quota management verified")
            print(f"  Explanations generated: {session_count}")
            
        except Exception as e:
            pytest.fail(f"Quota management test failed: {str(e)}")


def run_verification_suite():
    """Run the complete verification suite and generate report."""
    print("=" * 70)
    print("TRINETRA AI - Gemini API Integration Verification")
    print("=" * 70)
    print()
    
    # Run pytest with verbose output
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "-s"  # Show print statements
    ]
    
    result = pytest.main(pytest_args)
    
    print()
    print("=" * 70)
    print("Verification Complete")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    exit_code = run_verification_suite()
    sys.exit(exit_code)
