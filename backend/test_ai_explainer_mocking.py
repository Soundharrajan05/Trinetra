"""
Comprehensive Gemini API Mocking for TRINETRA AI - Trade Fraud Intelligence System

This module provides comprehensive mocking for the Gemini API to enable unit tests
to run without internet connection. It includes realistic mock responses for fraud
explanations and investigation queries.

Key Features:
- Mock Gemini API initialization and configuration
- Realistic fraud explanation responses based on transaction data
- Mock investigation query responses
- Error simulation for testing error handling
- Offline testing capability
- Configurable mock behaviors

Author: TRINETRA AI Team
Date: 2024
"""

import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any, Optional, List
import json
import random

# Temporarily disable TEST_MODE to test our comprehensive mocking
os.environ["TEST_MODE"] = "false"

# Import the AI explainer module
from backend.ai_explainer import (
    initialize_gemini, explain_transaction, answer_investigation_query,
    reset_session_count, get_session_count, can_make_explanation,
    increment_session_count, get_cached_explanation, cache_explanation,
    clear_explanation_cache, MAX_EXPLANATIONS_PER_SESSION,
    GeminiInitializationError, GeminiAPIError, GeminiRateLimitError,
    GeminiTimeoutError, GeminiQuotaExceededError
)


class MockGeminiResponse:
    """Mock response object that mimics Gemini API response structure."""
    
    def __init__(self, text: str):
        self.text = text
        self.candidates = [Mock(content=Mock(parts=[Mock(text=text)]))]
        self.prompt_feedback = Mock()


