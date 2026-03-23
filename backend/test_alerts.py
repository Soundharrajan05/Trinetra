"""
Unit tests for the alert prioritization system.
"""

import sys
sys.path.insert(0, '.')

from backend.alerts import (
    check_alerts,
    calculate_alert_severity_score,
    prioritize_alert,
    get_prioritized_alerts,
    get_alerts_by_priority,
    AlertPriority,
    AlertSeverity,
    ALERT_SEVERITY_MAP
)


def test_check_alerts():
    """Test basic alert checking functionality."""
    print("Testing check_alerts()...")
    
    # Test transaction with multiple alerts
    transaction = {
        'price_deviation': 0.6,
        'route_anomaly': 1,
        'company_risk_score': 0.85,
        'port_activity_index': 1.2
    }
    alerts = check_alerts(transaction)
    assert 'PRICE_ANOMALY' in alerts
    assert 'ROUTE_ANOMALY' in alerts
    assert 'HIGH_RISK_COMPANY' in alerts
    assert 'PORT_CONGESTION' not in alerts
    print(f"  ✓ Multiple alerts detected: {alerts}")
    
    # Test transaction with no alerts
    transaction_safe = {
        'price_deviation': 0.1,
        'route_anomaly': 0,
        'company_risk_score': 0.3,
        'port_activity_index': 1.0
    }
    alerts_safe = check_alerts(transaction_safe)
    assert len(alerts_safe) == 0
    print(f"  ✓ No alerts for safe transaction: {alerts_safe}")


def test_calculate_alert_severity_score():
    """Test severity score calculation."""
    print("\nTesting calculate_alert_severity_score()...")
    
    # High severity alerts
    alerts_high = ['PRICE_ANOMALY', 'HIGH_RISK_COMPANY']
    score_high = calculate_alert_severity_score(alerts_high)
    assert score_high == 6  # 3 + 3
    print(f"  ✓ High severity score: {score_high}")
    
    # Mixed severity alerts
    alerts_mixed = ['PRICE_ANOMALY', 'ROUTE_ANOMALY']
    score_mixed = calculate_alert_severity_score(alerts_mixed)
    assert score_mixed == 5  # 3 + 2
    print(f"  ✓ Mixed severity score: {score_mixed}")
    
    # Empty alerts
    score_empty = calculate_alert_severity_score([])
    assert score_empty == 0
    print(f"  ✓ Empty alerts score: {score_empty}")


def test_prioritize_alert():
    """Test alert prioritization logic."""
    print("\nTesting prioritize_alert()...")
    
    # CRITICAL: FRAUD with multiple alerts
    transaction_critical = {
        'risk_category': 'FRAUD',
        'price_deviation': 0.6,
        'route_anomaly': 1,
        'company_risk_score': 0.85,
        'port_activity_index': 1.2
    }
    alerts_critical = check_alerts(transaction_critical)
    priority, metadata = prioritize_alert(transaction_critical, alerts_critical)
    assert priority == AlertPriority.CRITICAL
    assert metadata['alert_count'] == 3
    print(f"  ✓ CRITICAL priority: {priority.name} - {metadata['priority_reason']}")
    
    # HIGH: FRAUD with single alert
    transaction_high = {
        'risk_category': 'FRAUD',
        'price_deviation': 0.6,
        'route_anomaly': 0,
        'company_risk_score': 0.3,
        'port_activity_index': 1.0
    }
    alerts_high = check_alerts(transaction_high)
    priority, metadata = prioritize_alert(transaction_high, alerts_high)
    assert priority == AlertPriority.HIGH
    print(f"  ✓ HIGH priority: {priority.name} - {metadata['priority_reason']}")
    
    # MEDIUM: SUSPICIOUS with alerts
    transaction_medium = {
        'risk_category': 'SUSPICIOUS',
        'price_deviation': 0.6,
        'route_anomaly': 0,
        'company_risk_score': 0.3,
        'port_activity_index': 1.0
    }
    alerts_medium = check_alerts(transaction_medium)
    priority, metadata = prioritize_alert(transaction_medium, alerts_medium)
    assert priority == AlertPriority.MEDIUM
    print(f"  ✓ MEDIUM priority: {priority.name} - {metadata['priority_reason']}")
    
    # LOW: No alerts
    transaction_low = {
        'risk_category': 'SAFE',
        'price_deviation': 0.1,
        'route_anomaly': 0,
        'company_risk_score': 0.3,
        'port_activity_index': 1.0
    }
    alerts_low = check_alerts(transaction_low)
    priority, metadata = prioritize_alert(transaction_low, alerts_low)
    assert priority == AlertPriority.LOW
    print(f"  ✓ LOW priority: {priority.name} - {metadata['priority_reason']}")


