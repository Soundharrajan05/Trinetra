"""
Test Data Generators for Property-Based Testing
TRINETRA AI - Trade Fraud Intelligence System

**Validates: All Correctness Properties (CP-1 through CP-5)**

This module provides hypothesis strategies for generating test data to support
property-based testing of the TRINETRA AI fraud detection system.

Generators support:
- CP-1: Data Integrity (valid transaction_id, date, fraud_label)
- CP-2: Risk Score Consistency (SAFE < SUSPICIOUS < FRAUD)
- CP-3: Feature Engineering Correctness (mathematical calculations)
- CP-4: API Response Validity (JSON schema compliance)
- CP-5: Alert Trigger Accuracy (threshold conditions)
"""

from hypothesis import strategies as st
from hypothesis.extra.pandas import data_frames, columns
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd


# ============================================================================
# Basic Field Generators
# ============================================================================

@st.composite
def transaction_id_strategy(draw):
    """
    Generate valid transaction IDs.
    
    Format: TXN followed by 5 digits
    
    Returns:
        str: Valid transaction ID (e.g., "TXN00123")
    """
    number = draw(st.integers(min_value=0, max_value=99999))
    return f"TXN{number:05d}"


@st.composite
def date_strategy(draw):
    """
    Generate valid dates for transactions.
    
    Range: 2020-01-01 to 2024-12-31
    
    Returns:
        str: Date string in YYYY-MM-DD format
    """
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    days_between = (end_date - start_date).days
    random_days = draw(st.integers(min_value=0, max_value=days_between))
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%d")


def fraud_label_strategy():
    """
    Generate valid fraud labels.
    
    Returns:
        Strategy: Generates 0 (not fraud) or 1 (fraud)
    """
    return st.integers(min_value=0, max_value=1)


def product_strategy():
    """
    Generate product names.
    
    Returns:
        Strategy: Generates realistic product names
    """
    products = [
        "Electronics", "Textiles", "Machinery", "Chemicals",
        "Pharmaceuticals", "Automotive Parts", "Steel", "Aluminum",
        "Plastics", "Furniture", "Toys", "Clothing", "Footwear",
        "Medical Equipment", "Computer Hardware", "Mobile Phones"
    ]
    return st.sampled_from(products)


def commodity_category_strategy():
    """
    Generate commodity categories.
    
    Returns:
        Strategy: Generates commodity category names
    """
    categories = [
        "Electronics", "Textiles", "Metals", "Chemicals",
        "Pharmaceuticals", "Machinery", "Consumer Goods",
        "Industrial Equipment", "Raw Materials"
    ]
    return st.sampled_from(categories)


def country_strategy():
    """
    Generate country names.
    
    Returns:
        Strategy: Generates country names
    """
    countries = [
        "USA", "China", "India", "Germany", "Japan",
        "UK", "France", "Canada", "Mexico", "Brazil",
        "South Korea", "Italy", "Spain", "Netherlands", "Singapore"
    ]
    return st.sampled_from(countries)


def company_strategy():
    """
    Generate company names.
    
    Returns:
        Strategy: Generates company names
    """
    prefixes = ["Global", "International", "United", "Pacific", "Atlantic"]
    suffixes = ["Trading Co", "Exports Ltd", "Imports Inc", "Corp", "Industries"]
    
    return st.builds(
        lambda p, s: f"{p} {s}",
        st.sampled_from(prefixes),
        st.sampled_from(suffixes)
    )


def shipping_route_strategy():
    """
    Generate shipping routes.
    
    Returns:
        Strategy: Generates shipping route names
    """
    routes = [
        "Pacific Route", "Atlantic Route", "Indian Ocean Route",
        "Mediterranean Route", "Arctic Route", "Trans-Pacific",
        "Trans-Atlantic", "Asia-Europe", "US-China", "Europe-Asia"
    ]
    return st.sampled_from(routes)


# ============================================================================
# Numeric Field Generators
# ============================================================================

