"""
Unit tests for the AlertStore in-memory persistence system.
"""

import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta
from backend.alerts import (
    Alert,
    AlertSummary,
    AlertStore,
    AlertPriority,
    AlertSeverity,
    get_alert_store,
    reset_alert_store
)


def test_store_and_retrieve_single_alert():
    """Test storing and retrieving a single alert."""
    print("Testing store_alert() and get_alerts_by_transaction()...")
    
    store = AlertStore()
    
    # Create and store an alert
    alert = Alert(
        transaction_id='TXN001',
        alert_type='PRICE_ANOMALY',
        severity=AlertSeverity.HIGH,
        message='Price deviation exceeds threshold'
    )
    store.store_alert(alert)
    
    # Retrieve the alert
    alerts = store.get_alerts_by_transaction('TXN001')
    assert len(alerts) == 1
    assert alerts[0].transaction_id == 'TXN001'
    assert alerts[0].alert_type == 'PRICE_ANOMALY'
    assert alerts[0].severity == AlertSeverity.HIGH
    
    print(f"  ✓ Stored and retrieved alert for TXN001")


def test_store_multiple_alerts_same_transaction():
    """Test storing multiple alerts for the same transaction."""
    print("\nTesting multiple alerts for same transaction...")
    
    store = AlertStore()
    
    # Create multiple alerts for same transaction
    alert1 = Alert(
        transaction_id='TXN002',
        alert_type='PRICE_ANOMALY',
        severity=AlertSeverity.HIGH
    )
    alert2 = Alert(
        transaction_id='TXN002',
        alert_type='ROUTE_ANOMALY',
        severity=AlertSeverity.MEDIUM
    )
    
    store.store_alert(alert1)
    store.store_alert(alert2)
    
    # Retrieve all alerts for the transaction
    alerts = store.get_alerts_by_transaction('TXN002')
    assert len(alerts) == 2
    assert alerts[0].alert_type == 'PRICE_ANOMALY'
    assert alerts[1].alert_type == 'ROUTE_ANOMALY'
    
    print(f"  ✓ Stored and retrieved {len(alerts)} alerts for TXN002")


def test_store_alerts_batch():
    """Test storing multiple alerts at once."""
    print("\nTesting store_alerts() batch operation...")
    
    store = AlertStore()
    
    alerts = [
        Alert(transaction_id='TXN003', alert_type='PRICE_ANOMALY', severity=AlertSeverity.HIGH),
        Alert(transaction_id='TXN003', alert_type='HIGH_RISK_COMPANY', severity=AlertSeverity.HIGH),
        Alert(transaction_id='TXN004', alert_type='PORT_CONGESTION', severity=AlertSeverity.MEDIUM)
    ]
    
    store.store_alerts(alerts)
    
    # Verify storage
    txn003_alerts = store.get_alerts_by_transaction('TXN003')
    txn004_alerts = store.get_alerts_by_transaction('TXN004')
    
    assert len(txn003_alerts) == 2
    assert len(txn004_alerts) == 1
    
    print(f"  ✓ Batch stored 3 alerts across 2 transactions")


def test_store_and_retrieve_summary():
    """Test storing and retrieving alert summaries."""
    print("\nTesting store_summary() and get_summary_by_transaction()...")
    
    store = AlertStore()
    
    # Create alerts
    alerts = [
        Alert(transaction_id='TXN005', alert_type='PRICE_ANOMALY', severity=AlertSeverity.HIGH),
        Alert(transaction_id='TXN005', alert_type='ROUTE_ANOMALY', severity=AlertSeverity.MEDIUM)
    ]
    
    # Create summary
    summary = AlertSummary(
        transaction_id='TXN005',
        alerts=alerts,
        priority=AlertPriority.CRITICAL,
        risk_category='FRAUD',
        alert_count=2,
        severity_score=5,
        priority_reason='FRAUD category with 2 alerts'
    )
    
    store.store_summary(summary)
    
    # Retrieve summary
    retrieved = store.get_summary_by_transaction('TXN005')
    assert retrieved is not None
    assert retrieved.transaction_id == 'TXN005'
    assert retrieved.priority == AlertPriority.CRITICAL
    assert retrieved.alert_count == 2
    
    print(f"  ✓ Stored and retrieved summary for TXN005")


