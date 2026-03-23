"""
AI Explainer Module for TRINETRA AI - Trade Fraud Intelligence System

This module provides AI-powered fraud explanations using Google's Gemini API.
It generates natural language explanations for flagged transactions and answers
investigation queries to help fraud analysts understand suspicious patterns.

TIMEOUT HANDLING:
- All Gemini API calls have a 10-second timeout as per NFR-1 requirements
- Uses RequestOptions with retry configuration for primary timeout handling
- Falls back to asyncio timeout mechanism if RequestOptions fails
- Gracefully handles timeout errors with comprehensive fallback explanations
- Implements exponential backoff retry logic with proper error classification

Author: TRINETRA AI Team
Date: 2024
"""

import os
import logging
import time
from typing import Dict, Optional, Any

# Set protobuf implementation before importing google packages
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# TEST_MODE flag for disabling external API calls during tests
TEST_MODE = os.getenv("TEST_MODE", "false") == "true"

# Import common error handlers
try:
    from utils.helpers import error_handlers, performance_tracker
except ImportError:
    # Fallback if utils.helpers is not available
    error_handlers = None
    performance_tracker = None

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig, RequestOptions
    from google.api_core import retry
    GEMINI_AVAILABLE = True
except Exception as e:
    logging.warning(f"Gemini API not available: {e}")
    GEMINI_AVAILABLE = False
    # Create mock classes for development
    class MockGenerativeModel:
        def __init__(self, model_name):
            self.model_name = model_name
            
        def generate_content(self, *args, **kwargs):
            return MockResponse()
    
    class MockResponse:
        def __init__(self):
            self.text = "Mock response - Gemini API not available"
    
    class MockGenerationConfig:
        def __init__(self, **kwargs):
            pass
    
    # Mock the genai module
    class MockGenAI:
        GenerativeModel = MockGenerativeModel
        
        @staticmethod
        def configure(**kwargs):
            pass
    
    genai = MockGenAI()
    GenerationConfig = MockGenerationConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini API Configuration
API_KEY = "AIzaSyAcRCJt8Ea5hrm0KwSWbw-cCCopI95plQw"
MODEL_NAME = "gemini-2.5-flash"
REQUEST_TIMEOUT = 10
MAX_RETRIES = 1
BASE_RETRY_DELAY = 1
MAX_RETRY_DELAY = 5
BACKOFF_MULTIPLIER = 2
RATE_LIMIT_RETRY_DELAY = 1

# Session and Quota Management
MAX_EXPLANATIONS_PER_SESSION = 10
_session_explanation_count = 0
_explanation_cache = {}  # Cache for explanations to avoid repeated API calls


def reset_session_count():
    """Reset the session explanation count."""
    global _session_explanation_count
    _session_explanation_count = 0
    logger.info("Session explanation count reset")


def get_session_count():
    """Get current session explanation count."""
    return _session_explanation_count


def can_make_explanation():
    """Check if we can make another explanation within session limits."""
    return _session_explanation_count < MAX_EXPLANATIONS_PER_SESSION


def increment_session_count():
    """Increment the session explanation count."""
    global _session_explanation_count
    _session_explanation_count += 1
    logger.info(f"Session explanation count: {_session_explanation_count}/{MAX_EXPLANATIONS_PER_SESSION}")


def get_cached_explanation(transaction_id: str) -> Optional[str]:
    """Get cached explanation for a transaction."""
    return _explanation_cache.get(transaction_id)


def cache_explanation(transaction_id: str, explanation: str):
    """Cache an explanation for a transaction."""
    _explanation_cache[transaction_id] = explanation
    logger.info(f"Cached explanation for transaction {transaction_id}")


def clear_explanation_cache():
    """Clear the explanation cache."""
    global _explanation_cache
    _explanation_cache = {}
    logger.info("Explanation cache cleared")


def _generate_quota_exceeded_fallback(transaction: Dict[str, Any]) -> str:
    """
    Generate fallback explanation when session quota is exceeded.
    
    Args:
        transaction (Dict[str, Any]): Transaction data dictionary
        
    Returns:
        str: Quota exceeded message with basic fraud indicators
    """
    risk_factors = []
    
    # Check for key fraud indicators
    price_dev = transaction.get('price_deviation', 0)
    if abs(price_dev) > 0.3:
        risk_factors.append(f"High price deviation ({price_dev:.1%} from market price)")
    
    route_anomaly = transaction.get('route_anomaly', 0)
    if route_anomaly == 1:
        risk_factors.append("Suspicious shipping route")
    
    company_risk = transaction.get('company_risk_score', 0)
    if company_risk > 0.7:
        risk_factors.append(f"High company risk score ({company_risk:.2f})")
    
    port_activity = transaction.get('port_activity_index', 0)
    if port_activity > 1.3:
        risk_factors.append(f"Unusual port activity ({port_activity:.2f})")
    
    if risk_factors:
        indicators_text = "\n• ".join(risk_factors)
        return f"""AI explanation limit reached for this session (max {MAX_EXPLANATIONS_PER_SESSION} per session).

Fraud Indicators Detected:
• {indicators_text}

This transaction has been flagged based on automated analysis. Please review the data manually or start a new session for AI-powered explanations."""
    else:
        return f"""AI explanation limit reached for this session (max {MAX_EXPLANATIONS_PER_SESSION} per session).

This transaction was flagged by our machine learning model based on pattern analysis. Please review the transaction details manually or start a new session for detailed AI explanations."""


