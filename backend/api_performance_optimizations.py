"""
API Performance Optimizations for TRINETRA AI

This module implements performance optimizations to ensure all API endpoints
respond within 1 second (NFR-1 requirement).

Task: 12.4 Performance Testing - API responses within 1 second

Optimizations implemented:
1. Response caching with TTL
2. Query result memoization
3. Lazy loading for expensive operations
4. DataFrame filtering optimization
5. Response time monitoring and logging

Author: TRINETRA AI Team
Date: 2024
"""

import time
import logging
from functools import wraps, lru_cache
from typing import Dict, Any, Optional, Callable
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ResponseCache:
    """
    Simple in-memory cache for API responses with TTL support.
    
    This cache stores API responses to avoid repeated expensive operations
    like DataFrame filtering and serialization.
    """
    
    def __init__(self, default_ttl: int = 30):
        """
        Initialize response cache.
        
        Args:
            default_ttl: Default time-to-live in seconds
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
        logger.info(f"ResponseCache initialized with TTL={default_ttl}s")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached response if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if expired/missing
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if datetime.now() > entry['expires_at']:
            # Expired, remove from cache
            del self._cache[key]
            return None
        
        logger.debug(f"Cache HIT: {key}")
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        ttl = ttl if ttl is not None else self._default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'cached_at': datetime.now()
        }
        
        logger.debug(f"Cache SET: {key} (TTL={ttl}s)")
    
    def invalidate(self, key: str) -> None:
        """Remove specific key from cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache INVALIDATE: {key}")
    
    def clear(self) -> None:
        """Clear all cached entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.now()
        active_entries = sum(1 for entry in self._cache.values() if now <= entry['expires_at'])
        
        return {
            'total_entries': len(self._cache),
            'active_entries': active_entries,
            'expired_entries': len(self._cache) - active_entries
        }


# Global response cache instance
_response_cache = ResponseCache(default_ttl=300)


def get_response_cache() -> ResponseCache:
    """Get the global response cache instance."""
    return _response_cache


def cached_response(ttl: int = 30, key_func: Optional[Callable] = None):
    """
    Decorator to cache API endpoint responses.
    
    Args:
        ttl: Time-to-live in seconds
        key_func: Optional function to generate cache key from args
        
    Usage:
        @cached_response(ttl=60)
        async def get_data():
            return expensive_operation()
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: use function name and stringified args
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached_value = _response_cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Cache miss - execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            _response_cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


def optimize_dataframe_filtering(df: pd.DataFrame, filter_column: str, filter_value: Any) -> pd.DataFrame:
    """
    Optimized DataFrame filtering using vectorized operations.
    
    Args:
        df: Source DataFrame
        filter_column: Column to filter on
        filter_value: Value to filter for
        
    Returns:
        Filtered DataFrame
    """
    start_time = time.time()
    
    # Use vectorized boolean indexing (faster than iterrows)
    result = df[df[filter_column] == filter_value]
    
    elapsed = time.time() - start_time
    logger.debug(f"DataFrame filter: {len(result)}/{len(df)} rows in {elapsed:.4f}s")
    
    return result


def optimize_dataframe_to_dict(df: pd.DataFrame, max_rows: Optional[int] = None) -> list:
    """
    Optimized DataFrame to dict conversion.
    
    Args:
        df: Source DataFrame
        max_rows: Maximum rows to convert (for pagination)
        
    Returns:
        List of dictionaries
    """
    start_time = time.time()
    
    # Limit rows if specified
    if max_rows and len(df) > max_rows:
        df = df.head(max_rows)
    
    # Use orient='records' for best performance
    result = df.to_dict('records')
    
    elapsed = time.time() - start_time
    logger.debug(f"DataFrame to dict: {len(result)} rows in {elapsed:.4f}s")
    
    return result


