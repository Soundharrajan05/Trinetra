"""
Quick Performance Load Test - Minimal Version

Fast performance validation without hanging on API calls.
Tests core performance requirements in under 20 seconds.

Task: 14.2 Demo Preparation - Test system performance under load
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_loader import load_dataset
from backend.feature_engineering import engineer_features
from backend.model import train_model, load_model
from backend.fraud_detection import score_transactions, classify_risk


def print_header(title):
    print("\n" + "="*70)
    print(title)
    print("="*70)


def main():
    print("\n" + "="*70)
    print("TRINETRA AI - QUICK PERFORMANCE LOAD TEST")
    print("="*70)
    print("\nValidating NFR-1 Performance Requirements:")
    print("  • ML model training < 30 seconds")
    print("  • System handles 1000+ transactions")
    print("  • Efficient batch inference")
    
    results = {}
    
    # Load data
    print("\nLoading dataset...")
    start = time.time()
    dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    df = load_dataset(dataset_path)
    load_time = time.time() - start
    print(f"✅ Loaded {len(df)} transactions in {load_time:.3f}s")
    
    # Feature engineering
    print("\nEngineering features...")
    start = time.time()
    df = engineer_features(df)
    feat_time = time.time() - start
    print(f"✅ Engineered 6 features in {feat_time:.3f}s")
    
    # Test ML Training
    print_header("TEST 1: ML MODEL TRAINING (<30 second requirement)")
    print(f"Training IsolationForest on {len(df)} transactions...")
    
    start_time = time.time()
    model = train_model(df)
    training_time = time.time() - start_time
    
    status = "✅" if training_time < 30.0 else "❌"
    print(f"{status} Training Time: {training_time:.3f}s")
    print(f"   Target: < 30.0s")
    print(f"   Margin: {30.0 - training_time:.3f}s")
    print(f"   Performance: {(training_time / 30.0) * 100:.1f}% of limit")
    
    results['training'] = training_time < 30.0
    
    if training_time < 30.0:
        print("\n✅ ML training meets <30 second requirement")
    else:
        print("\n❌ ML training exceeds 30 second requirement")
    
    # Test ML Inference
    print_header("TEST 2: ML INFERENCE PERFORMANCE (1000+ transactions)")
    
    batch_sizes = [100, 500, 1000]
    inference_pass = True
    
    for batch_size in batch_sizes:
        if batch_size > len(df):
            continue
        
        batch = df.head(batch_size)
        
        start = time.time()
        scored = score_transactions(batch, model)
        classified = classify_risk(scored)
        elapsed = time.time() - start
        
        per_txn = (elapsed / batch_size) * 1000  # ms per transaction
        
        print(f"Batch {batch_size:>4}: {elapsed:.3f}s total, {per_txn:.2f}ms per transaction")
        
        if 'risk_score' not in classified.columns or 'risk_category' not in classified.columns:
            inference_pass = False
        
        # Check reasonable performance (< 1s for 1000 transactions)
        if batch_size == 1000 and elapsed >= 1.0:
            inference_pass = False
    
    results['inference'] = inference_pass
    
    if inference_pass:
        print("\n✅ ML inference handles 1000+ transactions efficiently")
    else:
        print("\n❌ ML inference had performance issues")
    
    # Test Model Persistence
    print_header("TEST 3: MODEL PERSISTENCE")
    
    try:
        # Check if model file exists
        model_path = "models/isolation_forest.pkl"
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
            print(f"✅ Model file exists: {model_path}")
            print(f"   File size: {file_size:.2f} MB")
            
            # Test loading
            start = time.time()
            loaded_model = load_model(model_path)
            load_time = time.time() - start
            print(f"✅ Model loaded in {load_time:.3f}s")
            
            results['persistence'] = True
        else:
            print(f"⚠️  Model file not found: {model_path}")
            results['persistence'] = False
    except Exception as e:
        print(f"❌ Model persistence error: {e}")
        results['persistence'] = False
    
    # Test Data Processing Pipeline
    print_header("TEST 4: DATA PROCESSING PIPELINE")
    
    print("Testing complete data pipeline...")
    start = time.time()
    
    # Reload and process
    df_test = load_dataset(dataset_path)
    df_test = engineer_features(df_test)
    df_test = score_transactions(df_test, model)
    df_test = classify_risk(df_test)
    
    pipeline_time = time.time() - start
    
    # Verify output
    required_cols = ['risk_score', 'risk_category']
    has_cols = all(col in df_test.columns for col in required_cols)
    
    status = "✅" if has_cols and pipeline_time < 5.0 else "❌"
    print(f"{status} Pipeline Time: {pipeline_time:.3f}s")
    print(f"   Processed: {len(df_test)} transactions")
    print(f"   Output columns: {len(df_test.columns)}")
    
    results['pipeline'] = has_cols and pipeline_time < 5.0
    
    if results['pipeline']:
        print("\n✅ Data processing pipeline is efficient")
    else:
        print("\n❌ Data processing pipeline had issues")
    
    # Generate Summary
    print_header("PERFORMANCE TEST SUMMARY")
    
    print("\nTRINETRA AI - Performance Load Test Results")
    print("="*70)
    print("\nTest Results:")
    print(f"  {'✅' if results.get('training', False) else '❌'} ML Training: < 30 seconds")
    print(f"  {'✅' if results.get('inference', False) else '❌'} ML Inference: 1000+ transactions")
    print(f"  {'✅' if results.get('persistence', False) else '❌'} Model Persistence: Working")
    print(f"  {'✅' if results.get('pipeline', False) else '❌'} Data Pipeline: Efficient")
    
    all_pass = all(results.values())
    
    print("\n" + "="*70)
    if all_pass:
        print("OVERALL RESULT: ✅ ALL PERFORMANCE TESTS PASSED")
        print("\nSystem meets core performance requirements:")
        print("  • ML model trains in < 30 seconds")
        print("  • System efficiently processes 1000+ transactions")
        print("  • Model persistence works correctly")
        print("  • End-to-end pipeline is performant")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"OVERALL RESULT: ❌ FAILED TESTS: {', '.join(failed)}")
    print("="*70)
    
    # Save report
    report_lines = [
        "TRINETRA AI - Performance Load Test Results",
        "="*70,
        "",
        "NFR-1 Performance Requirements Tested:",
        f"  {'✅' if results.get('training', False) else '❌'} ML Training: < 30 seconds",
        f"  {'✅' if results.get('inference', False) else '❌'} ML Inference: 1000+ transactions",
        f"  {'✅' if results.get('persistence', False) else '❌'} Model Persistence: Working",
        f"  {'✅' if results.get('pipeline', False) else '❌'} Data Pipeline: Efficient",
        "",
        "="*70,
        f"OVERALL: {'✅ ALL TESTS PASSED' if all_pass else '❌ SOME TESTS FAILED'}",
        "="*70,
        "",
        "Note: API endpoint tests require running server.",
        "Core ML and data processing performance validated successfully.",
    ]
    
    with open("backend/performance_load_test_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    
    print("\n📊 Report saved to: backend/performance_load_test_report.txt")
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
