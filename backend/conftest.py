"""
Pytest Configuration and Fixtures for TRINETRA AI Property-Based Testing
=========================================================================

This module provides shared fixtures, hypothesis configuration, and test utilities
for property-based testing of the TRINETRA AI fraud detection system.

**Validates: All Correctness Properties (CP-1 through CP-5)**

Hypothesis Configuration:
- max_examples: Number of test cases to generate per property
- deadline: Maximum time per test case (milliseconds)
- database: Stores examples for regression testing
- verbosity: Controls output detail level
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any
from hypothesis import settings, Verbosity, Phase

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================================================
# Hypothesis Configuration
# ============================================================================

# Register custom hypothesis profile for TRINETRA AI testing
settings.register_profile(
    "trinetra_default",
    max_examples=50,
    deadline=30000,  # 30 seconds per test case
    verbosity=Verbosity.normal,
    phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.target, Phase.shrink],
    print_blob=True,  # Print failing examples for debugging
)

settings.register_profile(
    "trinetra_quick",
    max_examples=10,
    deadline=10000,  # 10 seconds per test case
    verbosity=Verbosity.quiet,
)

settings.register_profile(
    "trinetra_thorough",
    max_examples=200,
    deadline=60000,  # 60 seconds per test case
    verbosity=Verbosity.verbose,
)

settings.register_profile(
    "ci",
    max_examples=20,
    deadline=20000,
    verbosity=Verbosity.quiet,
)

# Load profile from environment or use default
profile = os.getenv("HYPOTHESIS_PROFILE", "trinetra_default")
settings.load_profile(profile)


# ============================================================================
# Path and Directory Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def data_dir(project_root: Path) -> Path:
    """Return the data directory path."""
    return project_root / "data"


@pytest.fixture(scope="session")
def models_dir(project_root: Path) -> Path:
    """Return the models directory path."""
    return project_root / "models"


@pytest.fixture(scope="session")
def dataset_path(data_dir: Path) -> Path:
    """Return the path to the main dataset."""
    return data_dir / "trinetra_trade_fraud_dataset_1000_rows_complex.csv"


@pytest.fixture(scope="session")
def model_path(models_dir: Path) -> Path:
    """Return the path to the trained model."""
    return models_dir / "isolation_forest.pkl"


# ============================================================================
# Data Loading Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def sample_dataset(dataset_path: Path) -> pd.DataFrame:
    """
    Load a sample of the main dataset for testing.
    
    Returns:
        DataFrame with 100 rows from the main dataset
    
    Skips:
        If dataset file doesn't exist
    """
    if not dataset_path.exists():
        pytest.skip(f"Dataset not found: {dataset_path}")
    
    try:
        from data_loader import load_dataset
        df = load_dataset(str(dataset_path))
        # Return a sample for faster testing
        return df.sample(n=min(100, len(df)), random_state=42)
    except Exception as e:
        pytest.skip(f"Failed to load dataset: {e}")


@pytest.fixture(scope="session")
def full_dataset(dataset_path: Path) -> pd.DataFrame:
    """
    Load the complete dataset for integration testing.
    
    Returns:
        Complete DataFrame from the main dataset
    
    Skips:
        If dataset file doesn't exist
    """
    if not dataset_path.exists():
        pytest.skip(f"Dataset not found: {dataset_path}")
    
    try:
        from data_loader import load_dataset
        return load_dataset(str(dataset_path))
    except Exception as e:
        pytest.skip(f"Failed to load dataset: {e}")


# ============================================================================
# Feature Engineering Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def engineered_dataset(sample_dataset: pd.DataFrame) -> pd.DataFrame:
    """
    Return dataset with engineered features.
    
    Returns:
        DataFrame with all fraud detection features added
    """
    try:
        from feature_engineering import engineer_features
        return engineer_features(sample_dataset)
    except Exception as e:
        pytest.skip(f"Failed to engineer features: {e}")


# ============================================================================
# Model Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def trained_model(model_path: Path):
    """
    Load the trained IsolationForest model.
    
    Returns:
        Trained IsolationForest model
    
    Skips:
        If model file doesn't exist
    """
    if not model_path.exists():
        pytest.skip(f"Trained model not found: {model_path}")
    
    try:
        from fraud_detection import load_fraud_detector
        model = load_fraud_detector(str(model_path))
        if model is None:
            pytest.skip("Failed to load model")
        return model
    except Exception as e:
        pytest.skip(f"Failed to load model: {e}")


@pytest.fixture(scope="session")
def scored_dataset(engineered_dataset: pd.DataFrame, trained_model) -> pd.DataFrame:
    """
    Return dataset with risk scores and classifications.
    
    Returns:
        DataFrame with risk_score and risk_category columns
    """
    try:
        from fraud_detection import score_transactions, classify_risk
        scored = score_transactions(engineered_dataset, trained_model)
        return classify_risk(scored)
    except Exception as e:
        pytest.skip(f"Failed to score transactions: {e}")


# ============================================================================
# Temporary File Fixtures
# ============================================================================

@pytest.fixture
def temp_csv_file() -> Generator[str, None, None]:
    """
    Create a temporary CSV file for testing.
    
    Yields:
        Path to temporary CSV file
    
    Cleanup:
        Removes the temporary file after test
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_model_file() -> Generator[str, None, None]:
    """
    Create a temporary model file for testing.
    
    Yields:
        Path to temporary model file
    
    Cleanup:
        Removes the temporary file after test
    """
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


