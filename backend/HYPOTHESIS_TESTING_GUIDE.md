# Hypothesis Testing Framework Guide
## TRINETRA AI - Property-Based Testing Setup

This guide explains the hypothesis testing framework setup for validating the 5 correctness properties defined in the TRINETRA AI requirements.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Framework Configuration](#framework-configuration)
4. [Correctness Properties](#correctness-properties)
5. [Running Tests](#running-tests)
6. [Writing New Property Tests](#writing-new-property-tests)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### What is Property-Based Testing?

Property-based testing (PBT) is a testing methodology where you define **properties** (universal truths) that should hold for all inputs, and the testing framework automatically generates hundreds of test cases to verify these properties.

Unlike traditional example-based testing where you write specific test cases, PBT:
- **Generates diverse test inputs** automatically
- **Finds edge cases** you might not think of
- **Shrinks failing examples** to minimal reproducible cases
- **Stores failing examples** for regression testing

### Why Hypothesis?

[Hypothesis](https://hypothesis.readthedocs.io/) is the leading property-based testing library for Python. It provides:
- Rich strategies for generating test data
- Intelligent shrinking of failing examples
- Database for storing examples
- Integration with pytest
- Excellent documentation and community support

---

## Installation

Hypothesis is already included in the project's `requirements.txt`:

```bash
# Install all dependencies including hypothesis
pip install -r requirements.txt
```

To verify installation:

```bash
python -c "import hypothesis; print(hypothesis.__version__)"
```

Expected output: `6.88.1` or higher

---

## Framework Configuration

### Configuration Files

#### 1. `conftest.py` - Pytest Configuration

Located at `backend/conftest.py`, this file provides:

- **Hypothesis Profiles**: Pre-configured test profiles for different scenarios
- **Shared Fixtures**: Reusable test data and resources
- **Custom Markers**: Tags for organizing tests
- **Utility Functions**: Helper functions for assertions

**Available Hypothesis Profiles:**

| Profile | Examples | Deadline | Use Case |
|---------|----------|----------|----------|
| `trinetra_default` | 50 | 30s | Standard testing |
| `trinetra_quick` | 10 | 10s | Fast feedback during development |
| `trinetra_thorough` | 200 | 60s | Comprehensive validation before release |
| `ci` | 20 | 20s | Continuous integration pipelines |

**To use a specific profile:**

```bash
# Set environment variable
export HYPOTHESIS_PROFILE=trinetra_thorough

# Or pass to pytest
pytest --hypothesis-profile=trinetra_thorough
```

#### 2. `pytest.ini` - Pytest Settings

Located at project root, configures:
- Test discovery patterns
- Coverage reporting
- Custom markers
- Warning filters

#### 3. `.hypothesis/` Directory

Hypothesis stores generated examples in `.hypothesis/` for:
- **Regression testing**: Re-run previously failing examples
- **Example database**: Track which inputs have been tested
- **Reproducibility**: Ensure consistent test behavior

---

## Correctness Properties

The TRINETRA AI system validates 5 correctness properties:

### CP-1: Data Integrity

**Property:** All loaded transactions must have valid `transaction_id`, `date`, and `fraud_label`

**Test File:** `test_data_integrity_property.py`

**Test Strategy:**
- Generate random row indices
- Validate required fields are non-null
- Test with various CSV formats
- Detect data corruption

**Key Tests:**
- `test_data_integrity_random_rows`: Random sampling validation
- `test_data_integrity_various_csv_formats`: Format compatibility
- `test_data_integrity_sample_validation`: Sample-based validation
- `test_data_integrity_corruption_detection`: Error detection

### CP-2: Risk Score Consistency

**Property:** Risk scores must be monotonically related to risk categories (SAFE < SUSPICIOUS < FRAUD)

**Test File:** `test_risk_score_consistency_property.py`

**Test Strategy:**
- Generate various risk scores
- Verify SAFE < SUSPICIOUS < FRAUD ordering
- Test boundary conditions (-0.2 and 0.2 thresholds)

**Key Tests:**
- `test_risk_score_monotonic_relationship`: Ordering validation
- `test_risk_score_boundary_conditions`: Threshold testing
- `test_risk_classification_with_generated_data`: Synthetic data validation
- `test_risk_score_ordering_property`: Pairwise ordering

### CP-3: Feature Engineering Correctness

**Property:** Engineered features must be mathematically correct and within expected ranges

**Test File:** `test_feature_correctness_property.py`

**Test Strategy:**
- Test with known input values
- Verify mathematical calculations
- Check feature ranges are reasonable
- Test edge cases (zero values, negative numbers)

**Key Tests:**
- `test_price_anomaly_score_mathematical_correctness`: abs(price_deviation)
- `test_route_risk_score_mathematical_correctness`: route_anomaly assignment
- `test_company_network_risk_mathematical_correctness`: company_risk_score assignment
- `test_port_congestion_score_mathematical_correctness`: port_activity_index assignment
- `test_shipment_duration_risk_mathematical_correctness`: duration / distance
- `test_volume_spike_score_mathematical_correctness`: volume / quantity
- `test_division_by_zero_edge_cases`: Zero denominator handling
- `test_feature_ranges_are_reasonable`: Range validation

### CP-4: API Response Validity

**Property:** All API endpoints must return valid JSON with expected schema

**Test File:** `test_api_response_validity_property.py`

**Test Strategy:**
- Test all endpoints with various inputs
- Validate JSON schema compliance
- Test error response formats
- Verify HTTP status codes

**Key Tests:**
- `test_api_response_schema_validity`: Schema validation
- `test_api_error_responses`: Error handling
- `test_api_pagination`: Pagination logic
- `test_api_filtering`: Filter functionality

### CP-5: Alert Trigger Accuracy

**Property:** Alerts must be triggered if and only if threshold conditions are met

**Test File:** `test_alert_trigger_property.py`

**Test Strategy:**
- Generate transactions at boundary conditions
- Verify alerts triggered correctly
- Test alert combinations
- Validate threshold logic

**Key Tests:**
- `test_alert_trigger_price_deviation`: price_deviation > 0.5
- `test_alert_trigger_route_anomaly`: route_anomaly == 1
- `test_alert_trigger_company_risk`: company_risk_score > 0.8
- `test_alert_trigger_port_activity`: port_activity_index > 1.5
- `test_alert_combinations`: Multiple alert conditions

---

## Running Tests

### Run All Property Tests

```bash
# Run all 5 correctness properties with default profile
python backend/run_all_property_tests.py

# Run with quick profile (faster)
python backend/run_all_property_tests.py --profile trinetra_quick

# Run with thorough profile (comprehensive)
python backend/run_all_property_tests.py --profile trinetra_thorough

# Run with verbose output
python backend/run_all_property_tests.py --verbose

# Generate markdown report
python backend/run_all_property_tests.py --report
```

### Run Individual Property Tests

```bash
# CP-1: Data Integrity
pytest backend/test_data_integrity_property.py -v

# CP-2: Risk Score Consistency
pytest backend/test_risk_score_consistency_property.py -v

# CP-3: Feature Engineering Correctness
pytest backend/test_feature_correctness_property.py -v

# CP-4: API Response Validity
pytest backend/test_api_response_validity_property.py -v

# CP-5: Alert Trigger Accuracy
pytest backend/test_alert_trigger_property.py -v
```

### Run Tests by Marker

```bash
# Run all property-based tests
pytest -m property

# Run specific correctness property
pytest -m cp1  # Data Integrity
pytest -m cp2  # Risk Score Consistency
pytest -m cp3  # Feature Engineering Correctness
pytest -m cp4  # API Response Validity
pytest -m cp5  # Alert Trigger Accuracy
```

### Run with Coverage

```bash
# Run with coverage report
pytest backend/test_*_property.py --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

---

## Writing New Property Tests

### Basic Structure

```python
from hypothesis import given, strategies as st, settings, example
import pytest

class TestMyProperty:
    """Property-based tests for my feature."""
    
    @given(
        # Define input strategies
        my_input=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=50, deadline=10000)
    @example(my_input=0)  # Explicit edge case
    @example(my_input=100)  # Another edge case
    def test_my_property(self, my_input: int):
        """
        **Validates: Requirements X.Y**
        
        Property: Description of the property being tested
        
        Test Strategy: How the property is validated
        """
        # Arrange
        # ... setup code ...
        
        # Act
        result = my_function(my_input)
        
        # Assert
        assert result >= 0, "Result must be non-negative"
```

### Common Hypothesis Strategies

```python
from hypothesis import strategies as st

# Integers
st.integers(min_value=0, max_value=100)

# Floats
st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)

# Strings
st.text(min_size=1, max_size=100)

# Lists
st.lists(st.integers(), min_size=1, max_size=50)

# Tuples
st.tuples(st.floats(), st.integers())

# Dictionaries
st.fixed_dictionaries({
    'key1': st.integers(),
    'key2': st.text()
})

# Sampling from options
st.sampled_from(['option1', 'option2', 'option3'])

# DataFrames (requires hypothesis.extra.pandas)
from hypothesis.extra.pandas import data_frames, columns
data_frames([
    columns(['col1'], dtype=int),
    columns(['col2'], dtype=float)
])
```

### Using Fixtures

```python
def test_with_fixture(self, sample_dataset):
    """Use shared fixtures from conftest.py"""
    assert len(sample_dataset) > 0
```

### Best Practices

1. **Use `@example` for edge cases**: Explicitly test boundary values
2. **Set reasonable deadlines**: Prevent tests from hanging
3. **Use `assume()` to filter inputs**: Skip invalid test cases
4. **Add descriptive docstrings**: Document what property is being tested
5. **Use markers**: Tag tests with appropriate markers (cp1, cp2, etc.)
6. **Keep properties simple**: Test one property per test function
7. **Use fixtures for setup**: Reuse common test data

---

## Troubleshooting

### Common Issues

#### 1. Tests Timeout

**Problem:** Tests exceed deadline

**Solution:**
```python
@settings(deadline=60000)  # Increase to 60 seconds
```

Or use a faster profile:
```bash
python backend/run_all_property_tests.py --profile trinetra_quick
```

#### 2. Flaky Tests

**Problem:** Tests pass sometimes, fail other times

**Solution:**
- Use `@example()` to capture failing cases
- Check for non-deterministic behavior
- Use fixed random seeds where appropriate
- Review hypothesis database for stored examples

#### 3. Too Many Examples

**Problem:** Tests take too long

**Solution:**
```python
@settings(max_examples=10)  # Reduce number of examples
```

#### 4. Dataset Not Found

**Problem:** `pytest.skip: Dataset not found`

**Solution:**
- Ensure dataset exists at `data/trinetra_trade_fraud_dataset_1000_rows_complex.csv`
- Check file permissions
- Verify working directory

#### 5. Model Not Found

**Problem:** `pytest.skip: Trained model not found`

**Solution:**
- Train the model first: `python backend/model.py`
- Ensure model exists at `models/isolation_forest.pkl`
- Check model loading logic

### Debugging Tips

1. **Use `--hypothesis-show-statistics`**:
   ```bash
   pytest --hypothesis-show-statistics
   ```

2. **Print generated examples**:
   ```python
   @given(x=st.integers())
   def test_something(self, x):
       print(f"Testing with x={x}")
       # ... test code ...
   ```

3. **Use `--hypothesis-seed`** for reproducibility:
   ```bash
   pytest --hypothesis-seed=12345
   ```

4. **Check hypothesis database**:
   ```bash
   ls -la backend/.hypothesis/examples/
   ```

5. **Run with verbose output**:
   ```bash
   pytest -vv --tb=long
   ```

---

## Additional Resources

### Documentation

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Hypothesis Strategies](https://hypothesis.readthedocs.io/en/latest/data.html)
- [Pytest Documentation](https://docs.pytest.org/)

### Examples

- See existing test files in `backend/test_*_property.py`
- Review `conftest.py` for fixtures and utilities
- Check `run_all_property_tests.py` for test orchestration

### Support

For issues or questions:
1. Check this guide first
2. Review hypothesis documentation
3. Examine existing test files for patterns
4. Check hypothesis database for stored examples

---

## Summary

The hypothesis testing framework for TRINETRA AI provides:

✅ **Automated test generation** for 5 correctness properties  
✅ **Comprehensive validation** with configurable test profiles  
✅ **Regression testing** with example database  
✅ **Easy integration** with pytest and CI/CD  
✅ **Detailed reporting** with markdown output  

**Next Steps:**
1. Run all property tests: `python backend/run_all_property_tests.py`
2. Review test results and reports
3. Add new property tests as needed
4. Integrate into CI/CD pipeline

---

*Last Updated: 2024*
*TRINETRA AI - Trade Fraud Intelligence System*
