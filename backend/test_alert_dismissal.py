"""
Test script for alert dismissal functionality.

This script tests the new alert dismissal features added to the TRINETRA AI system.
"""

from alerts import (
    Alert, AlertSummary, AlertStore, AlertPriority, AlertSeverity,
    get_alert_store, reset_alert_store
)
from datetime import datetime


def test_alert_dismissal():
    """Test alert dismissal functionality."""
    print("Testing Alert Dismissal Functionality")
    print("=" * 50)
    
    # Reset alert store
    reset_alert_store()
    store = get_alert_store()
    
    # Create test alert
    alert = Alert(
        transaction_id="TXN001",
        alert_type="PRICE_ANOMALY",
        severity=AlertSeverity.HIGH,
        message="Test alert"
    )
    
    # Create test summary
    summary = AlertSummary(
        transaction_id="TXN001",
        alerts=[alert],
        priority=AlertPriority.HIGH,
        risk_category="FRAUD",
        alert_count=1,
        severity_score=3,
        priority_reason="Test reason"
    )
    
    # Store the summary
    store.store_summary(summary)
    store.store_alert(alert)
    
    print("\n1. Initial state:")
    print(f"   - Alert dismissed: {alert.dismissed}")
    print(f"   - Summary dismissed: {summary.dismissed}")
    
    # Test dismissal
    print("\n2. Dismissing alert...")
    success = store.dismiss_alert_summary("TXN001", "test_user")
    print(f"   - Dismissal success: {success}")
    
    # Retrieve and check
    retrieved_summary = store.get_summary_by_transaction("TXN001")
    print(f"   - Summary dismissed: {retrieved_summary.dismissed}")
    print(f"   - Dismissed by: {retrieved_summary.dismissed_by}")
    print(f"   - Dismissed at: {retrieved_summary.dismissed_at}")
    
    # Test active/dismissed filtering
    print("\n3. Testing filtering:")
    active = store.get_active_summaries()
    dismissed = store.get_dismissed_summaries()
    print(f"   - Active summaries: {len(active)}")
    print(f"   - Dismissed summaries: {len(dismissed)}")
    
    # Test undismissal
    print("\n4. Undismissing alert...")
    success = store.undismiss_alert_summary("TXN001")
    print(f"   - Undismissal success: {success}")
    
    retrieved_summary = store.get_summary_by_transaction("TXN001")
    print(f"   - Summary dismissed: {retrieved_summary.dismissed}")
    
    # Test statistics
    print("\n5. Statistics:")
    stats = store.get_statistics()
    print(f"   - Total summaries: {stats['total_summaries']}")
    print(f"   - Active count: {stats['active_count']}")
    print(f"   - Dismissed count: {stats['dismissed_count']}")
    
    print("\n" + "=" * 50)
    print("✓ All tests passed!")


if __name__ == "__main__":
    test_alert_dismissal()
