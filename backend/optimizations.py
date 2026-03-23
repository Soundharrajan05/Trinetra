"""
Memory and Performance Optimizations for TRINETRA AI

This module contains optimization utilities to reduce memory usage and improve
performance across the fraud detection system.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def optimize_dataframe_dtypes(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Optimize DataFrame data types to reduce memory usage.
    
    This function:
    - Converts low-cardinality object columns to category
    - Downcasts numeric types to smaller representations
    - Preserves data integrity while reducing memory footprint
    
    Args:
        df: DataFrame to optimize
        verbose: Whether to log optimization details
        
    Returns:
        Optimized DataFrame with reduced memory usage
    """
    if df is None or df.empty:
        return df
    
    # Calculate initial memory usage
    initial_memory = df.memory_usage(deep=True).sum() / (1024 * 1024)
    
    if verbose:
        logger.info(f"Optimizing DataFrame dtypes...")
        logger.info(f"  Initial memory: {initial_memory:.2f} MB")
    
    df_optimized = df.copy()
    
    for col in df_optimized.columns:
        col_type = df_optimized[col].dtype
        
        # Optimize object/string columns
        if col_type == 'object':
            num_unique = df_optimized[col].nunique()
            num_total = len(df_optimized[col])
            
            # Convert to category if cardinality is low (< 50% unique values)
            if num_unique / num_total < 0.5:
                df_optimized[col] = df_optimized[col].astype('category')
                if verbose:
                    logger.info(f"  {col}: object → category ({num_unique} unique values)")
        
        # Downcast float columns
        elif col_type == 'float64':
            # Check if values fit in float32
            col_min = df_optimized[col].min()
            col_max = df_optimized[col].max()
            
            # float32 range: ±3.4e38
            if col_min > -3.4e38 and col_max < 3.4e38:
                df_optimized[col] = df_optimized[col].astype('float32')
                if verbose:
                    logger.info(f"  {col}: float64 → float32")
        
        # Downcast integer columns
        elif col_type == 'int64':
            col_min = df_optimized[col].min()
            col_max = df_optimized[col].max()
            
            # Try int8 (-128 to 127)
            if col_min >= -128 and col_max <= 127:
                df_optimized[col] = df_optimized[col].astype('int8')
                if verbose:
                    logger.info(f"  {col}: int64 → int8")
            # Try int16 (-32768 to 32767)
            elif col_min >= -32768 and col_max <= 32767:
                df_optimized[col] = df_optimized[col].astype('int16')
                if verbose:
                    logger.info(f"  {col}: int64 → int16")
            # Try int32
            elif col_min >= -2147483648 and col_max <= 2147483647:
                df_optimized[col] = df_optimized[col].astype('int32')
                if verbose:
                    logger.info(f"  {col}: int64 → int32")
    
    # Calculate final memory usage
    final_memory = df_optimized.memory_usage(deep=True).sum() / (1024 * 1024)
    memory_saved = initial_memory - final_memory
    percent_saved = (memory_saved / initial_memory) * 100
    
    if verbose:
        logger.info(f"  Final memory: {final_memory:.2f} MB")
        logger.info(f"  Memory saved: {memory_saved:.2f} MB ({percent_saved:.1f}%)")
    
    return df_optimized


def get_optimized_model_params(dataset_size: int) -> Dict[str, Any]:
    """
    Get optimized model parameters based on dataset size.
    
    Args:
        dataset_size: Number of rows in the dataset
        
    Returns:
        Dictionary of optimized model parameters
    """
    # Base parameters
    params = {
        'contamination': 0.1,
        'random_state': 42,
        'n_jobs': -1
    }
    
    # Adjust n_estimators based on dataset size
    if dataset_size < 1000:
        params['n_estimators'] = 50
        params['max_samples'] = min(256, dataset_size)
    elif dataset_size < 5000:
        params['n_estimators'] = 75
        params['max_samples'] = 512
    elif dataset_size < 10000:
        params['n_estimators'] = 100
        params['max_samples'] = 1024
    else:
        params['n_estimators'] = 100
        params['max_samples'] = 2048
    
    logger.info(f"Optimized model params for {dataset_size} rows:")
    logger.info(f"  n_estimators: {params['n_estimators']}")
    logger.info(f"  max_samples: {params['max_samples']}")
    
    return params


def load_dataset_chunked(file_path: str, chunk_size: int = 10000, 
                        optimize_dtypes: bool = True) -> pd.DataFrame:
    """
    Load large datasets in chunks to reduce memory footprint.
    
    Args:
        file_path: Path to CSV file
        chunk_size: Number of rows per chunk
        optimize_dtypes: Whether to optimize data types
        
    Returns:
        Complete DataFrame loaded efficiently
    """
    logger.info(f"Loading dataset in chunks of {chunk_size} rows...")
    
    chunks = []
    total_rows = 0
    
    for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size)):
        total_rows += len(chunk)
        
        # Optimize dtypes if requested
        if optimize_dtypes:
            chunk = optimize_dataframe_dtypes(chunk, verbose=False)
        
        chunks.append(chunk)
        
        if (i + 1) % 10 == 0:
            logger.info(f"  Loaded {total_rows} rows...")
    
    logger.info(f"Concatenating {len(chunks)} chunks...")
    df = pd.concat(chunks, ignore_index=True)
    
    logger.info(f"Dataset loaded: {len(df)} rows")
    return df


