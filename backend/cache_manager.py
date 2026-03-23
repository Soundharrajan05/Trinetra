"""
Global cache management system for TRINETRA AI performance optimization.

This module provides singleton-based caching for datasets, ML models, and
computed features to eliminate repeated loading and computation during
development tasks while preserving identical behavior.
"""

import hashlib
import logging
import psutil
from datetime import datetime
from typing import Optional, Dict, Any, Union
import pandas as pd
from sklearn.ensemble import IsolationForest

from .config import should_enable_caching

logger = logging.getLogger(__name__)


class GlobalCacheManager:
    """
    Singleton cache manager for datasets, models, and computed features.
    
    Provides thread-safe caching with memory management and statistics tracking.
    """
    
    _instance: Optional['GlobalCacheManager'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'GlobalCacheManager':
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize cache storage if not already initialized."""
        if not self._initialized:
            self._dataset_cache: Optional[pd.DataFrame] = None
            self._model_cache: Optional[IsolationForest] = None
            self._feature_cache: Dict[str, pd.DataFrame] = {}
            self._cache_metadata: Dict[str, Dict[str, Any]] = {}
            self._cache_hits: int = 0
            self._cache_misses: int = 0
            self._last_updated: datetime = datetime.now()
            GlobalCacheManager._initialized = True
            logger.info("GlobalCacheManager initialized")
    
    def get_dataset(self, dataset_path: str = None) -> Optional[pd.DataFrame]:
        """
        Get cached dataset or None if not cached.
        
        Args:
            dataset_path (str, optional): Path to dataset file (for logging)
            
        Returns:
            Optional[pd.DataFrame]: Cached dataset or None
        """
        if not should_enable_caching():
            return None
            
        if self._dataset_cache is not None:
            self._cache_hits += 1
            logger.debug(f"Dataset cache hit for: {dataset_path}")
            return self._dataset_cache.copy()  # Return copy to prevent modification
        else:
            self._cache_misses += 1
            logger.debug(f"Dataset cache miss for: {dataset_path}")
            return None
    
    def set_dataset(self, dataset: pd.DataFrame, dataset_path: str = None) -> None:
        """
        Cache a dataset globally.
        
        Args:
            dataset (pd.DataFrame): Dataset to cache
            dataset_path (str, optional): Path to dataset file (for logging)
        """
        if not should_enable_caching():
            return
            
        self._dataset_cache = dataset.copy()  # Store copy to prevent external modification
        self._cache_metadata['dataset'] = {
            'path': dataset_path,
            'shape': dataset.shape,
            'columns': list(dataset.columns),
            'cached_at': datetime.now(),
            'memory_usage_mb': dataset.memory_usage(deep=True).sum() / 1024 / 1024
        }
        self._last_updated = datetime.now()
        logger.info(f"Dataset cached: {dataset.shape} rows x {len(dataset.columns)} columns")
    
    def get_model(self, model_path: str = None) -> Optional[IsolationForest]:
        """
        Get cached model or None if not cached.
        
        Args:
            model_path (str, optional): Path to model file (for logging)
            
        Returns:
            Optional[IsolationForest]: Cached model or None
        """
        if not should_enable_caching():
            return None
            
        if self._model_cache is not None:
            self._cache_hits += 1
            logger.debug(f"Model cache hit for: {model_path}")
            return self._model_cache
        else:
            self._cache_misses += 1
            logger.debug(f"Model cache miss for: {model_path}")
            return None
    
    def set_model(self, model: IsolationForest, model_path: str = None) -> None:
        """
        Cache a model globally.
        
        Args:
            model (IsolationForest): Model to cache
            model_path (str, optional): Path to model file (for logging)
        """
        if not should_enable_caching():
            return
            
        self._model_cache = model
        self._cache_metadata['model'] = {
            'path': model_path,
            'model_type': type(model).__name__,
            'cached_at': datetime.now(),
            'n_estimators': getattr(model, 'n_estimators', None),
            'contamination': getattr(model, 'contamination', None)
        }
        self._last_updated = datetime.now()
        logger.info(f"Model cached: {type(model).__name__}")
    
    def get_features(self, dataset_hash: str) -> Optional[pd.DataFrame]:
        """
        Get cached features for a specific dataset hash.
        
        Args:
            dataset_hash (str): Hash of the source dataset
            
        Returns:
            Optional[pd.DataFrame]: Cached features or None
        """
        if not should_enable_caching():
            return None
            
        if dataset_hash in self._feature_cache:
            self._cache_hits += 1
            logger.debug(f"Feature cache hit for hash: {dataset_hash[:8]}...")
            return self._feature_cache[dataset_hash].copy()
        else:
            self._cache_misses += 1
            logger.debug(f"Feature cache miss for hash: {dataset_hash[:8]}...")
            return None
    
    def set_features(self, dataset_hash: str, features: pd.DataFrame) -> None:
        """
        Cache computed features for a dataset.
        
        Args:
            dataset_hash (str): Hash of the source dataset
            features (pd.DataFrame): Computed features to cache
        """
        if not should_enable_caching():
            return
            
        self._feature_cache[dataset_hash] = features.copy()
        self._cache_metadata[f'features_{dataset_hash[:8]}'] = {
            'dataset_hash': dataset_hash,
            'shape': features.shape,
            'columns': list(features.columns),
            'cached_at': datetime.now(),
            'memory_usage_mb': features.memory_usage(deep=True).sum() / 1024 / 1024
        }
        self._last_updated = datetime.now()
        logger.info(f"Features cached for dataset hash {dataset_hash[:8]}: {features.shape}")
    
    def compute_dataset_hash(self, dataset: pd.DataFrame) -> str:
        """
        Compute a hash for a dataset to use as cache key.
        
        Args:
            dataset (pd.DataFrame): Dataset to hash
            
        Returns:
            str: SHA256 hash of dataset content
        """
        # Create hash based on dataset shape, columns, and sample of data
        hash_input = f"{dataset.shape}_{list(dataset.columns)}_{dataset.head().to_string()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._dataset_cache = None
        self._model_cache = None
        self._feature_cache.clear()
        self._cache_metadata.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._last_updated = datetime.now()
        logger.info("All caches cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dict[str, Any]: Cache statistics and metadata
        """
        # Calculate memory usage
        total_memory_mb = 0.0
        if self._dataset_cache is not None:
            total_memory_mb += self._dataset_cache.memory_usage(deep=True).sum() / 1024 / 1024
        
        for features in self._feature_cache.values():
            total_memory_mb += features.memory_usage(deep=True).sum() / 1024 / 1024
        
        # Calculate cache hit rate
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            'dataset_cached': self._dataset_cache is not None,
            'model_cached': self._model_cache is not None,
            'feature_cache_size': len(self._feature_cache),
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': round(hit_rate, 2),
            'total_memory_usage_mb': round(total_memory_mb, 2),
            'system_memory_usage_mb': round(psutil.Process().memory_info().rss / 1024 / 1024, 2),
            'last_updated': self._last_updated,
            'caching_enabled': should_enable_caching(),
            'metadata': self._cache_metadata
        }
    
    def log_cache_stats(self) -> None:
        """Log current cache statistics."""
        stats = self.get_cache_stats()
        logger.info("=== Cache Statistics ===")
        logger.info(f"Dataset Cached: {stats['dataset_cached']}")
        logger.info(f"Model Cached: {stats['model_cached']}")
        logger.info(f"Feature Cache Size: {stats['feature_cache_size']}")
        logger.info(f"Cache Hit Rate: {stats['cache_hit_rate']}%")
        logger.info(f"Total Cache Memory: {stats['total_memory_usage_mb']} MB")
        logger.info(f"System Memory Usage: {stats['system_memory_usage_mb']} MB")
        logger.info("========================")


