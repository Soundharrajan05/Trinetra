"""
Gemini API Mock Utilities for TRINETRA AI - Trade Fraud Intelligence System

This module provides reusable mock utilities for the Gemini API that can be used
across different test files. It ensures consistent mocking behavior and realistic
responses for fraud detection testing.

Key Features:
- Centralized mock configuration
- Realistic response generation
- Error simulation capabilities
- Easy integration with existing tests
- Configurable mock behaviors

Author: TRINETRA AI Team
Date: 2024
"""

import os
from typing import Dict, Any, Optional, List, Union
from unittest.mock import Mock, MagicMock, patch
import json
import random


class GeminiMockConfig:
    """Configuration class for Gemini API mocking."""
    
    def __init__(self):
        self.should_fail = False
        self.failure_type = "api_error"
        self.failure_message = "Mock API failure"
        self.response_delay = 0  # Simulate network delay
        self.call_limit = None  # Limit number of successful calls
        self.call_count = 0
        
    def configure_failure(self, should_fail: bool, failure_type: str = "api_error", message: str = "Mock failure"):
        """Configure mock to simulate failures."""
        self.should_fail = should_fail
        self.failure_type = failure_type
        self.failure_message = message
        
    def configure_call_limit(self, limit: int):
        """Configure maximum number of successful calls."""
        self.call_limit = limit
        
    def reset(self):
        """Reset configuration to defaults."""
        self.should_fail = False
        self.failure_type = "api_error"
        self.failure_message = "Mock API failure"
        self.response_delay = 0
        self.call_limit = None
        self.call_count = 0


