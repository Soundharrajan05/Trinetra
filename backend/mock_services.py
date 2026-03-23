"""
Mock service layer for TRINETRA AI development mode.

This module provides deterministic mock responses for external services
to eliminate API calls and network dependencies during development tasks
while maintaining identical response structures.
"""

import logging
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from .config import is_test_mode, is_fast_dev_mode

logger = logging.getLogger(__name__)


class MockServiceLayer:
    """
    Mock service layer providing deterministic responses for external dependencies.
    
    Ensures consistent, fast responses during development while maintaining
    the same data structures as real services.
    """
    
    @staticmethod
    def should_use_mock() -> bool:
        """
        Determine if mock services should be used.
        
        Returns:
            bool: True if mock services should be used
        """
        return is_test_mode() or is_fast_dev_mode()
    
    @staticmethod
    def get_ai_explanation(transaction: Dict[str, Any]) -> str:
        """
        Generate mock AI explanation for a transaction.
        
        Args:
            transaction (Dict[str, Any]): Transaction data dictionary
            
        Returns:
            str: Deterministic mock explanation
        """
        if not MockServiceLayer.should_use_mock():
            raise ValueError("Mock services should not be used in production mode")
        
        # Generate deterministic explanation based on transaction data
        transaction_id = transaction.get('transaction_id', 'unknown')
        amount = transaction.get('amount', 0)
        merchant = transaction.get('merchant', 'unknown')
        
        # Create deterministic hash for consistent responses
        hash_input = f"{transaction_id}_{amount}_{merchant}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        # Generate explanation based on transaction characteristics
        if amount > 1000:
            risk_level = "HIGH"
            explanation = f"Large transaction amount (${amount}) detected. "
        elif amount > 500:
            risk_level = "MEDIUM"
            explanation = f"Moderate transaction amount (${amount}) observed. "
        else:
            risk_level = "LOW"
            explanation = f"Standard transaction amount (${amount}) processed. "
        
        # Add merchant-based analysis
        if 'online' in merchant.lower() or 'web' in merchant.lower():
            explanation += "Online merchant transaction pattern identified. "
        elif 'atm' in merchant.lower():
            explanation += "ATM withdrawal pattern detected. "
        else:
            explanation += "In-person merchant transaction pattern observed. "
        
        # Add deterministic risk factors
        explanation += f"Risk assessment ID: {hash_value}. "
        explanation += f"Fraud probability calculated using isolation forest model. "
        explanation += f"Transaction classified as {risk_level} risk based on historical patterns."
        
        logger.debug(f"Generated mock AI explanation for transaction {transaction_id}")
        return explanation
    
    @staticmethod
    def get_mock_query_response(query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate mock response for query processing.
        
        Args:
            query (str): User query string
            context (Optional[Dict[str, Any]]): Additional context data
            
        Returns:
            str: Deterministic mock query response
        """
        if not MockServiceLayer.should_use_mock():
            raise ValueError("Mock services should not be used in production mode")
        
        # Normalize query for consistent processing
        query_lower = query.lower().strip()
        
        # Generate deterministic response based on query content
        if 'fraud' in query_lower or 'suspicious' in query_lower:
            response = "Based on the fraud detection analysis, the system identified "
            response += "anomalous patterns in transaction behavior. The isolation forest "
            response += "model flagged transactions with unusual amounts, timing, or "
            response += "merchant patterns as potentially fraudulent."
            
        elif 'transaction' in query_lower or 'payment' in query_lower:
            response = "Transaction analysis shows normal payment processing patterns. "
            response += "The system monitors transaction amounts, merchant categories, "
            response += "and timing patterns to identify potential anomalies using "
            response += "machine learning algorithms."
            
        elif 'model' in query_lower or 'algorithm' in query_lower:
            response = "The fraud detection system uses an Isolation Forest algorithm "
            response += "to identify anomalous transactions. This unsupervised learning "
            response += "approach detects outliers in transaction patterns without "
            response += "requiring labeled fraud examples."
            
        elif 'alert' in query_lower or 'notification' in query_lower:
            response = "The alert system monitors transaction patterns in real-time "
            response += "and generates notifications when suspicious activity is detected. "
            response += "Alerts are prioritized based on risk scores and transaction "
            response += "characteristics."
            
        else:
            # Generic response for unrecognized queries
            response = "The TRINETRA AI fraud detection system provides comprehensive "
            response += "transaction monitoring and analysis capabilities. The system "
            response += "uses machine learning algorithms to identify suspicious patterns "
            response += "and generate real-time alerts for potential fraud."
        
        # Add context-specific information if provided
        if context:
            if 'user_id' in context:
                response += f" Analysis performed for user {context['user_id']}."
            if 'time_range' in context:
                response += f" Data analyzed for time period: {context['time_range']}."
        
        # Add deterministic timestamp
        response += f" Response generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        
        logger.debug(f"Generated mock query response for: {query[:50]}...")
        return response
    
    @staticmethod
    def get_mock_api_response(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock API response for various endpoints.
        
        Args:
            endpoint (str): API endpoint name
            params (Dict[str, Any]): Request parameters
            
        Returns:
            Dict[str, Any]: Mock API response with proper structure
        """
        if not MockServiceLayer.should_use_mock():
            raise ValueError("Mock services should not be used in production mode")
        
        timestamp = datetime.now().isoformat()
        
        if endpoint == 'fraud_detection':
            return {
                'status': 'success',
                'timestamp': timestamp,
                'results': {
                    'fraud_probability': 0.15,
                    'risk_score': 3.2,
                    'anomaly_score': -0.1,
                    'classification': 'normal',
                    'model_version': 'isolation_forest_v1.0',
                    'processing_time_ms': 45
                },
                'metadata': {
                    'request_id': hashlib.md5(str(params).encode()).hexdigest()[:16],
                    'model_features_used': 12,
                    'confidence_level': 0.85
                }
            }
        
        elif endpoint == 'transaction_analysis':
            return {
                'status': 'success',
                'timestamp': timestamp,
                'analysis': {
                    'total_transactions': 1247,
                    'flagged_transactions': 18,
                    'fraud_rate': 1.44,
                    'average_amount': 342.56,
                    'risk_distribution': {
                        'low': 1156,
                        'medium': 73,
                        'high': 18
                    }
                },
                'metadata': {
                    'analysis_period': '24h',
                    'last_updated': timestamp
                }
            }
        
        elif endpoint == 'alert_summary':
            return {
                'status': 'success',
                'timestamp': timestamp,
                'alerts': {
                    'total_alerts': 23,
                    'high_priority': 5,
                    'medium_priority': 12,
                    'low_priority': 6,
                    'resolved': 18,
                    'pending': 5
                },
                'recent_alerts': [
                    {
                        'id': 'alert_001',
                        'type': 'high_amount_transaction',
                        'priority': 'high',
                        'timestamp': timestamp,
                        'status': 'pending'
                    },
                    {
                        'id': 'alert_002',
                        'type': 'unusual_merchant',
                        'priority': 'medium',
                        'timestamp': timestamp,
                        'status': 'resolved'
                    }
                ]
            }
        
        else:
            # Generic response for unknown endpoints
            return {
                'status': 'success',
                'timestamp': timestamp,
                'message': f'Mock response for endpoint: {endpoint}',
                'data': params,
                'mock': True
            }
    
    @staticmethod
    def simulate_processing_delay(operation: str = 'default') -> None:
        """
        Simulate minimal processing delay for realistic behavior.
        
        Args:
            operation (str): Type of operation being simulated
        """
        import time
        
        # Very short delays to simulate processing without slowing down development
        delay_map = {
            'ai_explanation': 0.01,  # 10ms
            'query_processing': 0.005,  # 5ms
            'api_call': 0.002,  # 2ms
            'default': 0.001  # 1ms
        }
        
        delay = delay_map.get(operation, delay_map['default'])
        time.sleep(delay)
        logger.debug(f"Simulated {delay*1000}ms delay for {operation}")


# Convenience functions for common mock operations
def get_mock_explanation(transaction_data: Dict[str, Any]) -> str:
    """Get mock AI explanation for transaction."""
    MockServiceLayer.simulate_processing_delay('ai_explanation')
    return MockServiceLayer.get_ai_explanation(transaction_data)


def get_mock_query_response(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Get mock response for user query."""
    MockServiceLayer.simulate_processing_delay('query_processing')
    return MockServiceLayer.get_mock_query_response(query, context)


def get_mock_api_response(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get mock API response."""
    MockServiceLayer.simulate_processing_delay('api_call')
    return MockServiceLayer.get_mock_api_response(endpoint, params)


def is_mock_mode_enabled() -> bool:
    """Check if mock mode is currently enabled."""
    return MockServiceLayer.should_use_mock()


def log_mock_usage(operation: str, details: str = "") -> None:
    """Log mock service usage for debugging."""
    if MockServiceLayer.should_use_mock():
        logger.debug(f"Mock service used for {operation}: {details}")
    else:
        logger.warning(f"Mock service called in production mode for {operation}")


# Mock data generators for testing
class MockDataGenerator:
    """Generate mock data for testing and development."""
    
    @staticmethod
    def generate_mock_transactions(count: int = 10) -> List[Dict[str, Any]]:
        """Generate mock transaction data."""
        transactions = []
        for i in range(count):
            transaction = {
                'transaction_id': f'txn_{i:06d}',
                'amount': round(50 + (i * 47.3) % 2000, 2),
                'merchant': f'merchant_{i % 5}',
                'timestamp': datetime.now().isoformat(),
                'user_id': f'user_{i % 100}',
                'category': ['grocery', 'gas', 'restaurant', 'online', 'atm'][i % 5]
            }
            transactions.append(transaction)
        return transactions
    
    @staticmethod
    def generate_mock_features(transaction_count: int = 100) -> Dict[str, List[float]]:
        """Generate mock feature data."""
        import random
        random.seed(42)  # Deterministic for testing
        
        return {
            'amount_zscore': [random.gauss(0, 1) for _ in range(transaction_count)],
            'time_since_last': [random.uniform(0, 24) for _ in range(transaction_count)],
            'merchant_frequency': [random.uniform(0, 1) for _ in range(transaction_count)],
            'amount_percentile': [random.uniform(0, 100) for _ in range(transaction_count)]
        }