"""
Comprehensive Unit Tests for TRINETRA AI Alerts Module

This module contains unit tests for the alert system functions in alerts.py.
Tests cover alert checking, prioritization, alert objects, and alert store functionality.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime
from typing import List, Dict

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alerts import (
    check_alerts,
    create_alert_objects,
    create_alert_summary,
    calculate_alert_severity_score,
    prioritize_alert,
    get_prioritized_alerts,
    get_alerts_by_priority,
    Alert,
    AlertSummary,
    AlertPriority,
    AlertSeverity,
    AlertStore,
    ALERT_SEVERITY_MAP
)


class TestCheckAlerts:
    """Test cases for the check_alerts() function."""
    
    def test_check_alerts_no_alerts(self):
        """Test transaction with no alert conditions."""
        transaction = {
            'price_deviation': 0.1,      # Below 0.5 threshold
            'route_anomaly': 0,          # No anomaly
            'company_risk_score': 0.3,   # Below 0.8 threshold
            'port_activity_index': 1.0   # Below 1.5 threshold
        }
        
        alerts = check_alerts(transaction)
        
        assert alerts == []
    
    def test_check_alerts_price_anomaly(self):
        """Test price anomaly alert trigger."""
        transaction = {
            'price_deviation': 0.6,      # Above 0.5 threshold
            'route_anomaly': 0,
            'company_risk_score': 0.3,
            'port_activity_index': 1.0
        }
        
        alerts = check_alerts(transaction)
        
        assert alerts == ["PRICE_ANOMALY"]
    
    def test_check_alerts_route_anomaly(self):
        """Test route anomaly alert trigger."""
        transaction = {
            'price_deviation': 0.1,
            'route_anomaly': 1,          # Anomaly detected
            'company_risk_score': 0.3,
            'port_activity_index': 1.0
        }
        
        alerts = check_alerts(transaction)
        
        assert alerts == ["ROUTE_ANOMALY"]
    
    def test_check_alerts_high_risk_company(self):
        """Test high risk company alert trigger."""
        transaction = {
            'price_deviation': 0.1,
            'route_anomaly': 0,
            'company_risk_score': 0.9,   # Above 0.8 threshold
            'port_activity_index': 1.0
        }
        
        alerts = check_alerts(transaction)
        
        assert alerts == ["HIGH_RISK_COMPANY"]
    
    def test_check_alerts_port_congestion(self):
        """Test port congestion alert trigger."""
        transaction = {
            'price_deviation': 0.1,
            'route_anomaly': 0,
            'company_risk_score': 0.3,
            'port_activity_index': 1.8   # Above 1.5 threshold
        }
        
        alerts = check_alerts(transaction)
        
        assert alerts == ["PORT_CONGESTION"]
    
    def test_check_alerts_multiple_alerts(self):
        """Test transaction triggering multiple alerts."""
        transaction = {
            'price_deviation': 0.7,      # PRICE_ANOMALY
            'route_anomaly': 1,          # ROUTE_ANOMALY
            'company_risk_score': 0.9,   # HIGH_RISK_COMPANY
            'port_activity_index': 2.0   # PORT_CONGESTION
        }
        
        alerts = check_alerts(transaction)
        
        expected_alerts = ["PRICE_ANOMALY", "ROUTE_ANOMALY", "HIGH_RISK_COMPANY", "PORT_CONGESTION"]
        assert set(alerts) == set(expected_alerts)
        assert len(alerts) == 4
    
    def test_check_alerts_boundary_conditions(self):
        """Test alert triggers at exact boundary values."""
        # Test exact threshold values
        transaction_at_threshold = {
            'price_deviation': 0.5,      # Exactly at threshold
            'route_anomaly': 1,          # Exactly at threshold
            'company_risk_score': 0.8,   # Exactly at threshold
            'port_activity_index': 1.5   # Exactly at threshold
        }
        
        alerts = check_alerts(transaction_at_threshold)
        
        # Should NOT trigger alerts at exact threshold (> not >=)
        assert "PRICE_ANOMALY" not in alerts
        assert "HIGH_RISK_COMPANY" not in alerts
        assert "PORT_CONGESTION" not in alerts
        assert "ROUTE_ANOMALY" in alerts  # This uses == 1
    
    def test_check_alerts_missing_keys(self):
        """Test alert checking with missing transaction keys."""
        transaction = {
            'price_deviation': 0.6,
            # Missing other keys
        }
        
        # Should handle missing keys gracefully (KeyError expected)
        with pytest.raises(KeyError):
            check_alerts(transaction)
    
    def test_check_alerts_none_values(self):
        """Test alert checking with None values."""
        transaction = {
            'price_deviation': None,
            'route_anomaly': None,
            'company_risk_score': None,
            'port_activity_index': None
        }
        
        # Should handle None values (comparison will fail)
        with pytest.raises(TypeError):
            check_alerts(transaction)


class TestCreateAlertObjects:
    """Test cases for the create_alert_objects() function."""
    
    def create_test_transaction(self) -> Dict:
        """Create a test transaction dictionary."""
        return {
            'transaction_id': 'TXN001',
            'price_deviation': 0.6,
            'market_price': 100.0,
            'unit_price': 160.0,
            'shipping_route': 'A-B',
            'route_anomaly': 1,
            'company_risk_score': 0.9,
            'exporter_name': 'Company A',
            'importer_name': 'Company B',
            'port_activity_index': 1.8,
            'export_port': 'Port A',
            'import_port': 'Port B'
        }
    
    def test_create_alert_objects_single_alert(self):
        """Test creating alert objects for single alert type."""
        transaction = self.create_test_transaction()
        alert_types = ["PRICE_ANOMALY"]
        
        alerts = create_alert_objects(transaction, alert_types)
        
        assert len(alerts) == 1
        alert = alerts[0]
        assert isinstance(alert, Alert)
        assert alert.transaction_id == 'TXN001'
        assert alert.alert_type == 'PRICE_ANOMALY'
        assert alert.severity == AlertSeverity.HIGH
        assert 'Price deviation' in alert.message
        assert alert.metadata['price_deviation'] == 0.6
    
    def test_create_alert_objects_multiple_alerts(self):
        """Test creating alert objects for multiple alert types."""
        transaction = self.create_test_transaction()
        alert_types = ["PRICE_ANOMALY", "ROUTE_ANOMALY", "HIGH_RISK_COMPANY"]
        
        alerts = create_alert_objects(transaction, alert_types)
        
        assert len(alerts) == 3
        alert_types_created = [alert.alert_type for alert in alerts]
        assert set(alert_types_created) == set(alert_types)
        
        # Check that all alerts have proper structure
        for alert in alerts:
            assert isinstance(alert, Alert)
            assert alert.transaction_id == 'TXN001'
            assert alert.alert_type in alert_types
            assert isinstance(alert.severity, AlertSeverity)
            assert alert.message is not None
            assert isinstance(alert.metadata, dict)
    
    def test_create_alert_objects_empty_alert_types(self):
        """Test creating alert objects with empty alert types list."""
        transaction = self.create_test_transaction()
        alert_types = []
        
        alerts = create_alert_objects(transaction, alert_types)
        
        assert alerts == []
    
    def test_create_alert_objects_unknown_alert_type(self):
        """Test creating alert objects with unknown alert type."""
        transaction = self.create_test_transaction()
        alert_types = ["UNKNOWN_ALERT_TYPE"]
        
        alerts = create_alert_objects(transaction, alert_types)
        
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.alert_type == "UNKNOWN_ALERT_TYPE"
        assert alert.severity == AlertSeverity.LOW  # Default severity
        assert "UNKNOWN_ALERT_TYPE" in alert.message
    
    def test_create_alert_objects_missing_transaction_id(self):
        """Test creating alert objects with missing transaction ID."""
        transaction = {
            'price_deviation': 0.6,
            # Missing transaction_id
        }
        alert_types = ["PRICE_ANOMALY"]
        
        alerts = create_alert_objects(transaction, alert_types)
        
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.transaction_id == 'UNKNOWN'


class TestCalculateAlertSeverityScore:
    """Test cases for the calculate_alert_severity_score() function."""
    
    def test_calculate_alert_severity_score_single_alert(self):
        """Test severity score calculation for single alert."""
        alerts = ["PRICE_ANOMALY"]  # HIGH severity = 3
        
        score = calculate_alert_severity_score(alerts)
        
        assert score == 3
    
    def test_calculate_alert_severity_score_multiple_alerts(self):
        """Test severity score calculation for multiple alerts."""
        alerts = ["PRICE_ANOMALY", "ROUTE_ANOMALY", "PORT_CONGESTION"]
        # HIGH (3) + MEDIUM (2) + MEDIUM (2) = 7
        
        score = calculate_alert_severity_score(alerts)
        
        assert score == 7
    
    def test_calculate_alert_severity_score_empty_list(self):
        """Test severity score calculation for empty alert list."""
        alerts = []
        
        score = calculate_alert_severity_score(alerts)
        
        assert score == 0
    
    def test_calculate_alert_severity_score_unknown_alert(self):
        """Test severity score calculation with unknown alert type."""
        alerts = ["UNKNOWN_ALERT"]
        
        score = calculate_alert_severity_score(alerts)
        
        assert score == 1  # Default to LOW severity


class TestPrioritizeAlert:
    """Test cases for the prioritize_alert() function."""
    
    def test_prioritize_alert_fraud_multiple_alerts(self):
        """Test prioritization for FRAUD category with multiple alerts."""
        transaction = {'risk_category': 'FRAUD'}
        alerts = ["PRICE_ANOMALY", "HIGH_RISK_COMPANY"]
        
        priority, metadata = prioritize_alert(transaction, alerts)
        
        assert priority == AlertPriority.CRITICAL
        assert metadata['alert_count'] == 2
        assert metadata['risk_category'] == 'FRAUD'
        assert "FRAUD category with 2 alerts" in metadata['priority_reason']
    
    def test_prioritize_alert_fraud_single_alert(self):
        """Test prioritization for FRAUD category with single alert."""
        transaction = {'risk_category': 'FRAUD'}
        alerts = ["PRICE_ANOMALY"]
        
        priority, metadata = prioritize_alert(transaction, alerts)
        
        assert priority == AlertPriority.HIGH
        assert metadata['alert_count'] == 1
        assert "FRAUD category with 1 alert" in metadata['priority_reason']
    
    def test_prioritize_alert_suspicious_multiple_alerts(self):
        """Test prioritization for SUSPICIOUS category with multiple alerts."""
        transaction = {'risk_category': 'SUSPICIOUS'}
        alerts = ["PRICE_ANOMALY", "ROUTE_ANOMALY", "PORT_CONGESTION"]
        
        priority, metadata = prioritize_alert(transaction, alerts)
        
        assert priority == AlertPriority.CRITICAL  # 3+ alerts with high severity triggers CRITICAL
        assert metadata['alert_count'] == 3
        assert "3 alerts with high severity score" in metadata['priority_reason']
    
    def test_prioritize_alert_high_severity_score(self):
        """Test prioritization based on high severity score."""
        transaction = {'risk_category': 'SAFE'}
        alerts = ["PRICE_ANOMALY", "HIGH_RISK_COMPANY"]  # 3 + 3 = 6
        
        priority, metadata = prioritize_alert(transaction, alerts)
        
        assert priority == AlertPriority.HIGH
        assert metadata['severity_score'] == 6
        assert "High severity score" in metadata['priority_reason']
    
    def test_prioritize_alert_no_alerts(self):
        """Test prioritization with no alerts."""
        transaction = {'risk_category': 'SAFE'}
        alerts = []
        
        priority, metadata = prioritize_alert(transaction, alerts)
        
        assert priority == AlertPriority.LOW
        assert metadata['alert_count'] == 0
        assert "No alerts triggered" in metadata['priority_reason']
    
    def test_prioritize_alert_suspicious_single_alert(self):
        """Test prioritization for SUSPICIOUS category with single alert."""
        transaction = {'risk_category': 'SUSPICIOUS'}
        alerts = ["ROUTE_ANOMALY"]
        
        priority, metadata = prioritize_alert(transaction, alerts)
        
        assert priority == AlertPriority.MEDIUM
        assert "SUSPICIOUS category with 1 alert" in metadata['priority_reason']


class TestAlert:
    """Test cases for the Alert class."""
    
    def test_alert_creation(self):
        """Test Alert object creation."""
        alert = Alert(
            transaction_id='TXN001',
            alert_type='PRICE_ANOMALY',
            severity=AlertSeverity.HIGH,
            message='Test alert message',
            metadata={'key': 'value'}
        )
        
        assert alert.transaction_id == 'TXN001'
        assert alert.alert_type == 'PRICE_ANOMALY'
        assert alert.severity == AlertSeverity.HIGH
        assert alert.message == 'Test alert message'
        assert alert.metadata == {'key': 'value'}
        assert alert.dismissed is False
        assert alert.dismissed_at is None
        assert alert.dismissed_by is None
        assert isinstance(alert.timestamp, datetime)
    
    def test_alert_to_dict(self):
        """Test Alert to_dict conversion."""
        alert = Alert(
            transaction_id='TXN001',
            alert_type='PRICE_ANOMALY',
            severity=AlertSeverity.HIGH
        )
        
        alert_dict = alert.to_dict()
        
        assert isinstance(alert_dict, dict)
        assert alert_dict['transaction_id'] == 'TXN001'
        assert alert_dict['alert_type'] == 'PRICE_ANOMALY'
        assert alert_dict['severity'] == 'HIGH'
        assert 'timestamp' in alert_dict
        assert isinstance(alert_dict['timestamp'], str)
    
    def test_alert_to_json(self):
        """Test Alert to_json conversion."""
        alert = Alert(
            transaction_id='TXN001',
            alert_type='PRICE_ANOMALY',
            severity=AlertSeverity.HIGH
        )
        
        json_str = alert.to_json()
        
        assert isinstance(json_str, str)
        assert 'TXN001' in json_str
        assert 'PRICE_ANOMALY' in json_str
        assert 'HIGH' in json_str
    
    def test_alert_from_dict(self):
        """Test Alert from_dict creation."""
        alert_data = {
            'transaction_id': 'TXN001',
            'alert_type': 'PRICE_ANOMALY',
            'severity': 'HIGH',
            'timestamp': '2024-01-01T12:00:00',
            'message': 'Test message',
            'metadata': {'key': 'value'},
            'dismissed': False,
            'dismissed_at': None,
            'dismissed_by': None
        }
        
        alert = Alert.from_dict(alert_data)
        
        assert alert.transaction_id == 'TXN001'
        assert alert.alert_type == 'PRICE_ANOMALY'
        assert alert.severity == AlertSeverity.HIGH
        assert isinstance(alert.timestamp, datetime)


class TestAlertSummary:
    """Test cases for the AlertSummary class."""
    
    def create_test_alerts(self) -> List[Alert]:
        """Create test alerts for summary testing."""
        return [
            Alert('TXN001', 'PRICE_ANOMALY', AlertSeverity.HIGH),
            Alert('TXN001', 'ROUTE_ANOMALY', AlertSeverity.MEDIUM)
        ]
    
    def test_alert_summary_creation(self):
        """Test AlertSummary object creation."""
        alerts = self.create_test_alerts()
        
        summary = AlertSummary(
            transaction_id='TXN001',
            alerts=alerts,
            priority=AlertPriority.HIGH,
            risk_category='FRAUD',
            alert_count=2,
            severity_score=5,
            priority_reason='Test reason'
        )
        
        assert summary.transaction_id == 'TXN001'
        assert len(summary.alerts) == 2
        assert summary.priority == AlertPriority.HIGH
        assert summary.risk_category == 'FRAUD'
        assert summary.alert_count == 2
        assert summary.severity_score == 5
        assert summary.dismissed is False
    
    def test_alert_summary_to_dict(self):
        """Test AlertSummary to_dict conversion."""
        alerts = self.create_test_alerts()
        summary = AlertSummary(
            transaction_id='TXN001',
            alerts=alerts,
            priority=AlertPriority.HIGH,
            risk_category='FRAUD',
            alert_count=2,
            severity_score=5,
            priority_reason='Test reason'
        )
        
        summary_dict = summary.to_dict()
        
        assert isinstance(summary_dict, dict)
        assert summary_dict['transaction_id'] == 'TXN001'
        assert summary_dict['priority'] == 'HIGH'
        assert summary_dict['priority_value'] == 3
        assert len(summary_dict['alerts']) == 2
        assert summary_dict['alert_count'] == 2
    
    def test_alert_summary_from_dict(self):
        """Test AlertSummary from_dict creation."""
        summary_data = {
            'transaction_id': 'TXN001',
            'alerts': [
                {
                    'transaction_id': 'TXN001',
                    'alert_type': 'PRICE_ANOMALY',
                    'severity': 'HIGH',
                    'timestamp': '2024-01-01T12:00:00'
                }
            ],
            'priority': 'HIGH',
            'risk_category': 'FRAUD',
            'alert_count': 1,
            'severity_score': 3,
            'priority_reason': 'Test reason',
            'timestamp': '2024-01-01T12:00:00'
        }
        
        summary = AlertSummary.from_dict(summary_data)
        
        assert summary.transaction_id == 'TXN001'
        assert summary.priority == AlertPriority.HIGH
        assert len(summary.alerts) == 1
        assert isinstance(summary.alerts[0], Alert)


class TestCreateAlertSummary:
    """Test cases for the create_alert_summary() function."""
    
    def test_create_alert_summary_with_alerts(self):
        """Test creating alert summary for transaction with alerts."""
        transaction = {
            'transaction_id': 'TXN001',
            'risk_category': 'FRAUD',
            'price_deviation': 0.6,
            'route_anomaly': 1,
            'company_risk_score': 0.9,
            'port_activity_index': 1.2
        }
        
        summary = create_alert_summary(transaction)
        
        assert summary is not None
        assert isinstance(summary, AlertSummary)
        assert summary.transaction_id == 'TXN001'
        assert summary.risk_category == 'FRAUD'
        assert summary.alert_count > 0
        assert len(summary.alerts) > 0
        assert summary.priority in [AlertPriority.CRITICAL, AlertPriority.HIGH, AlertPriority.MEDIUM, AlertPriority.LOW]
    
    def test_create_alert_summary_no_alerts(self):
        """Test creating alert summary for transaction with no alerts."""
        transaction = {
            'transaction_id': 'TXN001',
            'risk_category': 'SAFE',
            'price_deviation': 0.1,
            'route_anomaly': 0,
            'company_risk_score': 0.3,
            'port_activity_index': 1.0
        }
        
        summary = create_alert_summary(transaction)
        
        assert summary is None


class TestAlertStore:
    """Test cases for the AlertStore class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.store = AlertStore()
        self.test_alert = Alert('TXN001', 'PRICE_ANOMALY', AlertSeverity.HIGH)
        self.test_summary = AlertSummary(
            transaction_id='TXN001',
            alerts=[self.test_alert],
            priority=AlertPriority.HIGH,
            risk_category='FRAUD',
            alert_count=1,
            severity_score=3,
            priority_reason='Test'
        )
    
    def test_store_alert(self):
        """Test storing a single alert."""
        self.store.store_alert(self.test_alert)
        
        alerts = self.store.get_alerts_by_transaction('TXN001')
        assert len(alerts) == 1
        assert alerts[0].transaction_id == 'TXN001'
        assert alerts[0].alert_type == 'PRICE_ANOMALY'
    
    def test_store_multiple_alerts(self):
        """Test storing multiple alerts."""
        alert2 = Alert('TXN001', 'ROUTE_ANOMALY', AlertSeverity.MEDIUM)
        alerts = [self.test_alert, alert2]
        
        self.store.store_alerts(alerts)
        
        stored_alerts = self.store.get_alerts_by_transaction('TXN001')
        assert len(stored_alerts) == 2
    
    def test_store_summary(self):
        """Test storing alert summary."""
        self.store.store_summary(self.test_summary)
        
        summary = self.store.get_summary_by_transaction('TXN001')
        assert summary is not None
        assert summary.transaction_id == 'TXN001'
        assert summary.priority == AlertPriority.HIGH
    
    def test_get_alerts_by_transaction_not_found(self):
        """Test getting alerts for non-existent transaction."""
        alerts = self.store.get_alerts_by_transaction('NONEXISTENT')
        assert alerts == []
    
    def test_get_summary_by_transaction_not_found(self):
        """Test getting summary for non-existent transaction."""
        summary = self.store.get_summary_by_transaction('NONEXISTENT')
        assert summary is None
    
    def test_get_alerts_by_priority(self):
        """Test getting alerts by priority level."""
        self.store.store_summary(self.test_summary)
        
        high_priority_alerts = self.store.get_alerts_by_priority(AlertPriority.HIGH)
        assert len(high_priority_alerts) == 1
        assert high_priority_alerts[0].priority == AlertPriority.HIGH
        
        critical_alerts = self.store.get_alerts_by_priority(AlertPriority.CRITICAL)
        assert len(critical_alerts) == 0
    
    def test_get_alerts_by_min_priority(self):
        """Test getting alerts by minimum priority level."""
        # Store summaries with different priorities
        summary_medium = AlertSummary(
            'TXN002', [], AlertPriority.MEDIUM, 'SUSPICIOUS', 1, 2, 'Test'
        )
        summary_critical = AlertSummary(
            'TXN003', [], AlertPriority.CRITICAL, 'FRAUD', 2, 6, 'Test'
        )
        
        self.store.store_summary(self.test_summary)  # HIGH
        self.store.store_summary(summary_medium)     # MEDIUM
        self.store.store_summary(summary_critical)   # CRITICAL
        
        # Get alerts with minimum HIGH priority
        high_and_above = self.store.get_alerts_by_min_priority(AlertPriority.HIGH)
        assert len(high_and_above) == 2  # HIGH and CRITICAL
        
        # Should be sorted by priority (highest first)
        assert high_and_above[0].priority == AlertPriority.CRITICAL
        assert high_and_above[1].priority == AlertPriority.HIGH
    
    def test_get_all_alerts(self):
        """Test getting all stored alerts."""
        alert2 = Alert('TXN002', 'ROUTE_ANOMALY', AlertSeverity.MEDIUM)
        self.store.store_alerts([self.test_alert, alert2])
        
        all_alerts = self.store.get_all_alerts()
        assert len(all_alerts) == 2
    
    def test_get_all_summaries(self):
        """Test getting all stored summaries."""
        summary2 = AlertSummary(
            'TXN002', [], AlertPriority.MEDIUM, 'SUSPICIOUS', 1, 2, 'Test'
        )
        
        self.store.store_summary(self.test_summary)
        self.store.store_summary(summary2)
        
        all_summaries = self.store.get_all_summaries()
        assert len(all_summaries) == 2


