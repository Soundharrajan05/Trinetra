"""
Configuration management for TRINETRA AI performance optimizations.

This module provides centralized control for FAST_DEV_MODE and related
performance settings to optimize development workflow speed while
preserving identical system behavior in production.
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceConfig:
    """Configuration class for performance optimization settings."""
    
    fast_dev_mode: bool = True
    test_mode: bool = True
    max_retries: int = 1
    rate_limit_retry_delay: int = 1
    base_retry_delay: int = 1
    skip_integration_tests: bool = True
    enable_caching: bool = True
    target_execution_time: int = 10  # seconds
    
    def __post_init__(self):
        """Adjust settings based on FAST_DEV_MODE after initialization."""
        if not self.fast_dev_mode:
            # Production settings
            self.max_retries = 3
            self.rate_limit_retry_delay = 5
            self.base_retry_delay = 3
            self.skip_integration_tests = False
            self.enable_caching = False
            self.test_mode = False


# Global configuration instance
_config: Optional[PerformanceConfig] = None


def get_config() -> PerformanceConfig:
    """
    Get the global performance configuration instance.
    
    Returns:
        PerformanceConfig: The current configuration instance
    """
    global _config
    if _config is None:
        # Check environment variable for FAST_DEV_MODE override
        fast_dev_mode = os.getenv('FAST_DEV_MODE', 'true').lower() == 'true'
        _config = PerformanceConfig(fast_dev_mode=fast_dev_mode)
        log_performance_settings()
    return _config


def set_fast_dev_mode(enabled: bool) -> None:
    """
    Set the FAST_DEV_MODE flag and update related settings.
    
    Args:
        enabled (bool): Whether to enable fast development mode
    """
    global _config
    _config = PerformanceConfig(fast_dev_mode=enabled)
    logger.info(f"FAST_DEV_MODE set to: {enabled}")
    log_performance_settings()


def is_fast_dev_mode() -> bool:
    """
    Check if FAST_DEV_MODE is currently enabled.
    
    Returns:
        bool: True if fast development mode is enabled
    """
    return get_config().fast_dev_mode


def is_test_mode() -> bool:
    """
    Check if TEST_MODE is currently enabled.
    
    Returns:
        bool: True if test mode is enabled
    """
    return get_config().test_mode


def should_skip_integration_tests() -> bool:
    """
    Check if integration tests should be skipped.
    
    Returns:
        bool: True if integration tests should be skipped
    """
    return get_config().skip_integration_tests


def should_enable_caching() -> bool:
    """
    Check if caching should be enabled.
    
    Returns:
        bool: True if caching should be enabled
    """
    return get_config().enable_caching


def get_retry_settings() -> tuple[int, int, int]:
    """
    Get current retry configuration settings.
    
    Returns:
        tuple: (max_retries, rate_limit_retry_delay, base_retry_delay)
    """
    config = get_config()
    return (config.max_retries, config.rate_limit_retry_delay, config.base_retry_delay)


def log_performance_settings() -> None:
    """Log current performance optimization settings."""
    config = get_config()
    logger.info("=== TRINETRA AI Performance Settings ===")
    logger.info(f"FAST_DEV_MODE: {config.fast_dev_mode}")
    logger.info(f"TEST_MODE: {config.test_mode}")
    logger.info(f"Caching Enabled: {config.enable_caching}")
    logger.info(f"Skip Integration Tests: {config.skip_integration_tests}")
    logger.info(f"Max Retries: {config.max_retries}")
    logger.info(f"Rate Limit Retry Delay: {config.rate_limit_retry_delay}s")
    logger.info(f"Base Retry Delay: {config.base_retry_delay}s")
    logger.info(f"Target Execution Time: {config.target_execution_time}s")
    logger.info("========================================")


def reset_config() -> None:
    """Reset configuration to default state. Used primarily for testing."""
    global _config
    _config = None


# Initialize configuration on module import
get_config()