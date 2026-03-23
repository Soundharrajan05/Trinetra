"""
Integration test for alerts system with real dataset

This test verifies that check_alerts() works correctly with actual
transaction data from the TRINETRA dataset.
"""

import pandas as pd
from alerts import check_alerts
from data_loader import load_dataset


def test_alerts_with_real_data():
    """Test check_alerts() with real transaction data"""
    
    # Load the dataset
    df = load_dataset("../data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
    
    print(f"\nLoaded {len(df)} transactions")
    
    # Test alerts on a sample of transactions
    alert_counts = {
        "PRICE_ANOMALY": 0,
        "ROUTE_ANOMALY": 0,
        "HIGH_RISK_COMPANY": 0,
        "PORT_CONGESTION": 0
    }
    
    transactions_with_alerts = 0
    
    for idx, row in df.head(100).iterrows():
        transaction = {
            'price_deviation': row['price_deviation'],
            'route_anomaly': row['route_anomaly'],
            'company_risk_score': row['company_risk_score'],
            'port_activity_index': row['port_activity_index']
        }
        
        alerts = check_alerts(transaction)
        
        if alerts:
            transactions_with_alerts += 1
            for alert in alerts:
                alert_counts[alert] += 1
    
    print(f"\nAlert Statistics (first 100 transactions):")
    print(f"Transactions with alerts: {transactions_with_alerts}")
    print(f"PRICE_ANOMALY: {alert_counts['PRICE_ANOMALY']}")
    print(f"ROUTE_ANOMALY: {alert_counts['ROUTE_ANOMALY']}")
    print(f"HIGH_RISK_COMPANY: {alert_counts['HIGH_RISK_COMPANY']}")
    print(f"PORT_CONGESTION: {alert_counts['PORT_CONGESTION']}")
    
    # Show a few examples
    print("\nExample transactions with alerts:")
    for idx, row in df.head(10).iterrows():
        transaction = {
            'price_deviation': row['price_deviation'],
            'route_anomaly': row['route_anomaly'],
            'company_risk_score': row['company_risk_score'],
            'port_activity_index': row['port_activity_index']
        }
        
        alerts = check_alerts(transaction)
        if alerts:
            print(f"\nTransaction {row['transaction_id']}:")
            print(f"  Price Deviation: {row['price_deviation']:.2f}")
            print(f"  Route Anomaly: {row['route_anomaly']}")
            print(f"  Company Risk Score: {row['company_risk_score']:.2f}")
            print(f"  Port Activity Index: {row['port_activity_index']:.2f}")
            print(f"  Alerts: {', '.join(alerts)}")


if __name__ == "__main__":
    test_alerts_with_real_data()
