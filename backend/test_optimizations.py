"""
Test script for memory optimizations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.optimizations import (
    optimize_dataframe_dtypes,
    get_optimized_model_params,
    get_memory_usage_report
)
from backend.data_loader import load_dataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_dtype_optimization():
    """Test DataFrame dtype optimization."""
    logger.info("=" * 80)
    logger.info("Testing DataFrame Dtype Optimization")
    logger.info("=" * 80)
    
    # Load dataset
    df = load_dataset("data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
    
    # Get memory report before optimization
    logger.info("\nBEFORE OPTIMIZATION:")
    report_before = get_memory_usage_report(df)
    logger.info(f"  Total Memory: {report_before['total_memory_mb']:.2f} MB")
    logger.info(f"  Memory per Row: {report_before['memory_per_row_kb']:.2f} KB")
    logger.info(f"  Top Memory Columns: {report_before['top_memory_columns']}")
    
    # Optimize dtypes
    df_optimized = optimize_dataframe_dtypes(df)
    
    # Get memory report after optimization
    logger.info("\nAFTER OPTIMIZATION:")
    report_after = get_memory_usage_report(df_optimized)
    logger.info(f"  Total Memory: {report_after['total_memory_mb']:.2f} MB")
    logger.info(f"  Memory per Row: {report_after['memory_per_row_kb']:.2f} KB")
    
    # Calculate savings
    memory_saved = report_before['total_memory_mb'] - report_after['total_memory_mb']
    percent_saved = (memory_saved / report_before['total_memory_mb']) * 100
    
    logger.info("\nOPTIMIZATION RESULTS:")
    logger.info(f"  Memory Saved: {memory_saved:.2f} MB")
    logger.info(f"  Percent Saved: {percent_saved:.1f}%")
    logger.info(f"  Rows: {len(df)}")
    logger.info(f"  Columns: {len(df.columns)}")


def test_model_params():
    """Test optimized model parameter selection."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Optimized Model Parameters")
    logger.info("=" * 80)
    
    test_sizes = [500, 1000, 5000, 10000, 50000]
    
    for size in test_sizes:
        params = get_optimized_model_params(size)
        logger.info(f"\nDataset size: {size:,} rows")
        logger.info(f"  n_estimators: {params['n_estimators']}")
        logger.info(f"  max_samples: {params['max_samples']}")


if __name__ == "__main__":
    test_dtype_optimization()
    test_model_params()
    
    logger.info("\n" + "=" * 80)
    logger.info("All optimization tests completed successfully!")
    logger.info("=" * 80)
