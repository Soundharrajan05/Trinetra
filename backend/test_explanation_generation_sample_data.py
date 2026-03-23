#!/usr/bin/env python3
"""
Test explanation generation with sample data for TRINETRA AI fraud detection system.

This test validates that the AI explanation functionality works correctly with real
transaction data from the dataset, testing different types of transactions (safe,
suspicious, fraud) and ensuring explanations are meaningful and contextual.

**Validates: Requirements US-4 (AI-Powered Fraud Explanations)**
"""

import unittest
import pandas as pd
import os
import sys
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any, List

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_dataset
from feature_engineering import engineer_features
from fraud_detection import score_transactions, classify_risk, load_fraud_detector
from ai_explainer import (
    explain_transaction, 
    answer_investigation_query,
    initialize_gemini,
    _generate_fallback_explanation,
    GeminiAPIError,
    GeminiTimeoutError,
    GeminiRateLimitError
)


class TestExplanationGenerationSampleData(unittest.TestCase):
    """Test AI explanation generation with real sample transaction data."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data once for all tests."""
        # Load and process real dataset
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            # Try alternative path
            dataset_path = "../data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found at {dataset_path}")
        
        # Load and process data
        cls.df = load_dataset(dataset_path)
        cls.df = engineer_features(cls.df)
        
        # Try to load model and score transactions
        try:
            model = load_fraud_detector()
            cls.df = score_transactions(cls.df, model)
            cls.df = classify_risk(cls.df)
            cls.has_risk_scores = True
        except Exception as e:
            print(f"Warning: Could not load model for risk scoring: {e}")
            # Add dummy risk scores for testing
            cls.df['risk_score'] = 0.0
            cls.df['risk_category'] = 'SAFE'
            cls.has_risk_scores = False
        
        # Select sample transactions for different risk categories
        cls.sample_transactions = cls._select_sample_transactions()
    
    @classmethod
    def _select_sample_transactions(cls) -> Dict[str, Dict[str, Any]]:
        """Select representative transactions for testing."""
        samples = {}
        
        # Get first few transactions as samples
        for i in range(min(5, len(cls.df))):
            transaction = cls.df.iloc[i].to_dict()
            samples[f"sample_{i+1}"] = transaction
        
        # If we have risk scores, try to get different categories
        if cls.has_risk_scores:
            try:
                # Get one from each category if available
                categories = ['SAFE', 'SUSPICIOUS', 'FRAUD']
                for category in categories:
                    category_transactions = cls.df[cls.df['risk_category'] == category]
                    if not category_transactions.empty:
                        transaction = category_transactions.iloc[0].to_dict()
                        samples[f"{category.lower()}_transaction"] = transaction
            except Exception as e:
                print(f"Warning: Could not categorize transactions: {e}")
        
        return samples
    
    def setUp(self):
        """Set up for each test."""
        self.mock_model = MagicMock()
        self.mock_model.generate_content.return_value.text = (
            "This transaction shows suspicious patterns due to significant price deviation "
            "from market rates and unusual shipping route characteristics that warrant investigation."
        )
    
    def test_explain_transaction_with_real_data(self):
        """Test explanation generation with real transaction data."""
        for sample_name, transaction in self.sample_transactions.items():
            with self.subTest(sample=sample_name):
                # Test with mock Gemini API to avoid quota issues
                with patch('ai_explainer.get_gemini_model', return_value=self.mock_model):
                    explanation = explain_transaction(transaction)
                    
                    # Validate explanation quality
                    self.assertIsInstance(explanation, str)
                    self.assertGreater(len(explanation), 50, 
                                     f"Explanation too short for {sample_name}")
                    self.assertLess(len(explanation), 2000, 
                                   f"Explanation too long for {sample_name}")
                    
                    # Check for key fraud indicators in explanation
                    explanation_lower = explanation.lower()
                    fraud_keywords = ['price', 'deviation', 'risk', 'suspicious', 'anomaly', 'fraud', 'analysis']
                    found_keywords = [kw for kw in fraud_keywords if kw in explanation_lower]
                    self.assertGreater(len(found_keywords), 0, 
                                     f"No fraud keywords found in explanation for {sample_name}")
    
    def test_explain_high_risk_transaction(self):
        """Test explanation for transactions with high fraud indicators."""
        # Create a synthetic high-risk transaction
        high_risk_transaction = {
            'transaction_id': 'TEST_HIGH_RISK_001',
            'product': 'Electronics',
            'commodity_category': 'Technology',
            'market_price': 1000.0,
            'unit_price': 1500.0,  # 50% above market price
            'price_deviation': 0.5,
            'shipping_route': 'Suspicious Route',
            'distance_km': 5000,
            'company_risk_score': 0.9,  # High risk company
            'port_activity_index': 2.0,  # High port activity
            'route_anomaly': 1,  # Anomalous route
            'price_anomaly_score': 0.5,
            'route_risk_score': 1,
            'company_network_risk': 0.9,
            'port_congestion_score': 2.0,
            'risk_score': 0.8,
            'risk_category': 'FRAUD'
        }
        
        with patch('ai_explainer.get_gemini_model', return_value=self.mock_model):
            explanation = explain_transaction(high_risk_transaction)
            
            # Validate explanation addresses high-risk factors
            explanation_lower = explanation.lower()
            self.assertIn('price', explanation_lower)
            self.assertIn('risk', explanation_lower)
            
            # Should be substantial explanation for high-risk transaction
            self.assertGreater(len(explanation), 100)
    
    def test_explain_safe_transaction(self):
        """Test explanation for low-risk transactions."""
        # Create a synthetic safe transaction
        safe_transaction = {
            'transaction_id': 'TEST_SAFE_001',
            'product': 'Textiles',
            'commodity_category': 'Manufacturing',
            'market_price': 100.0,
            'unit_price': 105.0,  # Slight premium
            'price_deviation': 0.05,
            'shipping_route': 'Standard Route',
            'distance_km': 2000,
            'company_risk_score': 0.1,  # Low risk company
            'port_activity_index': 0.8,  # Normal port activity
            'route_anomaly': 0,  # Normal route
            'price_anomaly_score': 0.05,
            'route_risk_score': 0,
            'company_network_risk': 0.1,
            'port_congestion_score': 0.8,
            'risk_score': -0.5,
            'risk_category': 'SAFE'
        }
        
        # Mock a response appropriate for safe transactions
        safe_mock_model = MagicMock()
        safe_mock_model.generate_content.return_value.text = (
            "This transaction appears legitimate with normal pricing patterns, "
            "standard shipping routes, and low-risk company profile."
        )
        
        with patch('ai_explainer.get_gemini_model', return_value=safe_mock_model):
            explanation = explain_transaction(safe_transaction)
            
            # Validate explanation reflects low risk
            explanation_lower = explanation.lower()
            positive_indicators = ['legitimate', 'normal', 'standard', 'low-risk']
            found_positive = [ind for ind in positive_indicators if ind in explanation_lower]
            self.assertGreater(len(found_positive), 0, 
                             "No positive indicators found in safe transaction explanation")
    
    def test_explanation_fallback_system(self):
        """Test fallback explanation system when Gemini API fails."""
        transaction = self.sample_transactions[list(self.sample_transactions.keys())[0]]
        
        # Test with various API failures
        api_errors = [
            GeminiAPIError("API Error"),
            GeminiTimeoutError("Timeout"),
            GeminiRateLimitError("Rate Limited")
        ]
        
        for error in api_errors:
            with self.subTest(error=type(error).__name__):
                with patch('ai_explainer.get_gemini_model') as mock_get_model:
                    mock_model = MagicMock()
                    mock_model.generate_content.side_effect = error
                    mock_get_model.return_value = mock_model
                    
                    explanation = explain_transaction(transaction)
                    
                    # Should get fallback explanation
                    self.assertIsInstance(explanation, str)
                    self.assertGreater(len(explanation), 20)
                    self.assertIn("analysis", explanation.lower())
    
    def test_investigation_query_with_sample_data(self):
        """Test natural language investigation queries with sample data."""
        # Use first sample transaction as context
        transaction = self.sample_transactions[list(self.sample_transactions.keys())[0]]
        context = {
            'transaction': transaction,
            'dataset_stats': {
                'total_transactions': len(self.df),
                'fraud_rate': 0.1,
                'avg_price_deviation': 0.2
            }
        }
        
        test_queries = [
            "Why is this transaction suspicious?",
            "What are the main fraud indicators?",
            "How does the price compare to market rates?",
            "Is the shipping route unusual?",
            "What is the company risk profile?"
        ]
        
        for query in test_queries:
            with self.subTest(query=query):
                with patch('ai_explainer.get_gemini_model', return_value=self.mock_model):
                    response = answer_investigation_query(query, context)
                    
                    # Validate response quality
                    self.assertIsInstance(response, str)
                    self.assertGreater(len(response), 30)
                    self.assertLess(len(response), 1500)
    
    def test_explanation_content_quality(self):
        """Test that explanations contain relevant fraud detection content."""
        # Test with a transaction that has clear fraud indicators
        transaction_with_indicators = {
            'transaction_id': 'TEST_QUALITY_001',
            'product': 'Gold',
            'commodity_category': 'Precious Metals',
            'market_price': 50000.0,
            'unit_price': 75000.0,  # 50% above market
            'price_deviation': 0.5,
            'shipping_route': 'High Risk Route',
            'distance_km': 8000,
            'company_risk_score': 0.8,
            'port_activity_index': 1.8,
            'route_anomaly': 1,
            'price_anomaly_score': 0.5,
            'route_risk_score': 1,
            'company_network_risk': 0.8,
            'port_congestion_score': 1.8
        }
        
        # Mock detailed response
        detailed_mock = MagicMock()
        detailed_mock.generate_content.return_value.text = (
            "This gold transaction exhibits multiple fraud indicators: "
            "1) Price is 50% above market rate suggesting potential over-invoicing, "
            "2) Route anomaly indicates unusual shipping path, "
            "3) High company risk score of 0.8 suggests previous suspicious activity, "
            "4) Elevated port activity index may indicate trade-based money laundering."
        )
        
        with patch('ai_explainer.get_gemini_model', return_value=detailed_mock):
            explanation = explain_transaction(transaction_with_indicators)
            
            # Check for specific fraud concepts
            fraud_concepts = [
                'price', 'market', 'over-invoicing', 'route', 'anomaly', 
                'risk', 'suspicious', 'money laundering'
            ]
            
            explanation_lower = explanation.lower()
            found_concepts = [concept for concept in fraud_concepts 
                            if concept in explanation_lower]
            
            self.assertGreaterEqual(len(found_concepts), 3, 
                                  f"Expected at least 3 fraud concepts, found: {found_concepts}")
    
    def test_explanation_error_handling(self):
        """Test error handling in explanation generation."""
        # Test with malformed transaction data
        malformed_transactions = [
            {},  # Empty transaction
            {'transaction_id': 'TEST_001'},  # Missing required fields
            {'transaction_id': None, 'product': 'Test'},  # None values
        ]
        
        for i, transaction in enumerate(malformed_transactions):
            with self.subTest(transaction_type=f"malformed_{i}"):
                # Should handle gracefully and return fallback
                explanation = explain_transaction(transaction)
                self.assertIsInstance(explanation, str)
                self.assertGreater(len(explanation), 10)
    
    def test_batch_explanation_generation(self):
        """Test generating explanations for multiple transactions."""
        # Test with first 3 sample transactions
        sample_keys = list(self.sample_transactions.keys())[:3]
        
        with patch('ai_explainer.get_gemini_model', return_value=self.mock_model):
            explanations = []
            
            for key in sample_keys:
                transaction = self.sample_transactions[key]
                explanation = explain_transaction(transaction)
                explanations.append(explanation)
            
            # Validate all explanations generated
            self.assertEqual(len(explanations), 3)
            
            for i, explanation in enumerate(explanations):
                with self.subTest(batch_item=i):
                    self.assertIsInstance(explanation, str)
                    self.assertGreater(len(explanation), 20)
    
    def test_explanation_consistency(self):
        """Test that similar transactions get consistent explanations."""
        # Create two similar transactions
        base_transaction = {
            'transaction_id': 'TEST_CONSISTENCY_001',
            'product': 'Electronics',
            'commodity_category': 'Technology',
            'market_price': 1000.0,
            'unit_price': 1200.0,
            'price_deviation': 0.2,
            'shipping_route': 'Standard Route',
            'distance_km': 3000,
            'company_risk_score': 0.3,
            'port_activity_index': 1.0,
            'route_anomaly': 0
        }
        
        similar_transaction = base_transaction.copy()
        similar_transaction['transaction_id'] = 'TEST_CONSISTENCY_002'
        similar_transaction['unit_price'] = 1210.0  # Slightly different price
        
        # Mock consistent responses
        consistent_mock = MagicMock()
        consistent_mock.generate_content.return_value.text = (
            "This electronics transaction shows moderate price deviation above market rates. "
            "The standard shipping route and moderate company risk profile suggest "
            "this requires routine monitoring but is not immediately suspicious."
        )
        
        with patch('ai_explainer.get_gemini_model', return_value=consistent_mock):
            explanation1 = explain_transaction(base_transaction)
            explanation2 = explain_transaction(similar_transaction)
            
            # Both should be substantial explanations
            self.assertGreater(len(explanation1), 50)
            self.assertGreater(len(explanation2), 50)
            
            # Should contain similar key concepts
            common_words = ['electronics', 'price', 'deviation', 'market']
            for word in common_words:
                self.assertIn(word.lower(), explanation1.lower())
                self.assertIn(word.lower(), explanation2.lower())
    
    def test_fallback_explanation_quality(self):
        """Test that fallback explanations are meaningful and informative."""
        # Test fallback with various transaction types
        test_transactions = [
            {
                'transaction_id': 'FALLBACK_001',
                'price_deviation': 0.6,  # High price deviation
                'route_anomaly': 0,
                'company_risk_score': 0.2,
                'port_activity_index': 1.0
            },
            {
                'transaction_id': 'FALLBACK_002',
                'price_deviation': 0.1,
                'route_anomaly': 1,  # Route anomaly
                'company_risk_score': 0.2,
                'port_activity_index': 1.0
            },
            {
                'transaction_id': 'FALLBACK_003',
                'price_deviation': 0.1,
                'route_anomaly': 0,
                'company_risk_score': 0.9,  # High company risk
                'port_activity_index': 1.0
            }
        ]
        
        for i, transaction in enumerate(test_transactions):
            with self.subTest(fallback_case=i):
                fallback_explanation = _generate_fallback_explanation(transaction)
                
                # Validate fallback quality
                self.assertIsInstance(fallback_explanation, str)
                self.assertGreater(len(fallback_explanation), 50)
                self.assertIn("analysis", fallback_explanation.lower())
                
                # Should mention specific risk factors
                if transaction.get('price_deviation', 0) > 0.5:
                    self.assertIn("price", fallback_explanation.lower())
                if transaction.get('route_anomaly', 0) == 1:
                    self.assertIn("route", fallback_explanation.lower())
                if transaction.get('company_risk_score', 0) > 0.8:
                    self.assertIn("company", fallback_explanation.lower())
    
    def test_real_data_integration(self):
        """Test integration with real dataset - verify data loading and processing works."""
        # Verify we have real data loaded
        self.assertGreater(len(self.df), 0, "No data loaded from dataset")
        self.assertGreater(len(self.sample_transactions), 0, "No sample transactions available")
        
        # Verify required columns exist
        required_columns = ['transaction_id', 'product', 'market_price', 'unit_price']
        for col in required_columns:
            self.assertIn(col, self.df.columns, f"Required column {col} missing from dataset")
        
        # Test explanation with actual data structure
        first_transaction = self.sample_transactions[list(self.sample_transactions.keys())[0]]
        
        # Should have transaction_id
        self.assertIn('transaction_id', first_transaction)
        self.assertIsNotNone(first_transaction['transaction_id'])
        
        # Test fallback explanation with real data
        fallback_explanation = _generate_fallback_explanation(first_transaction)
        self.assertIsInstance(fallback_explanation, str)
        self.assertGreater(len(fallback_explanation), 30)


def run_explanation_tests():
    """Run the explanation generation tests."""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestExplanationGenerationSampleData)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("EXPLANATION GENERATION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\\n')[-2]}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_explanation_tests()
    sys.exit(0 if success else 1)