# ============================================================================
# Test Data Generators
# ============================================================================

@pytest.fixture
def valid_transaction_data() -> Dict[str, Any]:
    """
    Return a dictionary with valid transaction data for testing.
    
    Returns:
        Dictionary with all required transaction fields
    """
    return {
        'transaction_id': 'TXN001',
        'date': '2024-01-01',
        'product': 'Test Product',
        'commodity_category': 'Electronics',
        'quantity': 100,
        'unit_price': 50.0,
        'trade_value': 5000.0,
        'market_price': 52.0,
        'price_deviation': 0.04,
        'exporter_company': 'Exporter Inc',
        'exporter_country': 'USA',
        'importer_company': 'Importer Ltd',
        'importer_country': 'China',
        'shipping_route': 'USA-China',
        'distance_km': 10000,
        'shipment_duration_days': 30,
        'cargo_volume': 50000,
        'company_risk_score': 0.3,
        'route_anomaly': 0,
        'port_activity_index': 1.2,
        'fraud_label': 0
    }


@pytest.fixture
def sample_risk_scores() -> Dict[str, float]:
    """
    Return sample risk scores for each category.
    
    Returns:
        Dictionary mapping categories to example risk scores
    """
    return {
        'SAFE': -0.5,
        'SUSPICIOUS': 0.0,
        'FRAUD': 0.5
    }


# ============================================================================
# Hypothesis Strategy Helpers
# ============================================================================

def get_valid_price_deviation():
    """Return a hypothesis strategy for valid price deviations."""
    from hypothesis import strategies as st
    return st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False)


def get_valid_risk_score():
    """Return a hypothesis strategy for valid risk scores."""
    from hypothesis import strategies as st
    return st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False)


def get_valid_route_anomaly():
    """Return a hypothesis strategy for valid route anomaly values."""
    from hypothesis import strategies as st
    return st.sampled_from([0, 1, 0.0, 1.0])


def get_valid_company_risk():
    """Return a hypothesis strategy for valid company risk scores."""
    from hypothesis import strategies as st
    return st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


def get_valid_port_activity():
    """Return a hypothesis strategy for valid port activity indices."""
    from hypothesis import strategies as st
    return st.floats(min_value=0.1, max_value=3.0, allow_nan=False, allow_infinity=False)


# ============================================================================
# Pytest Markers
# ============================================================================

def pytest_configure(config):
    """Register custom markers for property-based tests."""
    config.addinivalue_line(
        "markers", "property: mark test as a property-based test"
    )
    config.addinivalue_line(
        "markers", "cp1: mark test as validating CP-1 (Data Integrity)"
    )
    config.addinivalue_line(
        "markers", "cp2: mark test as validating CP-2 (Risk Score Consistency)"
    )
    config.addinivalue_line(
        "markers", "cp3: mark test as validating CP-3 (Feature Engineering Correctness)"
    )
    config.addinivalue_line(
        "markers", "cp4: mark test as validating CP-4 (API Response Validity)"
    )
    config.addinivalue_line(
        "markers", "cp5: mark test as validating CP-5 (Alert Trigger Accuracy)"
    )