class MockGenerativeModel:
    """
    Comprehensive mock for Gemini GenerativeModel that provides realistic responses.
    
    This mock generates contextual responses based on the input prompt content,
    simulating how the real Gemini API would respond to fraud analysis requests.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self._call_count = 0
        self._should_fail = False
        self._failure_type = None
        self._failure_message = "Mock API failure"
    
    def configure_failure(self, should_fail: bool, failure_type: str = "api_error", message: str = "Mock failure"):
        """Configure the mock to simulate failures for testing error handling."""
        self._should_fail = should_fail
        self._failure_type = failure_type
        self._failure_message = message
    
    def generate_content(self, prompt: str, generation_config=None, request_options=None) -> MockGeminiResponse:
        """
        Generate mock content based on the prompt.
        
        Analyzes the prompt to determine if it's a transaction explanation or investigation query,
        then generates appropriate realistic responses.
        """
        self._call_count += 1
        
        # Simulate failures if configured
        if self._should_fail:
            if self._failure_type == "rate_limit":
                raise Exception("Rate limit exceeded")
            elif self._failure_type == "timeout":
                raise Exception("Request timeout")
            elif self._failure_type == "quota":
                raise Exception("Quota exceeded")
            elif self._failure_type == "auth":
                raise Exception("Authentication failed")
            else:
                raise Exception(self._failure_message)
        
        # Generate response based on prompt content
        if "Transaction Details:" in prompt and "explain why it may be fraudulent" in prompt:
            return MockGeminiResponse(self._generate_transaction_explanation(prompt))
        elif "trade fraud investigation assistant" in prompt.lower():
            return MockGeminiResponse(self._generate_investigation_response(prompt))
        elif "Hello, please respond with just 'OK'" in prompt:
            return MockGeminiResponse("OK")
        else:
            return MockGeminiResponse("Mock response for unknown prompt type")
    
    def _generate_transaction_explanation(self, prompt: str) -> str:
        """Generate realistic transaction explanation based on prompt content."""
        # Extract transaction details from prompt
        transaction_data = self._extract_transaction_data(prompt)
        
        explanations = []
        
        # Analyze price deviation
        price_deviation = transaction_data.get('price_deviation', 0)
        if abs(price_deviation) > 0.3:
            if price_deviation > 0:
                explanations.append(f"The transaction shows significant over-invoicing with a {abs(price_deviation):.1%} price deviation above market value, which is commonly used for money laundering or capital flight.")
            else:
                explanations.append(f"The transaction exhibits under-invoicing with a {abs(price_deviation):.1%} price deviation below market value, typically used to evade customs duties and taxes.")
        
        # Analyze route anomaly
        route_anomaly = transaction_data.get('route_anomaly', 0)
        if route_anomaly == 1:
            explanations.append("The shipping route appears unusual or circuitous, which may indicate trade route laundering to obscure the true origin of goods or exploit preferential trade agreements.")
        
        # Analyze company risk
        company_risk = transaction_data.get('company_risk_score', 0)
        if company_risk > 0.7:
            explanations.append(f"The involved company has a high risk score of {company_risk:.2f}, suggesting previous involvement in suspicious activities or regulatory violations.")
        
        # Analyze port activity
        port_activity = transaction_data.get('port_activity_index', 0)
        if port_activity > 1.5:
            explanations.append(f"Unusual port activity levels (index: {port_activity:.2f}) may indicate coordination among multiple fraudulent shipments or exploitation of processing delays.")
        
        if not explanations:
            explanations.append("The transaction exhibits patterns that deviate from normal commercial behavior, triggering our machine learning fraud detection algorithms.")
        
        return " ".join(explanations)
    
    def _generate_investigation_response(self, prompt: str) -> str:
        """Generate realistic investigation query response based on prompt content."""
        query = self._extract_query_from_prompt(prompt)
        context = self._extract_context_from_prompt(prompt)
        
        query_lower = query.lower()
        
        # Pattern matching for different query types
        if any(keyword in query_lower for keyword in ['fraud rate', 'percentage', 'statistics']):
            total = context.get('total_transactions', 1000)
            fraud = context.get('fraud_cases', 50)
            suspicious = context.get('suspicious_cases', 150)
            fraud_rate = (fraud / total * 100) if total > 0 else 0
            suspicious_rate = (suspicious / total * 100) if total > 0 else 0
            return f"Based on the current analysis, {fraud_rate:.1f}% of transactions are classified as fraudulent ({fraud:,} out of {total:,}), with an additional {suspicious_rate:.1f}% flagged as suspicious ({suspicious:,} cases). This indicates a significant fraud risk requiring immediate attention."
        
        elif any(keyword in query_lower for keyword in ['patterns', 'common fraud', 'indicators']):
            patterns = context.get('fraud_patterns', ['Price manipulation', 'Route laundering', 'Volume misrepresentation'])
            return f"The most prevalent fraud patterns include: {', '.join(patterns[:3])}. These typically manifest through significant price deviations from market values, unusual shipping routes that don't align with commercial logic, and inconsistencies in reported cargo volumes or quantities."
        
        elif any(keyword in query_lower for keyword in ['high risk', 'companies', 'entities']):
            companies = context.get('high_risk_companies', ['CompanyA', 'CompanyB'])
            return f"High-risk entities currently flagged include: {', '.join(companies[:3])}. These companies exhibit elevated risk scores due to historical involvement in suspicious transactions, regulatory violations, or associations with sanctioned entities."
        
        elif 'suspicious' in query_lower and any(keyword in query_lower for keyword in ['txn', 'transaction']):
            return "Transactions are flagged as suspicious when they exhibit multiple risk indicators such as significant price deviations, unusual routing patterns, involvement of high-risk entities, or abnormal volume characteristics. Our machine learning model analyzes these factors collectively to assign risk scores."
        
        else:
            return f"Based on the available trade fraud intelligence data, I can provide analysis on transaction patterns, risk indicators, and investigation priorities. The current dataset shows {context.get('total_transactions', 'N/A')} transactions with various risk levels requiring different investigation approaches."
    
    def _extract_transaction_data(self, prompt: str) -> Dict[str, Any]:
        """Extract transaction data from explanation prompt."""
        data = {}
        lines = prompt.split('\n')
        
        for line in lines:
            if 'Price Deviation:' in line:
                try:
                    value = line.split(':')[1].strip().replace('%', '')
                    data['price_deviation'] = float(value) / 100
                except:
                    data['price_deviation'] = 0
            elif 'Route Anomaly:' in line:
                try:
                    value = line.split(':')[1].strip()
                    data['route_anomaly'] = int(float(value))
                except:
                    data['route_anomaly'] = 0
            elif 'Company Risk Score:' in line:
                try:
                    value = line.split(':')[1].strip()
                    data['company_risk_score'] = float(value)
                except:
                    data['company_risk_score'] = 0
            elif 'Port Activity Index:' in line:
                try:
                    value = line.split(':')[1].strip()
                    data['port_activity_index'] = float(value)
                except:
                    data['port_activity_index'] = 0
        
        return data
    
    def _extract_query_from_prompt(self, prompt: str) -> str:
        """Extract the actual query from investigation prompt."""
        lines = prompt.split('\n')
        for line in lines:
            if line.startswith('Question:'):
                return line.replace('Question:', '').strip()
        return ""
    
    def _extract_context_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Extract context data from investigation prompt."""
        context = {}
        lines = prompt.split('\n')
        
        for line in lines:
            if 'Total Transactions:' in line:
                try:
                    value = line.split(':')[1].strip()
                    context['total_transactions'] = int(value) if value != 'N/A' else 1000
                except:
                    context['total_transactions'] = 1000
            elif 'Fraud Cases:' in line:
                try:
                    value = line.split(':')[1].strip()
                    context['fraud_cases'] = int(value) if value != 'N/A' else 50
                except:
                    context['fraud_cases'] = 50
            elif 'Suspicious Cases:' in line:
                try:
                    value = line.split(':')[1].strip()
                    context['suspicious_cases'] = int(value) if value != 'N/A' else 150
                except:
                    context['suspicious_cases'] = 150
        
        return context
    
    @property
    def call_count(self) -> int:
        """Get the number of times generate_content was called."""
        return self._call_count
    
    def reset_call_count(self):
        """Reset the call counter."""
        self._call_count = 0


