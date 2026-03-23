# Test Data Generators Guide
## TRINETRA AI - Trade Fraud Intelligence System

This guide explains how to use the test data generators for property-based testing with Hypothesis.

## Overview

The `test_data_generators.py` module provides comprehensive Hypothesis strategies for generating realistic test data to support all five correctness properties (CP-1 through CP-5) defined in the requirements.

## Table of Contents

1. [Basic Field Generators](#basic-field-generators)
2. [Numeric Field Generators](#numeric-field-generators)
3. [Risk Score Generators (CP-2)](#risk-score-generators-cp-2)
4. [Alert Threshold Generators (CP-5)](#alert-threshold-generators-cp-5)
5. [Composite Transaction Generators](#composite-transaction-generators)
6. [DataFrame Generators](#dataframe-generators)
7. [API Response Generators (CP-4)](#api-response-generators-cp-4)
8. [Edge Case Generators](#edge-case-generators)
9. [Usage Examples](#usage-examples)

---

## Basic Field Generators

### `transaction_id_strategy()`
Generates valid transaction IDs in the format `TXN00000` to `TXN99999`.

```python
from hypothesis import given
from test_data_generators import transaction_id_strategy

@given(txn_id=transaction_id_strategy())
def test_transaction_id(txn_id):
    assert txn_id.startswith('TXN')
    assert len(txn_id) == 8
```

### `date_strategy()`
Generates dates between 2020-01-01 and 2024-12-31 in YYYY-MM-DD format.

```python
@given(date=date_strategy())
def test_date_format(date):
    assert len(date) == 10
    assert '-' in date
```

### `fraud_label_strategy()`
Generates fraud labels (0 or 1).

```python
@given(label=fraud_label_strategy())
def test_fraud_label(label):
    assert label in [0, 1]
```

### Other Basic Generators
- `product_strategy()` - Product names (Electronics, Textiles, etc.)
- `commodity_category_strategy()` - Commodity categories
- `country_strategy()` - Country names
- `company_strategy()` - Company names
- `shipping_route_strategy()` - Shipping route names

---

## Numeric Field Generators

### `quantity_strategy()`
Generates quantities between 100 and 10,000.

### `unit_price_strategy()`
Generates unit prices between $1 and $10,000.

### `price_deviation_strategy()`
Generates price deviations between -2.0 and 2.0.

### `company_risk_score_strategy()`
Generates company risk scores between 0.0 and 1.0.

### `port_activity_index_strategy()`
Generates port activity indices between 0.1 and 3.0.

### `distance_km_strategy()`
Generates shipping distances between 100 and 20,000 km.

### `shipment_duration_days_strategy()`
Generates shipment durations between 1 and 365 days.

### `cargo_volume_strategy()`
Generates cargo volumes between 1,000 and 200,000.

### `route_anomaly_strategy()`
Generates route anomaly flags (0 or 1).

**Example:**
```python
from test_data_generators import (
    quantity_strategy,
    unit_price_strategy,
    price_deviation_strategy
)

@given(
    qty=quantity_strategy(),
    price=unit_price_strategy(),
    deviation=price_deviation_strategy()
)
def test_pricing_calculation(qty, price, deviation):
    trade_value = qty * price
    assert trade_value > 0
```

---

## Risk Score Generators (CP-2)

These generators support testing **CP-2: Risk Score Consistency**.

### `risk_score_strategy()`
Generates any risk score between -2.0 and 2.0.

### `safe_risk_score_strategy()`
Generates risk scores in the SAFE category (< -0.2).

### `suspicious_risk_score_strategy()`
Generates risk scores in the SUSPICIOUS category (-0.2 to 0.2).

### `fraud_risk_score_strategy()`
Generates risk scores in the FRAUD category (>= 0.2).

### `boundary_risk_score_strategy()`
Generates risk scores near category boundaries (-0.2 and 0.2).

**Example:**
```python
from test_data_generators import (
    safe_risk_score_strategy,
    suspicious_risk_score_strategy,
    fraud_risk_score_strategy
)
from fraud_detection import get_risk_category

@given(score=safe_risk_score_strategy())
def test_safe_category(score):
    assert get_risk_category(score) == "SAFE"

@given(score=suspicious_risk_score_strategy())
def test_suspicious_category(score):
    assert get_risk_category(score) == "SUSPICIOUS"

@given(score=fraud_risk_score_strategy())
def test_fraud_category(score):
    assert get_risk_category(score) == "FRAUD"
```

---

## Alert Threshold Generators (CP-5)

These generators support testing **CP-5: Alert Trigger Accuracy**.

### `alert_price_deviation_strategy()`
Generates price deviations around the 0.5 alert threshold.

### `alert_company_risk_strategy()`
Generates company risk scores around the 0.8 alert threshold.

### `alert_port_activity_strategy()`
Generates port activity indices around the 1.5 alert threshold.

**Example:**
```python
from test_data_generators import (
    alert_price_deviation_strategy,
    alert_company_risk_strategy
)
from alerts import check_alerts

@given(
    price_dev=alert_price_deviation_strategy(),
    company_risk=alert_company_risk_strategy()
)
def test_alert_triggers(price_dev, company_risk):
    transaction = {
        'price_deviation': price_dev,
        'company_risk_score': company_risk,
        'route_anomaly': 0,
        'port_activity_index': 1.0
    }
    alerts = check_alerts(transaction)
    
    # Verify alert logic
    if abs(price_dev) > 0.5:
        assert 'PRICE_ANOMALY' in alerts
    if company_risk > 0.8:
        assert 'HIGH_RISK_COMPANY' in alerts
```

---

## Composite Transaction Generators

### `transaction_row_strategy()`
Generates a complete transaction row with all required fields.

**Example:**
```python
from test_data_generators import transaction_row_strategy

@given(transaction=transaction_row_strategy())
def test_complete_transaction(transaction):
    assert 'transaction_id' in transaction
    assert 'date' in transaction
    assert 'fraud_label' in transaction
    assert transaction['fraud_label'] in [0, 1]
```

### `feature_engineering_input_strategy()`
Generates input data for feature engineering testing (CP-3).

**Example:**
```python
from test_data_generators import feature_engineering_input_strategy
from feature_engineering import engineer_features
import pandas as pd

@given(features=feature_engineering_input_strategy())
def test_feature_engineering(features):
    df = pd.DataFrame([features])
    result = engineer_features(df)
    
    # Verify features were calculated
    assert 'price_anomaly_score' in result.columns
    assert 'route_risk_score' in result.columns
```

### `alert_trigger_transaction_strategy()`
Generates transactions for alert trigger testing.

### `risk_classified_transaction_strategy()`
Generates transactions with risk scores and categories that are consistent.

**Example:**
```python
from test_data_generators import risk_classified_transaction_strategy

@given(transaction=risk_classified_transaction_strategy())
def test_risk_consistency(transaction):
    score = transaction['risk_score']
    category = transaction['risk_category']
    
    # Verify consistency
    if score < -0.2:
        assert category == "SAFE"
    elif score < 0.2:
        assert category == "SUSPICIOUS"
    else:
        assert category == "FRAUD"
```

---

## DataFrame Generators

### `transaction_dataframe_strategy(min_rows, max_rows)`
Generates a complete DataFrame of transactions.

**Example:**
```python
from test_data_generators import transaction_dataframe_strategy

@given(df=transaction_dataframe_strategy(min_rows=10, max_rows=50))
@settings(max_examples=10, deadline=30000)
def test_dataframe_processing(df):
    assert len(df) >= 10
    assert len(df) <= 50
    assert 'transaction_id' in df.columns
    assert 'fraud_label' in df.columns
```

### `feature_engineering_dataframe_strategy(min_rows, max_rows)`
Generates a DataFrame for feature engineering testing.

**Example:**
```python
from test_data_generators import feature_engineering_dataframe_strategy
from feature_engineering import engineer_features

@given(df=feature_engineering_dataframe_strategy(min_rows=5, max_rows=20))
@settings(max_examples=10, deadline=30000)
def test_batch_feature_engineering(df):
    result = engineer_features(df)
    
    # Verify all features calculated
    assert len(result) == len(df)
    assert 'price_anomaly_score' in result.columns
```

---

## API Response Generators (CP-4)

These generators support testing **CP-4: API Response Validity**.

### `api_transaction_response_strategy()`
Generates API response with single transaction.

### `api_transactions_list_response_strategy(min_items, max_items)`
Generates API response with list of transactions.

### `api_stats_response_strategy()`
Generates API statistics response.

**Example:**
```python
from test_data_generators import (
    api_transaction_response_strategy,
    api_stats_response_strategy
)

@given(response=api_transaction_response_strategy())
def test_api_transaction_response(response):
    assert 'status' in response
    assert 'data' in response
    assert response['status'] == 'success'

@given(response=api_stats_response_strategy())
def test_api_stats_response(response):
    assert 'status' in response
    assert 'data' in response
    assert 'total_transactions' in response['data']
    assert 'fraud_rate' in response['data']
```

---

## Edge Case Generators

### `zero_value_strategy()`
Always generates 0 for testing division by zero.

### `negative_value_strategy()`
Generates negative values for edge case testing.

### `extreme_value_strategy()`
Generates very large or very small values.

### `edge_case_transaction_strategy(edge_case_type)`
Generates transactions with edge case values.

**Example:**
```python
from test_data_generators import (
    zero_value_strategy,
    edge_case_transaction_strategy
)
from feature_engineering import calculate_shipment_duration_risk
import pandas as pd

@given(distance=zero_value_strategy())
def test_zero_distance_handling(distance):
    df = pd.DataFrame({
        'shipment_duration_days': [10],
        'distance_km': [distance]
    })
    result = calculate_shipment_duration_risk(df)
    # Should handle zero distance gracefully
    assert not result.isna().any()

@given(transaction=edge_case_transaction_strategy(edge_case_type='zero'))
def test_zero_edge_cases(transaction):
    assert transaction['distance_km'] == 0
    assert transaction['quantity'] == 0
```

---

## Usage Examples

### Example 1: Testing Data Integrity (CP-1)

```python
from hypothesis import given, settings
from test_data_generators import transaction_dataframe_strategy
from data_loader import validate_schema

@given(df=transaction_dataframe_strategy(min_rows=5, max_rows=20))
@settings(max_examples=20, deadline=30000)
def test_data_integrity(df):
    """Validate all transactions have required fields."""
    for _, row in df.iterrows():
        assert pd.notna(row['transaction_id'])
        assert pd.notna(row['date'])
        assert pd.notna(row['fraud_label'])
```

### Example 2: Testing Feature Correctness (CP-3)

```python
from hypothesis import given, settings
from test_data_generators import feature_engineering_input_strategy
from feature_engineering import calculate_price_anomaly_score
import pandas as pd

@given(features=feature_engineering_input_strategy())
@settings(max_examples=50)
def test_price_anomaly_calculation(features):
    """Verify price anomaly score = abs(price_deviation)."""
    df = pd.DataFrame([features])
    result = calculate_price_anomaly_score(df)
    
    expected = abs(features['price_deviation'])
    actual = result.iloc[0]
    
    assert abs(actual - expected) < 1e-10
```

### Example 3: Testing Risk Score Consistency (CP-2)

```python
from hypothesis import given, settings
from test_data_generators import (
    safe_risk_score_strategy,
    suspicious_risk_score_strategy,
    fraud_risk_score_strategy
)
from fraud_detection import get_risk_category

@given(
    safe_score=safe_risk_score_strategy(),
    suspicious_score=suspicious_risk_score_strategy(),
    fraud_score=fraud_risk_score_strategy()
)
@settings(max_examples=30)
def test_risk_category_ordering(safe_score, suspicious_score, fraud_score):
    """Verify SAFE < SUSPICIOUS < FRAUD ordering."""
    assert get_risk_category(safe_score) == "SAFE"
    assert get_risk_category(suspicious_score) == "SUSPICIOUS"
    assert get_risk_category(fraud_score) == "FRAUD"
    
    # Verify ordering
    assert safe_score < suspicious_score < fraud_score
```

### Example 4: Testing API Response Validity (CP-4)

```python
from hypothesis import given, settings
from test_data_generators import api_transactions_list_response_strategy

@given(response=api_transactions_list_response_strategy(min_items=1, max_items=10))
@settings(max_examples=20, deadline=30000)
def test_api_response_schema(response):
    """Verify API response has valid schema."""
    assert 'status' in response
    assert 'data' in response
    assert isinstance(response['data'], list)
    
    for transaction in response['data']:
        assert 'transaction_id' in transaction
        assert 'fraud_label' in transaction
```

### Example 5: Testing Alert Trigger Accuracy (CP-5)

```python
from hypothesis import given, settings
from test_data_generators import alert_trigger_transaction_strategy
from alerts import check_alerts

@given(transaction=alert_trigger_transaction_strategy())
@settings(max_examples=50)
def test_alert_trigger_accuracy(transaction):
    """Verify alerts triggered correctly based on thresholds."""
    alerts = check_alerts(transaction)
    
    # Verify price deviation alert
    if abs(transaction['price_deviation']) > 0.5:
        assert 'PRICE_ANOMALY' in alerts
    else:
        assert 'PRICE_ANOMALY' not in alerts
    
    # Verify company risk alert
    if transaction['company_risk_score'] > 0.8:
        assert 'HIGH_RISK_COMPANY' in alerts
    else:
        assert 'HIGH_RISK_COMPANY' not in alerts
```

---

## Best Practices

### 1. Use Appropriate Generators
Choose generators that match your test requirements:
- Use `safe_risk_score_strategy()` when testing SAFE category
- Use `boundary_risk_score_strategy()` when testing edge cases
- Use `transaction_dataframe_strategy()` when testing batch operations

### 2. Set Reasonable Limits
```python
@given(df=transaction_dataframe_strategy(min_rows=5, max_rows=20))
@settings(max_examples=10, deadline=30000)  # Limit examples and set deadline
def test_with_dataframe(df):
    # Test implementation
    pass
```

### 3. Combine Generators
```python
from hypothesis import strategies as st

@given(
    transaction=transaction_row_strategy(),
    risk_score=risk_score_strategy()
)
def test_combined(transaction, risk_score):
    # Test with both generated values
    pass
```

### 4. Use Examples for Edge Cases
```python
from hypothesis import example

@given(score=risk_score_strategy())
@example(score=-0.2)  # Exact boundary
@example(score=0.2)   # Exact boundary
def test_with_examples(score):
    # Test implementation
    pass
```

### 5. Handle Edge Cases
```python
from test_data_generators import edge_case_transaction_strategy

@given(transaction=edge_case_transaction_strategy(edge_case_type='zero'))
def test_zero_handling(transaction):
    # Verify system handles zero values gracefully
    pass
```

---

## Utility Functions

### `create_test_dataframe(transactions)`
Creates a pandas DataFrame from a list of transaction dictionaries.

```python
from test_data_generators import create_test_dataframe

transactions = [
    {'transaction_id': 'TXN001', 'date': '2024-01-01', 'fraud_label': 0},
    {'transaction_id': 'TXN002', 'date': '2024-01-02', 'fraud_label': 1}
]
df = create_test_dataframe(transactions)
```

### `validate_transaction_schema(transaction)`
Validates that a transaction has all required fields.

```python
from test_data_generators import validate_transaction_schema

transaction = {'transaction_id': 'TXN001', ...}
is_valid = validate_transaction_schema(transaction)
```

---

## Running Tests with Generators

### Run All Property-Based Tests
```bash
python -m pytest backend/test_*_property.py -v
```

### Run Specific Property Test
```bash
python -m pytest backend/test_data_integrity_property.py -v
```

### Run with More Examples
```bash
python -m pytest backend/test_feature_correctness_property.py -v --hypothesis-show-statistics
```

### Run Validation Tests
```bash
python -m pytest backend/test_generators_validation.py -v
```

---

## Troubleshooting

### Issue: Tests Timeout
**Solution:** Increase deadline or reduce max_examples
```python
@settings(max_examples=10, deadline=60000)  # 60 second deadline
```

### Issue: Too Many Examples
**Solution:** Reduce max_examples
```python
@settings(max_examples=20)  # Fewer examples
```

### Issue: Need Specific Values
**Solution:** Use `@example` decorator
```python
@given(score=risk_score_strategy())
@example(score=-0.2)  # Test specific value
@example(score=0.2)
def test_boundaries(score):
    pass
```

---

## Summary

The test data generators provide comprehensive support for all five correctness properties:

- **CP-1 (Data Integrity)**: `transaction_row_strategy()`, `transaction_dataframe_strategy()`
- **CP-2 (Risk Score Consistency)**: `safe_risk_score_strategy()`, `suspicious_risk_score_strategy()`, `fraud_risk_score_strategy()`
- **CP-3 (Feature Engineering)**: `feature_engineering_input_strategy()`, `feature_engineering_dataframe_strategy()`
- **CP-4 (API Response Validity)**: `api_transaction_response_strategy()`, `api_stats_response_strategy()`
- **CP-5 (Alert Trigger Accuracy)**: `alert_trigger_transaction_strategy()`, alert threshold generators

Use these generators to write comprehensive property-based tests that validate system correctness across a wide range of inputs.