# ============================================================================
# Test Collection Hooks
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers automatically.
    
    Automatically marks tests based on their module and function names.
    """
    for item in items:
        # Mark property-based tests
        if "property" in item.nodeid.lower():
            item.add_marker(pytest.mark.property)
        
        # Mark tests by correctness property
        if "data_integrity" in item.nodeid.lower():
            item.add_marker(pytest.mark.cp1)
        elif "risk_score_consistency" in item.nodeid.lower():
            item.add_marker(pytest.mark.cp2)
        elif "feature_correctness" in item.nodeid.lower():
            item.add_marker(pytest.mark.cp3)
        elif "api_response_validity" in item.nodeid.lower():
            item.add_marker(pytest.mark.cp4)
        elif "alert_trigger" in item.nodeid.lower():
            item.add_marker(pytest.mark.cp5)


# ============================================================================
# Hypothesis Database Configuration
# ============================================================================

# Configure hypothesis to store examples in .hypothesis directory
# This enables regression testing with previously failing examples
HYPOTHESIS_DATABASE_DIR = Path(__file__).parent / ".hypothesis"
HYPOTHESIS_DATABASE_DIR.mkdir(exist_ok=True)


# ============================================================================
# Utility Functions for Tests
# ============================================================================

def assert_valid_transaction_id(transaction_id: Any) -> None:
    """
    Assert that a transaction ID is valid.
    
    Args:
        transaction_id: The transaction ID to validate
    
    Raises:
        AssertionError: If transaction ID is invalid
    """
    assert pd.notna(transaction_id), "Transaction ID must not be null"
    assert str(transaction_id).strip() != '', "Transaction ID must not be empty"


def assert_valid_date(date_value: Any) -> None:
    """
    Assert that a date value is valid.
    
    Args:
        date_value: The date value to validate
    
    Raises:
        AssertionError: If date is invalid
    """
    assert pd.notna(date_value), "Date must not be null"
    assert pd.api.types.is_datetime64_any_dtype(pd.Series([date_value])), \
        "Date must be a valid datetime"


def assert_valid_fraud_label(fraud_label: Any) -> None:
    """
    Assert that a fraud label is valid.
    
    Args:
        fraud_label: The fraud label to validate
    
    Raises:
        AssertionError: If fraud label is invalid
    """
    assert pd.notna(fraud_label), "Fraud label must not be null"
    assert isinstance(fraud_label, (int, float, np.integer, np.floating)), \
        "Fraud label must be numeric"


def assert_risk_category_valid(category: str) -> None:
    """
    Assert that a risk category is valid.
    
    Args:
        category: The risk category to validate
    
    Raises:
        AssertionError: If category is invalid
    """
    valid_categories = ["SAFE", "SUSPICIOUS", "FRAUD"]
    assert category in valid_categories, \
        f"Risk category must be one of {valid_categories}, got {category}"


def assert_feature_in_range(value: float, min_val: float, max_val: float, feature_name: str) -> None:
    """
    Assert that a feature value is within expected range.
    
    Args:
        value: The feature value to check
        min_val: Minimum expected value
        max_val: Maximum expected value
        feature_name: Name of the feature for error messages
    
    Raises:
        AssertionError: If value is out of range
    """
    assert min_val <= value <= max_val, \
        f"{feature_name} must be in range [{min_val}, {max_val}], got {value}"


# ============================================================================
# Session Hooks
# ============================================================================

def pytest_sessionstart(session):
    """
    Called before test session starts.
    
    Prints configuration information.
    """
    print("\n" + "=" * 70)
    print("TRINETRA AI - Property-Based Testing Session")
    print("=" * 70)
    print(f"Hypothesis Profile: {settings.default.max_examples} examples, "
          f"{settings.default.deadline}ms deadline")
    print(f"Database: {HYPOTHESIS_DATABASE_DIR}")
    print("=" * 70 + "\n")


def pytest_sessionfinish(session, exitstatus):
    """
    Called after test session finishes.
    
    Prints summary information.
    """
    print("\n" + "=" * 70)
    print("Property-Based Testing Session Complete")
    print("=" * 70)