class RealisticGeminiMock:
    """
    Realistic Gemini API mock that generates contextual responses.
    
    This mock analyzes input prompts and generates appropriate responses
    that would be similar to what the real Gemini API would return for
    fraud detection queries.
    """
    
    def __init__(self, config: Optional[GeminiMockConfig] = None):
        self.config = config or GeminiMockConfig()
        self.model_name = "gemini-2.5-flash"
        
        # Predefined response templates for different scenarios
        self.fraud_indicators = {
            'price_deviation_high': "significant price deviation indicating potential over-invoicing for money laundering",
            'price_deviation_low': "under-invoicing detected, commonly used to evade customs duties and taxes",
            'route_anomaly': "unusual shipping route suggesting trade route laundering or sanctions evasion",
            'company_risk': "high-risk company involvement based on historical suspicious activity patterns",
            'port_activity': "abnormal port activity levels indicating potential coordination of fraudulent shipments",
            'volume_inconsistency': "cargo volume and quantity inconsistencies suggesting misrepresentation"
        }
        
        self.investigation_templates = {
            'fraud_rate': "Based on current analysis, {fraud_rate:.1f}% of transactions are fraudulent ({fraud_cases:,} out of {total:,})",
            'patterns': "Primary fraud patterns include: {patterns}. These manifest through pricing anomalies, routing irregularities, and entity risk factors",
            'companies': "High-risk entities flagged: {companies}. These show elevated risk scores due to regulatory violations or suspicious transaction history",
            'recommendations': "Investigation priorities: Focus on {fraud_cases:,} confirmed fraud cases, then review {suspicious_cases:,} suspicious transactions"
        }
    
    def generate_content(self, prompt: str, generation_config=None, request_options=None):
        """Generate mock content based on prompt analysis."""
        import time
        
        # Simulate network delay if configured
        if self.config.response_delay > 0:
            time.sleep(self.config.response_delay)
        
        # Check call limit
        if self.config.call_limit and self.config.call_count >= self.config.call_limit:
            raise Exception("Call limit exceeded")
        
        # Simulate failures if configured
        if self.config.should_fail:
            self._simulate_failure()
        
        self.config.call_count += 1
        
        # Generate appropriate response based on prompt type
        if "Transaction Details:" in prompt:
            response_text = self._generate_transaction_explanation(prompt)
        elif "trade fraud investigation assistant" in prompt.lower():
            response_text = self._generate_investigation_response(prompt)
        elif "Hello, please respond with just 'OK'" in prompt:
            response_text = "OK"
        else:
            response_text = "Mock response: Analysis completed based on available fraud detection parameters."
        
        return MockGeminiResponse(response_text)
    
    def _simulate_failure(self):
        """Simulate different types of API failures."""
        failure_messages = {
            'rate_limit': "Rate limit exceeded. Please try again later.",
            'timeout': "Request timeout. The operation took too long to complete.",
            'quota': "Quota exceeded. You have reached your API usage limit.",
            'auth': "Authentication failed. Please check your API key.",
            'network': "Network error. Unable to connect to the service.",
            'api_error': self.config.failure_message
        }
        
        message = failure_messages.get(self.config.failure_type, self.config.failure_message)
        
        if self.config.failure_type == 'rate_limit':
            raise Exception(f"429 {message}")
        elif self.config.failure_type == 'timeout':
            raise Exception(f"Timeout: {message}")
        elif self.config.failure_type == 'quota':
            raise Exception(f"Quota: {message}")
        elif self.config.failure_type == 'auth':
            raise Exception(f"401 {message}")
        else:
            raise Exception(message)
    
    def _generate_transaction_explanation(self, prompt: str) -> str:
        """Generate realistic transaction explanation."""
        # Extract transaction data from prompt
        transaction_data = self._parse_transaction_prompt(prompt)
        
        explanations = []
        
        # Analyze each risk factor
        price_dev = transaction_data.get('price_deviation', 0)
        if abs(price_dev) > 0.3:
            if price_dev > 0:
                explanations.append(f"The transaction exhibits {self.fraud_indicators['price_deviation_high']} with a {abs(price_dev):.1%} deviation above market value.")
            else:
                explanations.append(f"The transaction shows {self.fraud_indicators['price_deviation_low']} with a {abs(price_dev):.1%} deviation below market value.")
        
        if transaction_data.get('route_anomaly') == 1:
            explanations.append(f"The shipping route appears irregular, indicating {self.fraud_indicators['route_anomaly']}.")
        
        company_risk = transaction_data.get('company_risk_score', 0)
        if company_risk > 0.7:
            explanations.append(f"The transaction involves {self.fraud_indicators['company_risk']} (risk score: {company_risk:.2f}).")
        
        port_activity = transaction_data.get('port_activity_index', 0)
        if port_activity > 1.5:
            explanations.append(f"Port activity analysis reveals {self.fraud_indicators['port_activity']} (activity index: {port_activity:.2f}).")
        
        if not explanations:
            explanations.append("The transaction exhibits patterns that deviate from normal commercial behavior, triggering machine learning fraud detection algorithms.")
        
        return " ".join(explanations)
    
    def _generate_investigation_response(self, prompt: str) -> str:
        """Generate realistic investigation query response."""
        query = self._extract_query(prompt)
        context = self._extract_context(prompt)
        
        query_lower = query.lower()
        
        # Match query patterns and generate appropriate responses
        if any(keyword in query_lower for keyword in ['fraud rate', 'percentage', 'statistics']):
            total = context.get('total_transactions', 1000)
            fraud = context.get('fraud_cases', 50)
            suspicious = context.get('suspicious_cases', 150)
            fraud_rate = (fraud / total * 100) if total > 0 else 0
            return self.investigation_templates['fraud_rate'].format(
                fraud_rate=fraud_rate, fraud_cases=fraud, total=total
            ) + f", with an additional {(suspicious/total*100):.1f}% flagged as suspicious."
        
        elif any(keyword in query_lower for keyword in ['patterns', 'common fraud', 'indicators']):
            patterns = context.get('fraud_patterns', ['Price manipulation', 'Route laundering', 'Volume misrepresentation'])
            return self.investigation_templates['patterns'].format(patterns=', '.join(patterns[:3]))
        
        elif any(keyword in query_lower for keyword in ['companies', 'entities', 'high risk']):
            companies = context.get('high_risk_companies', ['CompanyA', 'CompanyB'])
            return self.investigation_templates['companies'].format(companies=', '.join(companies[:3]))
        
        elif any(keyword in query_lower for keyword in ['investigate', 'priority', 'next steps']):
            fraud_cases = context.get('fraud_cases', 50)
            suspicious_cases = context.get('suspicious_cases', 150)
            return self.investigation_templates['recommendations'].format(
                fraud_cases=fraud_cases, suspicious_cases=suspicious_cases
            ) + ". Prioritize cases with multiple risk factors and high transaction values."
        
        else:
            return f"Based on the available trade fraud intelligence data with {context.get('total_transactions', 'N/A')} transactions, I can provide analysis on risk patterns, entity relationships, and investigation strategies."
    
    def _parse_transaction_prompt(self, prompt: str) -> Dict[str, Any]:
        """Parse transaction data from explanation prompt."""
        data = {}
        lines = prompt.split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if 'price deviation' in key:
                    try:
                        data['price_deviation'] = float(value.replace('%', '')) / 100
                    except:
                        data['price_deviation'] = 0
                elif 'route anomaly' in key:
                    try:
                        data['route_anomaly'] = int(float(value))
                    except:
                        data['route_anomaly'] = 0
                elif 'company risk score' in key:
                    try:
                        data['company_risk_score'] = float(value)
                    except:
                        data['company_risk_score'] = 0
                elif 'port activity index' in key:
                    try:
                        data['port_activity_index'] = float(value)
                    except:
                        data['port_activity_index'] = 0
        
        return data
    
    def _extract_query(self, prompt: str) -> str:
        """Extract query from investigation prompt."""
        lines = prompt.split('\n')
        for line in lines:
            if line.startswith('Question:'):
                return line.replace('Question:', '').strip()
        return ""
    
    def _extract_context(self, prompt: str) -> Dict[str, Any]:
        """Extract context from investigation prompt."""
        context = {}
        lines = prompt.split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line and any(keyword in line.lower() for keyword in ['total', 'fraud', 'suspicious', 'companies', 'patterns']):
                try:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'total transactions' in key:
                        context['total_transactions'] = int(value) if value != 'N/A' else 1000
                    elif 'fraud cases' in key:
                        context['fraud_cases'] = int(value) if value != 'N/A' else 50
                    elif 'suspicious cases' in key:
                        context['suspicious_cases'] = int(value) if value != 'N/A' else 150
                    elif 'high-risk companies' in key:
                        # Parse list format
                        companies = value.replace('[', '').replace(']', '').replace("'", "").split(',')
                        context['high_risk_companies'] = [c.strip() for c in companies if c.strip()]
                    elif 'fraud patterns' in key:
                        # Parse list format
                        patterns = value.replace('[', '').replace(']', '').replace("'", "").split(',')
                        context['fraud_patterns'] = [p.strip() for p in patterns if p.strip()]
                except:
                    pass
        
        return context