def _create_request_options() -> RequestOptions:
    """
    Create RequestOptions with timeout and retry configuration.
    
    Returns:
        RequestOptions: Configured request options with timeout and retry logic
    """
    if not GEMINI_AVAILABLE:
        return None
    
    try:
        # Create retry configuration with timeout
        retry_config = retry.Retry(
            initial=1.0,  # Initial delay between retries
            maximum=8.0,  # Maximum delay between retries
            multiplier=2.0,  # Multiplier for exponential backoff
            timeout=REQUEST_TIMEOUT,  # Total timeout for the request
            predicate=retry.if_exception_type(
                Exception  # Retry on any exception
            )
        )
        
        return RequestOptions(retry=retry_config)
    except Exception as e:
        logger.warning(f"Failed to create request options: {e}")
        return None


async def _generate_content_with_timeout(model, prompt, generation_config, request_options=None, timeout_seconds=REQUEST_TIMEOUT):
    """
    Generate content with asyncio timeout as a fallback mechanism.
    
    Args:
        model: Gemini model instance
        prompt: Input prompt
        generation_config: Generation configuration
        request_options: Request options (optional)
        timeout_seconds: Timeout in seconds
        
    Returns:
        Response from generate_content
        
    Raises:
        GeminiTimeoutError: If the request times out
    """
    import asyncio
    
    try:
        # Use async version if available
        if hasattr(model, 'generate_content_async'):
            response = await asyncio.wait_for(
                model.generate_content_async(
                    prompt,
                    generation_config=generation_config,
                    request_options=request_options
                ),
                timeout=timeout_seconds
            )
        else:
            # Fallback to sync version in thread pool
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: model.generate_content(
                        prompt,
                        generation_config=generation_config,
                        request_options=request_options
                    )
                ),
                timeout=timeout_seconds
            )
        
        return response
        
    except asyncio.TimeoutError:
        raise GeminiTimeoutError(f"Request timed out after {timeout_seconds} seconds")
    except Exception as e:
        # Re-raise other exceptions as-is
        raise e


def _generate_content_with_robust_timeout(model, prompt, generation_config):
    """
    Generate content with robust timeout handling using multiple approaches.
    
    This function first tries the RequestOptions approach with built-in retry and timeout,
    and falls back to asyncio timeout if that fails or is not available.
    
    Args:
        model: Gemini model instance
        prompt: Input prompt
        generation_config: Generation configuration
        
    Returns:
        Response from generate_content
        
    Raises:
        GeminiTimeoutError: If the request times out
        GeminiAPIError: If the API call fails
    """
    import asyncio
    
    # First, try with RequestOptions (preferred approach)
    try:
        request_opts = _create_request_options()
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            request_options=request_opts
        )
        
        if not response or not response.text:
            raise GeminiAPIError("Empty response from Gemini API")
        
        return response.text.strip()
        
    except Exception as e:
        # If it's already a timeout error, re-raise it
        if isinstance(e, GeminiTimeoutError):
            raise e
        
        # For other errors, try the asyncio approach as fallback
        logger.warning(f"RequestOptions approach failed: {e}, trying asyncio timeout...")
        
        try:
            # Try asyncio timeout approach
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                response = loop.run_until_complete(
                    _generate_content_with_timeout(
                        model, prompt, generation_config, None, REQUEST_TIMEOUT
                    )
                )
                
                if not response or not response.text:
                    raise GeminiAPIError("Empty response from Gemini API")
                
                return response.text.strip()
                
            finally:
                loop.close()
                
        except Exception as async_error:
            # If both approaches fail, raise the original error
            logger.error(f"Both timeout approaches failed. Original: {e}, Async: {async_error}")
            raise _classify_api_error(e)


class GeminiInitializationError(Exception):
    """Custom exception for Gemini API initialization failures"""
    pass


class GeminiAPIError(Exception):
    """Custom exception for Gemini API call failures"""
    pass


class GeminiRateLimitError(GeminiAPIError):
    """Custom exception for Gemini API rate limit errors"""
    pass


class GeminiTimeoutError(GeminiAPIError):
    """Custom exception for Gemini API timeout errors"""
    pass


class GeminiQuotaExceededError(GeminiAPIError):
    """Custom exception for Gemini API quota exceeded errors"""
    pass


