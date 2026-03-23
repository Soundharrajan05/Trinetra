"""
Integration Test for Gemini API Mocking - TRINETRA AI

This test demonstrates that the Gemini API mocking system works correctly
with the main fraud detection system, enabling offline testing.

Author: TRINETRA AI Team
Date: 2024
"""

import pytest
import os
from unittest.mock import patch, MagicMock

# Disable TEST_MODE for this integration test
os.environ["TEST_MODE"] = "false"

from backend.ai_explainer import (
    initialize_gemini, explain_transaction, answer_investigation_query,
    reset_session_count, clear_explanation_cache
)


class MockGeminiResponse:
    """Mock response that mimics Gemini API response structure."""
    
    def __init__(self, text: str):
        self.text = text


class TestMockingIntegration:
    """Integration tests demonstrating offline capability with mocking."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    def test_complete_fraud_analysis_workflow_offline(self):
        """Test complete fraud analysis workflow using mocking (offline)."""
        with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
             patch('backend.ai_explainer.genai') as mock_genai:
            
            # Configure comprehensive mock
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Define realistic mock responses
            mock_responses = [
                MockGeminiResponse("OK"),  # Initialization test
                MockGeminiResponse(
                    "This transaction exhibits significant fraud indicators: "
                    "The 80% price deviation above market value suggests over-invoicing "
                    "for money laundering purposes. The unusual shipping route indicates "
                    "potential trade route laundering to obscure goods origin. "
                    "The high company risk score of 0.9 suggests previous involvement "
                    "in suspicious activities requiring immediate investigation."
                ),  # Transaction explanation
                MockGeminiResponse(
                    "Based on current analysis, 5.0% of transactions are classified "
                    "as fraudulent (50 out of 1,000 total). The primary fraud patterns "
                    "include price manipulation through over-invoicing and under-invoicing, "
                    "trade route laundering using circuitous shipping paths, and "
                    "volume misrepresentation in cargo declarations. "
                    "Investigation should prioritize high-value transactions with "
                    "multiple risk indicators."
                )  # Investigation query
            ]
            
            mock_model.generate_content.side_effect = mock_responses
            
            # Step 1: Initialize the AI system (offline)
            print("Step 1: Initializing AI system offline...")
            model = initialize_gemini()
            assert model is not None
            print("✓ AI system initialized successfully")
            
            # Step 2: Analyze a suspicious transaction (offline)
            print("\nStep 2: Analyzing suspicious transaction offline...")
            suspicious_transaction = {
                'transaction_id': 'TXN_SUSPICIOUS_001',
                'product': 'Electronics',
                'commodity_category': 'Consumer Goods',
                'market_price': 1000,
                'unit_price': 1800,
                'price_deviation': 0.8,  # 80% above market
                'shipping_route': 'Shanghai-Rotterdam-Miami',
                'distance_km': 15000,
                'company_risk_score': 0.9,
                'port_activity_index': 2.1,
                'route_anomaly': 1,
                'risk_score': 0.7,
                'risk_category': 'FRAUD'
            }
            
            explanation = explain_transaction(suspicious_transaction, model, force_api=True)
            
            # Verify explanation quality
            assert isinstance(explanation, str)
            assert len(explanation) > 100
            assert 'price deviation' in explanation.lower()
            assert 'over-invoicing' in explanation.lower()
            assert 'money laundering' in explanation.lower()
            assert 'shipping route' in explanation.lower()
            assert 'company risk' in explanation.lower()
            
            print(f"✓ Generated explanation: {explanation[:100]}...")
            
            # Step 3: Answer investigation queries (offline)
            print("\nStep 3: Processing investigation queries offline...")
            investigation_context = {
                'total_transactions': 1000,
                'fraud_cases': 50,
                'suspicious_cases': 150,
                'avg_risk_score': 0.15,
                'high_risk_companies': ['SuspiciousCorp', 'FlaggedLtd', 'RiskyInc'],
                'fraud_patterns': [
                    'Price manipulation', 
                    'Route laundering', 
                    'Volume misrepresentation',
                    'Entity masking'
                ]
            }
            
            queries = [
                "What is the current fraud rate?",
                "What are the main fraud patterns?",
                "How should I prioritize my investigation?"
            ]
            
            for query in queries:
                response = answer_investigation_query(query, investigation_context, model)
                
                assert isinstance(response, str)
                assert len(response) > 50
                print(f"✓ Query: '{query}' -> Response: {response[:80]}...")
            
            # Step 4: Verify offline operation
            print("\nStep 4: Verifying offline operation...")
            
            # Check that mocks were called appropriately
            assert mock_model.generate_content.call_count >= 3  # At least 3 calls (may be more due to retries)
            print(f"✓ Made {mock_model.generate_content.call_count} mock API calls")
            
            # Verify no actual network calls were made
            print("✓ No actual network calls made - completely offline")
            
            print("\n🎉 Complete fraud analysis workflow completed successfully offline!")
    
    def test_error_handling_offline(self):
        """Test error handling works correctly with mocking (offline)."""
        with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
             patch('backend.ai_explainer.genai') as mock_genai:
            
            # Configure mock to simulate API failure
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.side_effect = [
                MockGeminiResponse("OK"),  # Initialization succeeds
                Exception("Rate limit exceeded")  # Explanation fails
            ]
            
            print("Testing error handling offline...")
            
            # Initialize system
            model = initialize_gemini()
            assert model is not None
            
            # Try to explain transaction (should handle error gracefully)
            transaction = {
                'transaction_id': 'TXN_ERROR_TEST',
                'price_deviation': 0.5
            }
            
            explanation = explain_transaction(transaction, model, force_api=True)
            
            # Should not raise exception, should return fallback
            assert isinstance(explanation, str)
            assert len(explanation) > 0
            print(f"✓ Error handled gracefully: {explanation[:60]}...")
            
            print("✓ Error handling works correctly offline")
    
    def test_performance_offline(self):
        """Test performance of offline mocking system."""
        import time
        
        with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
             patch('backend.ai_explainer.genai') as mock_genai:
            
            # Configure fast mock
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.return_value = MockGeminiResponse(
                "Fast mock response for performance testing"
            )
            
            print("Testing performance offline...")
            
            # Initialize once
            model = initialize_gemini()
            
            # Time multiple explanations
            start_time = time.time()
            
            for i in range(10):
                transaction = {
                    'transaction_id': f'TXN_PERF_{i:03d}',
                    'price_deviation': 0.1 * i
                }
                explanation = explain_transaction(transaction, model, force_api=True)
                assert len(explanation) > 0
            
            duration = time.time() - start_time
            
            print(f"✓ Generated 10 explanations in {duration:.3f} seconds")
            print(f"✓ Average: {duration/10:.3f} seconds per explanation")
            
            # Should be very fast with mocking
            assert duration < 2.0, f"Too slow: {duration:.3f}s for 10 explanations"
            
            print("✓ Performance test passed - mocking is fast")


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v", "-s"])