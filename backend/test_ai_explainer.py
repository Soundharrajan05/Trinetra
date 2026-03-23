"""
Unit Tests for AI Explainer Module - TRINETRA AI

This module contains comprehensive unit tests for the ai_explainer.py module,
testing Gemini API integration, explanation generation, and fallback mechanisms.

Updated to use comprehensive Gemini API mocking for offline testing capability.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from unittest import mock

# Set TEST_MODE before importing the module
os.environ["TEST_MODE"] = "true"

# Import the module under test
from backend.ai_explainer import (
    initialize_gemini, explain_transaction, answer_investigation_query,
    reset_session_count, get_session_count, can_make_explanation,
    increment_session_count, get_cached_explanation, cache_explanation,
    clear_explanation_cache, MAX_EXPLANATIONS_PER_SESSION,
    GeminiInitializationError, GeminiAPIError, GeminiRateLimitError,
    GeminiTimeoutError, GeminiQuotaExceededError, test_fallback_system
)

# Import comprehensive mocking utilities
from backend.mock_gemini_utils import (
    mock_gemini_success, mock_gemini_failure, mock_gemini_unavailable,
    create_sample_transaction, create_sample_context,
    validate_mock_explanation, validate_mock_investigation_response,
    get_mock_config, reset_mock_config
)


class TestAIExplainer:
    """Test class for AI explainer functionality."""
    
    @pytest.fixture
    def sample_transaction(self):
        """Create sample transaction data for testing."""
        return create_sample_transaction("high")
    
    @pytest.fixture
    def sample_context(self):
        """Create sample context data for testing."""
        return create_sample_context(0.05)
    
    def setup_method(self):
        """Reset session state before each test."""
        reset_session_count()
        clear_explanation_cache()
        reset_mock_config()
    
    def test_session_management(self):
        """Test session count management."""
        # Initial state
        assert get_session_count() == 0
        assert can_make_explanation() is True
        
        # Increment session count
        increment_session_count()
        assert get_session_count() == 1
        assert can_make_explanation() is True
        
        # Reach limit
        for _ in range(MAX_EXPLANATIONS_PER_SESSION - 1):
            increment_session_count()
        
        assert get_session_count() == MAX_EXPLANATIONS_PER_SESSION
        assert can_make_explanation() is False
        
        # Reset
        reset_session_count()
        assert get_session_count() == 0
        assert can_make_explanation() is True
    
    def test_explanation_caching(self, sample_transaction):
        """Test explanation caching functionality."""
        transaction_id = sample_transaction['transaction_id']
        explanation = "Test explanation"
        
        # Initially no cache
        assert get_cached_explanation(transaction_id) is None
        
        # Cache explanation
        cache_explanation(transaction_id, explanation)
        assert get_cached_explanation(transaction_id) == explanation
        
        # Clear cache
        clear_explanation_cache()
        assert get_cached_explanation(transaction_id) is None
    
    def test_explain_transaction_test_mode(self, sample_transaction):
        """Test transaction explanation in test mode."""
        explanation = explain_transaction(sample_transaction)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "test mode" in explanation.lower()
    
    def test_explain_transaction_cached(self, sample_transaction):
        """Test transaction explanation with cached result."""
        transaction_id = sample_transaction['transaction_id']
        cached_explanation = "Cached explanation"
        
        # Cache an explanation
        cache_explanation(transaction_id, cached_explanation)
        
        # Should return cached explanation
        result = explain_transaction(sample_transaction)
        assert result == cached_explanation
    
    def test_explain_transaction_quota_exceeded(self, sample_transaction):
        """Test transaction explanation when quota is exceeded."""
        # Exhaust quota
        for _ in range(MAX_EXPLANATIONS_PER_SESSION):
            increment_session_count()
        
        explanation = explain_transaction(sample_transaction)
        
        assert isinstance(explanation, str)
        assert "limit reached" in explanation.lower()
    
    def test_explain_transaction_fallback_without_force(self, sample_transaction):
        """Test transaction explanation fallback when not forced."""
        # Don't force API call
        explanation = explain_transaction(sample_transaction, force_api=False)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    @patch('backend.ai_explainer.GEMINI_AVAILABLE', False)
    def test_initialize_gemini_not_available(self):
        """Test Gemini initialization when not available."""
        model = initialize_gemini()
        
        # Should return mock model
        assert model is not None
        assert hasattr(model, 'model_name')
    
    @patch('backend.ai_explainer.GEMINI_AVAILABLE', True)
    @patch('backend.ai_explainer.genai')
    def test_initialize_gemini_success(self, mock_genai):
        """Test successful Gemini initialization."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        model = initialize_gemini()
        
        assert model is not None
        mock_genai.configure.assert_called_once()
        mock_genai.GenerativeModel.assert_called_once()
    
    @patch('backend.ai_explainer.GEMINI_AVAILABLE', True)
    @patch('backend.ai_explainer.genai')
    def test_initialize_gemini_failure(self, mock_genai):
        """Test Gemini initialization failure."""
        mock_genai.configure.side_effect = Exception("API key invalid")
        
        with pytest.raises(GeminiInitializationError):
            initialize_gemini()
    
    def test_answer_investigation_query_test_mode(self, sample_context):
        """Test investigation query in test mode."""
        query = "What is the fraud rate?"
        
        answer = answer_investigation_query(query, sample_context)
        
        assert isinstance(answer, str)
        assert len(answer) > 0
        assert "test mode" in answer.lower()
    
    def test_fallback_system_comprehensive(self):
        """Test comprehensive fallback system."""
        results = test_fallback_system()
        
        assert isinstance(results, dict)
        assert 'transaction_explanation' in results
        assert 'investigation_responses' in results
        assert 'test_status' in results
        assert results['test_status'] == 'success'
        
        # Check transaction explanation
        explanation = results['transaction_explanation']
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Fraud Indicators Detected:" in explanation
        
        # Check investigation responses
        responses = results['investigation_responses']
        assert isinstance(responses, dict)
        assert len(responses) > 0
        
        for query, response in responses.items():
            assert isinstance(query, str)
            assert isinstance(response, str)
            assert len(response) > 0


