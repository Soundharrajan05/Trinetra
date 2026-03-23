"""
Quick test to verify alert data structures work correctly.
"""

from backend.alerts import (
    Alert, AlertSummary, AlertSeverity, AlertPriority,
    check_alerts, create_alert_objects, create_alert_summary
)
from datetime import datetime
import json


def test_alert_creation():
    """Test creating an Alert object."""
    print("Testing Alert creation...")
    
    alert = Alert(
        transaction_id="TXN001",
        alert_type="PRICE_ANOMALY",
        severity=AlertSeverity.HIGH,
        message="Price deviation exceeds threshold",
        metadata={"price_deviation": 0.6}
    )
    
    print(f"  Alert created: {alert.transaction_id} - {alert.alert_type}")
    print(f"  Severity: {alert.severity.name}")
    assert alert.transaction_id == "TXN001"
    assert alert.alert_type == "PRICE_ANOMALY"
    print("  ✓ Alert creation successful")


def test_alert_serialization():
    """Test Alert JSON serialization."""
    print("\nTesting Alert serialization...")
    
    alert = Alert(
        transaction_id="TXN002",
        alert_type="ROUTE_ANOMALY",
        severity=AlertSeverity.MEDIUM,
        message="Unusual route detected"
    )
    
    # Test to_dict
    alert_dict = alert.to_dict()
    print(f"  Alert dict: {alert_dict}")
    assert isinstance(alert_dict, dict)
    assert alert_dict['severity'] == 'MEDIUM'
    assert isinstance(alert_dict['timestamp'], str)
    
    # Test to_json
    alert_json = alert.to_json()
    print(f"  Alert JSON: {alert_json[:100]}...")
    assert isinstance(alert_json, str)
    
    # Test from_dict
    alert_restored = Alert.from_dict(alert_dict)
    assert alert_restored.transaction_id == alert.transaction_id
    assert alert_restored.severity == alert.severity
    print("  ✓ Alert serialization successful")


def test_create_alert_objects():
    """Test creating Alert objects from transaction."""
    print("\nTesting create_alert_objects...")
    
    transaction = {
        'transaction_id': 'TXN003',
        'price_deviation': 0.6,
        'route_anomaly': 1,
        'company_risk_score': 0.85,
        'port_activity_index': 1.2,
        'market_price': 100,
        'unit_price': 160
    }
    
    alert_types = ['PRICE_ANOMALY', 'ROUTE_ANOMALY', 'HIGH_RISK_COMPANY']
    alerts = create_alert_objects(transaction, alert_types)
    
    print(f"  Created {len(alerts)} alerts")
    assert len(alerts) == 3
    assert all(isinstance(a, Alert) for a in alerts)
    assert alerts[0].alert_type == 'PRICE_ANOMALY'
    assert alerts[0].severity == AlertSeverity.HIGH
    print("  ✓ Alert object creation successful")


def test_alert_summary():
    """Test creating AlertSummary."""
    print("\nTesting AlertSummary creation...")
    
    transaction = {
        'transaction_id': 'TXN004',
        'risk_category': 'FRAUD',
        'price_deviation': 0.7,
        'route_anomaly': 1,
        'company_risk_score': 0.9,
        'port_activity_index': 1.6
    }
    
    summary = create_alert_summary(transaction)
    
    print(f"  Summary created for {summary.transaction_id}")
    print(f"  Priority: {summary.priority.name}")
    print(f"  Alert count: {summary.alert_count}")
    print(f"  Severity score: {summary.severity_score}")
    
    assert summary is not None
    assert summary.transaction_id == 'TXN004'
    assert summary.priority == AlertPriority.CRITICAL
    assert summary.alert_count == 4
    assert len(summary.alerts) == 4
    print("  ✓ AlertSummary creation successful")


def test_alert_summary_serialization():
    """Test AlertSummary JSON serialization."""
    print("\nTesting AlertSummary serialization...")
    
    transaction = {
        'transaction_id': 'TXN005',
        'risk_category': 'SUSPICIOUS',
        'price_deviation': 0.6,
        'route_anomaly': 0,
        'company_risk_score': 0.7,
        'port_activity_index': 1.2
    }
    
    summary = create_alert_summary(transaction)
    
    # Test to_dict
    summary_dict = summary.to_dict()
    print(f"  Summary dict keys: {list(summary_dict.keys())}")
    assert isinstance(summary_dict, dict)
    assert summary_dict['priority'] == 'MEDIUM'
    assert isinstance(summary_dict['alerts'], list)
    
    # Test to_json
    summary_json = summary.to_json()
    print(f"  Summary JSON length: {len(summary_json)} chars")
    assert isinstance(summary_json, str)
    
    # Verify JSON is valid
    parsed = json.loads(summary_json)
    assert parsed['transaction_id'] == 'TXN005'
    
    # Test from_dict
    summary_restored = AlertSummary.from_dict(summary_dict)
    assert summary_restored.transaction_id == summary.transaction_id
    assert summary_restored.priority == summary.priority
    print("  ✓ AlertSummary serialization successful")


def test_no_alerts():
    """Test transaction with no alerts."""
    print("\nTesting transaction with no alerts...")
    
    transaction = {
        'transaction_id': 'TXN006',
        'risk_category': 'SAFE',
        'price_deviation': 0.1,
        'route_anomaly': 0,
        'company_risk_score': 0.3,
        'port_activity_index': 0.8
    }
    
    summary = create_alert_summary(transaction)
    
    print(f"  Summary: {summary}")
    assert summary is None
    print("  ✓ No alerts case handled correctly")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Alert Data Structures")
    print("=" * 60)
    
    test_alert_creation()
    test_alert_serialization()
    test_create_alert_objects()
    test_alert_summary()
    test_alert_summary_serialization()
    test_no_alerts()
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