def quantity_strategy():
    """
    Generate realistic quantity values.
    
    Returns:
        Strategy: Generates quantities between 100 and 10000
    """
    return st.integers(min_value=100, max_value=10000)


def unit_price_strategy():
    """
    Generate realistic unit prices.
    
    Returns:
        Strategy: Generates prices between $1 and $10000
    """
    return st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False)


def trade_value_strategy():
    """
    Generate realistic trade values.
    
    Returns:
        Strategy: Generates trade values between $1000 and $10,000,000
    """
    return st.floats(min_value=1000.0, max_value=10000000.0, allow_nan=False, allow_infinity=False)


def price_deviation_strategy():
    """
    Generate price deviation values.
    
    Returns:
        Strategy: Generates deviations between -2.0 and 2.0
    """
    return st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False)


def company_risk_score_strategy():
    """
    Generate company risk scores.
    
    Returns:
        Strategy: Generates risk scores between 0.0 and 1.0
    """
    return st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


def port_activity_index_strategy():
    """
    Generate port activity indices.
    
    Returns:
        Strategy: Generates indices between 0.1 and 3.0
    """
    return st.floats(min_value=0.1, max_value=3.0, allow_nan=False, allow_infinity=False)


def distance_km_strategy():
    """
    Generate shipping distances in kilometers.
    
    Returns:
        Strategy: Generates distances between 100 and 20000 km
    """
    return st.floats(min_value=100.0, max_value=20000.0, allow_nan=False, allow_infinity=False)


def shipment_duration_days_strategy():
    """
    Generate shipment durations in days.
    
    Returns:
        Strategy: Generates durations between 1 and 365 days
    """
    return st.floats(min_value=1.0, max_value=365.0, allow_nan=False, allow_infinity=False)


def cargo_volume_strategy():
    """
    Generate cargo volumes.
    
    Returns:
        Strategy: Generates volumes between 1000 and 200000
    """
    return st.floats(min_value=1000.0, max_value=200000.0, allow_nan=False, allow_infinity=False)


def route_anomaly_strategy():
    """
    Generate route anomaly flags.
    
    Returns:
        Strategy: Generates 0 or 1
    """
    return st.sampled_from([0, 1])


# ============================================================================
# Risk Score Generators (CP-2)
# ============================================================================

def risk_score_strategy():
    """
    Generate risk scores for testing risk classification.
    
    Returns:
        Strategy: Generates risk scores between -2.0 and 2.0
    """
    return st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False)


def safe_risk_score_strategy():
    """
    Generate risk scores in the SAFE category.
    
    Returns:
        Strategy: Generates scores < -0.2
    """
    return st.floats(min_value=-2.0, max_value=-0.201, allow_nan=False, allow_infinity=False)


def suspicious_risk_score_strategy():
    """
    Generate risk scores in the SUSPICIOUS category.
    
    Returns:
        Strategy: Generates scores between -0.2 and 0.2
    """
    return st.floats(min_value=-0.2, max_value=0.199, allow_nan=False, allow_infinity=False)


def fraud_risk_score_strategy():
    """
    Generate risk scores in the FRAUD category.
    
    Returns:
        Strategy: Generates scores >= 0.2
    """
    return st.floats(min_value=0.2, max_value=2.0, allow_nan=False, allow_infinity=False)


def boundary_risk_score_strategy():
    """
    Generate risk scores near category boundaries.
    
    Returns:
        Strategy: Generates scores near -0.2 and 0.2 thresholds
    """
    return st.sampled_from([
        -0.2, 0.2,  # Exact boundaries
        -0.21, -0.19,  # Near lower boundary
        0.19, 0.21,  # Near upper boundary
        -0.20000001, -0.19999999,  # Very close to lower boundary
        0.19999999, 0.20000001  # Very close to upper boundary
    ])


# ============================================================================
# Alert Threshold Generators (CP-5)
# ============================================================================

