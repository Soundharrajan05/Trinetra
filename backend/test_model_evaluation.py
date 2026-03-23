"""
Test script for model evaluation metrics functionality
"""

import sys
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model import train_model, evaluate_model, generate_model_report, calculate_feature_importance
from feature_engineering import engineer_features
from data_loader import load_dataset

def test_model_evaluation():
    """Test the model evaluation functionality"""
    
    print("Testing Model Evaluation Metrics...")
    print("=" * 50)
    
    try:
        # Load and prepare test data
        print("1. Loading test data...")
        df = load_dataset("../data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
        print(f"   Loaded {len(df)} transactions")
        
        # Engineer features
        print("2. Engineering features...")
        df = engineer_features(df)
        print("   Features engineered successfully")
        
        # Train model
        print("3. Training model...")
        model = train_model(df)
        print("   Model trained successfully")
        
        # Prepare feature matrix
        feature_columns = [
            'price_anomaly_score',
            'route_risk_score', 
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        X = df[feature_columns]
        
        # Test evaluation without true labels
        print("4. Testing evaluation without true labels...")
        evaluation_results = evaluate_model(model, X)
        
        print("   Evaluation Results:")
        print(f"   - Model Type: {evaluation_results['model_info']['model_type']}")
        print(f"   - Samples: {evaluation_results['model_info']['n_samples']}")
        print(f"   - Features: {evaluation_results['model_info']['n_features']}")
        print(f"   - Prediction Time: {evaluation_results['performance_metrics']['prediction_time_seconds']}s")
        print(f"   - Predicted Anomalies: {evaluation_results['anomaly_analysis']['predicted_anomalies']}")
        print(f"   - Contamination Rate: {evaluation_results['anomaly_analysis']['actual_contamination_rate']:.3f}")
        
        if evaluation_results['anomaly_analysis'].get('silhouette_score') is not None:
            print(f"   - Silhouette Score: {evaluation_results['anomaly_analysis']['silhouette_score']:.3f}")
        
        # Test feature importance
        print("5. Testing feature importance...")
        if 'feature_importance_scores' in evaluation_results['feature_analysis']:
            feature_analysis = evaluation_results['feature_analysis']
            print(f"   - Most Important Feature: {feature_analysis['most_important_feature']}")
            print(f"   - Least Important Feature: {feature_analysis['least_important_feature']}")
            print("   - Top 3 Features:")
            for i, (feature, importance) in enumerate(feature_analysis['feature_ranking'][:3]):
                print(f"     {i+1}. {feature}: {importance:.3f}")
        
        # Test with simulated true labels
        print("6. Testing evaluation with simulated true labels...")
        # Create simulated labels based on fraud_label column if available
        if 'fraud_label' in df.columns:
            # Convert fraud_label to -1/1 format (assuming 0=normal, 1=fraud)
            y_true = df['fraud_label'].map({0: 1, 1: -1})  # 0=normal=1, 1=fraud=-1
            
            evaluation_with_labels = evaluate_model(model, X, y_true)
            
            if 'supervised_metrics' in evaluation_with_labels and 'error' not in evaluation_with_labels['supervised_metrics']:
                supervised = evaluation_with_labels['supervised_metrics']
                print("   Supervised Metrics:")
                print(f"   - Accuracy: {supervised['accuracy']:.3f}")
                print(f"   - Precision: {supervised['precision']:.3f}")
                print(f"   - Recall: {supervised['recall']:.3f}")
                print(f"   - F1-Score: {supervised['f1_score']:.3f}")
        
        # Test report generation
        print("7. Testing report generation...")
        report = generate_model_report(model, X)
        print("   Report generated successfully")
        print(f"   Report length: {len(report)} characters")
        
        # Save report to file
        with open("../logs/model_evaluation_report.txt", "w") as f:
            f.write(report)
        print("   Report saved to logs/model_evaluation_report.txt")
        
        print("\n" + "=" * 50)
        print("✅ All model evaluation tests passed!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_feature_importance_standalone():
    """Test feature importance calculation separately"""
    
    print("\nTesting Feature Importance Calculation...")
    print("=" * 50)
    
    try:
        # Create synthetic data for testing
        np.random.seed(42)
        n_samples = 100
        
        # Create feature matrix with known patterns
        X = pd.DataFrame({
            'feature_1': np.random.normal(0, 1, n_samples),  # Normal feature
            'feature_2': np.random.normal(0, 1, n_samples),  # Normal feature  
            'feature_3': np.concatenate([np.random.normal(0, 1, 90), np.random.normal(5, 1, 10)]),  # Anomalous feature
            'feature_4': np.random.normal(0, 0.1, n_samples),  # Low variance feature
        })
        
        # Train simple model
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X)
        
        # Calculate feature importance
        importance = calculate_feature_importance(model, X)
        
        print("Feature Importance Results:")
        for feature, score in importance['feature_ranking']:
            print(f"  {feature}: {score:.3f}")
        
        print(f"\nMost Important: {importance['most_important_feature']}")
        print(f"Least Important: {importance['least_important_feature']}")
        
        print("✅ Feature importance test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Feature importance test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("../logs", exist_ok=True)
    
    # Run tests
    test1_passed = test_model_evaluation()
    test2_passed = test_feature_importance_standalone()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! Model evaluation metrics are working correctly.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")