def reduce_dataframe_memory(df: pd.DataFrame, 
                           columns_to_drop: Optional[list] = None) -> pd.DataFrame:
    """
    Reduce DataFrame memory by dropping unnecessary columns and optimizing types.
    
    Args:
        df: DataFrame to optimize
        columns_to_drop: List of column names to drop (optional)
        
    Returns:
        Optimized DataFrame
    """
    df_reduced = df.copy()
    
    # Drop specified columns
    if columns_to_drop:
        existing_cols = [col for col in columns_to_drop if col in df_reduced.columns]
        if existing_cols:
            df_reduced = df_reduced.drop(columns=existing_cols)
            logger.info(f"Dropped {len(existing_cols)} columns: {existing_cols}")
    
    # Optimize remaining columns
    df_reduced = optimize_dataframe_dtypes(df_reduced)
    
    return df_reduced


def get_memory_usage_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate detailed memory usage report for a DataFrame.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary with memory usage statistics
    """
    memory_usage = df.memory_usage(deep=True)
    total_memory = memory_usage.sum() / (1024 * 1024)
    
    # Get per-column memory usage
    column_memory = {}
    for col in df.columns:
        col_memory = memory_usage[col] / (1024 * 1024)
        column_memory[col] = {
            'memory_mb': col_memory,
            'dtype': str(df[col].dtype),
            'percent': (col_memory / total_memory) * 100
        }
    
    # Sort by memory usage
    sorted_columns = sorted(column_memory.items(), 
                          key=lambda x: x[1]['memory_mb'], 
                          reverse=True)
    
    report = {
        'total_memory_mb': total_memory,
        'num_rows': len(df),
        'num_columns': len(df.columns),
        'memory_per_row_kb': (total_memory * 1024) / len(df) if len(df) > 0 else 0,
        'columns': dict(sorted_columns[:10]),  # Top 10 memory consumers
        'top_memory_columns': [col for col, _ in sorted_columns[:5]]
    }
    
    return report


def optimize_model_memory(model, keep_training_data: bool = False):
    """
    Optimize model memory by removing unnecessary training artifacts.
    
    Args:
        model: Trained model to optimize
        keep_training_data: Whether to keep training data (default: False)
        
    Returns:
        Optimized model
    """
    # For IsolationForest, we can't remove much without breaking functionality
    # But we can document what's taking space
    
    if hasattr(model, 'estimators_'):
        n_estimators = len(model.estimators_)
        logger.info(f"Model contains {n_estimators} estimators")
    
    # Note: Removing estimators would break the model
    # This function is mainly for documentation and future optimization
    
    return model


def benchmark_memory_usage(func, *args, **kwargs):
    """
    Benchmark memory usage of a function.
    
    Args:
        func: Function to benchmark
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (result, memory_delta_mb)
    """
    import tracemalloc
    import psutil
    
    process = psutil.Process()
    
    # Start tracking
    tracemalloc.start()
    mem_before = process.memory_info().rss / (1024 * 1024)
    
    # Execute function
    result = func(*args, **kwargs)
    
    # Get memory usage
    mem_after = process.memory_info().rss / (1024 * 1024)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    memory_delta = mem_after - mem_before
    
    logger.info(f"Function {func.__name__} memory usage:")
    logger.info(f"  Memory delta: {memory_delta:+.2f} MB")
    logger.info(f"  Peak traced: {peak / (1024 * 1024):.2f} MB")
    
    return result, memory_delta


# Optimization presets for different scenarios
OPTIMIZATION_PRESETS = {
    'minimal': {
        'optimize_dtypes': True,
        'drop_intermediate_columns': False,
        'use_chunked_loading': False,
        'model_estimators': 100
    },
    'balanced': {
        'optimize_dtypes': True,
        'drop_intermediate_columns': True,
        'use_chunked_loading': False,
        'model_estimators': 75
    },
    'aggressive': {
        'optimize_dtypes': True,
        'drop_intermediate_columns': True,
        'use_chunked_loading': True,
        'model_estimators': 50
    }
}


def apply_optimization_preset(preset_name: str = 'balanced') -> Dict[str, Any]:
    """
    Get optimization settings for a given preset.
    
    Args:
        preset_name: Name of preset ('minimal', 'balanced', 'aggressive')
        
    Returns:
        Dictionary of optimization settings
    """
    if preset_name not in OPTIMIZATION_PRESETS:
        logger.warning(f"Unknown preset '{preset_name}', using 'balanced'")
        preset_name = 'balanced'
    
    preset = OPTIMIZATION_PRESETS[preset_name]
    logger.info(f"Applied '{preset_name}' optimization preset")
    
    return preset.copy()


if __name__ == "__main__":
    # Test optimizations
    print("TRINETRA AI - Memory Optimization Utilities")
    print("=" * 60)
    
    # Example usage
    print("\nOptimization Presets:")
    for preset_name in OPTIMIZATION_PRESETS:
        preset = apply_optimization_preset(preset_name)
        print(f"\n{preset_name.upper()}:")
        for key, value in preset.items():
            print(f"  {key}: {value}")
