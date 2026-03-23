# TRINETRA AI Error Handlers Usage Guide

This document provides examples of how to use the comprehensive error handling utilities implemented in `utils/helpers.py`.

## Overview

The error handling system provides:
1. **API Error Handlers** - For Gemini API failures and network issues
2. **Data Validation Error Handlers** - For CSV loading and schema validation
3. **Model Error Handlers** - For training failures and prediction errors
4. **File System Error Handlers** - For model loading/saving and data file access
5. **General Application Error Handlers** - For any other application errors

## Quick Start

```python
from utils.helpers import error_handlers, safe_execute, retry_on_failure, handle_with_fallback

# Global error handler instance is available as 'error_handlers'
```

## Usage Examples

### 1. API Error Handling (Gemini API)

```python
# In ai_explainer.py or any module using Gemini API
try:
    response = gemini_model.generate_content(prompt)
    return response.text
except Exception as e:
    result = error_handlers.handle_gemini_api_error(e, "transaction explanation")
    
    if result['should_retry']:
        # Implement retry logic with exponential backoff
        time.sleep(result['retry_delay'])
        # Retry the operation
    else:
        # Use fallback content
        return result['fallback_content']
```

### 2. Data Loading Error Handling

```python
# In data_loader.py
try:
    df = pd.read_csv(file_path)
    return df
except Exception as e:
    result = error_handlers.handle_csv_loading_error(e, file_path)
    
    # Log user-friendly message
    logger.error(result['user_message'])
    
    # Show suggestions to user
    for suggestion in result['suggested_actions']:
        logger.info(f"Suggestion: {suggestion}")
    
    raise Exception(result['user_message'])
```

### 3. Model Error Handling

```python
# In model.py for training errors
try:
    model = IsolationForest(**params)
    model.fit(X_train)
    return model
except Exception as e:
    result = error_handlers.handle_model_training_error(e, "IsolationForest", len(X_train.columns))
    
    if result['can_retry']:
        # Implement recovery actions
        for action in result['recovery_actions']:
            logger.info(f"Recovery action: {action}")
    
    raise Exception(result['user_message'])

# In fraud_detection.py for prediction errors
try:
    predictions = model.predict(X)
    return predictions
except Exception as e:
    result = error_handlers.handle_model_prediction_error(e, X.shape, "IsolationForest")
    
    # Use fallback scores if available
    if result['fallback_scores'] is not None:
        logger.warning("Using fallback risk scores due to prediction error")
        return result['fallback_scores']
    
    raise Exception(result['user_message'])
```

### 4. File System Error Handling

```python
# For model loading/saving
try:
    model = joblib.load(model_path)
    return model
except Exception as e:
    result = error_handlers.handle_file_system_error(e, model_path, "load")
    
    if result['can_retrain']:
        logger.info("Model file not found, will retrain automatically")
        # Trigger model retraining
    else:
        logger.error(result['user_message'])
        for suggestion in result['suggested_actions']:
            logger.info(f"Suggestion: {suggestion}")
    
    return None
```

### 5. Network Error Handling

```python
# In api.py for external API calls
try:
    response = requests.get(external_api_url, timeout=10)
    return response.json()
except Exception as e:
    result = error_handlers.handle_network_error(e, "external_api", retry_count=0)
    
    if result['should_retry']:
        time.sleep(result['retry_delay'])
        # Retry the request
    else:
        logger.error(result['user_message'])
        return None
```

## Convenience Functions

### Safe Execute
```python
# Execute function with automatic error handling
def risky_operation():
    # Some operation that might fail
    return process_data()

success, result, error_info = safe_execute(
    risky_operation, 
    default_return=None,
    context="data processing"
)

if success:
    print(f"Operation succeeded: {result}")
else:
    print(f"Operation failed: {error_info['user_message']}")
```

### Retry on Failure
```python
# Automatically retry failed operations
def unreliable_api_call():
    # API call that might fail
    return call_external_service()

try:
    result = retry_on_failure(
        unreliable_api_call,
        max_retries=3,
        delay=1.0,
        backoff_factor=2.0,
        context="external API"
    )
    print(f"API call succeeded: {result}")
except Exception as e:
    print(f"API call failed after all retries: {e}")
```

### Handle with Fallback
```python
# Execute with automatic fallback value
def get_user_preferences():
    # Might fail to load user preferences
    return load_preferences_from_db()

preferences = handle_with_fallback(
    get_user_preferences,
    fallback_value={'theme': 'dark', 'language': 'en'},
    context="user preferences"
)
```

## Error Statistics and Monitoring

```python
# Get error statistics for monitoring
stats = error_handlers.get_error_statistics()
print(f"Total errors: {stats['total_errors']}")
print(f"Most common errors: {stats['most_common_errors']}")

# Reset error counters (useful for testing)
error_handlers.reset_error_counts()
```

## Schema Validation Error Handling

```python
# In data_loader.py for schema validation
from utils.helpers import ValidationHelpers

validation_result = ValidationHelpers.validate_dataset_schema(df, strict=True)
if not validation_result['valid']:
    result = error_handlers.handle_schema_validation_error(validation_result, "dataset loading")
    
    if result['can_continue']:
        logger.warning(result['user_message'])
        # Continue with warnings
    else:
        logger.error(result['user_message'])
        # Stop processing
        raise Exception(result['user_message'])
```

## Integration with Existing Modules

The error handlers are designed to work seamlessly with existing TRINETRA AI modules:

- **data_loader.py**: Use CSV loading and schema validation error handlers
- **model.py**: Use model training and loading error handlers  
- **fraud_detection.py**: Use model prediction and file system error handlers
- **ai_explainer.py**: Use Gemini API and network error handlers
- **api.py**: Use network and general application error handlers

## Best Practices

1. **Always use user-friendly messages**: The error handlers provide both technical and user-friendly messages
2. **Implement retry logic**: Use the retry recommendations from error handlers
3. **Provide fallback values**: Use fallback content when primary operations fail
4. **Log comprehensive context**: Include context information in error handling calls
5. **Monitor error statistics**: Use error statistics for system health monitoring
6. **Handle graceful degradation**: Use fallback mechanisms to keep the system functional

## Error Handler Configuration

The error handlers use configurable thresholds and settings:

```python
from utils.helpers import ConfigurationHelpers

# Get current thresholds
risk_thresholds = ConfigurationHelpers.get_risk_thresholds()
alert_thresholds = ConfigurationHelpers.get_alert_thresholds()
display_settings = ConfigurationHelpers.get_display_settings()
```

This comprehensive error handling system ensures that TRINETRA AI can handle failures gracefully while providing meaningful feedback to users and maintaining system stability.