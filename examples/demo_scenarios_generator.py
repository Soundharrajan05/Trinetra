"""
TRINETRA AI - Demo Scenarios Generator

This script generates curated demo scenarios for hackathon presentations.
It identifies the most interesting fraud cases and creates presentation-ready summaries.

Usage:
    python examples/demo_scenarios_generator.py
"""

import pandas as pd
import json
from pathlib import Path


def load_data():
    """Load the trade fraud dataset"""
    data_path = Path("data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
    return pd.read_csv(data_path)


def find_extreme_fraud_cases(df, top_n=5):
    """Find the most extreme fraud cases by price deviation"""
    fraud_cases = df[df['fraud_label'] == 2].copy()
    fraud_cases['abs_deviation'] = fraud_cases['price_deviation'].abs()
    return fraud_cases.nlargest(top_n, 'abs_deviation')


def find_multi_factor_cases(df, top_n=5):
    """Find cases with multiple risk factors"""
    df = df.copy()
    
    # Count risk factors
    df['risk_factors'] = 0
    df.loc[df['price_deviation'].abs() > 0.5, 'risk_factors'] += 1
    df.loc[df['route_anomaly'] == 1, 'risk_factors'] += 1
    df.loc[df['company_risk_score'] > 0.8, 'risk_factors'] += 1
    df.loc[df['port_activity_index'] > 1.5, 'risk_factors'] += 1
    
    return df.nlargest(top_n, 'risk_factors')


def find_high_value_fraud(df, top_n=5):
    """Find highest value fraudulent transactions"""
    fraud_cases = df[df['fraud_label'] == 2].copy()
    return fraud_cases.nlargest(top_n, 'trade_value')


def find_route_anomalies(df, top_n=5):
    """Find transactions with route anomalies and high risk"""
    route_cases = df[df['route_anomaly'] == 1].copy()
    return route_cases.nlargest(top_n, 'company_risk_score')


def find_port_exploitation(df, top_n=5):
    """Find cases exploiting congested ports"""
    port_cases = df[df['port_activity_index'] > 1.5].copy()
    return port_cases.nlargest(top_n, 'port_activity_index')


def format_transaction_summary(row):
    """Format a transaction as a readable summary"""
    return {
        'transaction_id': row['transaction_id'],
        'product': row['product'],
        'commodity_category': row['commodity_category'],
        'fraud_label': 'FRAUD' if row['fraud_label'] == 2 else 'SAFE',
        'price_info': {
            'market_price': f"${row['market_price']:.2f}",
            'trade_price': f"${row['unit_price']:.2f}",
            'deviation': f"{row['price_deviation']*100:.2f}%"
        },
        'trade_value': f"${row['trade_value']:,.2f}",
        'route': {
            'from': f"{row['export_port']}, {row['exporter_country']}",
            'to': f"{row['import_port']}, {row['importer_country']}",
            'distance_km': row['distance_km'],
            'route_name': row['shipping_route']
        },
        'risk_factors': {
            'company_risk_score': f"{row['company_risk_score']:.2f}",
            'route_anomaly': 'Yes' if row['route_anomaly'] == 1 else 'No',
            'port_activity_index': f"{row['port_activity_index']:.2f}"
        },
        'companies': {
            'exporter': row['exporter_company'],
            'importer': row['importer_company']
        }
    }


def generate_demo_scenarios():
    """Generate all demo scenarios"""
    print("Loading dataset...")
    df = load_data()
    
    print(f"Total transactions: {len(df)}")
    print(f"Fraud cases: {(df['fraud_label'] == 2).sum()}")
    print(f"Safe cases: {(df['fraud_label'] == 0).sum()}")
    print()
    
    scenarios = {}
    
    # Scenario 1: Extreme Price Manipulation
    print("Finding extreme price manipulation cases...")
    extreme_cases = find_extreme_fraud_cases(df, top_n=5)
    scenarios['extreme_price_manipulation'] = [
        format_transaction_summary(row) 
        for _, row in extreme_cases.iterrows()
    ]
    
    # Scenario 2: Multi-Factor Risk
    print("Finding multi-factor risk cases...")
    multi_factor = find_multi_factor_cases(df, top_n=5)
    scenarios['multi_factor_risk'] = [
        format_transaction_summary(row) 
        for _, row in multi_factor.iterrows()
    ]
    
    # Scenario 3: High-Value Fraud
    print("Finding high-value fraud cases...")
    high_value = find_high_value_fraud(df, top_n=5)
    scenarios['high_value_fraud'] = [
        format_transaction_summary(row) 
        for _, row in high_value.iterrows()
    ]
    
    # Scenario 4: Route Anomalies
    print("Finding route anomaly cases...")
    route_anomalies = find_route_anomalies(df, top_n=5)
    scenarios['route_anomalies'] = [
        format_transaction_summary(row) 
        for _, row in route_anomalies.iterrows()
    ]
    
    # Scenario 5: Port Exploitation
    print("Finding port exploitation cases...")
    port_cases = find_port_exploitation(df, top_n=5)
    scenarios['port_exploitation'] = [
        format_transaction_summary(row) 
        for _, row in port_cases.iterrows()
    ]
    
    return scenarios


def generate_statistics(df):
    """Generate dataset statistics for demo"""
    stats = {
        'overview': {
            'total_transactions': len(df),
            'fraud_cases': int((df['fraud_label'] == 2).sum()),
            'safe_cases': int((df['fraud_label'] == 0).sum()),
            'fraud_rate': f"{(df['fraud_label'] == 2).sum() / len(df) * 100:.2f}%"
        },
        'risk_factors': {
            'high_price_deviation': int((df['price_deviation'].abs() > 0.5).sum()),
            'route_anomalies': int((df['route_anomaly'] == 1).sum()),
            'high_risk_companies': int((df['company_risk_score'] > 0.8).sum()),
            'port_congestion': int((df['port_activity_index'] > 1.5).sum())
        },
        'products': {
            'most_common': df['product'].value_counts().head(5).to_dict(),
            'highest_fraud_rate': df.groupby('product')['fraud_label'].apply(
                lambda x: (x == 2).sum() / len(x) * 100
            ).nlargest(5).to_dict()
        },
        'countries': {
            'top_exporters': df['exporter_country'].value_counts().head(5).to_dict(),
            'top_importers': df['importer_country'].value_counts().head(5).to_dict()
        },
        'trade_value': {
            'total': f"${df['trade_value'].sum():,.2f}",
            'average': f"${df['trade_value'].mean():,.2f}",
            'fraud_total': f"${df[df['fraud_label'] == 2]['trade_value'].sum():,.2f}"
        }
    }
    
    return stats


def print_scenario_summary(scenarios):
    """Print a summary of generated scenarios"""
    print("\n" + "="*80)
    print("DEMO SCENARIOS SUMMARY")
    print("="*80)
    
    for scenario_name, cases in scenarios.items():
        print(f"\n{scenario_name.upper().replace('_', ' ')}")
        print("-" * 80)
        for i, case in enumerate(cases, 1):
            print(f"\n{i}. Transaction {case['transaction_id']}")
            print(f"   Product: {case['product']}")
            print(f"   Price Deviation: {case['price_info']['deviation']}")
            print(f"   Trade Value: {case['trade_value']}")
            print(f"   Company Risk: {case['risk_factors']['company_risk_score']}")
            print(f"   Route Anomaly: {case['risk_factors']['route_anomaly']}")


def save_scenarios(scenarios, stats, output_path="examples/demo_scenarios.json"):
    """Save scenarios to JSON file"""
    output = {
        'statistics': stats,
        'scenarios': scenarios,
        'metadata': {
            'generated_at': pd.Timestamp.now().isoformat(),
            'dataset': 'trinetra_trade_fraud_dataset_1000_rows_complex.csv',
            'version': '1.0'
        }
    }
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Scenarios saved to: {output_file}")


def generate_presentation_notes():
    """Generate presentation notes for each scenario"""
    notes = {
        'extreme_price_manipulation': {
            'title': 'Extreme Price Manipulation',
            'key_message': 'Massive price deviations indicate transfer pricing fraud or money laundering',
            'demo_script': [
                'Show the transaction with highest price deviation',
                'Highlight the market price vs trade price gap',
                'Explain why no legitimate business would do this',
                'Request AI explanation to show reasoning'
            ],
            'talking_points': [
                'Transfer pricing fraud shifts profits to avoid taxes',
                'Money laundering through undervalued exports',
                'Sanctions evasion by disguising transaction values'
            ]
        },
        'multi_factor_risk': {
            'title': 'Multi-Factor Risk Analysis',
            'key_message': 'Multiple risk factors compound to create high-confidence fraud detection',
            'demo_script': [
                'Show transaction with 3+ risk factors',
                'Explain how AI weighs multiple indicators',
                'Demonstrate risk scoring algorithm',
                'Show how this prioritizes investigation efforts'
            ],
            'talking_points': [
                'Single factors might be coincidence',
                'Multiple factors indicate systematic fraud',
                'AI learns patterns humans might miss'
            ]
        },
        'high_value_fraud': {
            'title': 'High-Value Fraud Cases',
            'key_message': 'Prioritize investigation by financial impact',
            'demo_script': [
                'Sort by trade value to show highest impact',
                'Calculate total fraud value detected',
                'Explain ROI of fraud detection',
                'Show business case for the system'
            ],
            'talking_points': [
                'Focus resources on highest-impact cases',
                'Prevent millions in losses',
                'Justify investment in fraud detection'
            ]
        },
        'route_anomalies': {
            'title': 'Route Anomaly Detection',
            'key_message': 'Unusual shipping routes suggest smuggling or customs evasion',
            'demo_script': [
                'Show route on map visualization',
                'Compare with normal routes',
                'Explain why fraudsters use indirect routes',
                'Demonstrate pattern recognition'
            ],
            'talking_points': [
                'Avoiding major customs checkpoints',
                'Smuggling through less-monitored ports',
                'Network analysis reveals patterns'
            ]
        },
        'port_exploitation': {
            'title': 'Port Congestion Exploitation',
            'key_message': 'Fraudsters exploit overwhelmed ports with weak inspection',
            'demo_script': [
                'Show port activity index distribution',
                'Highlight transactions through congested ports',
                'Explain why this matters for fraud',
                'Demonstrate alert system'
            ],
            'talking_points': [
                'Overwhelmed customs inspectors',
                'Higher chance of slipping through',
                'Systematic exploitation of weak points'
            ]
        }
    }
    
    return notes


def main():
    """Main execution function"""
    print("="*80)
    print("TRINETRA AI - Demo Scenarios Generator")
    print("="*80)
    print()
    
    # Load data
    df = load_data()
    
    # Generate statistics
    print("Generating statistics...")
    stats = generate_statistics(df)
    
    # Generate scenarios
    scenarios = generate_demo_scenarios()
    
    # Print summary
    print_scenario_summary(scenarios)
    
    # Generate presentation notes
    notes = generate_presentation_notes()
    
    # Save everything
    save_scenarios(scenarios, stats)
    
    # Save presentation notes
    notes_path = Path("examples/presentation_notes.json")
    with open(notes_path, 'w') as f:
        json.dump(notes, f, indent=2)
    print(f"✅ Presentation notes saved to: {notes_path}")
    
    print("\n" + "="*80)
    print("STATISTICS SUMMARY")
    print("="*80)
    print(f"Total Transactions: {stats['overview']['total_transactions']}")
    print(f"Fraud Cases: {stats['overview']['fraud_cases']}")
    print(f"Fraud Rate: {stats['overview']['fraud_rate']}")
    print(f"Total Trade Value: {stats['trade_value']['total']}")
    print(f"Fraud Value: {stats['trade_value']['fraud_total']}")
    print()
    print("Risk Factors:")
    for factor, count in stats['risk_factors'].items():
        print(f"  - {factor.replace('_', ' ').title()}: {count}")
    
    print("\n✅ Demo scenarios generated successfully!")
    print("\nNext steps:")
    print("1. Review examples/demo_scenarios.json")
    print("2. Read docs/DEMO_SCENARIOS.md for full guide")
    print("3. Use docs/DEMO_QUICK_REFERENCE.md during presentation")
    print("4. Practice with the generated scenarios")


if __name__ == "__main__":
    main()
