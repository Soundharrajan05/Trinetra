# CI Pipeline Quick Reference

## Running Tests Locally

### Property-Based Tests Only
```bash
# Linux/Mac
./run_property_tests.sh

# Windows
run_property_tests.bat

# Direct pytest
pytest backend/test_*_property.py -v --hypothesis-show-statistics
```

### All Tests with Coverage
```bash
pytest --cov=backend --cov=utils --cov-report=term-missing
```

### Specific Property Test
```bash
pytest backend/test_data_integrity_property.py -v
pytest backend/test_risk_score_consistency_property.py -v
pytest backend/test_feature_correctness_property.py -v
pytest backend/test_api_response_validity_property.py -v
pytest backend/test_alert_trigger_property.py -v
```

## CI Pipeline Triggers

- **Automatic**: Push to `main` or `develop`
- **Automatic**: Pull requests to `main` or `develop`
- **Manual**: Actions tab → CI - Property-Based Tests → Run workflow

## Required Secrets

| Secret Name | Purpose | Setup Guide |
|------------|---------|-------------|
| `GEMINI_API_KEY` | AI explanations | [SETUP_SECRETS.md](SETUP_SECRETS.md) |

## Test Coverage Requirements

- Minimum: 80%
- Configured in: `pytest.ini`

## Property Tests (5 Correctness Properties)

1. **CP-1**: Data Integrity
2. **CP-2**: Risk Score Consistency
3. **CP-3**: Feature Engineering Correctness
4. **CP-4**: API Response Validity
5. **CP-5**: Alert Trigger Accuracy

## Viewing Results

### GitHub Actions
1. Go to "Actions" tab
2. Click on workflow run
3. View logs and download artifacts

### Local HTML Report
```bash
pytest --html=report.html --self-contained-html
# Open report.html in browser
```

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests in test mode (no API calls)
TEST_MODE=true pytest backend/test_*_property.py

# Show hypothesis statistics
pytest --hypothesis-show-statistics

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific test class
pytest backend/test_alert_trigger_property.py::TestAlertTriggerAccuracyProperty
```

## Documentation

- **Full Guide**: [CI_PIPELINE_DOCUMENTATION.md](../CI_PIPELINE_DOCUMENTATION.md)
- **Setup Secrets**: [SETUP_SECRETS.md](SETUP_SECRETS.md)
- **Quick Start**: [README.md](README.md)