def alert_price_deviation_strategy():
    """
    Generate price deviations for alert testing.
    
    Returns:
        Strategy: Generates values around the 0.5 threshold
    """
    return st.floats(min_value=-1.0, max_value=2.0, allow_nan=False, allow_infinity=False)


def alert_company_risk_strategy():
    """
    Generate company risk scores for alert testing.
    
    Returns:
        Strategy: Generates values around the 0.8 threshold
    """
    return st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


def alert_port_activity_strategy():
    """
    Generate port activity indices for alert testing.
    
    Returns:
        Strategy: Generates values around the 1.5 threshold
    """
    return st.floats(min_value=0.5, max_value=3.0, allow_nan=False, allow_infinity=False)


# ============================================================================
# Composite Transaction Generators
# ============================================================================

@st.composite
def transaction_row_strategy(draw):
    """
    Generate a complete transaction row with all required fields.
    
    Returns:
        dict: Complete transaction data
    """
    return {
        'transaction_id': draw(transaction_id_strategy()),
        'date': draw(date_strategy()),
        'product': draw(product_strategy()),
        'commodity_category': draw(commodity_category_strategy()),
        'quantity': draw(quantity_strategy()),
        'unit_price': draw(unit_price_strategy()),
        'trade_value': draw(trade_value_strategy()),
        'market_price': draw(unit_price_strategy()),
        'price_deviation': draw(price_deviation_strategy()),
        'exporter_company': draw(company_strategy()),
        'exporter_country': draw(country_strategy()),
        'importer_company': draw(company_strategy()),
        'importer_country': draw(country_strategy()),
        'shipping_route': draw(shipping_route_strategy()),
        'distance_km': draw(distance_km_strategy()),
        'company_risk_score': draw(company_risk_score_strategy()),
        'port_activity_index': draw(port_activity_index_strategy()),
        'route_anomaly': draw(route_anomaly_strategy()),
        'shipment_duration_days': draw(shipment_duration_days_strategy()),
        'cargo_volume': draw(cargo_volume_strategy()),
        'fraud_label': draw(fraud_label_strategy())
    }


@st.composite
def feature_engineering_input_strategy(draw):
    """
    Generate input data for feature engineering testing.
    
    Returns:
        dict: Data with fields needed for feature engineering
    """
    return {
        'price_deviation': draw(price_deviation_strategy()),
        'route_anomaly': draw(route_anomaly_strategy()),
        'company_risk_score': draw(company_risk_score_strategy()),
        'port_activity_index': draw(port_activity_index_strategy()),
        'shipment_duration_days': draw(shipment_duration_days_strategy()),
        'distance_km': draw(distance_km_strategy()),
        'cargo_volume': draw(cargo_volume_strategy()),
        'quantity': draw(quantity_strategy())
    }


@st.composite
def alert_trigger_transaction_strategy(draw):
    """
    Generate transactions for alert trigger testing.
    
    Returns:
        dict: Transaction data with alert-relevant fields
    """
    return {
        'transaction_id': draw(transaction_id_strategy()),
        'price_deviation': draw(alert_price_deviation_strategy()),
        'route_anomaly': draw(route_anomaly_strategy()),
        'company_risk_score': draw(alert_company_risk_strategy()),
        'port_activity_index': draw(alert_port_activity_strategy())
    }


@st.composite
def risk_classified_transaction_strategy(draw):
    """
    Generate transactions with risk scores and categories.
    
    Returns:
        dict: Transaction with risk_score and risk_category
    """
    risk_score = draw(risk_score_strategy())
    
    # Determine category based on score
    if risk_score < -0.2:
        risk_category = "SAFE"
    elif risk_score < 0.2:
        risk_category = "SUSPICIOUS"
    else:
        risk_category = "FRAUD"
    
    return {
        'transaction_id': draw(transaction_id_strategy()),
        'risk_score': risk_score,
        'risk_category': risk_category
    }


# ============================================================================
# DataFrame Generators
# ============================================================================

