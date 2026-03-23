# CI Pipeline Documentation - TRINETRA AI

## Overview

This document describes the Continuous Integration (CI) pipeline for the TRINETRA AI Trade Fraud Intelligence System. The CI pipeline automatically runs property-based tests and validates all correctness properties whenever code is pushed or a pull request is created.

## CI Configuration

### Platform: GitHub Actions

The CI pipeline is configured using GitHub Actions and is defined in `.github/workflows/ci.yml`.

### Trigger Events

The pipeline runs automatically on:
- **Push events** to `main` and `develop` branches
- **Pull request events** targeting `main` and `develop` branches
- **Manual trigger** via workflow_dispatch (can be triggered from GitHub UI)

### Python Version Matrix

The pipeline tests against multiple Python versions to ensure compatibility:
- Python 3.9
- Python 3.10
- Python 3.11

## Pipeline Stages

### 1. Code Checkout
```yaml
- name: Checkout code
  uses: actions/checkout@v4
```
Checks out the repository code to the CI runner.

### 2. Python Environment Setup
```yaml
- name: Set up Python ${{ matrix.python-version }}
  uses: actions/setup-python@v4
```
Sets up the specified Python version from the matrix.

### 3. Dependency Caching
```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
```
Caches pip dependencies to speed up subsequent runs. The cache key is based on the `requirements.txt` file hash.

### 4. Dependency Installation
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```
Installs all required Python packages from `requirements.txt`, including:
- pytest (testing framework)
- hypothesis (property-based testing)
- All application dependencies

### 5. Property-Based Test Execution
```yaml
- name: Run property-based tests
  run: |
    pytest backend/test_*_property.py -v --tb=short --hypothesis-show-statistics
```

This stage specifically runs all property-based tests that validate the 5 correctness properties:

#### CP-1: Data Integrity (`test_data_integrity_property.py`)
- Validates that all loaded transactions have valid transaction_id, date, and fraud_label
- Uses hypothesis to generate random row indices and verify required fields

#### CP-2: Risk Score Consistency (`test_risk_score_consistency_property.py`)
- Verifies risk scores are monotonically related to risk categories
- Tests: SAFE < SUSPICIOUS < FRAUD ordering
- Validates boundary conditions

#### CP-3: Feature Engineering Correctness (`test_feature_correctness_property.py`)
- Tests that engineered features are mathematically correct
- Validates feature calculations with known input values
- Checks feature ranges are within expected bounds

#### CP-4: API Response Validity (`test_api_response_validity_property.py`)
- Validates all API endpoints return valid JSON with expected schema
- Tests pagination, error handling, and response formats
- Verifies HTTP status codes

#### CP-5: Alert Trigger Accuracy (`test_alert_trigger_property.py`)
- Verifies alerts are triggered if and only if threshold conditions are met
- Tests boundary conditions for all alert types
- Validates alert combinations

**Test Options:**
- `-v`: Verbose output showing each test
- `--tb=short`: Short traceback format for failures
- `--hypothesis-show-statistics`: Display hypothesis test statistics

### 6. Full Test Suite with Coverage
```yaml
- name: Run all tests with coverage
  run: |
    pytest --cov=backend --cov=utils --cov-report=xml --cov-report=term-missing
```

Runs the complete test suite including:
- All property-based tests
- Unit tests
- Integration tests
- Generates coverage reports in XML and terminal formats

**Coverage Requirements:**
- Minimum 80% code coverage (configured in `pytest.ini`)
- Coverage reports for `backend/` and `utils/` directories

### 7. Coverage Report Upload
```yaml
- name: Upload coverage reports
  uses: codecov/codecov-action@v3
```
Uploads coverage reports to Codecov for tracking coverage trends over time.

### 8. Test Report Generation
```yaml
- name: Generate test report
  run: |
    pytest --html=report.html --self-contained-html
```
Generates an HTML test report for detailed test results visualization.

### 9. Artifact Upload
```yaml
- name: Upload test report
  uses: actions/upload-artifact@v3
```
Uploads the HTML test report as a GitHub Actions artifact for later review.

## Environment Variables

The CI pipeline uses the following environment variables:

### Required Secrets
- `GEMINI_API_KEY`: API key for Google Gemini AI service
  - **Setup**: Add this secret in GitHub repository settings under Settings → Secrets and variables → Actions
  - **Note**: Tests will use mocked responses if the API key is not available

### Test Mode
- `TEST_MODE=true`: Enables test mode which may use mocked services for faster execution

## Running Tests Locally

To run the same tests locally that run in CI:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Property-Based Tests Only
```bash
pytest backend/test_*_property.py -v --tb=short --hypothesis-show-statistics
```

### 3. Run All Tests with Coverage
```bash
pytest --cov=backend --cov=utils --cov-report=term-missing
```

### 4. Run Specific Property Test
```bash
# Data Integrity
pytest backend/test_data_integrity_property.py -v