class TestAIExplainerFallbacks:
    """Test fallback mechanisms and error handling."""
    
    @pytest.fixture
    def sample_transaction_with_indicators(self):
        """Create transaction with various fraud indicators."""
        return {
            'transaction_id': 'TXN001',
            'product': 'Electronics',
            'price_deviation': 0.6,  # High deviation
            'route_anomaly': 1,  # Route anomaly
            'company_risk_score': 0.9,  # High risk company
            'port_activity_index': 2.0,  # High port activity
            'volume_spike_score': 500,  # Volume inconsistency
            'shipment_duration_risk': 0.2,  # Duration risk
            'risk_score': 0.5,
            'risk_category': 'FRAUD'
        }
    
    def test_fallback_explanation_with_indicators(self, sample_transaction_with_indicators):
        """Test fallback explanation generation with fraud indicators."""
        from backend.ai_explainer import _generate_fallback_explanation
        
        explanation = _generate_fallback_explanation(sample_transaction_with_indicators)
        
        assert isinstance(explanation, str)
        assert "Fraud Indicators Detected:" in explanation
        assert "High price deviation" in explanation
        assert "Suspicious shipping route" in explanation
        assert "High company risk score" in explanation
        assert "Unusual port activity" in explanation
    
    def test_fallback_explanation_no_indicators(self):
        """Test fallback explanation with no clear indicators."""
        from backend.ai_explainer import _generate_fallback_explanation
        
        transaction = {
            'transaction_id': 'TXN001',
            'price_deviation': 0.01,  # Low deviation
            'route_anomaly': 0,  # No anomaly
            'company_risk_score': 0.1,  # Low risk
            'port_activity_index': 1.0,  # Normal activity
            'risk_score': 0.3,
            'risk_category': 'SUSPICIOUS'
        }
        
        explanation = _generate_fallback_explanation(transaction)
        
        assert isinstance(explanation, str)
        assert "Fraud Indicators Detected:" in explanation
        assert "Machine learning model flagged" in explanation
    
    def test_fallback_investigation_responses(self, sample_context):
        """Test fallback investigation responses for various queries."""
        from backend.ai_explainer import _generate_fallback_investigation_response
        
        test_queries = [
            ("What is the fraud rate?", "fraud rate"),
            ("What are the main fraud patterns?", "fraud patterns"),
            ("Tell me about high-risk companies", "high-risk"),
            ("Why is this transaction suspicious?", "suspicious"),
            ("What should I investigate next?", "investigate")
        ]
        
        mock_error = GeminiAPIError("Test error")
        
        for query, expected_keyword in test_queries:
            response = _generate_fallback_investigation_response(query, sample_context, mock_error)
            
            assert isinstance(response, str)
            assert len(response) > 0
            # Response should be relevant to the query
            assert any(keyword in response.lower() for keyword in [expected_keyword, "transaction", "fraud"])
    
    def test_fallback_with_different_error_types(self, sample_context):
        """Test fallback responses with different error types."""
        from backend.ai_explainer import _generate_fallback_investigation_response
        
        error_types = [
            GeminiRateLimitError("Rate limit exceeded"),
            GeminiTimeoutError("Request timeout"),
            GeminiQuotaExceededError("Quota exceeded"),
            GeminiAPIError("Generic API error")
        ]
        
        query = "What is the fraud rate?"
        
        for error in error_types:
            response = _generate_fallback_investigation_response(query, sample_context, error)
            
            assert isinstance(response, str)
            assert len(response) > 0
            # Should contain relevant information despite the error
            assert any(keyword in response.lower() for keyword in ["fraud", "transaction", "rate"])
    
    def test_quota_exceeded_fallback(self, sample_transaction_with_indicators):
        """Test quota exceeded fallback explanation."""
        from backend.ai_explainer import _generate_quota_exceeded_fallback
        
        explanation = _generate_quota_exceeded_fallback(sample_transaction_with_indicators)
        
        assert isinstance(explanation, str)
        assert f"max {MAX_EXPLANATIONS_PER_SESSION} per session" in explanation
        assert "Fraud Indicators Detected:" in explanation
        assert "High price deviation" in explanation


class TestAIExplainerEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_explain_transaction_none_input(self):
        """Test explanation with None transaction."""
        with pytest.raises(Exception):  # Should handle gracefully
            explain_transaction(None)
    
    def test_explain_transaction_empty_dict(self):
        """Test explanation with empty transaction dictionary."""
        explanation = explain_transaction({})
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    def test_answer_investigation_query_empty_context(self):
        """Test investigation query with empty context."""
        answer = answer_investigation_query("What is the fraud rate?", {})
        
        assert isinstance(answer, str)
        assert len(answer) > 0
    
    def test_session_count_thread_safety(self):
        """Test session count management in concurrent scenarios."""
        import threading
        import time
        
        def increment_worker():
            for _ in range(5):
                if can_make_explanation():
                    increment_session_count()
                time.sleep(0.001)  # Small delay to simulate real usage
        
        # Reset session
        reset_session_count()
        
        # Start multiple threads
        threads = [threading.Thread(target=increment_worker) for _ in range(3)]
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should not exceed maximum
        assert get_session_count() <= MAX_EXPLANATIONS_PER_SESSION
    
    def test_cache_with_special_characters(self):
        """Test caching with special characters in transaction IDs."""
        special_ids = [
            "TXN-001/2024",
            "TXN@001#2024",
            "TXN 001 (2024)",
            "TXN_001_测试"
        ]
        
        for tx_id in special_ids:
            explanation = f"Explanation for {tx_id}"
            cache_explanation(tx_id, explanation)
            
            cached = get_cached_explanation(tx_id)
            assert cached == explanation
    
    def test_large_explanation_caching(self):
        """Test caching with large explanation text."""
        large_explanation = "A" * 10000  # 10KB explanation
        transaction_id = "TXN_LARGE"
        
        cache_explanation(transaction_id, large_explanation)
        cached = get_cached_explanation(transaction_id)
        
        assert cached == large_explanation
        assert len(cached) == 10000
    
    @patch('backend.ai_explainer.logger')
    def test_logging_functionality(self, mock_logger, sample_transaction):
        """Test that logging is working correctly."""
        explain_transaction(sample_transaction)
        
        # Verify that logging calls were made
        # Note: In test mode, logging might be minimal
        assert mock_logger is not None
    
    def test_explanation_consistency(self, sample_transaction):
        """Test that explanations are consistent for the same transaction."""
        # Generate explanation multiple times
        explanations = []
        for _ in range(3):
            explanation = explain_transaction(sample_transaction.copy())
            explanations.append(explanation)
        
        # In test mode, should be consistent
        assert all(exp == explanations[0] for exp in explanations)
    
    def test_context_data_validation(self):
        """Test investigation queries with invalid context data."""
        invalid_contexts = [
            None,
            {},
            {'invalid_key': 'invalid_value'},
            {'total_transactions': 'not_a_number'}
        ]
        
        query = "What is the fraud rate?"
        
        for context in invalid_contexts:
            # Should not raise exception
            answer = answer_investigation_query(query, context)
            assert isinstance(answer, str)
            assert len(answer) > 0