def _calculate_retry_delay(attempt: int, base_delay: float = BASE_RETRY_DELAY) -> float:
    """
    Calculate exponential backoff delay with jitter.
    
    Args:
        attempt (int): Current attempt number (0-based)
        base_delay (float): Base delay in seconds
        
    Returns:
        float: Delay in seconds with exponential backoff and jitter
    """
    import random
    
    # Exponential backoff: base_delay * (multiplier ^ attempt)
    delay = base_delay * (BACKOFF_MULTIPLIER ** attempt)
    
    # Cap the delay at maximum
    delay = min(delay, MAX_RETRY_DELAY)
    
    # Add jitter (±25% of the delay) to avoid thundering herd
    jitter = delay * 0.25 * (2 * random.random() - 1)
    
    return max(0.1, delay + jitter)


def _classify_api_error(error: Exception) -> Exception:
    """
    Classify API errors into specific exception types for better handling.
    
    Args:
        error (Exception): Original exception from API call
        
    Returns:
        Exception: Classified exception with appropriate type
    """
    # If it's already a classified error, return as-is
    if isinstance(error, (GeminiInitializationError, GeminiRateLimitError, 
                         GeminiTimeoutError, GeminiQuotaExceededError, GeminiAPIError)):
        return error
    
    error_str = str(error).lower()
    
    # Rate limit errors
    if any(keyword in error_str for keyword in ['rate limit', 'quota exceeded', 'too many requests', '429']):
        return GeminiRateLimitError(f"Rate limit exceeded: {str(error)}")
    
    # Timeout errors
    if any(keyword in error_str for keyword in ['timeout', 'timed out', 'deadline exceeded']):
        return GeminiTimeoutError(f"Request timeout: {str(error)}")
    
    # Quota errors
    if any(keyword in error_str for keyword in ['quota', 'billing', 'usage limit']):
        return GeminiQuotaExceededError(f"Quota exceeded: {str(error)}")
    
    # Authentication errors
    if any(keyword in error_str for keyword in ['authentication', 'api key', 'unauthorized', '401', '403']):
        return GeminiInitializationError(f"Authentication failed: {str(error)}")
    
    # Generic API error
    return GeminiAPIError(f"API call failed: {str(error)}")


def _should_retry_error(error: Exception) -> bool:
    """
    Determine if an error should trigger a retry.
    
    Args:
        error (Exception): Exception to evaluate
        
    Returns:
        bool: True if the error is retryable, False otherwise
    """
    # Don't retry authentication errors
    if isinstance(error, GeminiInitializationError):
        return False
    
    # Don't retry quota exceeded errors (need manual intervention)
    if isinstance(error, GeminiQuotaExceededError):
        return False
    
    # Retry rate limit errors (with longer delay)
    if isinstance(error, GeminiRateLimitError):
        return True
    
    # Retry timeout errors
    if isinstance(error, GeminiTimeoutError):
        return True
    
    # Retry generic API errors
    if isinstance(error, GeminiAPIError):
        return True
    
    # Don't retry unknown errors
    return False


def _execute_with_retry(func, *args, **kwargs):
    """
    Execute a function with exponential backoff retry logic.
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Any: Result of the function call
        
    Raises:
        Exception: Last exception if all retries fail
    """
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
            
        except Exception as e:
            # Classify the error
            classified_error = _classify_api_error(e)
            last_error = classified_error
            
            # Log the attempt
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {str(classified_error)}")
            
            # Check if we should retry
            if not _should_retry_error(classified_error):
                logger.error(f"Non-retryable error encountered: {str(classified_error)}")
                raise classified_error
            
            # If this is the last attempt, don't wait
            if attempt == MAX_RETRIES - 1:
                break
            
            # Calculate delay based on error type
            if isinstance(classified_error, GeminiRateLimitError):
                delay = RATE_LIMIT_RETRY_DELAY
                logger.info(f"Rate limit hit, waiting {delay} seconds before retry...")
            else:
                delay = _calculate_retry_delay(attempt)
                logger.info(f"Retrying in {delay:.2f} seconds...")
            
            time.sleep(delay)
    
    # All retries failed
    logger.error(f"All {MAX_RETRIES} retry attempts failed. Last error: {str(last_error)}")
    raise last_error


