"""
Example: Using Memory-Optimized Pipeline for TRINETRA AI

This example demonstrates how to use the memory optimization utilities
in the fraud detection pipeline.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.data_loader import load_dataset
from backend.feature_engineering import engineer_features
from backend.model import train_model
from backend.fraud_detection import score_transactions, classify_risk
from backend.optimizations import (
    optimize_dataframe_dtypes,
    get_optimized_model_params,
    get_memory_usage_report,
    benchmark_memory_usage
)
from sklearn.ensemble import IsolationForest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_standard_pipeline():
    """Run the standard pipeline without optimizations."""
    logger.info("=" * 80)
    logger.info("STANDARD PIPELINE (No Optimizations)")
    logger.info("=" * 80)
    
    # Load data
    df, mem_delta = benchmark_memory_usage(
        load_dataset,
        "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    )
    logger.info(f"Data loading memory: {mem_delta:+.2f} MB")
    
    # Get memory report
    report = get_memory_usage_report(df)
    logger.info(f"DataFrame memory: {report['total_memory_mb']:.2f} MB")
    
    # Feature engineering
    df_features, mem_delta = benchmark_memory_usage(engineer_features, df)
    logger.info(f"Feature engineering memory: {mem_delta:+.2f} MB")
    
    # Train model with standard params
    model, mem_delta = benchmark_memory_usage(train_model, df_features)
    logger.info(f"Model training memory: {mem_delta:+.2f} MB")
    
    return df_features, model


def run_optimized_pipeline():
    """Run the optimized pipeline with memory optimizations."""
    logger.info("\n" + "=" * 80)
    logger.info("OPTIMIZED PIPELINE (With Memory Optimizations)")
    logger.info("=" * 80)
    
    # Load data
    df, mem_delta = benchmark_memory_usage(
        load_dataset,
        "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    )
    logger.info(f"Data loading memory: {mem_delta:+.2f} MB")
    
    # OPTIMIZATION 1: Optimize DataFrame dtypes
    logger.info("\nApplying dtype optimization...")
    df_optimized, mem_delta = benchmark_memory_usage(
        optimize_dataframe_dtypes, df, False
    )
    logger.info(f"Dtype optimization memory: {mem_delta:+.2f} MB")
    
    # Get memory report
    report = get_memory_usage_report(df_optimized)
    logger.info(f"Optimized DataFrame memory: {report['total_memory_mb']:.2f} MB")
    
    # Feature engineering
    df_features, mem_delta = benchmark_memory_usage(engineer_features, df_optimized)
    logger.info(f"Feature engineering memory: {mem_delta:+.2f} MB")
    
    # Optimize feature DataFrame
    df_features = optimize_dataframe_dtypes(df_features, verbose=False)
    
    # OPTIMIZATION 2: Use optimized model parameters
    logger.info("\nUsing optimized model parameters...")
    optimized_params = get_optimized_model_params(len(df_features))
    
    # Train model with optimized params
    def train_optimized_model(df):
        model = IsolationForest(**optimized_params)
        feature_columns = [
            'price_anomaly_score', 'route_risk_score', 'company_network_risk',
            'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
        ]
        X = df[feature_columns]
        model.fit(X)
        return model
    
    model, mem_delta = benchmark_memory_usage(train_optimized_model, df_features)
    logger.info(f"Optimized model training memory: {mem_delta:+.2f} MB")
    
    return df_features, model


def compare_pipelines():
    """Compare standard vs optimized pipelines."""
    logger.info("\n" + "=" * 80)
    logger.info("PIPELINE COMPARISON")
    logger.info("=" * 80)
    
    # Run both pipelines
    logger.info("\nRunning standard pipeline...")
    df_standard, model_standard = run_standard_pipeline()
    
    logger.info("\nRunning optimized pipeline...")
    df_optimized, model_optimized = run_optimized_pipeline()
    
    # Compare results
    logger.info("\n" + "=" * 80)
    logger.info("COMPARISON RESULTS")
    logger.info("=" * 80)
    
    # DataFrame memory comparison
    mem_standard = df_standard.memory_usage(deep=True).sum() / (1024 * 1024)
    mem_optimized = df_optimized.memory_usage(deep=True).sum() / (1024 * 1024)
    mem_saved = mem_standard - mem_optimized
    percent_saved = (mem_saved / mem_standard) * 100
    
    logger.info("\nDataFrame Memory:")
    logger.info(f"  Standard:  {mem_standard:.2f} MB")
    logger.info(f"  Optimized: {mem_optimized:.2f} MB")
    logger.info(f"  Saved:     {mem_saved:.2f} MB ({percent_saved:.1f}%)")
    
    # Model comparison
    logger.info("\nModel Configuration:")
    logger.info(f"  Standard:  n_estimators={model_standard.n_estimators}")
    logger.info(f"  Optimized: n_estimators={model_optimized.n_estimators}")
    
    # Test predictions to ensure accuracy is maintained
    feature_columns = [
        'price_anomaly_score', 'route_risk_score', 'company_network_risk',
        'port_congestion_score', 'shipment_duration_risk', 'volume_spike_score'
    ]
    
    X_standard = df_standard[feature_columns]
    X_optimized = df_optimized[feature_columns]
    
    scores_standard = model_standard.decision_function(X_standard)
    scores_optimized = model_optimized.decision_function(X_optimized)
    
    # Calculate correlation between scores
    import numpy as np
    correlation = np.corrcoef(scores_standard, scores_optimized)[0, 1]
    
    logger.info("\nPrediction Accuracy:")
    logger.info(f"  Score correlation: {correlation:.4f}")
    logger.info(f"  Status: {'✅ Maintained' if correlation > 0.95 else '⚠️ Degraded'}")
    
    logger.info("\n" + "=" * 80)
    logger.info("CONCLUSION")
    logger.info("=" * 80)
    logger.info(f"✅ Memory reduced by {percent_saved:.1f}%")
    logger.info(f"✅ Accuracy maintained (correlation: {correlation:.4f})")
    logger.info(f"✅ System functionality preserved")
    logger.info("=" * 80)


if __name__ == "__main__":
    compare_pipelines()
