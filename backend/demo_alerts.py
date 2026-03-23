"""
Demonstration script for the Alert System

This script shows how to use the check_alerts() function with
real transaction data from the TRINETRA dataset.
"""

import pandas as pd
from backend.alerts import check_alerts
from backend.data_loader import load_dataset


def demonstrate_alert_system():
    """Demonstrate the alert system with real data"""
    
    print("=" * 70)
    print("TRINETRA AI - Alert System Demonstration")
    print("=" * 70)
    
    # Load the dataset
    print("\nLoading dataset...")
    df = load_dataset("../data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
    print(f"Loaded {len(df)} transactions\n")
    
    # Analyze all transactions for alerts
    alert_summary = {
        "PRICE_ANOMALY": [],
        "ROUTE_ANOMALY": [],
        "HIGH_RISK_COMPANY": [],
        "PORT_CONGESTION": []
    }
    
    transactions_with_alerts = []
    
    for idx, row in df.iterrows():
        transaction = {
            'transaction_id': row['transaction_id'],
            'price_deviation': row['price_deviation'],
            'route_anomaly': row['route_anomaly'],
            'company_risk_score': row['company_risk_score'],
            'port_activity_index': row['port_activity_index'],
            'product': row['product'],
            'exporter_country': row['exporter_country'],
            'importer_country': row['importer_country']
        }
        
        alerts = check_alerts(transaction)
        
        if alerts:
            transactions_with_alerts.append({
                'transaction': transaction,
                'alerts': alerts
            })
            for alert in alerts:
                alert_summary[alert].append(transaction['transaction_id'])
    
    # Print summary statistics
    print("=" * 70)
    print("ALERT SUMMARY")
    print("=" * 70)
    print(f"\nTotal Transactions Analyzed: {len(df)}")
    print(f"Transactions with Alerts: {len(transactions_with_alerts)}")
    print(f"Alert Rate: {len(transactions_with_alerts)/len(df)*100:.1f}%\n")
    
    print("Alert Type Breakdown:")
    print(f"  PRICE_ANOMALY:      {len(alert_summary['PRICE_ANOMALY']):4d} transactions")
    print(f"  ROUTE_ANOMALY:      {len(alert_summary['ROUTE_ANOMALY']):4d} transactions")
    print(f"  HIGH_RISK_COMPANY:  {len(alert_summary['HIGH_RISK_COMPANY']):4d} transactions")
    print(f"  PORT_CONGESTION:    {len(alert_summary['PORT_CONGESTION']):4d} transactions")
    
    # Show examples of each alert type
    print("\n" + "=" * 70)
    print("EXAMPLE ALERTS")
    print("=" * 70)
    
    alert_types = ["PRICE_ANOMALY", "ROUTE_ANOMALY", "HIGH_RISK_COMPANY", "PORT_CONGESTION"]
    
    for alert_type in alert_types:
        print(f"\n{alert_type}:")
        print("-" * 70)
        
        # Find first transaction with this alert
        found = False
        for item in transactions_with_alerts:
            if alert_type in item['alerts']:
                txn = item['transaction']
                print(f"  Transaction ID: {txn['transaction_id']}")
                print(f"  Product: {txn['product']}")
                print(f"  Route: {txn['exporter_country']} → {txn['importer_country']}")
                print(f"  Price Deviation: {txn['price_deviation']:.2f}")
                print(f"  Route Anomaly: {txn['route_anomaly']}")
                print(f"  Company Risk Score: {txn['company_risk_score']:.2f}")
                print(f"  Port Activity Index: {txn['port_activity_index']:.2f}")
                print(f"  All Alerts: {', '.join(item['alerts'])}")
                found = True
                break
        
        if not found:
            print("  No transactions found with this alert type")
    
    # Show transactions with multiple alerts
    print("\n" + "=" * 70)
    print("HIGH-PRIORITY TRANSACTIONS (Multiple Alerts)")
    print("=" * 70)
    
    multi_alert_transactions = [
        item for item in transactions_with_alerts 
        if len(item['alerts']) >= 3
    ]
    
    if multi_alert_transactions:
        print(f"\nFound {len(multi_alert_transactions)} transactions with 3+ alerts:\n")
        for i, item in enumerate(multi_alert_transactions[:5], 1):
            txn = item['transaction']
            print(f"{i}. Transaction {txn['transaction_id']}")
            print(f"   Product: {txn['product']}")
            print(f"   Route: {txn['exporter_country']} → {txn['importer_country']}")
            print(f"   Alerts ({len(item['alerts'])}): {', '.join(item['alerts'])}")
            print()
    else:
        print("\nNo transactions found with 3+ alerts")
    
    print("=" * 70)
    print("Alert System Demonstration Complete")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_alert_system()