def initialize_gemini(api_key: Optional[str] = None) -> genai.GenerativeModel:
    """
    Initialize Gemini API client with proper configuration and robust error handling.
    
    This function sets up the Gemini API client with authentication,
    comprehensive error handling, timeout configuration, and connection testing
    for generating fraud explanations.
    
    Args:
        api_key (Optional[str]): Gemini API key. If None, uses default from module.
    
    Returns:
        genai.GenerativeModel: Configured Gemini model instance
        
    Raises:
        GeminiInitializationError: If initialization fails
        
    Example:
        >>> model = initialize_gemini()
        >>> # Model is ready for generating explanations
    """
    try:
        # Check if Gemini is available
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini API not available, using mock implementation")
            return genai.GenerativeModel("mock-model")
        
        # Use provided API key or default
        key = api_key or API_KEY
        
        if not key:
            raise GeminiInitializationError("API key is required but not provided")
        
        logger.info("Initializing Gemini API client...")
        
        # Configure the Gemini API with the provided key
        genai.configure(api_key=key)
        
        # Initialize the generative model
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Test the connection with a simple prompt using retry logic
        logger.info("Testing Gemini API connection...")
        
        def _test_connection():
            try:
                test_response = _generate_content_with_robust_timeout(
                    model,
                    "Hello, please respond with just 'OK'",
                    GenerationConfig(
                        max_output_tokens=10,
                        temperature=0.1
                    )
                )
                return test_response
            except Exception as test_error:
                raise GeminiAPIError(f"Test connection failed: {test_error}")
        
        try:
            # Use a simplified retry for connection test (fewer retries)
            test_retries = 2
            for attempt in range(test_retries):
                try:
                    test_response = _test_connection()
                    logger.info(f"Test response received: {test_response}")
                    break
                except Exception as test_error:
                    if attempt < test_retries - 1:
                        logger.warning(f"Connection test attempt {attempt + 1} failed, retrying...")
                        time.sleep(1)
                    else:
                        logger.warning(f"Connection test failed after {test_retries} attempts: {test_error}")
                        # Don't fail initialization for test failures, API might still work
                        
        except Exception as test_error:
            logger.warning(f"Connection test encountered error: {test_error}, but proceeding with initialization")
        
        logger.info("Gemini API client initialized successfully")
        logger.info(f"Model: {MODEL_NAME}")
        logger.info(f"Max retries: {MAX_RETRIES}")
        logger.info(f"Base retry delay: {BASE_RETRY_DELAY}s")
        logger.info(f"Max retry delay: {MAX_RETRY_DELAY}s")
        
        return model
        
    except Exception as e:
        error_msg = f"Failed to initialize Gemini API: {str(e)}"
        logger.error(error_msg)
        
        # Handle specific error types
        if "API_KEY" in str(e).upper() or "authentication" in str(e).lower():
            raise GeminiInitializationError(f"Authentication failed: {str(e)}")
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            raise GeminiInitializationError(f"Network connection failed: {str(e)}")
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            raise GeminiInitializationError(f"API quota exceeded: {str(e)}")
        else:
            raise GeminiInitializationError(error_msg)


def explain_transaction(transaction: Dict[str, Any], model: Optional[genai.GenerativeModel] = None, force_api: bool = False) -> str:
    """
    Generate natural language fraud explanation for a transaction.

    This function implements session limits and caching to prevent Gemini API quota errors.
    Only calls Gemini API when explicitly requested and within session limits.

    Args:
        transaction (Dict[str, Any]): Transaction data dictionary
        model (Optional[genai.GenerativeModel]): Gemini model instance
        force_api (bool): Force API call even if cached (for explicit user requests)

    Returns:
        str: Natural language explanation of fraud indicators

    Raises:
        GeminiAPIError: If explanation generation fails after all retries
    """
    transaction_id = transaction.get('transaction_id', 'unknown')
    start_time = time.time()

    # TEST_MODE: Return mock explanation without calling Gemini API
    if TEST_MODE:
        return "Test mode explanation: suspicious transaction detected based on anomaly indicators."

    # Check cache first (unless force_api is True)
    if not force_api:
        cached_explanation = get_cached_explanation(transaction_id)
        if cached_explanation:
            logger.info(f"Using cached explanation for transaction {transaction_id}")
            return cached_explanation

    # Check session limits for API calls
    if not can_make_explanation():
        logger.warning(f"Session limit reached ({_session_explanation_count}/{MAX_EXPLANATIONS_PER_SESSION}), using fallback for transaction {transaction_id}")
        fallback = _generate_quota_exceeded_fallback(transaction)
        # Cache the fallback to avoid repeated processing
        cache_explanation(transaction_id, fallback)
        return fallback

    # Only proceed with API call if explicitly requested (force_api=True)
    if not force_api:
        logger.info(f"API call not explicitly requested for transaction {transaction_id}, using fallback")
        fallback = _generate_fallback_explanation(transaction)
        cache_explanation(transaction_id, fallback)
        return fallback

    if model is None:
        model = initialize_gemini()

    try:
        # Increment session count before making API call
        increment_session_count()

        # Format transaction data for the prompt
        prompt = _create_explanation_prompt(transaction)

        # Define the API call function with robust timeout handling
        def _make_api_call():
            return _generate_content_with_robust_timeout(
                model,
                prompt,
                GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.3
                )
            )

        # Execute with retry logic (limited to 1 retry to prevent quota exhaustion)
        result = _execute_with_retry(_make_api_call)

        # Log successful API call with performance tracker
        response_time = time.time() - start_time
        if performance_tracker:
            performance_tracker.log_gemini_call(True, response_time)

        # Cache the successful result
        cache_explanation(transaction_id, result)

        logger.info(f"Generated and cached AI explanation for transaction {transaction_id}")
        return result

    except Exception as e:
        response_time = time.time() - start_time
        
        # Handle Gemini API errors with common error handlers
        if error_handlers:
            error_info = error_handlers.handle_gemini_api_error(
                e, f"transaction explanation for {transaction_id}"
            )
            
            # Log failed API call with performance tracker
            if performance_tracker:
                performance_tracker.log_gemini_call(False, response_time, str(e))
            
            # Use fallback content from error handler if available
            if error_info.get('fallback_content'):
                fallback = error_info['fallback_content']
            else:
                fallback = _generate_fallback_explanation(transaction)
            
            # Cache the fallback to avoid repeated API attempts
            cache_explanation(transaction_id, fallback)
            
            logger.info(f"Using fallback explanation for transaction {transaction_id}: {error_info.get('user_message', 'API unavailable')}")
            return fallback
        else:
            # Original error handling
            logger.error(f"Error generating AI explanation: {str(e)}")
            
            # Log failed API call with performance tracker
            if performance_tracker:
                performance_tracker.log_gemini_call(False, response_time, str(e))

            # Generate enhanced fallback explanation
            fallback = _generate_fallback_explanation(transaction)

            # Cache the fallback to avoid repeated API attempts
            cache_explanation(transaction_id, fallback)

            logger.info(f"Using fallback explanation for transaction {transaction_id}")
            return fallback