@st.composite
def transaction_dataframe_strategy(draw, min_rows=1, max_rows=100):
    """
    Generate a complete DataFrame of transactions.
    
    Args:
        draw: Hypothesis draw function
        min_rows: Minimum number of rows
        max_rows: Maximum number of rows
    
    Returns:
        pd.DataFrame: DataFrame with transaction data
    """
    n_rows = draw(st.integers(min_value=min_rows, max_value=max_rows))
    
    transactions = [draw(transaction_row_strategy()) for _ in range(n_rows)]
    
    return pd.DataFrame(transactions)


@st.composite
def feature_engineering_dataframe_strategy(draw, min_rows=1, max_rows=50):
    """
    Generate a DataFrame for feature engineering testing.
    
    Args:
        draw: Hypothesis draw function
        min_rows: Minimum number of rows
        max_rows: Maximum number of rows
    
    Returns:
        pd.DataFrame: DataFrame with feature engineering input data
    """
    n_rows = draw(st.integers(min_value=min_rows, max_value=max_rows))
    
    data = [draw(feature_engineering_input_strategy()) for _ in range(n_rows)]
    
    return pd.DataFrame(data)


# ============================================================================
# API Response Generators (CP-4)
# ============================================================================

@st.composite
def api_transaction_response_strategy(draw):
    """
    Generate expected API transaction response structure.
    
    Returns:
        dict: API response with transaction data
    """
    transaction = draw(transaction_row_strategy())
    
    return {
        'status': 'success',
        'data': transaction,
        'message': draw(st.one_of(st.none(), st.text(min_size=0, max_size=100)))
    }


@st.composite
def api_transactions_list_response_strategy(draw, min_items=0, max_items=20):
    """
    Generate API response with list of transactions.
    
    Args:
        draw: Hypothesis draw function
        min_items: Minimum number of transactions
        max_items: Maximum number of transactions
    
    Returns:
        dict: API response with transaction list
    """
    n_items = draw(st.integers(min_value=min_items, max_value=max_items))
    
    transactions = [draw(transaction_row_strategy()) for _ in range(n_items)]
    
    return {
        'status': 'success',
        'data': transactions,
        'message': None
    }


@st.composite
def api_stats_response_strategy(draw):
    """
    Generate API statistics response.
    
    Returns:
        dict: API response with statistics
    """
    total_transactions = draw(st.integers(min_value=0, max_value=10000))
    fraud_count = draw(st.integers(min_value=0, max_value=total_transactions))
    
    return {
        'status': 'success',
        'data': {
            'total_transactions': total_transactions,
            'fraud_count': fraud_count,
            'fraud_rate': fraud_count / total_transactions if total_transactions > 0 else 0.0,
            'suspicious_count': draw(st.integers(min_value=0, max_value=total_transactions)),
            'safe_count': draw(st.integers(min_value=0, max_value=total_transactions)),
            'total_trade_value': draw(st.floats(min_value=0, max_value=1e9, allow_nan=False)),
            'high_risk_countries': draw(st.integers(min_value=0, max_value=50))
        },
        'message': None
    }


# ============================================================================
# Edge Case Generators
# ============================================================================

def zero_value_strategy():
    """
    Generate zero values for edge case testing.
    
    Returns:
        Strategy: Always returns 0
    """
    return st.just(0)


def negative_value_strategy():
    """
    Generate negative values for edge case testing.
    
    Returns:
        Strategy: Generates negative numbers
    """
    return st.floats(min_value=-1000.0, max_value=-0.001, allow_nan=False, allow_infinity=False)


def extreme_value_strategy():
    """
    Generate extreme values for edge case testing.
    
    Returns:
        Strategy: Generates very large or very small values
    """
    return st.one_of(
        st.floats(min_value=1e6, max_value=1e9, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-1e9, max_value=-1e6, allow_nan=False, allow_infinity=False),
        st.floats(min_value=0.0, max_value=1e-6, allow_nan=False, allow_infinity=False)
    )


