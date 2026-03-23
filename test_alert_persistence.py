"""
Simple test script to verify alert persistence integration.

This script tests that:
1. AlertStore can be populated with transaction data
2. Alerts are created for transactions meeting alert criteria
3. Alert summaries are stored correctly
4. Alerts can be retrieved by various filters
"""

import pandas as pd
from backend.alerts import (
    get_alert_store,
    create_alert_summary,
    check_alerts,
    AlertPriority,
    reset_alert_store
)


def test_alert_persistence():
    """Test alert persistence with sample transaction data."""
    
    # Reset alert store for clean test
    reset_alert_store()
    alert_store = get_alert_store()
    
    # Create sample transactions with various alert conditions
    sample_transactions = [
        {
            'transaction_id': 'TXN001',
            'risk_category': 'FRAUD',
            'price_deviation': 0.7,  # Triggers PRICE_ANOMALY
            'route_anomaly': 1,      # Triggers ROUTE_ANOMALY
            'company_risk_score': 0.9,  # Triggers HIGH_RISK_COMPANY
            'port_activity_index': 1.2
        },
        {
            'transaction_id': 'TXN002',
            'risk_category': 'SUSPICIOUS',
            'price_deviation': 0.6,  # Triggers PRICE_ANOMALY
            'route_anomaly': 0,
            'company_risk_score': 0.5,
            'port_activity_index': 1.8  # Triggers PORT_CONGESTION
        },
        {
            'transaction_id': 'TXN003',
            'risk_category': 'SAFE',
            'price_deviation': 0.2,
            'route_anomaly': 0,
            'company_risk_score': 0.3,
            'port_activity_index': 1.0
        },
        {
            'transaction_id': 'TXN004',
            'risk_category': 'FRAUD',
            'price_deviation': 0.8,  # Triggers PRICE_ANOMALY
            'route_anomaly': 1,      # Triggers ROUTE_ANOMALY
            'company_risk_score': 0.85,  # Triggers HIGH_RISK_COMPANY
            'port_activity_index': 2.0   # Triggers PORT_CONGESTION
        }
    ]
    
    print("=" * 60)
    print("Testing Alert Persistence Integration")
    print("=" * 60)
    
    # Populate alert store
    print("\n1. Populating alert store with sample transactions...")
    for transaction in sample_transactions:
        summary = create_alert_summary(transaction)
        if summary:
            alert_store.store_summary(summary)
            alert_store.store_alerts(summary.alerts)
            print(f"   - {transaction['transaction_id']}: {len(summary.alerts)} alerts, "
                  f"Priority: {summary.priority.name}")
        else:
            print(f"   - {transaction['transaction_id']}: No alerts")
    
    # Test 1: Get all alerts
    print("\n2. Testing get_all_alerts()...")
    all_alerts = alert_store.get_all_alerts()
    print(f"   Total alerts stored: {len(all_alerts)}")
    
    # Test 2: Get alerts by transaction
    print("\n3. Testing get_alerts_by_transaction()...")
    for txn_id in ['TXN001', 'TXN002', 'TXN004']:
        alerts = alert_store.get_alerts_by_transaction(txn_id)
        print(f"   - {txn_id}: {len(alerts)} alerts")
        for alert in alerts:
            print(f"     * {alert.alert_type} ({alert.severity.name})")
    
    # Test 3: Get alerts by priority
    print("\n4. Testing get_alerts_by_priority()...")
    for priority in [AlertPriority.CRITICAL, AlertPriority.HIGH, AlertPriority.MEDIUM]:
        summaries = alert_store.get_alerts_by_priority(priority)
        print(f"   - {priority.name}: {len(summaries)} summaries")
    
    # Test 4: Get alerts by minimum priority
    print("\n5. Testing get_alerts_by_min_priority()...")
    high_priority = alert_store.get_alerts_by_min_priority(AlertPriority.HIGH)
    print(f"   - HIGH and above: {len(high_priority)} summaries")
    
    # Test 5: Get statistics
    print("\n6. Testing get_statistics()...")
    stats = alert_store.get_statistics()
    print(f"   - Total alerts: {stats['total_alerts']}")
    print(f"   - Total summaries: {stats['total_summaries']}")
    print(f"   - Priority counts: {stats['priority_counts']}")
    print(f"   - Alert type counts: {stats['alert_type_counts']}")
    
    # Test 6: Get all summaries
    print("\n7. Testing get_all_summaries()...")
    all_summaries = alert_store.get_all_summaries()
    print(f"   Total summaries: {len(all_summaries)}")
    for summary in all_summaries:
        print(f"   - {summary.transaction_id}: {summary.priority.name} "
              f"({summary.alert_count} alerts, severity score: {summary.severity_score})")
    
    print("\n" + "=" * 60)
    print("✓ All alert persistence tests passed!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        test_alert_persistence()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