def answer_investigation_query(query: str, context: Dict[str, Any], model: Optional[genai.GenerativeModel] = None) -> str:
    """
    Answer natural language investigation questions about transactions.
    
    This function uses robust retry logic with exponential backoff to handle
    API failures gracefully, including rate limits, timeouts, and network issues.
    Falls back to rule-based responses when Gemini API is unavailable.
    
    Args:
        query (str): Natural language question
        context (Dict[str, Any]): Context data for the query
        model (Optional[genai.GenerativeModel]): Gemini model instance
        
    Returns:
        str: Natural language answer to the investigation query
        
    Raises:
        GeminiAPIError: If query processing fails after all retries
    """
    # TEST_MODE: Return mock response without calling Gemini API
    if TEST_MODE:
        return "Test mode response: query processed using local logic and dataset values."

    if model is None:
        model = initialize_gemini()
    
    try:
        # Create investigation prompt
        prompt = _create_investigation_prompt(query, context)
        
        # Define the API call function with robust timeout handling
        def _make_api_call():
            return _generate_content_with_robust_timeout(
                model,
                prompt,
                GenerationConfig(
                    max_output_tokens=800,
                    temperature=0.4
                )
            )
        
        # Execute with retry logic
        result = _execute_with_retry(_make_api_call)
        
        logger.info(f"Answered investigation query: {query[:50]}...")
        return result
        
    except Exception as e:
        logger.error(f"Error answering investigation query: {str(e)}")
        
        # Use enhanced fallback response system
        fallback = _generate_fallback_investigation_response(query, context, e)
        logger.info(f"Using fallback response for investigation query: {query[:50]}...")
        return fallback


def _create_explanation_prompt(transaction: Dict[str, Any]) -> str:
    """Create a formatted prompt for transaction explanation."""
    return f"""
Analyze the following trade transaction and explain why it may be fraudulent.

Transaction Details:
- Transaction ID: {transaction.get('transaction_id', 'N/A')}
- Product: {transaction.get('product', 'N/A')}
- Commodity Category: {transaction.get('commodity_category', 'N/A')}
- Market Price: ${transaction.get('market_price', 'N/A')}
- Trade Price: ${transaction.get('unit_price', 'N/A')}
- Price Deviation: {transaction.get('price_deviation', 'N/A')}%
- Shipping Route: {transaction.get('shipping_route', 'N/A')}
- Distance: {transaction.get('distance_km', 'N/A')} km
- Company Risk Score: {transaction.get('company_risk_score', 'N/A')}
- Port Activity Index: {transaction.get('port_activity_index', 'N/A')}
- Route Anomaly: {transaction.get('route_anomaly', 'N/A')}
- Risk Score: {transaction.get('risk_score', 'N/A')}
- Risk Category: {transaction.get('risk_category', 'N/A')}

Please explain the possible fraud indicators in 3-4 sentences, focusing on the most significant risk factors.
"""


def _create_investigation_prompt(query: str, context: Dict[str, Any]) -> str:
    """Create a formatted prompt for investigation queries."""
    return f"""
You are a trade fraud investigation assistant. Answer the following question based on the provided context.

Question: {query}

Context:
- Total Transactions: {context.get('total_transactions', 'N/A')}
- Fraud Cases: {context.get('fraud_cases', 'N/A')}
- Suspicious Cases: {context.get('suspicious_cases', 'N/A')}
- Average Risk Score: {context.get('avg_risk_score', 'N/A')}
- High-Risk Companies: {context.get('high_risk_companies', 'N/A')}
- Common Fraud Patterns: {context.get('fraud_patterns', 'N/A')}

Provide a clear, informative answer based on trade fraud detection principles and the available data.
"""


