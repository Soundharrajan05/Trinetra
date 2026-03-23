# GitHub Actions CI/CD Configuration

This directory contains the CI/CD configuration for TRINETRA AI.

## Files

- **workflows/ci.yml**: Main CI pipeline configuration
- **SETUP_SECRETS.md**: Guide for configuring GitHub Secrets

## Quick Start

### 1. Configure Secrets

Before the CI pipeline can run successfully, you need to configure the required secrets:

1. Go to your repository Settings → Secrets and variables → Actions
2. Add `GEMINI_API_KEY` secret (see [SETUP_SECRETS.md](SETUP_SECRETS.md) for details)

### 2. Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. If prompted, click "I understand my workflows, go ahead and enable them"

### 3. Trigger the Pipeline

The pipeline will automatically run on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual trigger from the Actions tab

## What Gets Tested

The CI pipeline runs:

1. **Property-Based Tests**: All 5 correctness properties
   - Data Integrity (CP-1)
   - Risk Score Consistency (CP-2)
   - Feature Engineering Correctness (CP-3)
   - API Response Validity (CP-4)
   - Alert Trigger Accuracy (CP-5)

2. **Full Test Suite**: All unit and integration tests

3. **Coverage Analysis**: Ensures >80% code coverage

## Viewing Results

### In GitHub

1. Go to the "Actions" tab
2. Click on a workflow run
3. View logs for each step
4. Download test report artifacts

### Locally

Run the same tests that run in CI:

```bash
# Linux/Mac
./run_property_tests.sh

# Windows
run_property_tests.bat

# Or directly with pytest
pytest backend/test_*_property.py -v --hypothesis-show-statistics
```

## Troubleshooting

See [SETUP_SECRETS.md](SETUP_SECRETS.md) for common issues and solutions.

## Documentation

For detailed information about the CI pipeline, see [CI_PIPELINE_DOCUMENTATION.md](../CI_PIPELINE_DOCUMENTATION.md) in the root directory.