class MockGenAI:
    """Mock for the google.generativeai module."""
    
    GenerativeModel = MockGenerativeModel
    
    @staticmethod
    def configure(api_key: str):
        """Mock configuration method."""
        if not api_key:
            raise Exception("API key is required")
        # Simulate authentication failure for invalid keys
        if api_key == "invalid_key":
            raise Exception("Invalid API key")


class MockGenerationConfig:
    """Mock for GenerationConfig."""
    
    def __init__(self, **kwargs):
        self.max_output_tokens = kwargs.get('max_output_tokens', 1000)
        self.temperature = kwargs.get('temperature', 0.3)


class MockRequestOptions:
    """Mock for RequestOptions."""
    
    def __init__(self, **kwargs):
        self.retry = kwargs.get('retry')
        self.timeout = kwargs.get('timeout', 10)


# Global mock instances for reuse
_mock_model = MockGenerativeModel()
_mock_genai = MockGenAI()
_mock_generation_config = MockGenerationConfig
_mock_request_options = MockRequestOptions


def get_mock_model() -> MockGenerativeModel:
    """Get the global mock model instance."""
    return _mock_model


def reset_mock_model():
    """Reset the global mock model state."""
    global _mock_model
    _mock_model = MockGenerativeModel()


# Comprehensive test fixtures and utilities
@pytest.fixture
def mock_gemini_success():
    """Fixture that mocks successful Gemini API calls."""
    with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
         patch('backend.ai_explainer.genai', _mock_genai), \
         patch('backend.ai_explainer.GenerationConfig', _mock_generation_config), \
         patch('backend.ai_explainer.RequestOptions', _mock_request_options):
        reset_mock_model()
        yield get_mock_model()


@pytest.fixture
def mock_gemini_failure():
    """Fixture that mocks Gemini API failures."""
    mock_model = MockGenerativeModel()
    mock_model.configure_failure(True, "api_error", "Mock API failure")
    
    with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
         patch('backend.ai_explainer.genai.GenerativeModel', return_value=mock_model), \
         patch('backend.ai_explainer.genai.configure'), \
         patch('backend.ai_explainer.GenerationConfig', _mock_generation_config):
        yield mock_model


@pytest.fixture
def mock_gemini_rate_limit():
    """Fixture that mocks Gemini API rate limit errors."""
    mock_model = MockGenerativeModel()
    mock_model.configure_failure(True, "rate_limit", "Rate limit exceeded")
    
    with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
         patch('backend.ai_explainer.genai.GenerativeModel', return_value=mock_model), \
         patch('backend.ai_explainer.genai.configure'), \
         patch('backend.ai_explainer.GenerationConfig', _mock_generation_config):
        yield mock_model


@pytest.fixture
def mock_gemini_timeout():
    """Fixture that mocks Gemini API timeout errors."""
    mock_model = MockGenerativeModel()
    mock_model.configure_failure(True, "timeout", "Request timeout")
    
    with patch('backend.ai_explainer.GEMINI_AVAILABLE', True), \
         patch('backend.ai_explainer.genai.GenerativeModel', return_value=mock_model), \
         patch('backend.ai_explainer.genai.configure'), \
         patch('backend.ai_explainer.GenerationConfig', _mock_generation_config):
        yield mock_model


@pytest.fixture
def mock_gemini_unavailable():
    """Fixture that mocks Gemini API being unavailable."""
    with patch('backend.ai_explainer.GEMINI_AVAILABLE', False):
        yield