class TestGetPrioritizedAlerts:
    """Test cases for the get_prioritized_alerts() function."""
    
    def create_test_transactions(self) -> List[Dict]:
        """Create test transactions with different risk levels."""
        return [
            {
                'transaction_id': 'TXN001',
                'risk_category': 'FRAUD',
                'price_deviation': 0.7,
                'route_anomaly': 1,
                'company_risk_score': 0.9,
                'port_activity_index': 2.0
            },
            {
                'transaction_id': 'TXN002',
                'risk_category': 'SUSPICIOUS',
                'price_deviation': 0.3,
                'route_anomaly': 0,
                'company_risk_score': 0.6,
                'port_activity_index': 1.2
            },
            {
                'transaction_id': 'TXN003',
                'risk_category': 'SAFE',
                'price_deviation': 0.1,
                'route_anomaly': 0,
                'company_risk_score': 0.2,
                'port_activity_index': 1.0
            }
        ]
    
    def test_get_prioritized_alerts_success(self):
        """Test getting prioritized alerts from transactions."""
        transactions = self.create_test_transactions()
        
        prioritized = get_prioritized_alerts(transactions)
        
        # Should only include transactions with alerts (TXN001 and possibly TXN002)
        assert len(prioritized) >= 1
        
        # Should be sorted by priority (highest first)
        if len(prioritized) > 1:
            for i in range(len(prioritized) - 1):
                assert prioritized[i]['priority_value'] >= prioritized[i + 1]['priority_value']
        
        # Check structure
        for item in prioritized:
            assert 'transaction' in item
            assert 'alerts' in item
            assert 'priority' in item
            assert 'priority_level' in item
            assert 'metadata' in item
    
    def test_get_prioritized_alerts_no_alerts(self):
        """Test getting prioritized alerts when no transactions have alerts."""
        transactions = [
            {
                'transaction_id': 'TXN001',
                'risk_category': 'SAFE',
                'price_deviation': 0.1,
                'route_anomaly': 0,
                'company_risk_score': 0.2,
                'port_activity_index': 1.0
            }
        ]
        
        prioritized = get_prioritized_alerts(transactions)
        
        assert prioritized == []


class TestGetAlertsByPriority:
    """Test cases for the get_alerts_by_priority() function."""
    
    def test_get_alerts_by_priority_filtering(self):
        """Test filtering alerts by minimum priority."""
        transactions = [
            {
                'transaction_id': 'TXN001',
                'risk_category': 'FRAUD',
                'price_deviation': 0.7,
                'route_anomaly': 1,
                'company_risk_score': 0.9,
                'port_activity_index': 2.0
            },
            {
                'transaction_id': 'TXN002',
                'risk_category': 'SUSPICIOUS',
                'price_deviation': 0.6,
                'route_anomaly': 0,
                'company_risk_score': 0.5,
                'port_activity_index': 1.0
            }
        ]
        
        # Get only CRITICAL alerts
        critical_alerts = get_alerts_by_priority(transactions, AlertPriority.CRITICAL)
        
        # Should only include transactions with CRITICAL priority
        for alert_info in critical_alerts:
            assert alert_info['priority'] == AlertPriority.CRITICAL


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])