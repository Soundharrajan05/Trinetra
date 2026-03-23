#!/usr/bin/env python3
"""
Test Explanation Quality and Relevance for TRINETRA AI

This module validates that AI-generated explanations meet quality standards:
- Explanations are relevant to transaction data
- Key fraud indicators are addressed (price deviation, route anomaly, company risk, etc.)
- Explanations are clear, concise, and actionable for fraud investigators
- Explanations meet usability requirements (NFR-2)

**Validates: Requirements US-4 (AI-Powered Fraud Explanations), NFR-2 (Usability)**

Author: TRINETRA AI Development Team
"""

import unittest
import sys
import os
from typing import Dict, Any, List, Set
from unittest.mock import patch, MagicMock

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_explainer import (
    explain_transaction,
    _generate_fallback_explanation,
    initialize_gemini,
    GeminiAPIError
)


class TestExplanationQuality(unittest.TestCase):
    """Test suite for validating explanation quality and relevance."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock Gemini model for consistent testing
        self.mock_model = MagicMock()
        
        # Sample transactions with different risk profiles
        self.high_risk_transaction = {
            'transaction_id': 'TXN_HIGH_001',
            'product': 'Gold Bars',
            'commodity_category': 'Precious Metals',
            'market_price': 50000.0,
            'unit_price': 75000.0,
            'price_deviation': 0.5,  # 50% above market
            'shipping_route': 'Dubai-Panama',
            'distance_km': 12000,
            'company_risk_score': 0.9,
            'port_activity_index': 2.0,
            'route_anomaly': 1,
            'risk_score': 0.8,
            'risk_category': 'FRAUD'
        }
        
        self.moderate_risk_transaction = {
            'transaction_id': 'TXN_MOD_001',
            'product': 'Electronics',
            'commodity_category': 'Technology',
            'market_price': 1000.0,
            'unit_price': 1300.0,
            'price_deviation': 0.3,  # 30% above market
            'shipping_route': 'Shanghai-Los Angeles',
            'distance_km': 11000,
            'company_risk_score': 0.5,
            'port_activity_index': 1.2,
            'route_anomaly': 0,
            'risk_score': 0.1,
            'risk_category': 'SUSPICIOUS'
        }
        
        self.low_risk_transaction = {
            'transaction_id': 'TXN_LOW_001',
            'product': 'Textiles',
            'commodity_category': 'Manufacturing',
            'market_price': 100.0,
            'unit_price': 105.0,
            'price_deviation': 0.05,  # 5% above market
            'shipping_route': 'Mumbai-London',
            'distance_km': 7200,
            'company_risk_score': 0.1,
            'port_activity_index': 0.8,
            'route_anomaly': 0,
            'risk_score': -0.3,
            'risk_category': 'SAFE'
        }
    
    def test_explanation_length_appropriate(self):
        """Test that explanations are concise but informative (not too short or too long)."""
        test_cases = [
            ('high_risk', self.high_risk_transaction),
            ('moderate_risk', self.moderate_risk_transaction),
            ('low_risk', self.low_risk_transaction)
        ]
        
        for case_name, transaction in test_cases:
            with self.subTest(case=case_name):
                explanation = _generate_fallback_explanation(transaction)
                
                # Explanations should be between 50 and 1000 characters
                self.assertGreaterEqual(len(explanation), 50,
                    f"{case_name}: Explanation too short ({len(explanation)} chars)")
                self.assertLessEqual(len(explanation), 1000,
                    f"{case_name}: Explanation too long ({len(explanation)} chars)")
    
    def test_explanation_addresses_price_deviation(self):
        """Test that explanations mention price deviation when significant."""
        # High price deviation transaction
        high_price_dev_transaction = {
            'transaction_id': 'TXN_PRICE_001',
            'product': 'Diamonds',
            'price_deviation': 0.6,  # 60% deviation
            'market_price': 10000,
            'unit_price': 16000,
            'company_risk_score': 0.2,
            'port_activity_index': 1.0,
            'route_anomaly': 0
        }
        
        explanation = _generate_fallback_explanation(high_price_dev_transaction)
        explanation_lower = explanation.lower()
        
        # Should mention price-related terms
        price_keywords = ['price', 'deviation', 'market', 'above', 'below']
        found_keywords = [kw for kw in price_keywords if kw in explanation_lower]
        
        self.assertGreater(len(found_keywords), 0,
            "Explanation should mention price deviation when significant")
        
        # Should include the actual deviation percentage
        self.assertIn('60', explanation.replace('%', ''),
            "Explanation should include deviation percentage")
    
    def test_explanation_addresses_route_anomaly(self):
        """Test that explanations mention route anomalies when present."""
        route_anomaly_transaction = {
            'transaction_id': 'TXN_ROUTE_001',
            'product': 'Oil',
            'price_deviation': 0.1,
            'route_anomaly': 1,  # Anomalous route
            'shipping_route': 'Unusual-Route',
            'company_risk_score': 0.2,
            'port_activity_index': 1.0
        }
        
        explanation = _generate_fallback_explanation(route_anomaly_transaction)
        explanation_lower = explanation.lower()
        
        # Should mention route-related terms
        route_keywords = ['route', 'shipping', 'suspicious']
        found_keywords = [kw for kw in route_keywords if kw in explanation_lower]
        
        self.assertGreater(len(found_keywords), 0,
            "Explanation should mention route anomaly when present")
    
    def test_explanation_addresses_company_risk(self):
        """Test that explanations mention company risk when high."""
        high_company_risk_transaction = {
            'transaction_id': 'TXN_COMPANY_001',
            'product': 'Chemicals',
            'price_deviation': 0.1,
            'route_anomaly': 0,
            'company_risk_score': 0.9,  # Very high risk
            'port_activity_index': 1.0
        }
        
        explanation = _generate_fallback_explanation(high_company_risk_transaction)
        explanation_lower = explanation.lower()
        
        # Should mention company risk
        company_keywords = ['company', 'risk', 'score']
        found_keywords = [kw for kw in company_keywords if kw in explanation_lower]
        
        self.assertGreater(len(found_keywords), 0,
            "Explanation should mention company risk when high")
        
        # Should include the risk score
        self.assertIn('0.9', explanation,
            "Explanation should include company risk score")
    
    def test_explanation_addresses_port_activity(self):
        """Test that explanations mention port activity when unusual."""
        high_port_activity_transaction = {
            'transaction_id': 'TXN_PORT_001',
            'product': 'Containers',
            'price_deviation': 0.1,
            'route_anomaly': 0,
            'company_risk_score': 0.2,
            'port_activity_index': 2.5  # Very high activity
        }
        
        explanation = _generate_fallback_explanation(high_port_activity_transaction)
        explanation_lower = explanation.lower()
        
        # Should mention port activity
        port_keywords = ['port', 'activity', 'unusual']
        found_keywords = [kw for kw in port_keywords if kw in explanation_lower]
        
        self.assertGreater(len(found_keywords), 0,
            "Explanation should mention port activity when unusual")
    
    def test_explanation_prioritizes_most_significant_indicators(self):
        """Test that explanations focus on the most significant fraud indicators."""
        # Transaction with multiple indicators of varying severity
        multi_indicator_transaction = {
            'transaction_id': 'TXN_MULTI_001',
            'product': 'Gold',
            'price_deviation': 0.7,  # Very high - should be mentioned
            'route_anomaly': 1,  # Present - should be mentioned
            'company_risk_score': 0.95,  # Very high - should be mentioned
            'port_activity_index': 1.1,  # Slightly elevated - less critical
            'volume_spike_score': 50,  # Low - less critical
            'shipment_duration_risk': 0.05  # Low - less critical
        }
        
        explanation = _generate_fallback_explanation(multi_indicator_transaction)
        explanation_lower = explanation.lower()
        
        # High-priority indicators should be mentioned
        high_priority_keywords = ['price', 'route', 'company']
        found_high_priority = [kw for kw in high_priority_keywords if kw in explanation_lower]
        
        self.assertGreaterEqual(len(found_high_priority), 2,
            "Explanation should mention at least 2 high-priority indicators")
    
    def test_explanation_clarity_and_readability(self):
        """Test that explanations are clear and readable for investigators."""
        explanation = _generate_fallback_explanation(self.high_risk_transaction)
        
        # Should use complete sentences
        self.assertIn('.', explanation,
            "Explanation should contain complete sentences")
        
        # Should not be overly technical
        # Check for presence of clear, investigator-friendly language
        investigator_friendly_terms = [
            'fraud', 'suspicious', 'risk', 'detected', 'flagged',
            'analysis', 'investigation', 'indicators'
        ]
        
        explanation_lower = explanation.lower()
        found_terms = [term for term in investigator_friendly_terms 
                      if term in explanation_lower]
        
        self.assertGreater(len(found_terms), 0,
            "Explanation should use investigator-friendly terminology")
    
    def test_explanation_actionability(self):
        """Test that explanations provide actionable information for investigators."""
        explanation = _generate_fallback_explanation(self.high_risk_transaction)
        explanation_lower = explanation.lower()
        
        # Should indicate what needs investigation
        actionable_keywords = [
            'investigation', 'review', 'requires', 'flagged',
            'detected', 'analysis', 'suspicious', 'fraud'
        ]
        
        found_actionable = [kw for kw in actionable_keywords if kw in explanation_lower]
        
        self.assertGreater(len(found_actionable), 0,
            "Explanation should provide actionable guidance")
    
    def test_explanation_relevance_to_transaction_data(self):
        """Test that explanations are relevant to the specific transaction data."""
        # Test with transaction that has specific characteristics
        specific_transaction = {
            'transaction_id': 'TXN_SPECIFIC_001',
            'product': 'Luxury Watches',
            'commodity_category': 'Luxury Goods',
            'price_deviation': 0.8,  # 80% above market
            'market_price': 5000,
            'unit_price': 9000,
            'route_anomaly': 1,
            'company_risk_score': 0.85,
            'port_activity_index': 1.9
        }
        
        explanation = _generate_fallback_explanation(specific_transaction)
        
        # Explanation should reference the actual data values
        # Check for price deviation percentage
        self.assertTrue(
            '80' in explanation or '0.8' in explanation,
            "Explanation should reference actual price deviation value"
        )
        
        # Check for company risk score
        self.assertTrue(
            '0.85' in explanation or '85' in explanation,
            "Explanation should reference actual company risk score"
        )
    
    def test_explanation_format_consistency(self):
        """Test that explanations follow a consistent format."""
        test_transactions = [
            self.high_risk_transaction,
            self.moderate_risk_transaction,
            self.low_risk_transaction
        ]
        
        explanations = [_generate_fallback_explanation(t) for t in test_transactions]
        
        # All explanations should start with "Fraud Indicators Detected:"
        for i, explanation in enumerate(explanations):
            with self.subTest(transaction=i):
                self.assertIn('Fraud Indicators Detected:', explanation,
                    "Explanation should follow standard format")
                
                # Should use bullet points for indicators
                self.assertIn('•', explanation,
                    "Explanation should use bullet points for clarity")
    
    def test_explanation_handles_missing_data_gracefully(self):
        """Test that explanations handle missing or incomplete data."""
        incomplete_transaction = {
            'transaction_id': 'TXN_INCOMPLETE_001',
            'product': 'Unknown',
            # Missing many fields
        }
        
        # Should not crash
        explanation = _generate_fallback_explanation(incomplete_transaction)
        
        # Should still provide some explanation
        self.assertIsInstance(explanation, str)
        self.assertGreater(len(explanation), 20)
        self.assertIn('Fraud Indicators Detected:', explanation)
    
    def test_explanation_differentiates_risk_levels(self):
        """Test that explanations appropriately reflect different risk levels."""
        high_risk_explanation = _generate_fallback_explanation(self.high_risk_transaction)
        low_risk_explanation = _generate_fallback_explanation(self.low_risk_transaction)
        
        # High risk should have more indicators mentioned
        high_risk_indicators = high_risk_explanation.count('•')
        low_risk_indicators = low_risk_explanation.count('•')
        
        self.assertGreaterEqual(high_risk_indicators, low_risk_indicators,
            "High-risk transactions should have more indicators mentioned")
    
    def test_explanation_includes_quantitative_data(self):
        """Test that explanations include specific quantitative data when relevant."""
        explanation = _generate_fallback_explanation(self.high_risk_transaction)
        
        # Should include numerical values
        has_numbers = any(char.isdigit() for char in explanation)
        self.assertTrue(has_numbers,
            "Explanation should include quantitative data (numbers)")
        
        # Should include percentages or decimal values for scores
        has_decimal_or_percent = '.' in explanation or '%' in explanation
        self.assertTrue(has_decimal_or_percent,
            "Explanation should include decimal values or percentages")
    
    def test_explanation_avoids_technical_jargon(self):
        """Test that explanations avoid overly technical jargon."""
        explanation = _generate_fallback_explanation(self.high_risk_transaction)
        explanation_lower = explanation.lower()
        
        # Should not contain overly technical ML terms
        technical_jargon = [
            'isolation forest', 'anomaly score', 'feature engineering',
            'model prediction', 'algorithm', 'neural network'
        ]
        
        found_jargon = [term for term in technical_jargon if term in explanation_lower]
        
        self.assertEqual(len(found_jargon), 0,
            f"Explanation should avoid technical jargon. Found: {found_jargon}")
    
    def test_explanation_multiple_indicators_combined(self):
        """Test that explanations properly combine multiple fraud indicators."""
        # Transaction with 4 significant indicators
        multi_indicator_transaction = {
            'transaction_id': 'TXN_MULTI_002',
            'product': 'Pharmaceuticals',
            'price_deviation': 0.5,  # High
            'route_anomaly': 1,  # Present
            'company_risk_score': 0.8,  # High
            'port_activity_index': 1.6,  # High
            'volume_spike_score': 200,  # High
            'shipment_duration_risk': 0.15  # High
        }
        
        explanation = _generate_fallback_explanation(multi_indicator_transaction)
        
        # Should mention multiple indicators
        indicator_count = explanation.count('•')
        self.assertGreaterEqual(indicator_count, 3,
            "Explanation should mention multiple indicators when present")
        
        # Should indicate combination of factors
        combination_keywords = ['combination', 'multiple', 'factors', 'indicators']
        explanation_lower = explanation.lower()
        found_combination = any(kw in explanation_lower for kw in combination_keywords)
        
        self.assertTrue(found_combination,
            "Explanation should indicate multiple factors are present")
    
    def test_explanation_usability_requirements(self):
        """Test that explanations meet NFR-2 usability requirements."""
        explanation = _generate_fallback_explanation(self.high_risk_transaction)
        
        # Clear visual hierarchy (bullet points)
        self.assertIn('•', explanation,
            "Should use bullet points for visual hierarchy")
        
        # Structured format
        self.assertIn('Fraud Indicators Detected:', explanation,
            "Should have clear section headers")
        
        # Not overly verbose
        word_count = len(explanation.split())
        self.assertLessEqual(word_count, 200,
            f"Explanation too verbose ({word_count} words). Should be concise.")
        
        # Contains actionable conclusion
        self.assertIn('investigation', explanation.lower(),
            "Should provide actionable conclusion")


class TestExplanationRelevance(unittest.TestCase):
    """Test suite for validating explanation relevance to transaction context."""
    
    def test_explanation_relevance_to_product_category(self):
        """Test that explanations consider product category context."""
        # High-value luxury goods should have different context than bulk commodities
        luxury_transaction = {
            'transaction_id': 'TXN_LUXURY_001',
            'product': 'Diamond Jewelry',
            'commodity_category': 'Luxury Goods',
            'price_deviation': 0.4,
            'market_price': 100000,
            'unit_price': 140000,
            'company_risk_score': 0.3,
            'route_anomaly': 0,
            'port_activity_index': 1.0
        }
        
        explanation = _generate_fallback_explanation(luxury_transaction)
        
        # Should provide meaningful explanation even for luxury goods
        self.assertGreater(len(explanation), 50)
        self.assertIn('price', explanation.lower())
    
    def test_explanation_relevance_to_risk_category(self):
        """Test that explanations are relevant to the assigned risk category."""
        fraud_transaction = {
            'transaction_id': 'TXN_FRAUD_001',
            'price_deviation': 0.7,
            'route_anomaly': 1,
            'company_risk_score': 0.9,
            'port_activity_index': 2.0,
            'risk_category': 'FRAUD'
        }
        
        suspicious_transaction = {
            'transaction_id': 'TXN_SUSP_001',
            'price_deviation': 0.25,
            'route_anomaly': 0,
            'company_risk_score': 0.4,
            'port_activity_index': 1.1,
            'risk_category': 'SUSPICIOUS'
        }
        
        fraud_explanation = _generate_fallback_explanation(fraud_transaction)
        suspicious_explanation = _generate_fallback_explanation(suspicious_transaction)
        
        # Fraud explanation should have more indicators
        fraud_indicator_count = fraud_explanation.count('•')
        suspicious_indicator_count = suspicious_explanation.count('•')
        
        self.assertGreater(fraud_indicator_count, suspicious_indicator_count,
            "FRAUD category should have more indicators than SUSPICIOUS")
    
    def test_explanation_addresses_all_key_fraud_indicators(self):
        """Test that explanations can address all key fraud indicator types from US-4."""
        # US-4 specifies: product, pricing, route, and risk factors
        
        comprehensive_transaction = {
            'transaction_id': 'TXN_COMP_001',
            'product': 'Electronics',  # Product
            'commodity_category': 'Technology',
            'market_price': 1000,  # Pricing
            'unit_price': 1600,
            'price_deviation': 0.6,
            'shipping_route': 'Suspicious-Route',  # Route
            'route_anomaly': 1,
            'company_risk_score': 0.85,  # Risk factors
            'port_activity_index': 1.8
        }
        
        explanation = _generate_fallback_explanation(comprehensive_transaction)
        explanation_lower = explanation.lower()
        
        # Should address pricing
        self.assertTrue(
            any(kw in explanation_lower for kw in ['price', 'deviation', 'market']),
            "Should address pricing factors"
        )
        
        # Should address route
        self.assertTrue(
            any(kw in explanation_lower for kw in ['route', 'shipping']),
            "Should address route factors"
        )
        
        # Should address risk factors
        self.assertTrue(
            any(kw in explanation_lower for kw in ['risk', 'company', 'port']),
            "Should address risk factors"
        )


def run_quality_tests():
    """Run all explanation quality and relevance tests."""
    print("=" * 70)
    print("TRINETRA AI - Explanation Quality and Relevance Validation")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestExplanationQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestExplanationRelevance))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"\n- {test}:")
            print(f"  {traceback.split('AssertionError: ')[-1].split(chr(10))[0]}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"\n- {test}:")
            error_lines = traceback.split('\n')
            print(f"  {error_lines[-2] if len(error_lines) > 1 else error_lines[0]}")
    
    # Overall result
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED - Explanation quality validated!")
        print("\nKey Validation Results:")
        print("  ✓ Explanations are appropriate length (50-1000 chars)")
        print("  ✓ Key fraud indicators are addressed (price, route, company, port)")
        print("  ✓ Explanations are clear and actionable for investigators")
        print("  ✓ Format is consistent and follows usability requirements")
        print("  ✓ Explanations are relevant to transaction context")
    else:
        print("❌ SOME TESTS FAILED - Review explanation quality issues")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_quality_tests()
    sys.exit(0 if success else 1)