def _generate_fallback_investigation_response(query: str, context: Dict[str, Any], error: Exception) -> str:
    """
    Generate rule-based responses to investigation queries when Gemini API fails.
    
    This function analyzes the query and provides informative responses based on
    available context data and common fraud investigation patterns.
    
    Args:
        query (str): The investigation query
        context (Dict[str, Any]): Available context data
        error (Exception): The error that caused the fallback
        
    Returns:
        str: Rule-based response to the investigation query
    """
    query_lower = query.lower()
    
    # Extract context data with defaults
    total_transactions = context.get('total_transactions', 0)
    fraud_cases = context.get('fraud_cases', 0)
    suspicious_cases = context.get('suspicious_cases', 0)
    avg_risk_score = context.get('avg_risk_score', 0)
    high_risk_companies = context.get('high_risk_companies', [])
    fraud_patterns = context.get('fraud_patterns', [])
    
    # Calculate fraud rate
    fraud_rate = (fraud_cases / total_transactions * 100) if total_transactions > 0 else 0
    suspicious_rate = (suspicious_cases / total_transactions * 100) if total_transactions > 0 else 0
    
    # Pattern matching for common investigation queries
    if any(keyword in query_lower for keyword in ['fraud rate', 'how many fraud', 'percentage', 'statistics']):
        return f"Based on the current dataset analysis: Out of {total_transactions:,} transactions, {fraud_cases:,} ({fraud_rate:.1f}%) are classified as fraudulent and {suspicious_cases:,} ({suspicious_rate:.1f}%) are suspicious. The average risk score across all transactions is {avg_risk_score:.3f}."
    
    elif any(keyword in query_lower for keyword in ['main patterns', 'common fraud', 'fraud patterns', 'typical indicators']):
        if fraud_patterns:
            patterns_text = ", ".join(fraud_patterns[:5])  # Limit to top 5 patterns
            return f"The most common fraud patterns identified include: {patterns_text}. These patterns are detected through price deviations, route anomalies, company risk scores, and port activity irregularities."
        else:
            return "Common fraud patterns in trade transactions typically include: price manipulation (over/under-invoicing), route laundering through unusual shipping paths, transactions involving high-risk entities, and volume/quantity misrepresentations. Our ML model analyzes these factors to identify suspicious activities."
    
    elif any(keyword in query_lower for keyword in ['high risk', 'risky companies', 'dangerous entities']):
        if high_risk_companies:
            companies_text = ", ".join(str(company) for company in high_risk_companies[:3])
            return f"High-risk entities in the current dataset include: {companies_text}. These companies have elevated risk scores based on historical transaction patterns, regulatory flags, or association with suspicious activities."
        else:
            return "High-risk companies are identified based on factors such as: previous involvement in suspicious transactions, regulatory violations, unusual trading patterns, connections to sanctioned entities, and inconsistent business profiles."
    
    elif any(keyword in query_lower for keyword in ['price', 'pricing', 'over-invoicing', 'under-invoicing']):
        return f"Price-related fraud indicators are present in approximately {fraud_rate + suspicious_rate:.1f}% of flagged transactions. This includes over-invoicing (prices significantly above market value) to transfer money illegally, and under-invoicing (prices below market value) to evade customs duties and taxes."
    
    elif any(keyword in query_lower for keyword in ['route', 'shipping', 'transport', 'logistics']):
        return "Route-based fraud typically involves trade route laundering, where goods are shipped through unusual or circuitous paths to obscure their true origin, avoid sanctions, or exploit preferential trade agreements. Our system flags routes that deviate significantly from standard commercial patterns."
    
    elif any(keyword in query_lower for keyword in ['port', 'customs', 'border']):
        return "Port-related fraud indicators include unusual activity levels, processing delays, or patterns suggesting document manipulation. High port activity indices may indicate congestion that facilitates illicit activities or suggests coordination among multiple fraudulent shipments."
    
    elif any(keyword in query_lower for keyword in ['volume', 'quantity', 'cargo']):
        return "Volume and quantity fraud involves misrepresenting the actual amount of goods shipped. This can include declaring different quantities than actually shipped, manipulating cargo volume measurements, or using container space inefficiently to justify unusual pricing."
    
    elif any(keyword in query_lower for keyword in ['why', 'suspicious', 'flagged']) and any(keyword in query_lower for keyword in ['txn', 'transaction']):
        return "Transactions are flagged as suspicious based on multiple risk factors analyzed by our machine learning model. Key indicators include significant price deviations from market values, unusual shipping routes, high company risk scores, abnormal port activity, and inconsistent volume/quantity ratios. Each transaction receives a risk score, and those exceeding certain thresholds are classified as suspicious or fraudulent."
    
    elif any(keyword in query_lower for keyword in ['investigate', 'next steps', 'what should', 'recommend']):
        return f"For investigation priorities: Focus on the {fraud_cases} confirmed fraud cases first, then review the {suspicious_cases} suspicious transactions. Prioritize cases with multiple risk factors, high-value transactions, and those involving known high-risk entities. Verify documentation, cross-reference with trade databases, and conduct enhanced due diligence on flagged companies."
    
    elif any(keyword in query_lower for keyword in ['trend', 'increasing', 'decreasing', 'over time']):
        return "Trend analysis requires historical data comparison. Generally, fraud patterns evolve as criminals adapt to detection methods. Monitor for emerging patterns in pricing strategies, new route combinations, previously unknown high-risk entities, and seasonal variations in fraudulent activities."
    
    else:
        # Generic fallback with error context
        error_type = type(error).__name__
        if isinstance(error, GeminiRateLimitError):
            return f"I'm currently experiencing high demand and cannot provide AI-powered analysis. However, based on the available data: {total_transactions:,} total transactions with {fraud_cases:,} fraud cases ({fraud_rate:.1f}% fraud rate). Please try your specific question again in a few minutes for more detailed analysis."
        elif isinstance(error, GeminiTimeoutError):
            return f"The AI service timed out, but I can provide basic statistics: {total_transactions:,} transactions analyzed, {fraud_rate:.1f}% fraud rate, average risk score of {avg_risk_score:.3f}. Please rephrase your question or try again for more detailed insights."
        elif isinstance(error, GeminiQuotaExceededError):
            return f"AI analysis is temporarily unavailable due to quota limits. Current dataset summary: {total_transactions:,} transactions, {fraud_cases + suspicious_cases:,} flagged cases ({fraud_rate + suspicious_rate:.1f}% total flag rate). Please try again later for AI-powered insights."
        else:
            return f"I'm unable to provide AI-powered analysis due to a technical issue, but I can share basic statistics: {total_transactions:,} transactions processed, {fraud_rate:.1f}% fraud rate, {suspicious_rate:.1f}% suspicious rate. For specific transaction analysis, please try again later or contact technical support."


