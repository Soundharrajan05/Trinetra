"""
Example integration of model evaluation metrics in TRINETRA AI system
This demonstrates how the evaluation metrics would be used in the main application.
"""

import sys
import os
import pandas as pd

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model import train_model, save_model, load_model, evaluate_model, generate_model_report
from feature_engineering import engineer_features
from data_loader import load_dataset

def main_with_evaluation():
    """
    Example of how model evaluation would be integrated into the main TRINETRA AI pipeline
    """
    
    print("TRINETRA AI - Model Training and Evaluation Pipeline")
    print("=" * 60)
    
    # 1. Load and prepare data
    print("1. Loading dataset...")
    df = load_dataset("../data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
    
    # 2. Engineer features
    print("2. Engineering features...")
    df = engineer_features(df)
    
    # 3. Train model
    print("3. Training IsolationForest model...")
    model = train_model(df)
    
    # 4. Save model
    print("4. Saving trained model...")
    os.makedirs("../models", exist_ok=True)
    save_model(model, "../models/isolation_forest_with_evaluation.pkl")
    
    # 5. Evaluate model performance
    print("5. Evaluating model performance...")
    feature_columns = [
        'price_anomaly_score',
        'route_risk_score', 
        'company_network_risk',
        'port_congestion_score',
        'shipment_duration_risk',
        'volume_spike_score'
    ]
    X = df[feature_columns]
    
    # Get comprehensive evaluation metrics
    evaluation_results = evaluate_model(model, X)
    
    # 6. Display key metrics
    print("6. Key Performance Metrics:")
    print("-" * 30)
    
    model_info = evaluation_results['model_info']
    performance = evaluation_results['performance_metrics']
    anomaly_analysis = evaluation_results['anomaly_analysis']
    feature_analysis = evaluation_results['feature_analysis']
    
    print(f"Model Configuration:")
    print(f"  • Estimators: {model_info['n_estimators']}")
    print(f"  • Expected Contamination: {model_info['contamination']}")
    print(f"  • Features Used: {model_info['n_features']}")
    
    print(f"\nPerformance:")
    print(f"  • Prediction Speed: {performance['predictions_per_second']:.0f} predictions/sec")
    print(f"  • Processing Time: {performance['prediction_time_seconds']} seconds")
    
    print(f"\nAnomaly Detection Results:")
    print(f"  • Anomalies Detected: {anomaly_analysis['predicted_anomalies']}")
    print(f"  • Normal Transactions: {anomaly_analysis['predicted_normal']}")
    print(f"  • Actual Contamination Rate: {anomaly_analysis['actual_contamination_rate']:.1%}")
    print(f"  • Model Quality (Silhouette): {anomaly_analysis.get('silhouette_score', 'N/A')}")
    
    if 'feature_importance_scores' in feature_analysis:
        print(f"\nFeature Importance:")
        print(f"  • Most Critical Feature: {feature_analysis['most_important_feature']}")
        print(f"  • Top 3 Features:")
        for i, (feature, importance) in enumerate(feature_analysis['feature_ranking'][:3]):
            print(f"    {i+1}. {feature}: {importance:.1%}")
    
    # 7. Generate and save detailed report
    print("\n7. Generating detailed evaluation report...")
    report = generate_model_report(model, X)
    
    # Save report with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"../logs/model_evaluation_report_{timestamp}.txt"
    
    os.makedirs("../logs", exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"   Report saved to: {report_path}")
    
    # 8. Model validation checks
    print("\n8. Model Validation:")
    print("-" * 20)
    
    # Check if contamination rate is reasonable
    actual_contamination = anomaly_analysis['actual_contamination_rate']
    expected_contamination = model_info['contamination']
    contamination_diff = abs(actual_contamination - expected_contamination)
    
    if contamination_diff < 0.02:  # Within 2%
        print("✅ Contamination rate is within expected range")
    else:
        print(f"⚠️  Contamination rate deviation: {contamination_diff:.1%}")
    
    # Check silhouette score
    silhouette_score = anomaly_analysis.get('silhouette_score')
    if silhouette_score is not None:
        if silhouette_score > 0.3:
            print("✅ Good cluster separation (Silhouette > 0.3)")
        elif silhouette_score > 0.1:
            print("⚠️  Moderate cluster separation")
        else:
            print("❌ Poor cluster separation")
    
    # Check prediction speed
    if performance['predictions_per_second'] > 1000:
        print("✅ Fast prediction speed (>1000 predictions/sec)")
    else:
        print("⚠️  Consider optimizing prediction speed")
    
    print("\n" + "=" * 60)
    print("Model training and evaluation completed successfully!")
    print(f"Model saved to: ../models/isolation_forest_with_evaluation.pkl")
    print(f"Evaluation report: {report_path}")
    
    return model, evaluation_results

if __name__ == "__main__":
    try:
        model, evaluation = main_with_evaluation()
        print("\n🎉 Pipeline completed successfully!")
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()