"""
Unit Tests for Gemini API Mocking - TRINETRA AI

This module provides focused unit tests for Gemini API mocking functionality,
ensuring that external dependencies can be properly mocked for offline testing.

Key Features:
- Mock Gemini API initialization and configuration
- Mock transaction explanation generation
- Mock investigation query responses
- Error simulation and handling
- Offline testing capability

Author: TRINETRA AI Team
Date: 2024
"""

import pytest
import os
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any

# Ensure we're not in TEST_MODE for these specific mocking tests
os.environ["TEST_MODE"] = "false"

# Import the AI explainer module
from backend.ai_explainer import (
    initialize_gemini, explain_transaction, answer_investigation_query,
    reset_session_count, clear_explanation_cache,
    GeminiInitializationError, GeminiAPIError
)


class MockGeminiResponse:
    """Mock response that mimics Gemini API response structure."""
    
    def __init__(self, text: str):
        self.text = text


class TestGeminiMockingBasics:
    """Basic tests for Gemini API mocking functionality."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    @patch('backend.ai_explainer.GEMINI_AVAILABLE', True)
    @patch('backend.ai_explainer.genai')
    def test_mock_gemini_initialization_success(self, mock_genai):
        """Test successful Gemini initialization with mocking."""
        # Configure mock
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.return_value = MockGeminiResponse("OK")
        
        # Test initialization
        model = initialize_gemini()
        
        # Verify calls
        mock_genai.configure.assert_called_once()
        mock_genai.GenerativeModel.assert_called_once()
        assert model is not None
    
    @patch('backend.ai_explainer.GEMINI_AVAILABLE', True)
    @patch('backend.ai_explainer.genai')
    def test_mock_gemini_initialization_failure(self, mock_genai):
        """Test Gemini initialization failure with mocking."""
        # Configure mock to fail
        mock_genai.configure.side_effect = Exception("Invalid API key")
        
        # Test initialization failure
        with pytest.raises(GeminiInitializationError):
            initialize_gemini()
    
    @patch('backend.ai_explainer.GEMINI_AVAILABLE', True)
    @patch('backend.ai_explainer.genai')
    def test_mock_transaction_explanation_basic(self, mock_genai):
        """Test basic transaction explanation with mocking."""
        # Configure mock
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Mock responses
        mock_model.generate_content.side_effect = [
            MockGeminiResponse("OK"),  # For initialization test
            MockGeminiResponse("This transaction shows suspicious pricing patterns indicating potential fraud.")
        ]
        
        # Sample transaction
        transaction = {
            'transaction_id': 'TXN001',
            'price_deviation': 0.5,
            'route_anomaly': 1,
            'company_risk_score': 0.8
        }
        
        # Test explanation generation
        explanation = explain_transaction(transaction, force_api=True)
        
        # Verify result
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "suspicious" in explanation.lower()
        
        # Verify mock was called
        assert mock_model.generate_content.call_count >= 1
    
    @patch('backend.ai_explainer.GEMINI_AVAILABLE', True)
    @patch('backend.ai_explainer.genai')
    def test_mock_investigation_query_basic(self, mock_genai):
        """Test basic investigation query with mocking."""
        # Configure mock
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Mock responses
        mock_model.generate_content.side_effect = [
            MockGeminiResponse("OK"),  # For initialization test
            MockGeminiResponse("Based on the analysis, 5% of transactions are fraudulent.")
        ]
        
        # Sample context
        context = {
            'total_transactions': 1000,
            'fraud_cases': 50,
            'suspicious_cases': 100
        }
        
        # Test query response
        query = "What is the fraud rate?"
        response = answer_investigation_query(query, context)
        
        # Verify result
        assert isinstance(response, str)
        assert len(response) > 0
        assert any(keyword in response.lower() for keyword in ['fraud', 'analysis', 'transactions'])
        
        # Verify mock was called
        assert mock_model.generate_content.call_count >= 1
    
    @patch('backend.ai_explainer.GEMINI_AVAILABLE', True)
    @patch('backend.ai_explainer.genai')
    def test_mock_api_error_handling(self, mock_genai):
        """Test API error handling with mocking."""
        # Configure mock
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Mock initialization success, then API failure
        mock_model.generate_content.side_effect = [
            MockGeminiResponse("OK"),  # For initialization test
            Exception("API Error")     # For explanation call
        ]
        
        # Sample transaction
        transaction = {
            'transaction_id': 'TXN001',
            'price_deviation': 0.5
        }
        
        # Test error handling - should not raise exception
        explanation = explain_transaction(transaction, force_api=True)
        
        # Should return fallback explanation
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        # Should contain fallback content
        assert any(keyword in explanation.lower() for keyword in ['fraud indicators', 'detected', 'analysis'])
    
    @patch('backend.ai_explainer.GEMINI_AVAILABLE', False)
    def test_mock_gemini_unavailable(self):
        """Test behavior when Gemini is unavailable."""
        # Test initialization with unavailable Gemini
        model = initialize_gemini()
        
        # Should return mock model
        assert model is not None
        
        # Test explanation with unavailable Gemini
        transaction = {'transaction_id': 'TXN001'}
        explanation = explain_transaction(transaction, model)
        
        # Should work with fallback
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    def test_mock_realistic_explanation_content(self):
        """Test that mocked explanations contain realistic fraud analysis content."""
        with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
             patch('backend.ai_explainer.genai') as mock_genai:
            
            # Configure realistic mock response
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            realistic_explanation = """
            This transaction exhibits several fraud indicators: The price deviation of 50% above market value 
            suggests over-invoicing, commonly used for money laundering. The unusual shipping route indicates 
            potential trade route laundering to obscure the true origin of goods. The high company risk score 
            of 0.8 suggests previous involvement in suspicious activities.
            """
            
            mock_model.generate_content.side_effect = [
                MockGeminiResponse("OK"),
                MockGeminiResponse(realistic_explanation.strip())
            ]
            
            # Test with high-risk transaction
            transaction = {
                'transaction_id': 'TXN001',
                'price_deviation': 0.5,
                'route_anomaly': 1,
                'company_risk_score': 0.8,
                'product': 'Electronics'
            }
            
            explanation = explain_transaction(transaction, force_api=True)
            
            # Verify realistic content
            assert len(explanation) > 100
            assert 'price deviation' in explanation.lower()
            assert 'over-invoicing' in explanation.lower()
            assert 'money laundering' in explanation.lower()
            assert 'shipping route' in explanation.lower()
    
    def test_mock_realistic_investigation_content(self):
        """Test that mocked investigation responses contain realistic analysis content."""
        with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
             patch('backend.ai_explainer.genai') as mock_genai:
            
            # Configure realistic mock response
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            realistic_response = """
            Based on the current dataset analysis, 5.0% of transactions are classified as fraudulent 
            (50 out of 1,000 total transactions). The most common fraud patterns include price manipulation 
            through over-invoicing and under-invoicing, trade route laundering using circuitous shipping 
            paths, and volume misrepresentation in cargo declarations.
            """
            
            mock_model.generate_content.side_effect = [
                MockGeminiResponse("OK"),
                MockGeminiResponse(realistic_response.strip())
            ]
            
            # Test investigation query
            context = {
                'total_transactions': 1000,
                'fraud_cases': 50,
                'fraud_patterns': ['Price manipulation', 'Route laundering', 'Volume misrepresentation']
            }
            
            query = "What are the main fraud patterns?"
            response = answer_investigation_query(query, context)
            
            # Verify realistic content
            assert len(response) > 100
            assert '5.0%' in response
            assert 'price manipulation' in response.lower()
            assert 'route laundering' in response.lower()
            assert 'over-invoicing' in response.lower()


class TestGeminiMockingIntegration:
    """Integration tests for Gemini mocking with existing functionality."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    def test_mock_preserves_caching_functionality(self):
        """Test that mocking preserves the caching system."""
        with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
             patch('backend.ai_explainer.genai') as mock_genai:
            
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.side_effect = [
                MockGeminiResponse("OK"),
                MockGeminiResponse("Cached explanation content")
            ]
            
            transaction = {'transaction_id': 'TXN_CACHE_TEST'}
            
            # First call should generate and cache
            explanation1 = explain_transaction(transaction, force_api=True)
            
            # Second call should use cache (no additional API call)
            explanation2 = explain_transaction(transaction)
            
            # Should be identical
            assert explanation1 == explanation2
            
            # Should have made only 2 calls (init test + first explanation)
            assert mock_model.generate_content.call_count == 2
    
    def test_mock_with_session_limits(self):
        """Test that mocking works with session limit functionality."""
        with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
             patch('backend.ai_explainer.genai') as mock_genai:
            
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.return_value = MockGeminiResponse("OK")
            
            # Import session management functions
            from backend.ai_explainer import (
                increment_session_count, can_make_explanation, 
                MAX_EXPLANATIONS_PER_SESSION
            )
            
            # Exhaust session limit
            for _ in range(MAX_EXPLANATIONS_PER_SESSION):
                increment_session_count()
            
            assert can_make_explanation() is False
            
            # Should return quota exceeded message
            transaction = {'transaction_id': 'TXN_QUOTA_TEST'}
            explanation = explain_transaction(transaction)
            
            assert "limit reached" in explanation.lower()
    
    def test_mock_error_simulation_comprehensive(self):
        """Test comprehensive error simulation with mocking."""
        error_scenarios = [
            (Exception("Rate limit exceeded"), "rate limit"),
            (Exception("Request timeout"), "timeout"),
            (Exception("Authentication failed"), "authentication"),
            (Exception("Network error"), "network")
        ]
        
        for error, error_type in error_scenarios:
            with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
                 patch('backend.ai_explainer.genai') as mock_genai:
                
                mock_model = MagicMock()
                mock_genai.GenerativeModel.return_value = mock_model
                mock_model.generate_content.side_effect = [
                    MockGeminiResponse("OK"),  # Init test
                    error  # Explanation call fails
                ]
                
                transaction = {'transaction_id': f'TXN_{error_type.upper()}'}
                
                # Should handle error gracefully
                explanation = explain_transaction(transaction, force_api=True)
                
                assert isinstance(explanation, str)
                assert len(explanation) > 0
                # Should use fallback explanation (could be different formats)
                assert any(keyword in explanation.lower() for keyword in ['fraud', 'automated', 'analysis', 'busy'])


