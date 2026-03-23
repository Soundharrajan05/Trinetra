# Gemini API Mocking Guide for TRINETRA AI

This guide explains how to use the comprehensive Gemini API mocking system for offline testing in the TRINETRA AI fraud detection system.

## Overview

The mocking system provides:
- **Offline Testing**: Run unit tests without internet connection
- **Realistic Responses**: Mock responses that simulate real Gemini API behavior
- **Error Simulation**: Test error handling with various failure scenarios
- **Performance Testing**: Consistent, fast test execution
- **Integration Testing**: Works with existing session management and caching

## Files

### Core Mocking Files
- `backend/mock_gemini_utils.py` - Reusable mock utilities and classes
- `backend/test_gemini_mocking_unit.py` - Focused unit tests for mocking
- `backend/test_ai_explainer_mocking.py` - Comprehensive mocking tests
- `backend/GEMINI_MOCKING_GUIDE.md` - This documentation

### Integration with Existing Tests
- `backend/test_ai_explainer.py` - Updated to use comprehensive mocking
- `backend/test_ai_explainer_unit.py` - Existing unit tests

## Quick Start

### Basic Mocking Example

```python
import pytest
from unittest.mock import patch, MagicMock
from backend.ai_explainer import explain_transaction

class MockGeminiResponse:
    def __init__(self, text: str):
        self.text = text

@patch('backend.ai_explainer.GEMINI_AVAILABLE', True)
@patch('backend.ai_explainer.genai')
def test_basic_mocking(mock_genai):
    # Configure mock
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    mock_model.generate_content.side_effect = [
        MockGeminiResponse("OK"),  # For initialization
        MockGeminiResponse("This transaction shows suspicious pricing patterns.")
    ]
    
    # Test transaction explanation
    transaction = {'transaction_id': 'TXN001', 'price_deviation': 0.5}
    explanation = explain_transaction(transaction, force_api=True)
    
    assert "suspicious" in explanation.lower()
```

### Using Mock Utilities

```python
from backend.mock_gemini_utils import (
    mock_gemini_success, create_sample_transaction, 
    validate_mock_explanation
)

def test_with_utilities():
    with mock_gemini_success():
        transaction = create_sample_transaction("high")
        explanation = explain_transaction(transaction, force_api=True)
        
        assert validate_mock_explanation(explanation, transaction)
```

## Mocking Patterns

### 1. Successful API Calls

```python
@patch('backend.ai_explainer.GEMINI_AVAILABLE', True)
@patch('backend.ai_explainer.genai')
def test_successful_api_call(mock_genai):
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    mock_model.generate_content.return_value = MockGeminiResponse("Success response")
    
    # Your test code here
```

### 2. API Failures

```python
@patch('backend.ai_explainer.GEMINI_AVAILABLE', True)
@patch('backend.ai_explainer.genai')
def test_api_failure(mock_genai):
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    mock_model.generate_content.side_effect = [
        MockGeminiResponse("OK"),  # Init success
        Exception("API Error")    # Explanation fails
    ]
    
    # Test should handle error gracefully
```

### 3. Gemini Unavailable

```python
@patch('backend.ai_explainer.GEMINI_AVAILABLE', False)
def test_gemini_unavailable():
    # Test fallback behavior when Gemini is not available
    model = initialize_gemini()
    # Should work with mock implementation
```

## Realistic Mock Responses

The mocking system generates realistic responses based on transaction data:

### Transaction Explanations

For a transaction with high price deviation:
```python
transaction = {
    'price_deviation': 0.6,  # 60% deviation
    'route_anomaly': 1,
    'company_risk_score': 0.8
}
```

Mock generates:
```
"This transaction exhibits price manipulation with 60% deviation above market value, 
indicating potential over-invoicing fraud. The unusual shipping route suggests trade 
route laundering. High company risk score of 0.8 indicates previous suspicious activity."
```

### Investigation Queries

For query "What is the fraud rate?" with context:
```python
context = {
    'total_transactions': 1000,
    'fraud_cases': 50,
    'suspicious_cases': 100
}
```

Mock generates:
```
"Based on current analysis, 5.0% of transactions are fraudulent (50 out of 1,000). 
Main patterns include price manipulation and route laundering."
```

## Error Simulation

### Rate Limit Errors
```python
mock_model.generate_content.side_effect = Exception("Rate limit exceeded")
```

### Timeout Errors
```python
mock_model.generate_content.side_effect = Exception("Request timeout")
```

### Authentication Errors
```python
mock_genai.configure.side_effect = Exception("Invalid API key")
```

## Integration with Existing Features

### Session Management
```python
def test_session_limits_with_mocking():
    with mock_gemini_success():
        # Exhaust session limit
        for _ in range(MAX_EXPLANATIONS_PER_SESSION):
            increment_session_count()
        
        # Should return quota exceeded message
        explanation = explain_transaction(transaction)
        assert "limit reached" in explanation.lower()
```

