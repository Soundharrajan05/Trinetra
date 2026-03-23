"""
Example demonstrating how to use alert data structures in the API.

This shows how the alert system integrates with the FastAPI backend
to provide rich alert information to the frontend dashboard.
"""

from backend.alerts import (
    Alert, AlertSummary, AlertPriority,
    create_alert_summary, get_prioritized_alerts
)
import json


def example_api_response():
    """
    Example of how alerts would be returned in an API response.
    """
    print("=" * 70)
    print("Example: API Response with Alert Data Structures")
    print("=" * 70)
    
    # Sample transaction with multiple alerts
    transaction = {
        'transaction_id': 'TXN00452',
        'risk_category': 'FRAUD',
        'price_deviation': 0.75,
        'route_anomaly': 1,
        'company_risk_score': 0.92,
        'port_activity_index': 1.8,
        'product': 'Electronics',
        'market_price': 1000,
        'unit_price': 1750,
        'exporter_name': 'Suspicious Corp',
        'importer_name': 'Shell Company Ltd',
        'shipping_route': 'Shanghai -> Rotterdam',
        'export_port': 'Shanghai',
        'import_port': 'Rotterdam'
    }
    
    # Create alert summary
    summary = create_alert_summary(transaction)
    
    # Convert to API response format
    api_response = {
        'status': 'success',
        'data': {
            'transaction_id': summary.transaction_id,
            'alert_summary': summary.to_dict()
        }
    }
    
    print("\nAPI Response (GET /alerts/{transaction_id}):")
    print(json.dumps(api_response, indent=2))
    
    return api_response


def example_dashboard_alerts():
    """
    Example of how alerts would be displayed in the dashboard.
    """
    print("\n" + "=" * 70)
    print("Example: Dashboard Alert Display")
    print("=" * 70)
    
    # Multiple transactions with varying alert levels
    transactions = [
        {
            'transaction_id': 'TXN001',
            'risk_category': 'FRAUD',
            'price_deviation': 0.8,
            'route_anomaly': 1,
            'company_risk_score': 0.95,
            'port_activity_index': 1.9
        },
        {
            'transaction_id': 'TXN002',
            'risk_category': 'SUSPICIOUS',
            'price_deviation': 0.6,
            'route_anomaly': 0,
            'company_risk_score': 0.85,
            'port_activity_index': 1.2
        },
        {
            'transaction_id': 'TXN003',
            'risk_category': 'SUSPICIOUS',
            'price_deviation': 0.4,
            'route_anomaly': 1,
            'company_risk_score': 0.5,
            'port_activity_index': 1.0
        },
        {
            'transaction_id': 'TXN004',
            'risk_category': 'SAFE',
            'price_deviation': 0.2,
            'route_anomaly': 0,
            'company_risk_score': 0.3,
            'port_activity_index': 0.8
        }
    ]
    
    # Get prioritized alerts
    prioritized = get_prioritized_alerts(transactions)
    
    print(f"\nFound {len(prioritized)} transactions with alerts")
    print("\nAlert Dashboard View:")
    print("-" * 70)
    
    for item in prioritized:
        summary_data = item['transaction']
        alerts = item['alerts']
        priority = item['priority_level']
        
        # Display alert banner
        priority_symbols = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }
        
        symbol = priority_symbols.get(priority, '⚪')
        print(f"\n{symbol} {priority} PRIORITY - Transaction {summary_data['transaction_id']}")
        print(f"   Risk Category: {summary_data['risk_category']}")
        print(f"   Alerts: {', '.join(alerts)}")
        print(f"   Reason: {item['metadata']['priority_reason']}")
    
    print("\n" + "-" * 70)
    
    # API response format for dashboard
    api_response = {
        'status': 'success',
        'data': {
            'total_alerts': len(prioritized),
            'critical_count': sum(1 for x in prioritized if x['priority_level'] == 'CRITICAL'),
            'high_count': sum(1 for x in prioritized if x['priority_level'] == 'HIGH'),
            'alerts': [
                {
                    'transaction_id': item['transaction']['transaction_id'],
                    'priority': item['priority_level'],
                    'alerts': item['alerts'],
                    'risk_category': item['transaction']['risk_category']
                }
                for item in prioritized
            ]
        }
    }
    
    print("\nAPI Response (GET /alerts/summary):")
    print(json.dumps(api_response, indent=2))