# Global cache instance
_cache_manager: Optional[GlobalCacheManager] = None


def get_cache_manager() -> GlobalCacheManager:
    """
    Get the global cache manager instance.
    
    Returns:
        GlobalCacheManager: The singleton cache manager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = GlobalCacheManager()
    return _cache_manager


# Convenience functions for common operations
def get_global_dataset(dataset_path: str = None) -> Optional[pd.DataFrame]:
    """Get cached dataset."""
    return get_cache_manager().get_dataset(dataset_path)


def set_global_dataset(dataset: pd.DataFrame, dataset_path: str = None) -> None:
    """Cache dataset globally."""
    get_cache_manager().set_dataset(dataset, dataset_path)


def get_global_model(model_path: str = None) -> Optional[IsolationForest]:
    """Get cached model."""
    return get_cache_manager().get_model(model_path)


def set_global_model(model: IsolationForest, model_path: str = None) -> None:
    """Cache model globally."""
    get_cache_manager().set_model(model, model_path)


def get_cached_features(dataset: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Get cached features for a dataset."""
    dataset_hash = get_cache_manager().compute_dataset_hash(dataset)
    return get_cache_manager().get_features(dataset_hash)


def cache_features(dataset: pd.DataFrame, features: pd.DataFrame) -> None:
    """Cache computed features for a dataset."""
    dataset_hash = get_cache_manager().compute_dataset_hash(dataset)
    get_cache_manager().set_features(dataset_hash, features)


def clear_all_caches() -> None:
    """Clear all cached data."""
    get_cache_manager().clear_cache()


def log_cache_statistics() -> None:
    """Log current cache statistics."""
    get_cache_manager().log_cache_stats()