### Caching System
```python
def test_caching_with_mocking():
    with mock_gemini_success():
        # First call generates and caches
        explanation1 = explain_transaction(transaction, force_api=True)
        
        # Second call uses cache
        explanation2 = explain_transaction(transaction)
        
        assert explanation1 == explanation2
```

## Best Practices

### 1. Use Appropriate Mock Scope
- Use `@patch` decorators for individual tests
- Use context managers (`with mock_gemini_success():`) for test blocks
- Reset state between tests with `setup_method()`

### 2. Mock Realistic Scenarios
```python
# Good: Realistic transaction data
transaction = {
    'transaction_id': 'TXN001',
    'price_deviation': 0.5,
    'route_anomaly': 1,
    'company_risk_score': 0.8
}

# Bad: Empty or unrealistic data
transaction = {}
```

### 3. Test Both Success and Failure Cases
```python
def test_comprehensive_scenarios():
    # Test successful API call
    with mock_gemini_success():
        explanation = explain_transaction(transaction, force_api=True)
        assert len(explanation) > 50
    
    # Test API failure
    with mock_gemini_failure("rate_limit"):
        explanation = explain_transaction(transaction, force_api=True)
        assert "fraud" in explanation.lower()  # Should use fallback
```

### 4. Validate Mock Responses
```python
from backend.mock_gemini_utils import validate_mock_explanation

def test_response_quality():
    with mock_gemini_success():
        explanation = explain_transaction(transaction, force_api=True)
        assert validate_mock_explanation(explanation, transaction)
```

## Running Tests

### Run All Mocking Tests
```bash
python -m pytest backend/test_gemini_mocking_unit.py -v
```

### Run Specific Test Class
```bash
python -m pytest backend/test_gemini_mocking_unit.py::TestGeminiMockingBasics -v
```

### Run with Coverage
```bash
python -m pytest backend/test_gemini_mocking_unit.py --cov=backend.ai_explainer
```

## Troubleshooting

### Common Issues

1. **TEST_MODE Interference**
   - Ensure `os.environ["TEST_MODE"] = "false"` in test files
   - TEST_MODE overrides mocking with simple responses

2. **Mock Not Applied**
   - Check patch target: `'backend.ai_explainer.genai'`
   - Ensure GEMINI_AVAILABLE is patched to True

3. **Inconsistent Responses**
   - Reset session state in `setup_method()`
   - Clear explanation cache between tests

4. **Import Errors**
   - Ensure backend directory is in Python path
   - Check relative imports in test files

### Debug Tips

1. **Check Mock Calls**
```python
assert mock_model.generate_content.call_count == 2
print(mock_model.generate_content.call_args_list)
```

2. **Verify Mock Configuration**
```python
assert mock_genai.configure.called
assert mock_genai.GenerativeModel.called
```

3. **Test Fallback Behavior**
```python
# Force error to test fallback
mock_model.generate_content.side_effect = Exception("Test error")
explanation = explain_transaction(transaction, force_api=True)
# Should not raise exception, should return fallback
```

## Advanced Usage

### Custom Mock Responses
```python
class CustomMockResponse:
    def __init__(self, text: str, metadata: dict = None):
        self.text = text
        self.metadata = metadata or {}

def test_custom_response():
    custom_response = CustomMockResponse(
        "Custom fraud analysis response",
        {"confidence": 0.95}
    )
    mock_model.generate_content.return_value = custom_response
```

### Conditional Mocking
```python
def conditional_mock_response(prompt):
    if "fraud rate" in prompt.lower():
        return MockGeminiResponse("Fraud rate is 5%")
    elif "patterns" in prompt.lower():
        return MockGeminiResponse("Main patterns: price manipulation")
    else:
        return MockGeminiResponse("General analysis response")

mock_model.generate_content.side_effect = conditional_mock_response
```

### Performance Testing
```python
import time

def test_mock_performance():
    start_time = time.time()
    
    with mock_gemini_success():
        for i in range(100):
            transaction = {'transaction_id': f'TXN_{i:03d}'}
            explanation = explain_transaction(transaction, force_api=True)
    
    duration = time.time() - start_time
    assert duration < 1.0  # Should be very fast with mocking
```

## Conclusion

The Gemini API mocking system enables:
- **Reliable offline testing** without external dependencies
- **Realistic test scenarios** with contextual responses
- **Comprehensive error testing** with various failure modes
- **Fast test execution** for continuous integration
- **Integration testing** with existing system features

Use this mocking system to ensure your fraud detection tests are reliable, fast, and comprehensive while maintaining realistic behavior that matches the actual Gemini API integration.