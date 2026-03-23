"""
Demonstration of the Alert Prioritization System

This script shows how the alert prioritization logic works with various
transaction scenarios.
"""

import sys
sys.path.insert(0, '.')

from backend.alerts import (
    check_alerts,
    prioritize_alert,
    get_prioritized_alerts,
    get_alerts_by_priority,
    AlertPriority
)


def print_separator():
    print("\n" + "=" * 80 + "\n")


def demo_alert_prioritization():
    """Demonstrate alert prioritization with various scenarios."""
    
    print_separator()
    print("TRINETRA AI - Alert Prioritization System Demo")
    print_separator()
    
    # Sample transactions with different risk profiles
    transactions = [
        {
            'transaction_id': 'TXN001',
            'product': 'Electronics',
            'risk_category': 'FRAUD',
            'price_deviation': 0.8,
            'route_anomaly': 1,
            'company_risk_score': 0.95,
            'port_activity_index': 1.8
        },
        {
            'transaction_id': 'TXN002',
            'product': 'Textiles',
            'risk_category': 'FRAUD',
            'price_deviation': 0.6,
            'route_anomaly': 0,
            'company_risk_score': 0.4,
            'port_activity_index': 1.0
        },
        {
            'transaction_id': 'TXN003',
            'product': 'Machinery',
            'risk_category': 'SUSPICIOUS',
            'price_deviation': 0.7,
            'route_anomaly': 1,
            'company_risk_score': 0.85,
            'port_activity_index': 1.6
        },
        {
            'transaction_id': 'TXN004',
            'product': 'Food Products',
            'risk_category': 'SUSPICIOUS',
            'price_deviation': 0.55,
            'route_anomaly': 0,
            'company_risk_score': 0.6,
            'port_activity_index': 1.2
        },
        {
            'transaction_id': 'TXN005',
            'product': 'Chemicals',
            'risk_category': 'SAFE',
            'price_deviation': 0.2,
            'route_anomaly': 0,
            'company_risk_score': 0.3,
            'port_activity_index': 0.9
        }
    ]
    
    print("Sample Transactions:")
    print("-" * 80)
    for txn in transactions:
        print(f"  {txn['transaction_id']}: {txn['product']} - Risk: {txn['risk_category']}")
    
    print_separator()
    print("Alert Analysis for Each Transaction:")
    print("-" * 80)
    
    for txn in transactions:
        alerts = check_alerts(txn)
        if alerts:
            priority, metadata = prioritize_alert(txn, alerts)
            print(f"\n{txn['transaction_id']} - {txn['product']}")
            print(f"  Risk Category: {txn['risk_category']}")
            print(f"  Alerts Triggered: {', '.join(alerts)}")
            print(f"  Alert Count: {metadata['alert_count']}")
            print(f"  Severity Score: {metadata['severity_score']}")
            print(f"  Priority: {priority.name} (Level {priority.value})")
            print(f"  Reason: {metadata['priority_reason']}")
        else:
            print(f"\n{txn['transaction_id']} - {txn['product']}")
            print(f"  Risk Category: {txn['risk_category']}")
            print(f"  No alerts triggered")
    
    print_separator()
    print("Prioritized Alert Queue (Highest Priority First):")
    print("-" * 80)
    
    prioritized = get_prioritized_alerts(transactions)
    
    for i, alert_info in enumerate(prioritized, 1):
        txn = alert_info['transaction']
        print(f"\n{i}. {txn['transaction_id']} - {txn['product']}")
        print(f"   Priority: {alert_info['priority_level']} (Level {alert_info['priority_value']})")
        print(f"   Risk Category: {txn['risk_category']}")
        print(f"   Alerts: {', '.join(alert_info['alerts'])}")
        print(f"   Reason: {alert_info['metadata']['priority_reason']}")
    
    print_separator()
    print("Filtering by Priority Level:")
    print("-" * 80)
    
    # Show CRITICAL alerts only
    critical_alerts = get_alerts_by_priority(transactions, AlertPriority.CRITICAL)
    print(f"\nCRITICAL Alerts ({len(critical_alerts)}):")
    for alert_info in critical_alerts:
        txn = alert_info['transaction']
        print(f"  - {txn['transaction_id']}: {txn['product']} ({len(alert_info['alerts'])} alerts)")
    
    # Show HIGH and above
    high_alerts = get_alerts_by_priority(transactions, AlertPriority.HIGH)
    print(f"\nHIGH+ Alerts ({len(high_alerts)}):")
    for alert_info in high_alerts:
        txn = alert_info['transaction']
        print(f"  - {txn['transaction_id']}: {txn['product']} "
              f"[{alert_info['priority_level']}] ({len(alert_info['alerts'])} alerts)")
    
    # Show MEDIUM and above
    medium_alerts = get_alerts_by_priority(transactions, AlertPriority.MEDIUM)
    print(f"\nMEDIUM+ Alerts ({len(medium_alerts)}):")
    for alert_info in medium_alerts:
        txn = alert_info['transaction']
        print(f"  - {txn['transaction_id']}: {txn['product']} "
              f"[{alert_info['priority_level']}] ({len(alert_info['alerts'])} alerts)")
    
    print_separator()
    print("Priority Distribution Summary:")
    print("-" * 80)
    
    priority_counts = {
        'CRITICAL': 0,
        'HIGH': 0,
        'MEDIUM': 0,
        'LOW': 0
    }
    
    for alert_info in prioritized:
        priority_counts[alert_info['priority_level']] += 1
    
    total_alerts = len(prioritized)
    print(f"\nTotal Transactions with Alerts: {total_alerts}")
    print(f"Total Transactions Analyzed: {len(transactions)}")
    print(f"\nPriority Breakdown:")
    for priority_name in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = priority_counts[priority_name]
        percentage = (count / total_alerts * 100) if total_alerts > 0 else 0
        print(f"  {priority_name:10s}: {count:2d} ({percentage:5.1f}%)")
    
    print_separator()
    print("Investigator Action Recommendations:")
    print("-" * 80)
    print("\nBased on the prioritization:")
    print("  1. CRITICAL alerts should be investigated immediately")
    print("  2. HIGH alerts should be reviewed within 24 hours")
    print("  3. MEDIUM alerts should be reviewed within 48 hours")
    print("  4. LOW alerts can be reviewed during routine audits")
    
    if critical_alerts:
        print(f"\n⚠️  URGENT: {len(critical_alerts)} CRITICAL alert(s) require immediate attention!")
    
    print_separator()


if __name__ == "__main__":
    demo_alert_prioritization()