def test_get_alerts_by_priority():
    """Test filtering alerts by priority level."""
    print("\nTesting get_alerts_by_priority()...")
    
    store = AlertStore()
    
    # Create summaries with different priorities
    summaries = [
        AlertSummary(
            transaction_id='TXN006',
            alerts=[],
            priority=AlertPriority.CRITICAL,
            risk_category='FRAUD',
            alert_count=3,
            severity_score=9,
            priority_reason='Critical'
        ),
        AlertSummary(
            transaction_id='TXN007',
            alerts=[],
            priority=AlertPriority.HIGH,
            risk_category='FRAUD',
            alert_count=1,
            severity_score=3,
            priority_reason='High'
        ),
        AlertSummary(
            transaction_id='TXN008',
            alerts=[],
            priority=AlertPriority.MEDIUM,
            risk_category='SUSPICIOUS',
            alert_count=1,
            severity_score=2,
            priority_reason='Medium'
        )
    ]
    
    for summary in summaries:
        store.store_summary(summary)
    
    # Get CRITICAL alerts
    critical = store.get_alerts_by_priority(AlertPriority.CRITICAL)
    assert len(critical) == 1
    assert critical[0].priority == AlertPriority.CRITICAL
    
    # Get HIGH alerts
    high = store.get_alerts_by_priority(AlertPriority.HIGH)
    assert len(high) == 1
    assert high[0].priority == AlertPriority.HIGH
    
    print(f"  ✓ Filtered alerts by priority: {len(critical)} CRITICAL, {len(high)} HIGH")


def test_get_alerts_by_min_priority():
    """Test filtering alerts by minimum priority level."""
    print("\nTesting get_alerts_by_min_priority()...")
    
    store = AlertStore()
    
    # Create summaries with different priorities
    summaries = [
        AlertSummary(
            transaction_id='TXN009',
            alerts=[],
            priority=AlertPriority.CRITICAL,
            risk_category='FRAUD',
            alert_count=3,
            severity_score=9,
            priority_reason='Critical'
        ),
        AlertSummary(
            transaction_id='TXN010',
            alerts=[],
            priority=AlertPriority.HIGH,
            risk_category='FRAUD',
            alert_count=1,
            severity_score=3,
            priority_reason='High'
        ),
        AlertSummary(
            transaction_id='TXN011',
            alerts=[],
            priority=AlertPriority.MEDIUM,
            risk_category='SUSPICIOUS',
            alert_count=1,
            severity_score=2,
            priority_reason='Medium'
        ),
        AlertSummary(
            transaction_id='TXN012',
            alerts=[],
            priority=AlertPriority.LOW,
            risk_category='SAFE',
            alert_count=0,
            severity_score=0,
            priority_reason='Low'
        )
    ]
    
    for summary in summaries:
        store.store_summary(summary)
    
    # Get HIGH and above
    high_and_above = store.get_alerts_by_min_priority(AlertPriority.HIGH)
    assert len(high_and_above) == 2
    assert high_and_above[0].priority == AlertPriority.CRITICAL  # Sorted by priority
    assert high_and_above[1].priority == AlertPriority.HIGH
    
    # Get MEDIUM and above
    medium_and_above = store.get_alerts_by_min_priority(AlertPriority.MEDIUM)
    assert len(medium_and_above) == 3
    
    print(f"  ✓ Filtered by min priority: {len(high_and_above)} HIGH+, {len(medium_and_above)} MEDIUM+")


def test_get_alerts_by_time_range():
    """Test filtering alerts by time range."""
    print("\nTesting get_alerts_by_time_range()...")
    
    store = AlertStore()
    
    # Create alerts with different timestamps
    now = datetime.now()
    
    alert1 = Alert(
        transaction_id='TXN013',
        alert_type='PRICE_ANOMALY',
        severity=AlertSeverity.HIGH,
        timestamp=now - timedelta(hours=2)
    )
    alert2 = Alert(
        transaction_id='TXN014',
        alert_type='ROUTE_ANOMALY',
        severity=AlertSeverity.MEDIUM,
        timestamp=now - timedelta(hours=1)
    )
    alert3 = Alert(
        transaction_id='TXN015',
        alert_type='HIGH_RISK_COMPANY',
        severity=AlertSeverity.HIGH,
        timestamp=now
    )
    
    store.store_alerts([alert1, alert2, alert3])
    
    # Get alerts from last 90 minutes
    start_time = now - timedelta(minutes=90)
    end_time = now
    recent_alerts = store.get_alerts_by_time_range(start_time, end_time)
    
    assert len(recent_alerts) == 2  # alert2 and alert3
    assert recent_alerts[0].timestamp >= start_time
    assert recent_alerts[-1].timestamp <= end_time
    
    print(f"  ✓ Retrieved {len(recent_alerts)} alerts within time range")