class TestOfflineTestingCapability:
    """Test complete offline testing capability."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    def test_complete_offline_workflow(self):
        """Test complete fraud detection workflow offline."""
        with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
             patch('backend.ai_explainer.genai') as mock_genai:
            
            # Configure comprehensive mock
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Mock responses for different calls
            mock_responses = [
                MockGeminiResponse("OK"),  # Initialization test
                MockGeminiResponse("This transaction shows price manipulation with 60% deviation above market value, indicating potential over-invoicing fraud."),  # Transaction explanation
                MockGeminiResponse("Current fraud rate is 5% with 50 confirmed cases out of 1000 transactions. Main patterns include price manipulation and route laundering.")  # Investigation query
            ]
            
            mock_model.generate_content.side_effect = mock_responses
            
            # Initialize system
            model = initialize_gemini()
            assert model is not None
            
            # Test transaction explanation
            transaction = {
                'transaction_id': 'TXN_OFFLINE_001',
                'price_deviation': 0.6,
                'route_anomaly': 1,
                'company_risk_score': 0.7
            }
            
            explanation = explain_transaction(transaction, model, force_api=True)
            assert isinstance(explanation, str)
            assert len(explanation) > 50
            assert 'price manipulation' in explanation.lower()
            
            # Test investigation query
            context = {
                'total_transactions': 1000,
                'fraud_cases': 50,
                'suspicious_cases': 100
            }
            
            query = "What is the fraud rate?"
            response = answer_investigation_query(query, context, model)
            assert isinstance(response, str)
            assert len(response) > 50
            assert 'fraud rate' in response.lower()
            
            # Verify all mocked calls were made
            assert mock_model.generate_content.call_count == 3
    
    def test_offline_unit_test_reliability(self):
        """Test that offline unit tests are reliable and deterministic."""
        # Run the same test multiple times to ensure consistency
        for iteration in range(3):
            with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
                 patch('backend.ai_explainer.genai') as mock_genai:
                
                mock_model = MagicMock()
                mock_genai.GenerativeModel.return_value = mock_model
                mock_model.generate_content.side_effect = [
                    MockGeminiResponse("OK"),
                    MockGeminiResponse(f"Consistent explanation for iteration {iteration}")
                ]
                
                transaction = {'transaction_id': f'TXN_RELIABLE_{iteration}'}
                explanation = explain_transaction(transaction, force_api=True)
                
                # Should be consistent and predictable
                assert isinstance(explanation, str)
                assert f"iteration {iteration}" in explanation.lower()
                assert mock_model.generate_content.call_count == 2
                
                # Reset for next iteration
                reset_session_count()
                clear_explanation_cache()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])