# Risk Score Consistency
pytest backend/test_risk_score_consistency_property.py -v

# Feature Correctness
pytest backend/test_feature_correctness_property.py -v

# API Response Validity
pytest backend/test_api_response_validity_property.py -v

# Alert Trigger Accuracy
pytest backend/test_alert_trigger_property.py -v
```

### 5. Generate HTML Report
```bash
pip install pytest-html
pytest --html=report.html --self-contained-html
```

## Hypothesis Configuration

Property-based tests use Hypothesis with the following configuration (in `backend/conftest.py`):

```python
from hypothesis import settings, Verbosity, Phase

settings.register_profile("ci", max_examples=100, verbosity=Verbosity.verbose)
settings.register_profile("dev", max_examples=20, verbosity=Verbosity.normal)
settings.register_profile("debug", max_examples=10, verbosity=Verbosity.debug)
```

The CI pipeline uses the default profile with sufficient examples to catch edge cases.

## Test Data Generators

Property-based tests use custom data generators defined in `backend/test_data_generators.py`:

- `transaction_id_strategy()`: Generates valid transaction IDs
- `date_strategy()`: Generates valid date strings
- `fraud_label_strategy()`: Generates fraud labels (0 or 1)
- `risk_score_strategy()`: Generates risk scores in valid ranges
- `transaction_row_strategy()`: Generates complete transaction records
- `feature_engineering_input_strategy()`: Generates feature engineering inputs
- `alert_trigger_transaction_strategy()`: Generates transactions for alert testing

## Troubleshooting

### Common Issues

#### 1. Test Failures Due to Missing API Key
**Symptom**: Tests fail with authentication errors
**Solution**: Ensure `GEMINI_API_KEY` is set in GitHub Secrets or use `TEST_MODE=true` to enable mocking

#### 2. Coverage Below Threshold
**Symptom**: Pipeline fails with "coverage below 80%"
**Solution**: Add tests for uncovered code or adjust threshold in `pytest.ini`

#### 3. Hypothesis Test Failures
**Symptom**: Property tests fail with counterexamples
**Solution**: Review the counterexample in the test output and fix the underlying issue in the code

#### 4. Dependency Installation Failures
**Symptom**: pip install fails
**Solution**: Check `requirements.txt` for version conflicts or update package versions

### Viewing Test Results

1. **In GitHub Actions UI**:
   - Navigate to the "Actions" tab in your repository
   - Click on the workflow run
   - View logs for each step
   - Download test report artifacts

2. **Locally**:
   - Run tests with `-v` flag for verbose output
   - Open `report.html` in a browser for detailed results
   - Check `htmlcov/index.html` for coverage report

## Performance Considerations

### Pipeline Optimization

1. **Dependency Caching**: Pip dependencies are cached to reduce installation time
2. **Matrix Strategy**: Tests run in parallel across Python versions
3. **Hypothesis Examples**: Configured for reasonable number of examples (balance between speed and thoroughness)

### Expected Run Times

- Property-based tests only: ~2-5 minutes
- Full test suite with coverage: ~5-10 minutes
- Total pipeline (all Python versions): ~15-30 minutes

## Maintenance

### Updating the Pipeline

To modify the CI pipeline:

1. Edit `.github/workflows/ci.yml`
2. Test changes locally first
3. Commit and push to a feature branch
4. Verify pipeline runs successfully on the PR
5. Merge to main/develop

### Adding New Property Tests

When adding new correctness properties:

1. Create test file: `backend/test_<property_name>_property.py`
2. Use naming convention: `test_*_property.py`
3. Import hypothesis: `from hypothesis import given, strategies as st`
4. Add test generators to `backend/test_data_generators.py` if needed
5. Document the property in this file
6. The CI pipeline will automatically pick up the new test

### Monitoring Test Health

- Review test results regularly in GitHub Actions
- Monitor coverage trends in Codecov
- Address flaky tests promptly
- Update test data generators as the system evolves

## Integration with Development Workflow

### Pre-commit Checks (Recommended)

Add a pre-commit hook to run property tests locally:

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest backend/test_*_property.py -v --tb=short
```

### Branch Protection Rules (Recommended)

Configure GitHub branch protection to require:
- CI pipeline must pass before merging
- At least one code review approval
- Up-to-date branches before merging

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.com/)

## Support

For issues with the CI pipeline:
1. Check the troubleshooting section above
2. Review GitHub Actions logs for detailed error messages
3. Consult the test documentation in `backend/HYPOTHESIS_TESTING_GUIDE.md`
4. Review property test implementation in individual test files
