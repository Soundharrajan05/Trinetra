#!/usr/bin/env python3
"""
Generate Demo Materials for TRINETRA AI

This script generates backup materials for demo presentations:
- Pre-generated explanations for key transactions
- Demo data summaries
- Quick reference data

Usage:
    python scripts/generate_demo_materials.py
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from data_loader import load_dataset
from feature_engineering import engineer_features
from fraud_detection import load_fraud_detector, score_transactions, classify_risk


def generate_demo_explanations():
    """Generate pre-written explanations for key demo transactions."""
    
    explanations = {
        "TXN00006": {
            "transaction_id": "TXN00006",
            "risk_category": "FRAUD",
            "risk_score": 0.85,
            "explanation": (
                "This crude oil transaction exhibits extreme price manipulation with a 73% "
                "deviation below market value. The trade price of $20 per ton compared to "
                "the market price of $75 per ton represents a $55 discount that no legitimate "
                "business would offer. This pattern is consistent with transfer pricing fraud "
                "or money laundering schemes where the true value is disguised through "
                "artificially low pricing."
            ),
            "key_indicators": [
                "Price deviation: -73.12%",
                "Trade price: $20/ton vs Market: $75/ton",
                "Product: Crude Oil (high-value commodity)",
                "Risk classification: FRAUD",
                "Potential schemes: Transfer pricing fraud, Money laundering"
            ],
            "investigation_priority": "CRITICAL",
            "recommended_actions": [
                "Verify exporter and importer relationship",
                "Check for shell company involvement",
                "Review historical transactions between these entities",
                "Investigate ultimate beneficial owners",
                "Flag for customs inspection"
            ]
        },
        "TXN00017": {
            "transaction_id": "TXN00017",
            "risk_category": "SUSPICIOUS",
            "risk_score": 0.45,
            "explanation": (
                "This wheat shipment involves a company with a very high risk score of 0.93, "
                "indicating a history of suspicious activity. The trade price is 19% above "
                "market value ($358 vs $300 per ton), suggesting potential invoice fraud or "
                "kickback schemes. The combination of overpricing and high-risk company "
                "involvement warrants detailed investigation."
            ),
            "key_indicators": [
                "Company risk score: 0.93 (Very High)",
                "Price deviation: +19.33%",
                "Trade price: $358/ton vs Market: $300/ton",
                "Product: Wheat",
                "Risk classification: SUSPICIOUS"
            ],
            "investigation_priority": "HIGH",
            "recommended_actions": [
                "Review company's transaction history",
                "Investigate pricing justification",
                "Check for related party transactions",
                "Verify quality specifications",
                "Monitor for pattern of overpricing"
            ]
        },

        "TXN00010": {
            "transaction_id": "TXN00010",
            "risk_category": "SUSPICIOUS",
            "risk_score": 0.52,
            "explanation": (
                "This transaction triggers multiple fraud indicators simultaneously. "
                "The port activity index of 1.5 indicates routing through a congested port "
                "where customs inspection is less thorough. Combined with route anomalies "
                "and elevated company risk, this suggests deliberate exploitation of "
                "overwhelmed inspection points to avoid detection."
            ),
            "key_indicators": [
                "Port activity index: 1.5 (Highly congested)",
                "Route anomaly detected",
                "Company risk score: 0.78",
                "Multiple simultaneous alerts",
                "Risk classification: SUSPICIOUS"
            ],
            "investigation_priority": "HIGH",
            "recommended_actions": [
                "Verify routing justification",
                "Check for pattern of congested port usage",
                "Inspect cargo if possible",
                "Review company's routing history",
                "Coordinate with port authorities"
            ]
        },
        "TXN00452": {
            "transaction_id": "TXN00452",
            "risk_category": "SUSPICIOUS",
            "risk_score": 0.38,
            "explanation": (
                "This shipment follows an unusual route that deviates from standard "
                "shipping lanes. Route anomalies often indicate attempts to avoid "
                "inspection at major customs checkpoints or to obscure the true origin "
                "or destination of goods. This pattern requires investigation to rule "
                "out sanctions evasion or smuggling."
            ),
            "key_indicators": [
                "Route anomaly: Yes",
                "Non-standard shipping route",
                "Distance: Longer than typical",
                "Risk classification: SUSPICIOUS"
            ],
            "investigation_priority": "MEDIUM",
            "recommended_actions": [
                "Verify route justification",
                "Check intermediate ports",
                "Review shipping documentation",
                "Investigate for sanctions evasion",
                "Monitor for repeated pattern"
            ]
        }
    }
    
    # Save to file
    output_path = Path("docs/demo_explanations.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(explanations, f, indent=2)
    
    print(f"✅ Generated demo explanations: {output_path}")
    return explanations


def generate_demo_statistics():
    """Generate demo statistics summary."""
    
    try:
        # Load and process data
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        df = load_dataset(dataset_path)
        df = engineer_features(df)
        
        # Load model and score
        model = load_fraud_detector()
        df = score_transactions(df, model)
        df = classify_risk(df)
        
        # Calculate statistics
        stats = {
            "total_transactions": len(df),
            "fraud_cases": len(df[df['risk_category'] == 'FRAUD']),
            "suspicious_cases": len(df[df['risk_category'] == 'SUSPICIOUS']),
            "safe_cases": len(df[df['risk_category'] == 'SAFE']),
            "fraud_rate": f"{(len(df[df['risk_category'] == 'FRAUD']) / len(df) * 100):.2f}%",
            "avg_risk_score": f"{df['risk_score'].mean():.3f}",
            "high_risk_transactions": len(df[df['risk_score'] > 0.5]),
            "key_demo_transactions": {
                "TXN00006": {
                    "product": "Crude Oil",
                    "price_deviation": "-73.12%",
                    "risk_category": "FRAUD"
                },
                "TXN00017": {
                    "product": "Wheat",
                    "price_deviation": "+19.33%",
                    "risk_category": "SUSPICIOUS"
                },
                "TXN00010": {
                    "product": "Electronics",
                    "alerts": "Multiple",
                    "risk_category": "SUSPICIOUS"
                }
            }
        }
        
        # Save to file
        output_path = Path("docs/demo_statistics.json")
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✅ Generated demo statistics: {output_path}")
        return stats
        
    except Exception as e:
        print(f"⚠️ Could not generate statistics: {e}")
        print("   This is normal if the system hasn't been started yet.")
        return None


def generate_quick_reference():
    """Generate quick reference data for demo."""
    
    quick_ref = {
        "demo_flow": {
            "1_overview": "Show KPI metrics and fraud rate",
            "2_alerts": "Highlight critical fraud alerts",
            "3_transaction": "Investigate TXN00006 (extreme fraud)",
            "4_explanation": "Get AI explanation for fraud indicators",
            "5_visualizations": "Show route map and company network",
            "6_ai_assistant": "Ask investigation questions"
        },
        "key_talking_points": [
            "11.7% fraud rate detected across 1,000 transactions",
            "AI-powered explanations using Google Gemini",
            "Real-time fraud detection with IsolationForest ML",
            "Multi-factor risk scoring (price, route, company, port)",
            "Interactive visualizations for pattern analysis",
            "RESTful API for system integration"
        ],
        "demo_transactions": {
            "extreme_fraud": "TXN00006",
            "high_risk_company": "TXN00017",
            "multiple_alerts": "TXN00010",
            "route_anomaly": "TXN00452"
        },
        "backup_plans": {
            "gemini_fails": "Use fallback explanations (automatic)",
            "dashboard_slow": "Switch to demo mode (500 rows)",
            "system_crash": "Use backup instance on port 8502",
            "network_down": "System works offline (local data)"
        },
        "emergency_commands": {
            "restart_all": "pkill -f python && python main.py",
            "restart_api": "pkill -f uvicorn && python -m uvicorn backend.api:app --port 8000 &",
            "restart_dashboard": "pkill -f streamlit && streamlit run frontend/dashboard.py &"
        }
    }
    
    # Save to file
    output_path = Path("docs/demo_quick_reference.json")
    with open(output_path, 'w') as f:
        json.dump(quick_ref, f, indent=2)
    
    print(f"✅ Generated quick reference: {output_path}")
    return quick_ref


def create_demo_directories():
    """Create necessary directories for demo materials."""
    
    directories = [
        "docs/demo_screenshots/dashboard",
        "docs/demo_screenshots/api",
        "data/backup",
        "models/backup"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created demo directories")


def main():
    """Main function to generate all demo materials."""
    
    print("🎬 Generating Demo Materials for TRINETRA AI")
    print("=" * 60)
    
    # Create directories
    create_demo_directories()
    
    # Generate explanations
    print("\n📝 Generating pre-written explanations...")
    explanations = generate_demo_explanations()
    print(f"   Generated {len(explanations)} transaction explanations")
    
    # Generate statistics
    print("\n📊 Generating demo statistics...")
    stats = generate_demo_statistics()
    if stats:
        print(f"   Total transactions: {stats['total_transactions']}")
        print(f"   Fraud rate: {stats['fraud_rate']}")
    
    # Generate quick reference
    print("\n📋 Generating quick reference...")
    quick_ref = generate_quick_reference()
    print(f"   Created quick reference with {len(quick_ref)} sections")
    
    print("\n" + "=" * 60)
    print("✅ Demo materials generation complete!")
    print("\nGenerated files:")
    print("  - docs/demo_explanations.json")
    print("  - docs/demo_statistics.json")
    print("  - docs/demo_quick_reference.json")
    print("\nNext steps:")
    print("  1. Review generated explanations")
    print("  2. Take screenshots of dashboard (save to docs/demo_screenshots/)")
    print("  3. Record demo video (save to docs/demo_video.mp4)")
    print("  4. Test backup plans before actual demo")
    print("\nFor backup plans, see: docs/DEMO_BACKUP_PLANS.md")


if __name__ == "__main__":
    main()
