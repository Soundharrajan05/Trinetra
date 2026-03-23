# TRINETRA AI Data Formatting Utilities

This module provides comprehensive data formatting utilities for the TRINETRA AI Trade Fraud Intelligence System.

## Overview

The `utils/helpers.py` module contains essential formatting functions used throughout the TRINETRA AI system for:
- Dashboard display formatting
- API response formatting  
- Gemini AI prompt formatting
- Data validation and sanitization
- Configuration management

## Main Components

### DataFormatter Class

The core formatting class with static methods for:

#### Currency & Numeric Formatting
- `format_currency(value, symbol="$", precision=2)` - Format monetary values
- `format_percentage(value, precision=2)` - Format percentages  
- `format_decimal(value, precision=4)` - Format decimal numbers
- `format_large_number(number)` - Format with K/M/B suffixes

#### Date & Time Formatting
- `format_date(value, format_string="%Y-%m-%d")` - Consistent date formatting

#### Risk Score Formatting
- `format_risk_score(score, precision=3)` - Format ML risk scores
- `get_risk_category(score)` - Convert scores to SAFE/SUSPICIOUS/FRAUD

#### Transaction Formatting
- `format_transaction_for_display(transaction)` - Dashboard-ready formatting
- `format_transaction_for_api(transaction)` - API response formatting
- `format_transaction_for_gemini(transaction)` - AI prompt formatting

#### Alert & Statistics Formatting
- `format_alert_message(alert_type, transaction)` - Alert notifications
- `format_statistics_for_dashboard(stats)` - KPI metrics formatting

### ValidationHelpers Class

Data validation and security utilities:
- `validate_transaction_data(transaction)` - Validate transaction integrity
- `sanitize_string_input(input_string)` - Security sanitization

### ConfigurationHelpers Class

System configuration management:
- `get_risk_thresholds()` - Risk classification thresholds
- `get_alert_thresholds()` - Alert trigger thresholds  
- `get_display_settings()` - UI formatting settings

### Utility Functions

Additional helper functions:
- `safe_divide(numerator, denominator)` - Division with zero handling
- `truncate_text(text, max_length)` - Text truncation
- `get_color_for_risk_category(category)` - Risk category colors
- `get_priority_color(priority)` - Alert priority colors

## Usage Examples

```python
from utils.helpers import DataFormatter, ValidationHelpers

# Format currency
price = DataFormatter.format_currency(1234.56)  # "$1,234.56"

# Format percentage  
deviation = DataFormatter.format_percentage(0.15)  # "15.00%"

# Format risk score with category
risk = DataFormatter.format_risk_score(0.5, include_category=True)  # "0.500 (FRAUD)"

# Format transaction for dashboard
transaction = {"transaction_id": "TXN001", "unit_price": 25.50, "risk_score": 0.15}
formatted = DataFormatter.format_transaction_for_display(transaction)

# Validate transaction data
validation = ValidationHelpers.validate_transaction_data(transaction)
if validation['errors']:
    print("Validation errors:", validation['errors'])
```

## Integration with TRINETRA AI

These utilities are designed to work seamlessly with:
- **FastAPI Backend** - API response formatting
- **Streamlit Dashboard** - Display formatting  
- **Gemini AI Integration** - Prompt formatting
- **ML Pipeline** - Risk score formatting
- **Alert System** - Alert message formatting

## Testing

Run the test suite to verify functionality:
```bash
python -m pytest utils/test_helpers.py -v
```

## Constants

The module defines important constants used throughout the system:
- `CURRENCY_SYMBOL = "$"`
- `PERCENTAGE_PRECISION = 2`
- `DECIMAL_PRECISION = 4`
- `RISK_COLORS` - Color mapping for risk categories
- `PRIORITY_COLORS` - Color mapping for alert priorities

## Error Handling

All formatting functions include comprehensive error handling:
- Invalid inputs return safe default values
- Logging for debugging problematic data
- Graceful degradation when formatting fails

This ensures the TRINETRA AI system remains stable even with unexpected data.