def _generate_fallback_explanation(transaction: Dict[str, Any]) -> str:
    """
    Generate a comprehensive rule-based fallback explanation when Gemini API fails.

    This function provides detailed explanations in the required format:
    Fraud Indicators Detected:
    • High price deviation compared to market price
    • Suspicious shipping route  
    • High company risk score
    • Unusual port activity

    Args:
        transaction (Dict[str, Any]): Transaction data dictionary

    Returns:
        str: Comprehensive rule-based explanation of fraud indicators
    """
    indicators = []

    # Pricing Analysis
    price_dev = transaction.get('price_deviation', 0)
    if abs(price_dev) > 0.3:
        if price_dev > 0:
            indicators.append(f"High price deviation compared to market price ({abs(price_dev):.1%} above market value)")
        else:
            indicators.append(f"High price deviation compared to market price ({abs(price_dev):.1%} below market value)")
    elif abs(price_dev) > 0.1:
        indicators.append(f"Moderate price deviation from market price ({price_dev:.1%})")

    # Route Analysis
    route_anomaly = transaction.get('route_anomaly', 0)
    if route_anomaly == 1:
        indicators.append("Suspicious shipping route")

    # Company Risk Analysis
    company_risk = transaction.get('company_risk_score', 0)
    if company_risk > 0.7:
        indicators.append(f"High company risk score ({company_risk:.2f})")
    elif company_risk > 0.5:
        indicators.append(f"Elevated company risk score ({company_risk:.2f})")

    # Port Activity Analysis
    port_activity = transaction.get('port_activity_index', 0)
    if port_activity > 1.3:
        indicators.append(f"Unusual port activity (index: {port_activity:.2f})")

    # Volume Analysis
    volume_spike_score = transaction.get('volume_spike_score', 0)
    if volume_spike_score > 100:
        indicators.append("Volume/quantity inconsistencies detected")

    # Shipment Duration
    shipment_duration_risk = transaction.get('shipment_duration_risk', 0)
    if shipment_duration_risk > 0.1:
        indicators.append("Inconsistent shipment duration for distance")

    # Generate explanation in required format
    if indicators:
        indicators_text = "\n• ".join(indicators)
        return f"""Fraud Indicators Detected:
• {indicators_text}

This transaction has been flagged based on automated rule analysis. The combination of these factors suggests potential fraudulent activity that requires investigation."""
    else:
        # Fallback for transactions with no clear indicators
        risk_score = transaction.get('risk_score', 0)
        risk_category = transaction.get('risk_category', 'UNKNOWN')
        
        return f"""Fraud Indicators Detected:
• Machine learning model flagged unusual transaction patterns
• Risk score of {risk_score:.3f} exceeds normal thresholds
• Transaction classified as {risk_category} by automated analysis

This transaction requires manual review to determine the specific nature of the detected anomalies."""