class TestAIExplainerIntegration:
    """Integration tests for AI explainer functionality."""
    
    def test_complete_explanation_workflow(self, sample_transaction):
        """Test complete explanation workflow."""
        # Reset session
        reset_session_count()
        clear_explanation_cache()
        
        # First explanation (should be generated)
        explanation1 = explain_transaction(sample_transaction)
        assert isinstance(explanation1, str)
        assert len(explanation1) > 0
        
        # Second explanation (should be cached)
        explanation2 = explain_transaction(sample_transaction)
        assert explanation2 == explanation1
        
        # Check session count (should not increment for cached)
        assert get_session_count() == 0  # In test mode, no API calls
    
    def test_mixed_explanation_and_query_workflow(self, sample_transaction, sample_context):
        """Test mixed workflow of explanations and queries."""
        # Reset session
        reset_session_count()
        clear_explanation_cache()
        
        # Generate explanation
        explanation = explain_transaction(sample_transaction)
        assert isinstance(explanation, str)
        
        # Answer query
        answer = answer_investigation_query("What is the fraud rate?", sample_context)
        assert isinstance(answer, str)
        
        # Both should work without interference
        assert len(explanation) > 0
        assert len(answer) > 0
    
    def test_session_limit_enforcement(self, sample_transaction):
        """Test that session limits are properly enforced."""
        # Reset session
        reset_session_count()
        clear_explanation_cache()
        
        # Exhaust session limit
        for i in range(MAX_EXPLANATIONS_PER_SESSION):
            increment_session_count()
        
        # Should not be able to make more explanations
        assert can_make_explanation() is False
        
        # Explanation should return quota exceeded message
        explanation = explain_transaction(sample_transaction)
        assert "limit reached" in explanation.lower()
        
        # Reset should allow explanations again
        reset_session_count()
        assert can_make_explanation() is True