@pytest.fixture
def sample_transaction():
    """Sample transaction data for testing."""
    return {
        'transaction_id': 'TXN001',
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


@pytest.fixture
def sample_context():
    """Sample context data for investigation queries."""
    return {
        'total_transactions': 1000,
        'fraud_cases': 50,
        'suspicious_cases': 150,
        'avg_risk_score': 0.1,
        'high_risk_companies': ['CompanyA', 'CompanyB', 'CompanyC'],
        'fraud_patterns': ['Price manipulation', 'Route laundering', 'Volume misrepresentation']
    }


def setup_module():
    """Module-level setup for mocking tests."""
    # Ensure TEST_MODE is set
    os.environ["TEST_MODE"] = "true"
    
    # Reset session state
    reset_session_count()
    clear_explanation_cache()


def teardown_module():
    """Module-level teardown for mocking tests."""
    # Clean up any global state
    reset_session_count()
    clear_explanation_cache()


class TestGeminiAPIMocking:
    """Test cases for Gemini API mocking functionality."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
        reset_mock_model()
    
    def test_mock_model_initialization(self, mock_gemini_success):
        """Test that mock model initializes correctly."""
        model = initialize_gemini()
        
        assert model is not None
        assert hasattr(model, 'model_name')
        assert model.model_name == "gemini-2.5-flash"
        assert hasattr(model, 'generate_content')
    
    def test_mock_model_call_tracking(self, mock_gemini_success):
        """Test that mock model tracks API calls."""
        model = get_mock_model()
        initial_count = model.call_count
        
        # Make a test call
        response = model.generate_content("Test prompt")
        
        assert model.call_count == initial_count + 1
        assert response.text is not None
    
    def test_mock_transaction_explanation_realistic(self, mock_gemini_success, sample_transaction):
        """Test that mock generates realistic transaction explanations."""
        explanation = explain_transaction(sample_transaction, force_api=True)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 50  # Should be substantial
        
        # Check for realistic fraud indicators based on transaction data
        if sample_transaction.get('price_deviation', 0) > 0.3:
            assert any(keyword in explanation.lower() for keyword in ['price', 'deviation', 'invoicing'])
        
        if sample_transaction.get('route_anomaly') == 1:
            assert any(keyword in explanation.lower() for keyword in ['route', 'shipping', 'unusual'])
        
        if sample_transaction.get('company_risk_score', 0) > 0.7:
            assert any(keyword in explanation.lower() for keyword in ['company', 'risk', 'score'])
    
    def test_mock_investigation_query_realistic(self, mock_gemini_success, sample_context):
        """Test that mock generates realistic investigation responses."""
        queries_and_expected = [
            ("What is the fraud rate?", ["fraud rate", "percentage", "transactions"]),
            ("What are the main fraud patterns?", ["patterns", "price", "route"]),
            ("Tell me about high-risk companies", ["high-risk", "companies", "entities"]),
            ("Why is this transaction suspicious?", ["suspicious", "risk", "indicators"])
        ]
        
        for query, expected_keywords in queries_and_expected:
            response = answer_investigation_query(query, sample_context)
            
            assert isinstance(response, str)
            assert len(response) > 30  # Should be substantial
            
            # Check that response contains relevant keywords
            response_lower = response.lower()
            assert any(keyword in response_lower for keyword in expected_keywords)
    
    def test_mock_api_failure_simulation(self, mock_gemini_failure, sample_transaction):
        """Test that mock can simulate API failures."""
        # This should trigger fallback behavior
        explanation = explain_transaction(sample_transaction, force_api=True)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        # Should use fallback explanation when API fails
        assert any(keyword in explanation.lower() for keyword in ['fraud indicators', 'detected', 'analysis'])
    
    def test_mock_rate_limit_simulation(self, mock_gemini_rate_limit, sample_transaction):
        """Test that mock can simulate rate limit errors."""
        explanation = explain_transaction(sample_transaction, force_api=True)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        # Should handle rate limit gracefully
    
    def test_mock_timeout_simulation(self, mock_gemini_timeout, sample_transaction):
        """Test that mock can simulate timeout errors."""
        explanation = explain_transaction(sample_transaction, force_api=True)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        # Should handle timeout gracefully
    
    def test_mock_gemini_unavailable(self, mock_gemini_unavailable, sample_transaction):
        """Test behavior when Gemini API is unavailable."""
        model = initialize_gemini()
        explanation = explain_transaction(sample_transaction, model)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        # Should work with mock implementation
    
    def test_mock_preserves_session_management(self, mock_gemini_success, sample_transaction):
        """Test that mocking preserves session management functionality."""
        # Test session limits still work with mocks
        assert can_make_explanation() is True
        
        # Exhaust session limit
        for _ in range(MAX_EXPLANATIONS_PER_SESSION):
            increment_session_count()
        
        assert can_make_explanation() is False
        
        # Should return quota exceeded message even with mocks
        explanation = explain_transaction(sample_transaction)
        assert "limit reached" in explanation.lower()
    
    def test_mock_preserves_caching(self, mock_gemini_success, sample_transaction):
        """Test that mocking preserves caching functionality."""
        transaction_id = sample_transaction['transaction_id']
        
        # First call should generate and cache
        explanation1 = explain_transaction(sample_transaction, force_api=True)
        cached = get_cached_explanation(transaction_id)
        assert cached == explanation1
        
        # Second call should use cache
        explanation2 = explain_transaction(sample_transaction)
        assert explanation2 == explanation1
    
    def test_mock_different_transaction_types(self, mock_gemini_success):
        """Test mock responses for different transaction risk profiles."""
        # High-risk transaction
        high_risk_transaction = {
            'transaction_id': 'TXN_HIGH',
            'price_deviation': 0.8,  # Very high deviation
            'route_anomaly': 1,
            'company_risk_score': 0.95,
            'port_activity_index': 2.5
        }
        
        # Low-risk transaction
        low_risk_transaction = {
            'transaction_id': 'TXN_LOW',
            'price_deviation': 0.05,  # Low deviation
            'route_anomaly': 0,
            'company_risk_score': 0.1,
            'port_activity_index': 1.0
        }
        
        high_risk_explanation = explain_transaction(high_risk_transaction, force_api=True)
        low_risk_explanation = explain_transaction(low_risk_transaction, force_api=True)
        
        # High-risk should have more detailed explanation
        assert len(high_risk_explanation) > len(low_risk_explanation)
        
        # High-risk should mention specific indicators
        assert any(keyword in high_risk_explanation.lower() for keyword in ['over-invoicing', 'deviation', 'risk'])
    
    def test_mock_investigation_query_context_sensitivity(self, mock_gemini_success):
        """Test that mock investigation responses are sensitive to context."""
        high_fraud_context = {
            'total_transactions': 1000,
            'fraud_cases': 200,  # High fraud rate
            'suspicious_cases': 300
        }
        
        low_fraud_context = {
            'total_transactions': 1000,
            'fraud_cases': 10,   # Low fraud rate
            'suspicious_cases': 20
        }
        
        query = "What is the fraud rate?"
        
        high_fraud_response = answer_investigation_query(query, high_fraud_context)
        low_fraud_response = answer_investigation_query(query, low_fraud_context)
        
        # Responses should reflect different fraud rates
        assert "20.0%" in high_fraud_response  # 200/1000 = 20%
        assert "1.0%" in low_fraud_response    # 10/1000 = 1%
    
    def test_mock_error_classification(self, mock_gemini_success):
        """Test that mock can simulate different error types for testing error handling."""
        model = get_mock_model()
        
        # Test different failure types
        failure_types = ["api_error", "rate_limit", "timeout", "quota", "auth"]
        
        for failure_type in failure_types:
            model.configure_failure(True, failure_type, f"Mock {failure_type} error")
            
            try:
                model.generate_content("Test prompt")
                assert False, f"Expected {failure_type} error"
            except Exception as e:
                assert failure_type.replace('_', ' ') in str(e).lower()
            
            # Reset for next test
            model.configure_failure(False)


class TestOfflineCapability:
    """Test that the system works completely offline with mocks."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
        reset_mock_model()
    
    def test_complete_offline_workflow(self, mock_gemini_success, sample_transaction, sample_context):
        """Test complete fraud analysis workflow without internet."""
        # Initialize system
        model = initialize_gemini()
        assert model is not None
        
        # Generate transaction explanation
        explanation = explain_transaction(sample_transaction, model, force_api=True)
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        
        # Answer investigation query
        query = "What are the main fraud patterns?"
        answer = answer_investigation_query(query, sample_context, model)
        assert isinstance(answer, str)
        assert len(answer) > 0
        
        # Verify no actual network calls were made (all mocked)
        mock_model = get_mock_model()
        assert mock_model.call_count >= 2  # At least explanation + query calls
    
    def test_offline_error_handling(self, mock_gemini_failure, sample_transaction):
        """Test error handling works offline."""
        # Should gracefully handle mock failures
        explanation = explain_transaction(sample_transaction, force_api=True)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        # Should fall back to rule-based explanation
        assert "Fraud Indicators Detected:" in explanation
    
    def test_offline_session_management(self, mock_gemini_success, sample_transaction):
        """Test session management works offline."""
        # Test quota enforcement
        for i in range(MAX_EXPLANATIONS_PER_SESSION + 2):
            explanation = explain_transaction(
                {**sample_transaction, 'transaction_id': f'TXN_{i:03d}'}, 
                force_api=True
            )
            
            if i >= MAX_EXPLANATIONS_PER_SESSION:
                assert "limit reached" in explanation.lower()
            else:
                assert "limit reached" not in explanation.lower()
    
    def test_offline_caching_behavior(self, mock_gemini_success, sample_transaction):
        """Test caching works correctly offline."""
        transaction_id = sample_transaction['transaction_id']
        
        # Clear cache
        clear_explanation_cache()
        assert get_cached_explanation(transaction_id) is None
        
        # Generate explanation (should cache)
        explanation1 = explain_transaction(sample_transaction, force_api=True)
        cached = get_cached_explanation(transaction_id)
        assert cached == explanation1
        
        # Get cached explanation (should not call API again)
        mock_model = get_mock_model()
        initial_calls = mock_model.call_count
        
        explanation2 = explain_transaction(sample_transaction)
        assert explanation2 == explanation1
        assert mock_model.call_count == initial_calls  # No additional API calls


class TestMockRealism:
    """Test that mock responses are realistic and useful for testing."""
    
    def setup_method(self):
        """Reset state before each test."""
        reset_session_count()
        clear_explanation_cache()
        reset_mock_model()
    
    def test_explanation_quality_metrics(self, mock_gemini_success, sample_transaction):
        """Test that mock explanations meet quality standards."""
        explanation = explain_transaction(sample_transaction, force_api=True)
        
        # Quality checks
        assert len(explanation) >= 100  # Substantial content
        assert len(explanation.split()) >= 20  # At least 20 words
        assert explanation.count('.') >= 1  # At least one complete sentence
        
        # Content relevance checks
        transaction_keywords = ['transaction', 'fraud', 'suspicious', 'risk', 'analysis']
        assert any(keyword in explanation.lower() for keyword in transaction_keywords)
    
    def test_investigation_response_quality(self, mock_gemini_success, sample_context):
        """Test that mock investigation responses are high quality."""
        queries = [
            "What is the current fraud rate?",
            "What are the most common fraud patterns?",
            "Which companies should I investigate first?",
            "How should I prioritize my investigation?"
        ]
        
        for query in queries:
            response = answer_investigation_query(query, sample_context)
            
            # Quality checks
            assert len(response) >= 50  # Substantial content
            assert len(response.split()) >= 10  # At least 10 words
            assert response.count('.') >= 1  # At least one complete sentence
            
            # Relevance checks
            query_keywords = query.lower().split()
            response_lower = response.lower()
            # Should contain at least one keyword from the query
            assert any(keyword in response_lower for keyword in query_keywords if len(keyword) > 3)
    
    def test_mock_consistency(self, mock_gemini_success, sample_transaction):
        """Test that mock responses are consistent for identical inputs."""
        # Generate multiple explanations for the same transaction
        explanations = []
        for _ in range(3):
            clear_explanation_cache()  # Force regeneration
            explanation = explain_transaction(sample_transaction, force_api=True)
            explanations.append(explanation)
        
        # Should be identical (deterministic mocking)
        assert all(exp == explanations[0] for exp in explanations)
    
    def test_mock_variety_across_transactions(self, mock_gemini_success):
        """Test that mock provides variety across different transactions."""
        transactions = [
            {'transaction_id': 'TXN1', 'price_deviation': 0.8, 'route_anomaly': 1},
            {'transaction_id': 'TXN2', 'price_deviation': -0.6, 'route_anomaly': 0},
            {'transaction_id': 'TXN3', 'price_deviation': 0.1, 'company_risk_score': 0.9}
        ]
        
        explanations = []
        for transaction in transactions:
            explanation = explain_transaction(transaction, force_api=True)
            explanations.append(explanation)
        
        # Should have different explanations for different transactions
        assert len(set(explanations)) == len(explanations)  # All unique
        
        # Should mention relevant indicators
        assert 'over-invoicing' in explanations[0].lower()  # High positive deviation
        assert 'under-invoicing' in explanations[1].lower()  # High negative deviation
        assert 'company' in explanations[2].lower()  # High company risk


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])