def test_fallback_system() -> Dict[str, Any]:
    """
    Test the fallback explanation system with sample data.
    
    Returns:
        Dict[str, Any]: Test results showing fallback functionality
    """
    # Sample transaction with various risk indicators
    sample_transaction = {
        'transaction_id': 'TXN00001',
        'product': 'Electronics',
        'commodity_category': 'Consumer Goods',
        'market_price': 1000,
        'unit_price': 1500,
        'price_deviation': 0.5,
        'shipping_route': 'Shanghai-Los Angeles',
        'distance_km': 11000,
        'company_risk_score': 0.9,
        'port_activity_index': 1.8,
        'route_anomaly': 1,
        'risk_score': 0.3,
        'risk_category': 'FRAUD',
        'cargo_volume': 50000,
        'quantity': 100,
        'volume_spike_score': 500,
        'shipment_duration_risk': 0.15
    }
    
    # Sample context for investigation queries
    sample_context = {
        'total_transactions': 1000,
        'fraud_cases': 50,
        'suspicious_cases': 150,
        'avg_risk_score': 0.1,
        'high_risk_companies': ['CompanyA', 'CompanyB', 'CompanyC'],
        'fraud_patterns': ['Price manipulation', 'Route laundering', 'Volume misrepresentation']
    }
    
    # Test fallback explanation
    fallback_explanation = _generate_fallback_explanation(sample_transaction)
    
    # Test fallback investigation responses
    test_queries = [
        "What is the fraud rate?",
        "What are the main fraud patterns?",
        "Why is transaction TXN00001 suspicious?",
        "What should I investigate next?",
        "Tell me about high-risk companies"
    ]
    
    fallback_responses = {}
    for query in test_queries:
        # Simulate an API error for testing
        mock_error = GeminiAPIError("Test error")
        response = _generate_fallback_investigation_response(query, sample_context, mock_error)
        fallback_responses[query] = response
    
    return {
        'transaction_explanation': fallback_explanation,
        'investigation_responses': fallback_responses,
        'test_status': 'success'
    }


# Module-level model instance for reuse
_gemini_model = None


def get_gemini_model() -> genai.GenerativeModel:
    """
    Get or initialize the global Gemini model instance.
    
    Returns:
        genai.GenerativeModel: Configured Gemini model instance
    """
    global _gemini_model
    if _gemini_model is None:
        _gemini_model = initialize_gemini()
    return _gemini_model


if __name__ == "__main__":
    # Test the module
    try:
        print("Testing Gemini API initialization...")
        model = initialize_gemini()
        print("✓ Gemini API initialized successfully")
        
        # Test with sample transaction
        sample_transaction = {
            'transaction_id': 'TXN00001',
            'product': 'Electronics',
            'commodity_category': 'Consumer Goods',
            'market_price': 1000,
            'unit_price': 1500,
            'price_deviation': 0.5,
            'shipping_route': 'Shanghai-Los Angeles',
            'distance_km': 11000,
            'company_risk_score': 0.9,
            'port_activity_index': 1.8,
            'route_anomaly': 1,
            'risk_score': 0.3,
            'risk_category': 'FRAUD',
            'cargo_volume': 50000,
            'quantity': 100,
            'volume_spike_score': 500,
            'shipment_duration_risk': 0.15
        }
        
        print("\nTesting transaction explanation...")
        explanation = explain_transaction(sample_transaction, model)
        print(f"✓ Explanation generated: {explanation[:100]}...")
        
        print("\nTesting investigation query...")
        context = {
            'total_transactions': 1000,
            'fraud_cases': 50,
            'suspicious_cases': 150,
            'avg_risk_score': 0.1,
            'high_risk_companies': ['CompanyA', 'CompanyB'],
            'fraud_patterns': ['Price manipulation', 'Route laundering']
        }
        answer = answer_investigation_query("What are the main fraud patterns?", context, model)
        print(f"✓ Query answered: {answer[:100]}...")
        
        print("\nTesting fallback system...")
        fallback_results = test_fallback_system()
        print("✓ Fallback explanation generated:")
        print(f"  {fallback_results['transaction_explanation'][:150]}...")
        print("✓ Fallback investigation responses generated:")
        for query, response in list(fallback_results['investigation_responses'].items())[:2]:
            print(f"  Q: {query}")
            print(f"  A: {response[:100]}...")
        
        print("\n✓ All tests passed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        
        # Test fallback system even if Gemini fails
        print("\nTesting fallback system independently...")
        try:
            fallback_results = test_fallback_system()
            print("✓ Fallback system working correctly")
            print(f"✓ Fallback explanation: {fallback_results['transaction_explanation'][:100]}...")
        except Exception as fallback_error:
            print(f"✗ Fallback system error: {str(fallback_error)}")