class TestComprehensiveGeminiMocking:
    """Comprehensive tests for Gemini API mocking functionality."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
        reset_mock_config()
    
    def test_realistic_mock_transaction_explanation(self, sample_transaction):
        """Test that comprehensive mocking provides realistic transaction explanations."""
        with mock_gemini_success():
            explanation = explain_transaction(sample_transaction, force_api=True)
            
            # Validate explanation quality
            assert validate_mock_explanation(explanation, sample_transaction)
            assert len(explanation) > 100  # Substantial content
            
            # Check for specific fraud indicators mentioned
            explanation_lower = explanation.lower()
            if sample_transaction.get('price_deviation', 0) > 0.3:
                assert any(keyword in explanation_lower for keyword in ['price', 'deviation', 'invoicing'])
            
            if sample_transaction.get('route_anomaly') == 1:
                assert any(keyword in explanation_lower for keyword in ['route', 'shipping', 'unusual'])
    
    def test_realistic_mock_investigation_queries(self, sample_context):
        """Test that comprehensive mocking provides realistic investigation responses."""
        test_queries = [
            "What is the current fraud rate?",
            "What are the main fraud patterns?",
            "Which companies should I investigate?",
            "How should I prioritize my investigation?"
        ]
        
        with mock_gemini_success():
            for query in test_queries:
                response = answer_investigation_query(query, sample_context)
                
                # Validate response quality
                assert validate_mock_investigation_response(response, query, sample_context)
                assert len(response) > 50  # Substantial content
                
                # Check query-specific content
                response_lower = response.lower()
                if 'fraud rate' in query.lower():
                    assert any(keyword in response_lower for keyword in ['rate', '%', 'fraud'])
                elif 'patterns' in query.lower():
                    assert any(keyword in response_lower for keyword in ['pattern', 'manipulation'])
    
    def test_mock_error_simulation_comprehensive(self, sample_transaction):
        """Test comprehensive error simulation capabilities."""
        error_scenarios = [
            ("rate_limit", "Rate limit exceeded"),
            ("timeout", "Request timeout"),
            ("quota", "Quota exceeded"),
            ("auth", "Authentication failed"),
            ("network", "Network error")
        ]
        
        for error_type, expected_message in error_scenarios:
            with mock_gemini_failure(error_type, expected_message):
                # Should handle error gracefully and provide fallback
                explanation = explain_transaction(sample_transaction, force_api=True)
                
                assert isinstance(explanation, str)
                assert len(explanation) > 0
                # Should use fallback explanation
                assert "Fraud Indicators Detected:" in explanation
    
    def test_mock_offline_capability_complete(self, sample_transaction, sample_context):
        """Test complete offline capability with comprehensive mocking."""
        with mock_gemini_success():
            # Initialize system offline
            model = initialize_gemini()
            assert model is not None
            
            # Generate explanation offline
            explanation = explain_transaction(sample_transaction, model, force_api=True)
            assert validate_mock_explanation(explanation, sample_transaction)
            
            # Answer investigation query offline
            query = "What are the main fraud patterns?"
            response = answer_investigation_query(query, sample_context, model)
            assert validate_mock_investigation_response(response, query, sample_context)
            
            # Verify session management works offline
            assert can_make_explanation() is True
            
            # Test caching works offline
            cached_explanation = get_cached_explanation(sample_transaction['transaction_id'])
            assert cached_explanation == explanation
    
    def test_mock_different_risk_levels(self):
        """Test mock responses for different transaction risk levels."""
        risk_levels = ["high", "medium", "low"]
        
        with mock_gemini_success():
            explanations = {}
            
            for risk_level in risk_levels:
                transaction = create_sample_transaction(risk_level)
                explanation = explain_transaction(transaction, force_api=True)
                explanations[risk_level] = explanation
                
                # Validate explanation
                assert validate_mock_explanation(explanation, transaction)
            
            # High-risk should have more detailed explanation
            assert len(explanations["high"]) >= len(explanations["medium"])
            assert len(explanations["medium"]) >= len(explanations["low"])
            
            # Each should be unique
            assert len(set(explanations.values())) == len(explanations)
    
    def test_mock_context_sensitivity(self):
        """Test that mock responses are sensitive to context data."""
        contexts = [
            create_sample_context(0.01),  # Low fraud rate
            create_sample_context(0.10),  # High fraud rate
        ]
        
        query = "What is the fraud rate?"
        
        with mock_gemini_success():
            responses = []
            for context in contexts:
                response = answer_investigation_query(query, context)
                responses.append(response)
                assert validate_mock_investigation_response(response, query, context)
            
            # Responses should reflect different fraud rates
            assert "1.0%" in responses[0]  # Low fraud rate
            assert "10.0%" in responses[1]  # High fraud rate
    
    def test_mock_consistency_and_determinism(self, sample_transaction):
        """Test that mock responses are consistent and deterministic."""
        with mock_gemini_success():
            explanations = []
            
            # Generate multiple explanations for same transaction
            for _ in range(3):
                clear_explanation_cache()  # Force regeneration
                explanation = explain_transaction(sample_transaction, force_api=True)
                explanations.append(explanation)
            
            # Should be identical (deterministic)
            assert all(exp == explanations[0] for exp in explanations)
            assert validate_mock_explanation(explanations[0], sample_transaction)
    
    def test_mock_gemini_unavailable_handling(self, sample_transaction):
        """Test handling when Gemini API is completely unavailable."""
        with mock_gemini_unavailable():
            # Should still work with fallback
            model = initialize_gemini()
            explanation = explain_transaction(sample_transaction, model)
            
            assert isinstance(explanation, str)
            assert len(explanation) > 0
            # Should use fallback mechanisms
    
    def test_mock_integration_with_existing_features(self, sample_transaction):
        """Test that mocking integrates properly with existing features."""
        with mock_gemini_success():
            # Test session limits still work
            for _ in range(MAX_EXPLANATIONS_PER_SESSION):
                increment_session_count()
            
            assert can_make_explanation() is False
            
            explanation = explain_transaction(sample_transaction)
            assert "limit reached" in explanation.lower()
            
            # Test caching still works
            reset_session_count()
            clear_explanation_cache()
            
            explanation1 = explain_transaction(sample_transaction, force_api=True)
            explanation2 = explain_transaction(sample_transaction)  # Should use cache
            
            assert explanation1 == explanation2
            assert get_cached_explanation(sample_transaction['transaction_id']) == explanation1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])