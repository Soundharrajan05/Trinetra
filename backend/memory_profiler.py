"""
Memory Profiler for TRINETRA AI Trade Fraud Detection System

This module profiles memory usage across all system components and identifies
optimization opportunities.
"""

import tracemalloc
import psutil
import pandas as pd
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MemoryProfiler:
    """Memory profiling utility for TRINETRA AI system."""
    
    def __init__(self):
        """Initialize the memory profiler."""
        self.results = []
        self.process = psutil.Process()
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        mem_info = self.process.memory_info()
        return {
            'rss_mb': mem_info.rss / (1024 * 1024),  # Resident Set Size
            'vms_mb': mem_info.vms / (1024 * 1024),  # Virtual Memory Size
        }
    
    def profile_function(self, func, *args, **kwargs) -> Tuple[Any, Dict[str, Any]]:
        """
        Profile memory usage of a function.
        
        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Tuple of (function result, profiling stats)
        """
        # Start memory tracking
        tracemalloc.start()
        mem_before = self.get_memory_usage()
        time_start = time.time()
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Get memory statistics
        time_elapsed = time.time() - time_start
        mem_after = self.get_memory_usage()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        stats = {
            'function': func.__name__,
            'time_seconds': time_elapsed,
            'memory_before_mb': mem_before['rss_mb'],
            'memory_after_mb': mem_after['rss_mb'],
            'memory_delta_mb': mem_after['rss_mb'] - mem_before['rss_mb'],
            'peak_traced_mb': peak / (1024 * 1024),
            'current_traced_mb': current / (1024 * 1024),
        }
        
        self.results.append(stats)
        return result, stats
    
    def get_dataframe_memory(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get detailed memory usage of a DataFrame."""
        memory_usage = df.memory_usage(deep=True)
        return {
            'total_mb': memory_usage.sum() / (1024 * 1024),
            'index_mb': memory_usage.iloc[0] / (1024 * 1024),
            'columns_mb': {col: memory_usage[col] / (1024 * 1024) 
                          for col in df.columns},
            'shape': df.shape,
            'dtypes': df.dtypes.to_dict()
        }
    
    def generate_report(self) -> str:
        """Generate a memory profiling report."""
        report = []
        report.append("=" * 80)
        report.append("TRINETRA AI - MEMORY PROFILING REPORT")
        report.append("=" * 80)
        report.append("")
        
        if not self.results:
            report.append("No profiling data available.")
            return "\n".join(report)
        
        # Summary statistics
        total_time = sum(r['time_seconds'] for r in self.results)
        max_memory = max(r['memory_after_mb'] for r in self.results)
        
        report.append("SUMMARY:")
        report.append(f"  Total profiled functions: {len(self.results)}")
        report.append(f"  Total execution time: {total_time:.2f} seconds")
        report.append(f"  Peak memory usage: {max_memory:.2f} MB")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("")
        
        for i, stats in enumerate(self.results, 1):
            report.append(f"{i}. {stats['function']}")
            report.append(f"   Time: {stats['time_seconds']:.3f}s")
            report.append(f"   Memory Before: {stats['memory_before_mb']:.2f} MB")
            report.append(f"   Memory After: {stats['memory_after_mb']:.2f} MB")
            report.append(f"   Memory Delta: {stats['memory_delta_mb']:+.2f} MB")
            report.append(f"   Peak Traced: {stats['peak_traced_mb']:.2f} MB")
            report.append("")
        
        # Identify memory hotspots
        report.append("MEMORY HOTSPOTS:")
        sorted_by_delta = sorted(self.results, key=lambda x: x['memory_delta_mb'], reverse=True)
        for i, stats in enumerate(sorted_by_delta[:5], 1):
            report.append(f"  {i}. {stats['function']}: {stats['memory_delta_mb']:+.2f} MB")
        report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)


def profile_data_loader():
    """Profile the data loader module."""
    logger.info("Profiling data_loader module...")
    profiler = MemoryProfiler()
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from backend.data_loader import load_dataset
    
    dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    
    # Profile dataset loading
    df, stats = profiler.profile_function(load_dataset, dataset_path)
    
    logger.info(f"Data Loader Stats:")
    logger.info(f"  Time: {stats['time_seconds']:.3f}s")
    logger.info(f"  Memory Delta: {stats['memory_delta_mb']:+.2f} MB")
    
    # Analyze DataFrame memory
    df_memory = profiler.get_dataframe_memory(df)
    logger.info(f"  DataFrame Memory: {df_memory['total_mb']:.2f} MB")
    logger.info(f"  DataFrame Shape: {df_memory['shape']}")
    
    return profiler, df


def profile_feature_engineering(df: pd.DataFrame):
    """Profile the feature engineering module."""
    logger.info("Profiling feature_engineering module...")
    profiler = MemoryProfiler()
    
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from backend.feature_engineering import engineer_features
    
    # Profile feature engineering
    df_engineered, stats = profiler.profile_function(engineer_features, df)
    
    logger.info(f"Feature Engineering Stats:")
    logger.info(f"  Time: {stats['time_seconds']:.3f}s")
    logger.info(f"  Memory Delta: {stats['memory_delta_mb']:+.2f} MB")
    
    # Analyze DataFrame memory
    df_memory = profiler.get_dataframe_memory(df_engineered)
    logger.info(f"  DataFrame Memory: {df_memory['total_mb']:.2f} MB")
    
    return profiler, df_engineered


def profile_model_operations(df: pd.DataFrame):
    """Profile model training and inference."""
    logger.info("Profiling model operations...")
    profiler = MemoryProfiler()
    
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from backend.model import train_model, save_model, load_model
    from backend.fraud_detection import score_transactions, classify_risk
    
    # Profile model training
    model, train_stats = profiler.profile_function(train_model, df)
    
    logger.info(f"Model Training Stats:")
    logger.info(f"  Time: {train_stats['time_seconds']:.3f}s")
    logger.info(f"  Memory Delta: {train_stats['memory_delta_mb']:+.2f} MB")
    
    # Profile model saving
    temp_model_path = "models/temp_profile_model.pkl"
    _, save_stats = profiler.profile_function(save_model, model, temp_model_path)
    
    logger.info(f"Model Save Stats:")
    logger.info(f"  Time: {save_stats['time_seconds']:.3f}s")
    logger.info(f"  Memory Delta: {save_stats['memory_delta_mb']:+.2f} MB")
    
    # Profile model loading
    loaded_model, load_stats = profiler.profile_function(load_model, temp_model_path)
    
    logger.info(f"Model Load Stats:")
    logger.info(f"  Time: {load_stats['time_seconds']:.3f}s")
    logger.info(f"  Memory Delta: {load_stats['memory_delta_mb']:+.2f} MB")
    
    # Profile scoring
    df_scored, score_stats = profiler.profile_function(score_transactions, df, loaded_model)
    
    logger.info(f"Transaction Scoring Stats:")
    logger.info(f"  Time: {score_stats['time_seconds']:.3f}s")
    logger.info(f"  Memory Delta: {score_stats['memory_delta_mb']:+.2f} MB")
    
    # Profile classification
    df_classified, classify_stats = profiler.profile_function(classify_risk, df_scored)
    
    logger.info(f"Risk Classification Stats:")
    logger.info(f"  Time: {classify_stats['time_seconds']:.3f}s")
    logger.info(f"  Memory Delta: {classify_stats['memory_delta_mb']:+.2f} MB")
    
    # Clean up temp file
    Path(temp_model_path).unlink(missing_ok=True)
    
    return profiler, df_classified


def run_full_profile():
    """Run complete memory profiling of the system."""
    logger.info("=" * 80)
    logger.info("Starting Full System Memory Profile")
    logger.info("=" * 80)
    
    all_results = []
    
    # Profile data loading
    loader_profiler, df = profile_data_loader()
    all_results.extend(loader_profiler.results)
    
    # Profile feature engineering
    fe_profiler, df_engineered = profile_feature_engineering(df)
    all_results.extend(fe_profiler.results)
    
    # Profile model operations
    model_profiler, df_final = profile_model_operations(df_engineered)
    all_results.extend(model_profiler.results)
    
    # Create combined profiler for final report
    combined_profiler = MemoryProfiler()
    combined_profiler.results = all_results
    
    # Generate and save report
    report = combined_profiler.generate_report()
    
    # Save report to file
    report_dir = Path("logs")
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / "memory_profile_report.txt"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("Memory Profiling Complete")
    logger.info(f"Report saved to: {report_file}")
    logger.info("=" * 80)
    
    # Print report to console
    print("\n" + report)
    
    return combined_profiler


if __name__ == "__main__":
    run_full_profile()
