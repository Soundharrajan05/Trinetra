# Quick Start: Property-Based Testing
## TRINETRA AI - 5-Minute Setup Guide

This guide gets you running property-based tests in 5 minutes.

---

## ✅ Prerequisites

Ensure hypothesis is installed:

```bash
pip install -r requirements.txt
```

Verify installation:

```bash
python -c "import hypothesis; print(f'✅ Hypothesis {hypothesis.__version__} installed')"
```

---

## 🚀 Quick Test Commands

### Run All 5 Correctness Properties

```bash
# Standard run (recommended)
python backend/run_all_property_tests.py

# Quick run (faster, fewer examples)
python backend/run_all_property_tests.py --profile trinetra_quick

# Thorough run (comprehensive, more examples)
python backend/run_all_property_tests.py --profile trinetra_thorough

# With detailed output
python backend/run_all_property_tests.py --verbose

# Generate markdown report
python backend/run_all_property_tests.py --report
```

### Run Individual Properties

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

### Run by Marker

```bash
# All property tests
pytest -m property -v

# Specific correctness property
pytest -m cp1 -v  # Data Integrity
pytest -m cp2 -v  # Risk Score Consistency
pytest -m cp3 -v  # Feature Engineering
pytest -m cp4 -v  # API Response Validity
pytest -m cp5 -v  # Alert Trigger Accuracy
```

---

## 📊 Understanding Output

### Successful Test

```
✅ CP-1 PASSED (2.34s)
```

Means:
- All generated test cases passed
- Property holds for all tested inputs
- No counterexamples found

### Failed Test

```
❌ CP-2 FAILED (1.56s)
Falsifying example: test_risk_score_monotonic_relationship(
    risk_scores=[-0.2, 0.2]
)
```

Means:
- Hypothesis found a counterexample
- The property doesn't hold for the given input
- Example is automatically shrunk to minimal failing case

### Skipped Test

```
⚠️ CP-4: Not executed
Error: Test file not found
```

Means:
- Test file doesn't exist yet
- Or dataset/model not available
- Check error message for details

---

## 🎯 What Each Property Tests

| Property | What It Validates | Key Checks |
|----------|-------------------|------------|
| **CP-1** | Data Integrity | transaction_id, date, fraud_label are valid |
| **CP-2** | Risk Score Consistency | SAFE < SUSPICIOUS < FRAUD ordering |
| **CP-3** | Feature Engineering | Mathematical correctness of 6 features |
| **CP-4** | API Response Validity | JSON schema, HTTP codes, error handling |
| **CP-5** | Alert Trigger Accuracy | Alerts fire at correct thresholds |

---

## 🔧 Configuration Profiles

| Profile | Examples | Deadline | When to Use |
|---------|----------|----------|-------------|
| `trinetra_quick` | 10 | 10s | Development, quick feedback |
| `trinetra_default` | 50 | 30s | Standard testing |
| `trinetra_thorough` | 200 | 60s | Pre-release validation |
| `ci` | 20 | 20s | Continuous integration |

Set profile via environment variable:

```bash
# Windows
set HYPOTHESIS_PROFILE=trinetra_thorough

# Linux/Mac
export HYPOTHESIS_PROFILE=trinetra_thorough
```

Or pass to runner:

```bash
python backend/run_all_property_tests.py --profile trinetra_thorough
```

---

## 📁 Key Files

```
backend/
├── conftest.py                              # Pytest & Hypothesis config
├── run_all_property_tests.py                # Main test runner
├── test_data_integrity_property.py          # CP-1 tests
├── test_risk_score_consistency_property.py  # CP-2 tests
├── test_feature_correctness_property.py     # CP-3 tests
├── test_api_response_validity_property.py   # CP-4 tests
├── test_alert_trigger_property.py           # CP-5 tests
├── HYPOTHESIS_TESTING_GUIDE.md              # Detailed guide
└── QUICK_START_PROPERTY_TESTS.md            # This file
```

---

## 🐛 Common Issues

### Issue: Dataset not found

```
pytest.skip: Dataset not found: data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
```

**Solution:** Ensure dataset exists in `data/` directory

### Issue: Model not found

```
pytest.skip: Trained model not found: models/isolation_forest.pkl
```

**Solution:** Train model first:
```bash
python backend/model.py
```

### Issue: Tests timeout

```
⏰ CP-3 TIMED OUT (30.00s)
```

**Solution:** Use quick profile or increase deadline:
```bash
python backend/run_all_property_tests.py --profile trinetra_quick
```

### Issue: Import errors

```
ModuleNotFoundError: No module named 'hypothesis'
```

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📈 Expected Results

After running all tests, you should see:

```
======================================================================
PROPERTY-BASED TESTING SUMMARY
======================================================================

Results: 5/5 properties validated
Total Duration: 12.45s
Profile: trinetra_default

Detailed Results:
----------------------------------------------------------------------
✅ PASS | CP-1: Data Integrity (2.34s)
✅ PASS | CP-2: Risk Score Consistency (3.12s)
✅ PASS | CP-3: Feature Engineering Correctness (4.56s)
✅ PASS | CP-4: API Response Validity (1.89s)
✅ PASS | CP-5: Alert Trigger Accuracy (0.54s)

======================================================================
🎉 ALL CORRECTNESS PROPERTIES VALIDATED!
✅ System meets all formal specifications
======================================================================
```

---

## 🎓 Next Steps

1. **Run all tests** to validate current implementation
2. **Review failing tests** if any
3. **Check generated report** for detailed analysis
4. **Read full guide** at `HYPOTHESIS_TESTING_GUIDE.md`
5. **Write new tests** as needed for new features

---

## 💡 Pro Tips

1. **Start with quick profile** during development
2. **Use thorough profile** before commits
3. **Check hypothesis database** for stored examples
4. **Add `@example()` decorators** for edge cases you discover
5. **Run specific tests** when debugging failures

---

## 📚 More Information

- **Full Guide:** `backend/HYPOTHESIS_TESTING_GUIDE.md`
- **Hypothesis Docs:** https://hypothesis.readthedocs.io/
- **Pytest Docs:** https://docs.pytest.org/

---

*TRINETRA AI - Trade Fraud Intelligence System*
*Property-Based Testing with Hypothesis*