def test_get_prioritized_alerts():
    """Test getting prioritized alerts from multiple transactions."""
    print("\nTesting get_prioritized_alerts()...")
    
    transactions = [
        {
            'transaction_id': 'TXN001',
            'risk_category': 'SUSPICIOUS',
            'price_deviation': 0.3,
            'route_anomaly': 0,
            'company_risk_score': 0.5,
            'port_activity_index': 1.0
        },
        {
            'transaction_id': 'TXN002',
            'risk_category': 'FRAUD',
            'price_deviation': 0.6,
            'route_anomaly': 1,
            'company_risk_score': 0.9,
            'port_activity_index': 1.6
        },
        {
            'transaction_id': 'TXN003',
            'risk_category': 'SAFE',
            'price_deviation': 0.1,
            'route_anomaly': 0,
            'company_risk_score': 0.2,
            'port_activity_index': 0.8
        }
    ]
    
    prioritized = get_prioritized_alerts(transactions)
    
    # Should only include transactions with alerts (TXN001 and TXN002)
    assert len(prioritized) == 1  # Only TXN002 has alerts
    
    # Highest priority should be first
    assert prioritized[0]['transaction']['transaction_id'] == 'TXN002'
    assert prioritized[0]['priority'] == AlertPriority.CRITICAL
    
    print(f"  ✓ Prioritized {len(prioritized)} transactions")
    for item in prioritized:
        print(f"    - {item['transaction']['transaction_id']}: {item['priority_level']} "
              f"({len(item['alerts'])} alerts)")


def test_get_alerts_by_priority():
    """Test filtering alerts by minimum priority."""
    print("\nTesting get_alerts_by_priority()...")
    
    transactions = [
        {
            'transaction_id': 'TXN001',
            'risk_category': 'SUSPICIOUS',
            'price_deviation': 0.6,
            'route_anomaly': 0,
            'company_risk_score': 0.5,
            'port_activity_index': 1.0
        },
        {
            'transaction_id': 'TXN002',
            'risk_category': 'FRAUD',
            'price_deviation': 0.6,
            'route_anomaly': 1,
            'company_risk_score': 0.9,
            'port_activity_index': 1.6
        }
    ]
    
    # Get only CRITICAL alerts
    critical_alerts = get_alerts_by_priority(transactions, AlertPriority.CRITICAL)
    assert len(critical_alerts) == 1
    assert critical_alerts[0]['priority'] == AlertPriority.CRITICAL
    print(f"  ✓ Found {len(critical_alerts)} CRITICAL alerts")
    
    # Get HIGH and above
    high_alerts = get_alerts_by_priority(transactions, AlertPriority.HIGH)
    assert len(high_alerts) >= 1
    print(f"  ✓ Found {len(high_alerts)} HIGH+ alerts")


def run_all_tests():
    """Run all test functions."""
    print("=" * 60)
    print("Running Alert Prioritization Tests")
    print("=" * 60)
    
    try:
        test_check_alerts()
        test_calculate_alert_severity_score()
        test_prioritize_alert()
        test_get_prioritized_alerts()
        test_get_alerts_by_priority()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
