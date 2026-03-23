"""
Comprehensive Unit Tests for TRINETRA AI AI Explainer Module

This module contains unit tests for the AI explanation functions in ai_explainer.py.
Tests cover Gemini API integration, explanation generation, and error handling with mocking.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set TEST_MODE to avoid actual API calls
os.environ["TEST_MODE"] = "true"

from ai_explainer import (
    initialize_gemini,
    explain_transaction,
    answer_investigation_query,
    reset_session_count,
    get_session_count,
    can_make_explanation,
    increment_session_count,
    get_cached_explanation,
    cache_explanation,
    clear_explanation_cache,
    _generate_quota_exceeded_fallback,
    _create_explanation_prompt,
    _create_investigation_prompt,
    _generate_fallback_explanation,
    _generate_fallback_investigation_response,
    MAX_EXPLANATIONS_PER_SESSION,
    GeminiInitializationError,
    GeminiAPIError,
    GeminiRateLimitError,
    GeminiTimeoutError,
    GeminiQuotaExceededError
)


class TestSessionManagement:
    """Test cases for session management functions."""
    
    def setup_method(self):
        """Reset session state before each test."""
        reset_session_count()
        clear_explanation_cache()
    
    def test_reset_session_count(self):
        """Test session count reset."""
        # Increment count first
        increment_session_count()
        increment_session_count()
        assert get_session_count() == 2
        
        # Reset and verify
        reset_session_count()
        assert get_session_count() == 0
    
    def test_get_session_count_initial(self):
        """Test initial session count is zero."""
        assert get_session_count() == 0
    
    def test_increment_session_count(self):
        """Test session count increment."""
        initial_count = get_session_count()
        
        increment_session_count()
        assert get_session_count() == initial_count + 1
        
        increment_session_count()
        assert get_session_count() == initial_count + 2
    
    def test_can_make_explanation(self):
        """Test explanation availability check."""
        # Initially should be able to make explanations
        assert can_make_explanation() is True
        
        # Increment to maximum
        for _ in range(MAX_EXPLANATIONS_PER_SESSION):
            increment_session_count()
        
        # Should no longer be able to make explanations
        assert can_make_explanation() is False
    
    def test_can_make_explanation_boundary(self):
        """Test explanation availability at boundary conditions."""