class MockGeminiResponse:
    """Mock response object that mimics Gemini API response structure."""
    
    def __init__(self, text: str):
        self.text = text
        self.candidates = [Mock(content=Mock(parts=[Mock(text=text)]))]
        self.prompt_feedback = Mock()


class MockGenAIModule:
    """Mock for the google.generativeai module."""
    
    def __init__(self, config: Optional[GeminiMockConfig] = None):
        self.config = config or GeminiMockConfig()
        self.GenerativeModel = lambda model_name: RealisticGeminiMock(self.config)
    
    def configure(self, api_key: str):
        """Mock configuration method."""
        if not api_key:
            raise Exception("API key is required")
        if api_key == "invalid_key":
            raise Exception("Invalid API key")


# Global mock instances
_global_config = GeminiMockConfig()
_global_mock_genai = MockGenAIModule(_global_config)


def get_mock_config() -> GeminiMockConfig:
    """Get the global mock configuration."""
    return _global_config


def reset_mock_config():
    """Reset the global mock configuration."""
    global _global_config
    _global_config.reset()


def create_gemini_mock_patches(config: Optional[GeminiMockConfig] = None):
    """
    Create patch objects for mocking Gemini API.
    
    Returns a dictionary of patch objects that can be used as context managers
    or applied to test functions.
    """
    mock_config = config or _global_config
    mock_genai = MockGenAIModule(mock_config)
    
    return {
        'gemini_available': patch('backend.ai_explainer.GEMINI_AVAILABLE', True),
        'genai_module': patch('backend.ai_explainer.genai', mock_genai),
        'generation_config': patch('backend.ai_explainer.GenerationConfig', Mock),
        'request_options': patch('backend.ai_explainer.RequestOptions', Mock)
    }


def mock_gemini_success():
    """Context manager for successful Gemini API mocking."""
    patches = create_gemini_mock_patches()
    return patch.multiple('backend.ai_explainer', **{k: v.new for k, v in patches.items()})


def mock_gemini_failure(failure_type: str = "api_error", message: str = "Mock failure"):
    """Context manager for Gemini API failure mocking."""
    config = GeminiMockConfig()
    config.configure_failure(True, failure_type, message)
    patches = create_gemini_mock_patches(config)
    return patch.multiple('backend.ai_explainer', **{k: v.new for k, v in patches.items()})


def mock_gemini_unavailable():
    """Context manager for Gemini API unavailable mocking."""
    return patch('backend.ai_explainer.GEMINI_AVAILABLE', False)