class PerformanceMonitor:
    """
    Monitor and log API endpoint performance.
    
    Tracks response times and identifies slow endpoints.
    """
    
    def __init__(self, threshold: float = 1.0):
        """
        Initialize performance monitor.
        
        Args:
            threshold: Warning threshold in seconds
        """
        self._threshold = threshold
        self._metrics: Dict[str, list] = {}
        logger.info(f"PerformanceMonitor initialized (threshold={threshold}s)")
    
    def record(self, endpoint: str, response_time: float) -> None:
        """
        Record endpoint response time.
        
        Args:
            endpoint: API endpoint path
            response_time: Response time in seconds
        """
        if endpoint not in self._metrics:
            self._metrics[endpoint] = []
        
        self._metrics[endpoint].append(response_time)
        
        # Log warning if over threshold
        if response_time > self._threshold:
            logger.warning(
                f"SLOW ENDPOINT: {endpoint} took {response_time:.3f}s "
                f"(threshold: {self._threshold}s)"
            )
    
    def get_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Args:
            endpoint: Specific endpoint or None for all
            
        Returns:
            Performance statistics
        """
        if endpoint:
            if endpoint not in self._metrics:
                return {}
            
            times = self._metrics[endpoint]
            return {
                'endpoint': endpoint,
                'count': len(times),
                'avg': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'over_threshold': sum(1 for t in times if t > self._threshold)
            }
        else:
            # All endpoints
            return {
                ep: self.get_stats(ep)
                for ep in self._metrics.keys()
            }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._metrics.clear()
        logger.info("Performance metrics reset")


# Global performance monitor
_performance_monitor = PerformanceMonitor(threshold=1.0)


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return _performance_monitor


def monitor_performance(func):
    """
    Decorator to monitor endpoint performance.
    
    Usage:
        @monitor_performance
        async def my_endpoint():
            return data
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed = time.time() - start_time
            endpoint = func.__name__
            _performance_monitor.record(endpoint, elapsed)
    
    return wrapper


# Optimized query response cache
_query_response_cache: Dict[str, str] = {}


def get_cached_query_response(query: str) -> Optional[str]:
    """
    Get cached response for a query.
    
    Args:
        query: Query string
        
    Returns:
        Cached response or None
    """
    # Normalize query (lowercase, strip whitespace)
    normalized_query = query.lower().strip()
    
    return _query_response_cache.get(normalized_query)


def cache_query_response(query: str, response: str) -> None:
    """
    Cache a query response.
    
    Args:
        query: Query string
        response: Response to cache
    """
    # Normalize query
    normalized_query = query.lower().strip()
    
    # Limit cache size to prevent memory issues
    if len(_query_response_cache) > 100:
        # Remove oldest entry (simple FIFO)
        _query_response_cache.pop(next(iter(_query_response_cache)))
    
    _query_response_cache[normalized_query] = response
    logger.debug(f"Cached query response: {normalized_query[:50]}...")


def clear_query_cache() -> None:
    """Clear the query response cache."""
    _query_response_cache.clear()
    logger.info("Query cache cleared")


# Pre-computed fallback responses for common queries
FALLBACK_QUERY_RESPONSES = {
    "total transactions": "Based on the current dataset, there are {total_transactions} total transactions.",
    "fraud cases": "The system has identified {fraud_cases} confirmed fraud cases ({fraud_rate}% fraud rate).",
    "suspicious transactions": "There are {suspicious_cases} suspicious transactions requiring investigation ({suspicious_rate}% of total).",
    "fraud rate": "The current fraud rate is {fraud_rate}%, with {fraud_cases} confirmed fraud cases out of {total_transactions} total transactions.",
    "high risk": "High-risk transactions include those with significant price deviations, route anomalies, or connections to high-risk entities.",
    "price deviation": "Price deviations indicate transactions where the trade price significantly differs from market price, suggesting potential fraud.",
    "route anomaly": "Route anomalies flag unusual shipping routes that deviate from standard trade patterns.",
    "company risk": "Company risk scores are based on historical transaction patterns and known fraud indicators.",
}


def get_fast_query_response(query: str, context: Dict[str, Any]) -> str:
    """
    Get fast query response using pre-computed templates.
    
    This avoids calling the Gemini API for common queries, ensuring
    sub-second response times.
    
    Args:
        query: User query
        context: Context data for template filling
        
    Returns:
        Response string
    """
    # Normalize query
    normalized_query = query.lower().strip()
    
    # Check for keyword matches in fallback responses
    for keyword, template in FALLBACK_QUERY_RESPONSES.items():
        if keyword in normalized_query:
            try:
                return template.format(**context)
            except KeyError:
                # Missing context key, return template as-is
                return template
    
    # Default response
    return (
        f"I can help you analyze the fraud detection data. "
        f"Currently tracking {context.get('total_transactions', 'N/A')} transactions "
        f"with {context.get('fraud_cases', 'N/A')} confirmed fraud cases. "
        f"What specific aspect would you like to investigate?"
    )


def log_performance_summary() -> None:
    """Log comprehensive performance summary."""
    logger.info("="*60)
    logger.info("API PERFORMANCE SUMMARY")
    logger.info("="*60)
    
    # Cache stats
    cache_stats = _response_cache.get_stats()
    logger.info(f"Response Cache: {cache_stats['active_entries']} active entries")
    
    # Performance stats
    perf_stats = _performance_monitor.get_stats()
    for endpoint, stats in perf_stats.items():
        if stats:
            logger.info(
                f"{endpoint}: avg={stats['avg']:.3f}s, "
                f"max={stats['max']:.3f}s, "
                f"slow={stats['over_threshold']}"
            )
    
    logger.info("="*60)