def test_get_all_alerts():
    """Test retrieving all alerts."""
    print("\nTesting get_all_alerts()...")
    
    store = AlertStore()
    
    alerts = [
        Alert(transaction_id='TXN016', alert_type='PRICE_ANOMALY', severity=AlertSeverity.HIGH),
        Alert(transaction_id='TXN017', alert_type='ROUTE_ANOMALY', severity=AlertSeverity.MEDIUM),
        Alert(transaction_id='TXN018', alert_type='PORT_CONGESTION', severity=AlertSeverity.MEDIUM)
    ]
    
    store.store_alerts(alerts)
    
    all_alerts = store.get_all_alerts()
    assert len(all_alerts) == 3
    
    print(f"  ✓ Retrieved all {len(all_alerts)} alerts")


def test_get_all_summaries():
    """Test retrieving all summaries."""
    print("\nTesting get_all_summaries()...")
    
    store = AlertStore()
    
    summaries = [
        AlertSummary(
            transaction_id='TXN019',
            alerts=[],
            priority=AlertPriority.CRITICAL,
            risk_category='FRAUD',
            alert_count=2,
            severity_score=6,
            priority_reason='Critical'
        ),
        AlertSummary(
            transaction_id='TXN020',
            alerts=[],
            priority=AlertPriority.HIGH,
            risk_category='FRAUD',
            alert_count=1,
            severity_score=3,
            priority_reason='High'
        )
    ]
    
    for summary in summaries:
        store.store_summary(summary)
    
    all_summaries = store.get_all_summaries()
    assert len(all_summaries) == 2
    assert all_summaries[0].priority == AlertPriority.CRITICAL  # Sorted by priority
    
    print(f"  ✓ Retrieved all {len(all_summaries)} summaries")


def test_get_counts():
    """Test count methods."""
    print("\nTesting count methods...")
    
    store = AlertStore()
    
    # Store some alerts and summaries
    alerts = [
        Alert(transaction_id='TXN021', alert_type='PRICE_ANOMALY', severity=AlertSeverity.HIGH),
        Alert(transaction_id='TXN021', alert_type='ROUTE_ANOMALY', severity=AlertSeverity.MEDIUM),
        Alert(transaction_id='TXN022', alert_type='PORT_CONGESTION', severity=AlertSeverity.MEDIUM)
    ]
    store.store_alerts(alerts)
    
    summary = AlertSummary(
        transaction_id='TXN021',
        alerts=[],
        priority=AlertPriority.HIGH,
        risk_category='FRAUD',
        alert_count=2,
        severity_score=5,
        priority_reason='High'
    )
    store.store_summary(summary)
    
    # Test counts
    alert_count = store.get_alert_count()
    summary_count = store.get_summary_count()
    transaction_ids = store.get_transaction_ids()
    
    assert alert_count == 3
    assert summary_count == 1
    assert len(transaction_ids) == 2
    assert 'TXN021' in transaction_ids
    assert 'TXN022' in transaction_ids
    
    print(f"  ✓ Counts: {alert_count} alerts, {summary_count} summaries, {len(transaction_ids)} transactions")