# Convenience functions for common test scenarios
def create_sample_transaction(risk_level: str = "high") -> Dict[str, Any]:
    """Create sample transaction data for testing."""
    base_transaction = {
        'transaction_id': f'TXN_{risk_level.upper()}_001',
        'product': 'Electronics',
        'commodity_category': 'Consumer Goods',
        'market_price': 1000,
        'shipping_route': 'Shanghai-Los Angeles',
        'distance_km': 11000
    }
    
    if risk_level == "high":
        base_transaction.update({
            'unit_price': 1800,
            'price_deviation': 0.8,
            'route_anomaly': 1,
            'company_risk_score': 0.95,
            'port_activity_index': 2.5,
            'risk_score': 0.7,
            'risk_category': 'FRAUD'
        })
    elif risk_level == "medium":
        base_transaction.update({
            'unit_price': 1200,
            'price_deviation': 0.2,
            'route_anomaly': 0,
            'company_risk_score': 0.6,
            'port_activity_index': 1.3,
            'risk_score': 0.3,
            'risk_category': 'SUSPICIOUS'
        })
    else:  # low risk
        base_transaction.update({
            'unit_price': 1050,
            'price_deviation': 0.05,
            'route_anomaly': 0,
            'company_risk_score': 0.2,
            'port_activity_index': 1.0,
            'risk_score': -0.1,
            'risk_category': 'SAFE'
        })
    
    return base_transaction


def create_sample_context(fraud_rate: float = 0.05) -> Dict[str, Any]:
    """Create sample context data for investigation queries."""
    total_transactions = 1000
    fraud_cases = int(total_transactions * fraud_rate)
    suspicious_cases = int(total_transactions * fraud_rate * 2)
    
    return {
        'total_transactions': total_transactions,
        'fraud_cases': fraud_cases,
        'suspicious_cases': suspicious_cases,
        'avg_risk_score': fraud_rate * 2,
        'high_risk_companies': ['HighRiskCorp', 'SuspiciousLtd', 'FlaggedInc'],
        'fraud_patterns': ['Price manipulation', 'Route laundering', 'Volume misrepresentation', 'Entity masking']
    }


# Test utilities
def validate_mock_explanation(explanation: str, transaction: Dict[str, Any]) -> bool:
    """Validate that a mock explanation is realistic and relevant."""
    if not explanation or len(explanation) < 50:
        return False
    
    # Check for relevant keywords based on transaction risk factors
    explanation_lower = explanation.lower()
    
    # Price deviation check
    price_dev = abs(transaction.get('price_deviation', 0))
    if price_dev > 0.3:
        if not any(keyword in explanation_lower for keyword in ['price', 'deviation', 'invoicing']):
            return False
    
    # Route anomaly check
    if transaction.get('route_anomaly') == 1:
        if not any(keyword in explanation_lower for keyword in ['route', 'shipping', 'unusual']):
            return False
    
    # Company risk check
    if transaction.get('company_risk_score', 0) > 0.7:
        if not any(keyword in explanation_lower for keyword in ['company', 'risk', 'entity']):
            return False
    
    return True


def validate_mock_investigation_response(response: str, query: str, context: Dict[str, Any]) -> bool:
    """Validate that a mock investigation response is realistic and relevant."""
    if not response or len(response) < 30:
        return False
    
    query_lower = query.lower()
    response_lower = response.lower()
    
    # Check query-specific relevance
    if 'fraud rate' in query_lower:
        return any(keyword in response_lower for keyword in ['rate', 'percentage', '%', 'fraud'])
    elif 'patterns' in query_lower:
        return any(keyword in response_lower for keyword in ['pattern', 'manipulation', 'laundering'])
    elif 'companies' in query_lower or 'entities' in query_lower:
        return any(keyword in response_lower for keyword in ['company', 'entities', 'risk'])
    
    return True


if __name__ == "__main__":
    # Test the mock utilities
    print("Testing Gemini Mock Utilities...")
    
    # Test mock configuration
    config = GeminiMockConfig()
    print(f"✓ Mock configuration created: {config}")
    
    # Test realistic mock
    mock = RealisticGeminiMock(config)
    print(f"✓ Realistic mock created: {mock.model_name}")
    
    # Test sample data creation
    high_risk_tx = create_sample_transaction("high")
    print(f"✓ Sample high-risk transaction: {high_risk_tx['transaction_id']}")
    
    context = create_sample_context(0.1)
    print(f"✓ Sample context: {context['total_transactions']} transactions, {context['fraud_cases']} fraud cases")
    
    print("✓ All mock utilities working correctly!")