def example_alert_filtering():
    """
    Example of filtering alerts by priority level.
    """
    print("\n" + "=" * 70)
    print("Example: Filtering Critical Alerts Only")
    print("=" * 70)
    
    from backend.alerts import get_alerts_by_priority
    
    transactions = [
        {
            'transaction_id': 'TXN101',
            'risk_category': 'FRAUD',
            'price_deviation': 0.9,
            'route_anomaly': 1,
            'company_risk_score': 0.95,
            'port_activity_index': 2.0
        },
        {
            'transaction_id': 'TXN102',
            'risk_category': 'SUSPICIOUS',
            'price_deviation': 0.6,
            'route_anomaly': 1,
            'company_risk_score': 0.7,
            'port_activity_index': 1.2
        }
    ]
    
    # Get only critical alerts
    critical_alerts = get_alerts_by_priority(transactions, AlertPriority.CRITICAL)
    
    print(f"\nCritical Alerts: {len(critical_alerts)}")
    for item in critical_alerts:
        print(f"  - {item['transaction']['transaction_id']}: {item['priority_level']}")
    
    # API response for critical alerts endpoint
    api_response = {
        'status': 'success',
        'data': {
            'count': len(critical_alerts),
            'alerts': [
                {
                    'transaction_id': item['transaction']['transaction_id'],
                    'priority': item['priority_level'],
                    'alert_count': item['metadata']['alert_count'],
                    'severity_score': item['metadata']['severity_score']
                }
                for item in critical_alerts
            ]
        }
    }
    
    print("\nAPI Response (GET /alerts/critical):")
    print(json.dumps(api_response, indent=2))


def example_individual_alert_details():
    """
    Example of getting detailed information for individual alerts.
    """
    print("\n" + "=" * 70)
    print("Example: Individual Alert Details")
    print("=" * 70)
    
    transaction = {
        'transaction_id': 'TXN999',
        'risk_category': 'FRAUD',
        'price_deviation': 0.85,
        'route_anomaly': 1,
        'company_risk_score': 0.92,
        'port_activity_index': 1.7,
        'market_price': 500,
        'unit_price': 925,
        'shipping_route': 'Hong Kong -> Miami',
        'exporter_name': 'Risky Exports Inc',
        'importer_name': 'Questionable Imports LLC'
    }
    
    summary = create_alert_summary(transaction)
    
    print(f"\nTransaction: {summary.transaction_id}")
    print(f"Priority: {summary.priority.name}")
    print(f"\nIndividual Alerts:")
    
    for alert in summary.alerts:
        print(f"\n  Alert Type: {alert.alert_type}")
        print(f"  Severity: {alert.severity.name}")
        print(f"  Message: {alert.message}")
        print(f"  Metadata: {json.dumps(alert.metadata, indent=4)}")
    
    # API response with full alert details
    api_response = {
        'status': 'success',
        'data': {
            'summary': summary.to_dict()
        }
    }
    
    print("\nAPI Response (GET /alerts/{transaction_id}/details):")
    print(json.dumps(api_response, indent=2)[:500] + "...")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "TRINETRA AI - Alert System Examples" + " " * 17 + "║")
    print("╚" + "═" * 68 + "╝")
    
    example_api_response()
    example_dashboard_alerts()
    example_alert_filtering()
    example_individual_alert_details()
    
    print("\n" + "=" * 70)
    print("Examples completed successfully!")
    print("=" * 70 + "\n")