def test_get_statistics():
    """Test statistics generation."""
    print("\nTesting get_statistics()...")
    
    store = AlertStore()
    
    # Store alerts
    alerts = [
        Alert(transaction_id='TXN023', alert_type='PRICE_ANOMALY', severity=AlertSeverity.HIGH),
        Alert(transaction_id='TXN023', alert_type='ROUTE_ANOMALY', severity=AlertSeverity.MEDIUM),
        Alert(transaction_id='TXN024', alert_type='PRICE_ANOMALY', severity=AlertSeverity.HIGH)
    ]
    store.store_alerts(alerts)
    
    # Store summaries
    summaries = [
        AlertSummary(
            transaction_id='TXN023',
            alerts=[],
            priority=AlertPriority.CRITICAL,
            risk_category='FRAUD',
            alert_count=2,
            severity_score=5,
            priority_reason='Critical'
        ),
        AlertSummary(
            transaction_id='TXN024',
            alerts=[],
            priority=AlertPriority.HIGH,
            risk_category='FRAUD',
            alert_count=1,
            severity_score=3,
            priority_reason='High'
        )
    ]
    for summary in summaries:
        store.store_summary(summary)
    
    # Get statistics
    stats = store.get_statistics()
    
    assert stats['total_alerts'] == 3
    assert stats['total_summaries'] == 2
    assert stats['total_transactions'] == 2
    assert stats['priority_counts']['CRITICAL'] == 1
    assert stats['priority_counts']['HIGH'] == 1
    assert stats['alert_type_counts']['PRICE_ANOMALY'] == 2
    assert stats['alert_type_counts']['ROUTE_ANOMALY'] == 1
    
    print(f"  ✓ Statistics: {stats['total_alerts']} alerts, {stats['total_summaries']} summaries")
    print(f"    Priority counts: {stats['priority_counts']}")
    print(f"    Alert type counts: {stats['alert_type_counts']}")


def test_clear():
    """Test clearing the store."""
    print("\nTesting clear()...")
    
    store = AlertStore()
    
    # Store some data
    alert = Alert(transaction_id='TXN025', alert_type='PRICE_ANOMALY', severity=AlertSeverity.HIGH)
    store.store_alert(alert)
    
    summary = AlertSummary(
        transaction_id='TXN025',
        alerts=[],
        priority=AlertPriority.HIGH,
        risk_category='FRAUD',
        alert_count=1,
        severity_score=3,
        priority_reason='High'
    )
    store.store_summary(summary)
    
    # Verify data exists
    assert store.get_alert_count() == 1
    assert store.get_summary_count() == 1
    
    # Clear the store
    store.clear()
    
    # Verify data is cleared
    assert store.get_alert_count() == 0
    assert store.get_summary_count() == 0
    assert len(store.get_transaction_ids()) == 0
    
    print(f"  ✓ Store cleared successfully")


def test_global_alert_store():
    """Test global alert store singleton."""
    print("\nTesting get_alert_store() singleton...")
    
    # Reset first
    reset_alert_store()
    
    # Get global store
    store1 = get_alert_store()
    store2 = get_alert_store()
    
    # Should be the same instance
    assert store1 is store2
    
    # Store data in one
    alert = Alert(transaction_id='TXN026', alert_type='PRICE_ANOMALY', severity=AlertSeverity.HIGH)
    store1.store_alert(alert)
    
    # Should be accessible from the other
    alerts = store2.get_alerts_by_transaction('TXN026')
    assert len(alerts) == 1
    
    print(f"  ✓ Global singleton works correctly")
    
    # Reset for cleanup
    reset_alert_store()


def test_nonexistent_transaction():
    """Test retrieving alerts for non-existent transaction."""
    print("\nTesting non-existent transaction retrieval...")
    
    store = AlertStore()
    
    # Try to get alerts for non-existent transaction
    alerts = store.get_alerts_by_transaction('NONEXISTENT')
    assert len(alerts) == 0
    
    # Try to get summary for non-existent transaction
    summary = store.get_summary_by_transaction('NONEXISTENT')
    assert summary is None
    
    print(f"  ✓ Handles non-existent transactions gracefully")


def run_all_tests():
    """Run all test functions."""
    print("=" * 60)
    print("Running AlertStore Tests")
    print("=" * 60)
    
    try:
        test_store_and_retrieve_single_alert()
        test_store_multiple_alerts_same_transaction()
        test_store_alerts_batch()
        test_store_and_retrieve_summary()
        test_get_alerts_by_priority()
        test_get_alerts_by_min_priority()
        test_get_alerts_by_time_range()
        test_get_all_alerts()
        test_get_all_summaries()
        test_get_counts()
        test_get_statistics()
        test_clear()
        test_global_alert_store()
        test_nonexistent_transaction()
        
        print("\n" + "=" * 60)
        print("✓ All AlertStore tests passed!")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