@st.composite
def edge_case_transaction_strategy(draw, edge_case_type='zero'):
    """
    Generate transactions with edge case values.
    
    Args:
        draw: Hypothesis draw function
        edge_case_type: Type of edge case ('zero', 'negative', 'extreme')
    
    Returns:
        dict: Transaction with edge case values
    """
    base_transaction = draw(transaction_row_strategy())
    
    if edge_case_type == 'zero':
        # Introduce zero values in numeric fields
        base_transaction['distance_km'] = 0
        base_transaction['quantity'] = 0
    elif edge_case_type == 'negative':
        # Introduce negative values
        base_transaction['price_deviation'] = draw(negative_value_strategy())
        base_transaction['shipment_duration_days'] = draw(negative_value_strategy())
    elif edge_case_type == 'extreme':
        # Introduce extreme values
        base_transaction['trade_value'] = draw(extreme_value_strategy())
        base_transaction['cargo_volume'] = draw(extreme_value_strategy())
    
    return base_transaction


# ============================================================================
# Utility Functions
# ============================================================================

def create_test_dataframe(transactions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create a pandas DataFrame from a list of transaction dictionaries.
    
    Args:
        transactions: List of transaction dictionaries
    
    Returns:
        pd.DataFrame: DataFrame with transaction data
    """
    return pd.DataFrame(transactions)


def validate_transaction_schema(transaction: Dict[str, Any]) -> bool:
    """
    Validate that a transaction has all required fields.
    
    Args:
        transaction: Transaction dictionary
    
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = [
        'transaction_id', 'date', 'product', 'commodity_category',
        'quantity', 'unit_price', 'trade_value', 'market_price',
        'price_deviation', 'exporter_company', 'exporter_country',
        'importer_company', 'importer_country', 'shipping_route',
        'distance_km', 'company_risk_score', 'port_activity_index',
        'route_anomaly', 'shipment_duration_days', 'cargo_volume',
        'fraud_label'
    ]
    
    return all(field in transaction for field in required_fields)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of test data generators.
    """
    from hypothesis import find
    
    print("=== Test Data Generators Demo ===\n")
    
    # Generate a single transaction
    print("1. Single Transaction:")
    transaction = find(transaction_row_strategy(), lambda x: True)
    print(f"   Transaction ID: {transaction['transaction_id']}")
    print(f"   Product: {transaction['product']}")
    print(f"   Price Deviation: {transaction['price_deviation']:.4f}")
    print(f"   Risk Score: {transaction['company_risk_score']:.4f}\n")
    
    # Generate risk scores for each category
    print("2. Risk Score Categories:")
    safe_score = find(safe_risk_score_strategy(), lambda x: True)
    suspicious_score = find(suspicious_risk_score_strategy(), lambda x: True)
    fraud_score = find(fraud_risk_score_strategy(), lambda x: True)
    print(f"   SAFE: {safe_score:.4f}")
    print(f"   SUSPICIOUS: {suspicious_score:.4f}")
    print(f"   FRAUD: {fraud_score:.4f}\n")
    
    # Generate feature engineering input
    print("3. Feature Engineering Input:")
    features = find(feature_engineering_input_strategy(), lambda x: True)
    print(f"   Price Deviation: {features['price_deviation']:.4f}")
    print(f"   Route Anomaly: {features['route_anomaly']}")
    print(f"   Duration/Distance: {features['shipment_duration_days']:.1f} days / {features['distance_km']:.1f} km\n")
    
    # Generate API response
    print("4. API Response:")
    api_response = find(api_stats_response_strategy(), lambda x: True)
    print(f"   Status: {api_response['status']}")
    print(f"   Total Transactions: {api_response['data']['total_transactions']}")
    print(f"   Fraud Rate: {api_response['data']['fraud_rate']:.2%}\n")
    
    print("=== All generators working correctly! ===")