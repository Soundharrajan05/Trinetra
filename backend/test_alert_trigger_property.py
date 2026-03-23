"""
Property-Based Test for Alert Trigger Accuracy (CP-5)
TRINETRA AI - Trade Fraud Intelligence System

**Validates: Requirements CP-5**

This module implements property-based testing for alert trigger accuracy validation.
Tests ensure that alerts are triggered if and only if threshold conditions are met.

Property: Alerts must be triggered if and only if threshold conditions are met
Test Strategy: Property-based test with transactions at boundary conditions verifying alert logic

Alert Trigger Conditions:
- price_deviation > 0.5 → PRICE_ANOMALY alert
- route_anomaly == 1 → ROUTE_ANOMALY alert
- company_risk_score > 0.8 → HIGH_RISK_COMPANY alert
- port_activity_index > 1.5 → PORT_CONGESTION alert
"""

import pytest
import sys
import os
from typing import List, Dict, Any
from hypothesis import given, strategies as st, settings, assume, example
from decimal import Decimal

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alerts import check_alerts


class TestAlertTriggerAccuracyProperty:
    """Property-based tests for alert trigger accuracy validation (CP-5)."""
    
    @given(
        price_deviation=st.floats(min_value=-1.0, max_value=2.0, allow_nan=False, allow_infinity=False),
        route_anomaly=st.integers(min_value=0, max_value=1),
        company_risk_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        port_activity_index=st.floats(min_value=0.0, max_value=3.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=5000)
    @example(price_deviation=0.5, route_anomaly=1, company_risk_score=0.8, port_activity_index=1.5)
    @example(price_deviation=0.50001, route_anomaly=1, company_risk_score=0.80001, port_activity_index=1.50001)
    @example(price_deviation=0.49999, route_anomaly=0, company_risk_score=0.79999, port_activity_index=1.49999)
    def test_alert_trigger_boundary_conditions(
        self,
        price_deviation: float,
        route_anomaly: int,
        company_risk_score: float,
        port_activity_index: float
    ):
        """
        **Validates: Requirements CP-5**
        
        Property: Alerts must be triggered if and only if threshold conditions are met
        
        Test Strategy: Generate transactions with values at boundary conditions
        and verify alerts are triggered correctly
        """
        # Create transaction with generated values
        transaction = {
            'price_deviation': price_deviation,
            'route_anomaly': route_anomaly,
            'company_risk_score': company_risk_score,
            'port_activity_index': port_activity_index
        }
        
        # Get triggered alerts
        alerts = check_alerts(transaction)
        
        # Verify PRICE_ANOMALY alert
        if price_deviation > 0.5:
            assert "PRICE_ANOMALY" in alerts, \
                f"PRICE_ANOMALY should be triggered when price_deviation={price_deviation} > 0.5"
        else:
            assert "PRICE_ANOMALY" not in alerts, \
                f"PRICE_ANOMALY should NOT be triggered when price_deviation={price_deviation} <= 0.5"
        
        # Verify ROUTE_ANOMALY alert
        if route_anomaly == 1:
            assert "ROUTE_ANOMALY" in alerts, \
                f"ROUTE_ANOMALY should be triggered when route_anomaly={route_anomaly} == 1"
        else:
            assert "ROUTE_ANOMALY" not in alerts, \
                f"ROUTE_ANOMALY should NOT be triggered when route_anomaly={route_anomaly} != 1"
        
        # Verify HIGH_RISK_COMPANY alert
        if company_risk_score > 0.8:
            assert "HIGH_RISK_COMPANY" in alerts, \
                f"HIGH_RISK_COMPANY should be triggered when company_risk_score={company_risk_score} > 0.8"
        else:
            assert "HIGH_RISK_COMPANY" not in alerts, \
                f"HIGH_RISK_COMPANY should NOT be triggered when company_risk_score={company_risk_score} <= 0.8"
        
        # Verify PORT_CONGESTION alert
        if port_activity_index > 1.5:
            assert "PORT_CONGESTION" in alerts, \
                f"PORT_CONGESTION should be triggered when port_activity_index={port_activity_index} > 1.5"
        else:
            assert "PORT_CONGESTION" not in alerts, \
                f"PORT_CONGESTION should NOT be triggered when port_activity_index={port_activity_index} <= 1.5"
    
    @given(
        num_alerts=st.integers(min_value=0, max_value=4)
    )
    @settings(max_examples=20, deadline=5000)
    @example(num_alerts=0)
    @example(num_alerts=1)
    @example(num_alerts=4)
    def test_alert_combinations(self, num_alerts: int):
        """
        **Validates: Requirements CP-5**
        
        Property: Multiple alerts can be triggered simultaneously
        
        Test Strategy: Generate transactions that should trigger specific numbers of alerts
        """
        # Create transaction that triggers exactly num_alerts alerts
        transaction = {
            'price_deviation': 0.6 if num_alerts >= 1 else 0.3,
            'route_anomaly': 1 if num_alerts >= 2 else 0,
            'company_risk_score': 0.9 if num_alerts >= 3 else 0.5,
            'port_activity_index': 2.0 if num_alerts >= 4 else 1.0
        }
        
        alerts = check_alerts(transaction)
        
        # Verify the correct number of alerts are triggered
        assert len(alerts) == num_alerts, \
            f"Expected {num_alerts} alerts but got {len(alerts)}: {alerts}"
        
        # Verify specific alerts based on num_alerts
        if num_alerts >= 1:
            assert "PRICE_ANOMALY" in alerts
        if num_alerts >= 2:
            assert "ROUTE_ANOMALY" in alerts
        if num_alerts >= 3:
            assert "HIGH_RISK_COMPANY" in alerts
        if num_alerts >= 4:
            assert "PORT_CONGESTION" in alerts
    
    @given(
        price_deviation=st.floats(min_value=0.0, max_value=0.5, allow_nan=False, allow_infinity=False),
        company_risk_score=st.floats(min_value=0.0, max_value=0.8, allow_nan=False, allow_infinity=False),
        port_activity_index=st.floats(min_value=0.0, max_value=1.5, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50, deadline=5000)
    def test_no_false_positives(
        self,
        price_deviation: float,
        company_risk_score: float,
        port_activity_index: float
    ):
        """
        **Validates: Requirements CP-5**
        
        Property: No alerts should be triggered when all conditions are below thresholds
        
        Test Strategy: Generate transactions with all values below thresholds
        and verify no alerts are triggered (no false positives)
        """
        transaction = {
            'price_deviation': price_deviation,
            'route_anomaly': 0,
            'company_risk_score': company_risk_score,
            'port_activity_index': port_activity_index
        }
        
        alerts = check_alerts(transaction)
        
        # No alerts should be triggered
        assert len(alerts) == 0, \
            f"No alerts should be triggered for safe transaction, but got: {alerts}"
        assert "PRICE_ANOMALY" not in alerts
        assert "ROUTE_ANOMALY" not in alerts
        assert "HIGH_RISK_COMPANY" not in alerts
        assert "PORT_CONGESTION" not in alerts
    
    @given(
        price_deviation=st.floats(min_value=0.50001, max_value=2.0, allow_nan=False, allow_infinity=False),
        company_risk_score=st.floats(min_value=0.80001, max_value=1.0, allow_nan=False, allow_infinity=False),
        port_activity_index=st.floats(min_value=1.50001, max_value=3.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50, deadline=5000)
    def test_no_false_negatives(
        self,
        price_deviation: float,
        company_risk_score: float,
        port_activity_index: float
    ):
        """
        **Validates: Requirements CP-5**
        
        Property: All alerts should be triggered when all conditions exceed thresholds
        
        Test Strategy: Generate transactions with all values above thresholds
        and verify all alerts are triggered (no false negatives)
        """
        transaction = {
            'price_deviation': price_deviation,
            'route_anomaly': 1,
            'company_risk_score': company_risk_score,
            'port_activity_index': port_activity_index
        }
        
        alerts = check_alerts(transaction)
        
        # All 4 alerts should be triggered
        assert len(alerts) == 4, \
            f"All 4 alerts should be triggered for high-risk transaction, but got {len(alerts)}: {alerts}"
        assert "PRICE_ANOMALY" in alerts, "PRICE_ANOMALY should be triggered"
        assert "ROUTE_ANOMALY" in alerts, "ROUTE_ANOMALY should be triggered"
        assert "HIGH_RISK_COMPANY" in alerts, "HIGH_RISK_COMPANY should be triggered"
        assert "PORT_CONGESTION" in alerts, "PORT_CONGESTION should be triggered"


class TestAlertTriggerExactBoundaries:
    """Edge case tests for exact boundary values."""
    
    def test_exact_threshold_price_deviation(self):
        """Test exact threshold value for price_deviation (0.5)."""
        # Exactly at threshold - should NOT trigger
        transaction = {
            'price_deviation': 0.5,
            'route_anomaly': 0,
            'company_risk_score': 0.5,
            'port_activity_index': 1.0
        }
        alerts = check_alerts(transaction)
        assert "PRICE_ANOMALY" not in alerts, "Alert should NOT trigger at exact threshold 0.5"
        
        # Just above threshold - should trigger
        transaction['price_deviation'] = 0.500001
        alerts = check_alerts(transaction)
        assert "PRICE_ANOMALY" in alerts, "Alert should trigger just above threshold"
        
        # Just below threshold - should NOT trigger
        transaction['price_deviation'] = 0.499999
        alerts = check_alerts(transaction)
        assert "PRICE_ANOMALY" not in alerts, "Alert should NOT trigger just below threshold"
    
    def test_exact_threshold_company_risk_score(self):
        """Test exact threshold value for company_risk_score (0.8)."""
        # Exactly at threshold - should NOT trigger
        transaction = {
            'price_deviation': 0.3,
            'route_anomaly': 0,
            'company_risk_score': 0.8,
            'port_activity_index': 1.0
        }
        alerts = check_alerts(transaction)
        assert "HIGH_RISK_COMPANY" not in alerts, "Alert should NOT trigger at exact threshold 0.8"
        
        # Just above threshold - should trigger
        transaction['company_risk_score'] = 0.800001
        alerts = check_alerts(transaction)
        assert "HIGH_RISK_COMPANY" in alerts, "Alert should trigger just above threshold"
        
        # Just below threshold - should NOT trigger
        transaction['company_risk_score'] = 0.799999
        alerts = check_alerts(transaction)
        assert "HIGH_RISK_COMPANY" not in alerts, "Alert should NOT trigger just below threshold"
    
    def test_exact_threshold_port_activity_index(self):
        """Test exact threshold value for port_activity_index (1.5)."""
        # Exactly at threshold - should NOT trigger
        transaction = {
            'price_deviation': 0.3,
            'route_anomaly': 0,
            'company_risk_score': 0.5,
            'port_activity_index': 1.5
        }
        alerts = check_alerts(transaction)
        assert "PORT_CONGESTION" not in alerts, "Alert should NOT trigger at exact threshold 1.5"
        
        # Just above threshold - should trigger
        transaction['port_activity_index'] = 1.500001
        alerts = check_alerts(transaction)
        assert "PORT_CONGESTION" in alerts, "Alert should trigger just above threshold"
        
        # Just below threshold - should NOT trigger
        transaction['port_activity_index'] = 1.499999
        alerts = check_alerts(transaction)
        assert "PORT_CONGESTION" not in alerts, "Alert should NOT trigger just below threshold"
    
    def test_route_anomaly_binary(self):
        """Test route_anomaly binary behavior."""
        transaction = {
            'price_deviation': 0.3,
            'route_anomaly': 0,
            'company_risk_score': 0.5,
            'port_activity_index': 1.0
        }
        
        # route_anomaly = 0 should NOT trigger
        alerts = check_alerts(transaction)
        assert "ROUTE_ANOMALY" not in alerts, "Alert should NOT trigger when route_anomaly=0"
        
        # route_anomaly = 1 should trigger
        transaction['route_anomaly'] = 1
        alerts = check_alerts(transaction)
        assert "ROUTE_ANOMALY" in alerts, "Alert should trigger when route_anomaly=1"
    
    def test_all_alerts_at_boundaries(self):
        """Test all alerts at exact boundary conditions."""
        # All at exact thresholds - no alerts should trigger
        transaction = {
            'price_deviation': 0.5,
            'route_anomaly': 0,
            'company_risk_score': 0.8,
            'port_activity_index': 1.5
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 0, f"No alerts should trigger at exact thresholds, got: {alerts}"
        
        # All just above thresholds - all alerts should trigger
        transaction = {
            'price_deviation': 0.500001,
            'route_anomaly': 1,
            'company_risk_score': 0.800001,
            'port_activity_index': 1.500001
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 4, f"All 4 alerts should trigger just above thresholds, got {len(alerts)}: {alerts}"
        
        # All just below thresholds - no alerts should trigger
        transaction = {
            'price_deviation': 0.499999,
            'route_anomaly': 0,
            'company_risk_score': 0.799999,
            'port_activity_index': 1.499999
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 0, f"No alerts should trigger just below thresholds, got: {alerts}"
    
    def test_extreme_values(self):
        """Test extreme values for alert conditions."""
        # Extremely high values - all alerts should trigger
        transaction = {
            'price_deviation': 10.0,
            'route_anomaly': 1,
            'company_risk_score': 1.0,
            'port_activity_index': 10.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 4, "All alerts should trigger for extreme high values"
        
        # Extremely low values - no alerts should trigger
        transaction = {
            'price_deviation': 0.0,
            'route_anomaly': 0,
            'company_risk_score': 0.0,
            'port_activity_index': 0.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 0, "No alerts should trigger for extreme low values"
        
        # Negative values (edge case) - no alerts should trigger
        transaction = {
            'price_deviation': -0.5,
            'route_anomaly': 0,
            'company_risk_score': 0.0,
            'port_activity_index': 0.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 0, "No alerts should trigger for negative values"


class TestAlertTriggerCombinations:
    """Test various combinations of alert conditions."""
    
    def test_single_alert_combinations(self):
        """Test each alert triggered individually."""
        # Only PRICE_ANOMALY
        transaction = {
            'price_deviation': 0.6,
            'route_anomaly': 0,
            'company_risk_score': 0.5,
            'port_activity_index': 1.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 1
        assert alerts == ["PRICE_ANOMALY"]
        
        # Only ROUTE_ANOMALY
        transaction = {
            'price_deviation': 0.3,
            'route_anomaly': 1,
            'company_risk_score': 0.5,
            'port_activity_index': 1.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 1
        assert alerts == ["ROUTE_ANOMALY"]
        
        # Only HIGH_RISK_COMPANY
        transaction = {
            'price_deviation': 0.3,
            'route_anomaly': 0,
            'company_risk_score': 0.9,
            'port_activity_index': 1.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 1
        assert alerts == ["HIGH_RISK_COMPANY"]
        
        # Only PORT_CONGESTION
        transaction = {
            'price_deviation': 0.3,
            'route_anomaly': 0,
            'company_risk_score': 0.5,
            'port_activity_index': 2.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 1
        assert alerts == ["PORT_CONGESTION"]
    
    def test_two_alert_combinations(self):
        """Test pairs of alerts triggered together."""
        # PRICE_ANOMALY + ROUTE_ANOMALY
        transaction = {
            'price_deviation': 0.6,
            'route_anomaly': 1,
            'company_risk_score': 0.5,
            'port_activity_index': 1.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 2
        assert "PRICE_ANOMALY" in alerts
        assert "ROUTE_ANOMALY" in alerts
        
        # HIGH_RISK_COMPANY + PORT_CONGESTION
        transaction = {
            'price_deviation': 0.3,
            'route_anomaly': 0,
            'company_risk_score': 0.9,
            'port_activity_index': 2.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 2
        assert "HIGH_RISK_COMPANY" in alerts
        assert "PORT_CONGESTION" in alerts
    
    def test_three_alert_combinations(self):
        """Test three alerts triggered together."""
        # PRICE_ANOMALY + ROUTE_ANOMALY + HIGH_RISK_COMPANY
        transaction = {
            'price_deviation': 0.6,
            'route_anomaly': 1,
            'company_risk_score': 0.9,
            'port_activity_index': 1.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 3
        assert "PRICE_ANOMALY" in alerts
        assert "ROUTE_ANOMALY" in alerts
        assert "HIGH_RISK_COMPANY" in alerts
        
        # ROUTE_ANOMALY + HIGH_RISK_COMPANY + PORT_CONGESTION
        transaction = {
            'price_deviation': 0.3,
            'route_anomaly': 1,
            'company_risk_score': 0.9,
            'port_activity_index': 2.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 3
        assert "ROUTE_ANOMALY" in alerts
        assert "HIGH_RISK_COMPANY" in alerts
        assert "PORT_CONGESTION" in alerts
    
    def test_all_four_alerts(self):
        """Test all four alerts triggered together."""
        transaction = {
            'price_deviation': 0.6,
            'route_anomaly': 1,
            'company_risk_score': 0.9,
            'port_activity_index': 2.0
        }
        alerts = check_alerts(transaction)
        assert len(alerts) == 4
        assert "PRICE_ANOMALY" in alerts
        assert "ROUTE_ANOMALY" in alerts
        assert "HIGH_RISK_COMPANY" in alerts
        assert "PORT_CONGESTION" in alerts


if __name__ == "__main__":
    # Run the property-based tests
    pytest.main([__file__, "-v", "--tb=short"])
