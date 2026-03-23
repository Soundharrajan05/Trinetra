#!/usr/bin/env python3
"""
Hypothesis Framework Setup Validation Script
============================================

This script validates that the hypothesis testing framework is properly configured.

Usage:
    python backend/validate_hypothesis_setup.py
"""

import sys
import os
from pathlib import Path


def check_hypothesis_installed():
    """Check if hypothesis is installed."""
    try:
        import hypothesis
        print(f"✅ Hypothesis installed: version {hypothesis.__version__}")
        return True
    except ImportError:
        print("❌ Hypothesis not installed")
        print("   Run: pip install -r requirements.txt")
        return False


def check_conftest_exists():
    """Check if conftest.py exists."""
    conftest_path = Path(__file__).parent / "conftest.py"
    if conftest_path.exists():
        print(f"✅ conftest.py exists: {conftest_path}")
        return True
    else:
        print(f"❌ conftest.py not found: {conftest_path}")
        return False


def check_conftest_valid():
    """Check if conftest.py is valid Python."""
    try:
        import conftest
        print("✅ conftest.py is valid Python")
        return True
    except Exception as e:
        print(f"❌ conftest.py has errors: {e}")
        return False


def check_test_runner_exists():
    """Check if test runner exists."""
    runner_path = Path(__file__).parent / "run_all_property_tests.py"
    if runner_path.exists():
        print(f"✅ Test runner exists: {runner_path}")
        return True
    else:
        print(f"❌ Test runner not found: {runner_path}")
        return False


def check_property_test_files():
    """Check if property test files exist."""
    test_files = [
        "test_data_integrity_property.py",
        "test_risk_score_consistency_property.py",
        "test_feature_correctness_property.py",
        "test_api_response_validity_property.py",
        "test_alert_trigger_property.py"
    ]
    
    all_exist = True
    for test_file in test_files:
        test_path = Path(__file__).parent / test_file
        if test_path.exists():
            print(f"✅ {test_file} exists")
        else:
            print(f"❌ {test_file} not found")
            all_exist = False
    
    return all_exist


def check_documentation_exists():
    """Check if documentation files exist."""
    doc_files = [
        "HYPOTHESIS_TESTING_GUIDE.md",
        "QUICK_START_PROPERTY_TESTS.md",
        "HYPOTHESIS_SETUP_SUMMARY.md"
    ]
    
    all_exist = True
    for doc_file in doc_files:
        doc_path = Path(__file__).parent / doc_file
        if doc_path.exists():
            print(f"✅ {doc_file} exists")
        else:
            print(f"❌ {doc_file} not found")
            all_exist = False
    
    return all_exist


def check_hypothesis_profiles():
    """Check if hypothesis profiles are configured."""
    try:
        from hypothesis import settings
        
        profiles = ["trinetra_default", "trinetra_quick", "trinetra_thorough", "ci"]
        all_configured = True
        
        for profile in profiles:
            try:
                # Try to load the profile
                settings.load_profile(profile)
                print(f"✅ Profile '{profile}' configured")
            except Exception as e:
                print(f"❌ Profile '{profile}' not configured: {e}")
                all_configured = False
        
        return all_configured
    except Exception as e:
        print(f"❌ Error checking profiles: {e}")
        return False


def check_pytest_markers():
    """Check if pytest markers are configured."""
    try:
        import pytest
        
        # Check if pytest.ini exists
        pytest_ini = Path(__file__).parent.parent / "pytest.ini"
        if pytest_ini.exists():
            print(f"✅ pytest.ini exists: {pytest_ini}")
            
            # Check for property markers in content
            content = pytest_ini.read_text()
            if "property" in content or "markers" in content:
                print("✅ Custom markers configured in pytest.ini")
                return True
            else:
                print("⚠️  Custom markers may not be configured in pytest.ini")
                return True  # Not critical
        else:
            print(f"⚠️  pytest.ini not found: {pytest_ini}")
            return True  # Not critical
    except Exception as e:
        print(f"❌ Error checking pytest markers: {e}")
        return False


def check_hypothesis_database():
    """Check if hypothesis database directory exists."""
    db_path = Path(__file__).parent / ".hypothesis"
    if db_path.exists():
        print(f"✅ Hypothesis database exists: {db_path}")
        
        # Check for examples
        examples_path = db_path / "examples"
        if examples_path.exists():
            example_count = len(list(examples_path.glob("*")))
            print(f"✅ {example_count} example directories in database")
        
        return True
    else:
        print(f"⚠️  Hypothesis database not found: {db_path}")
        print("   (Will be created on first test run)")
        return True  # Not critical, will be created


def run_validation():
    """Run all validation checks."""
    print("=" * 70)
    print("HYPOTHESIS FRAMEWORK SETUP VALIDATION")
    print("=" * 70)
    print()
    
    checks = [
        ("Hypothesis Installation", check_hypothesis_installed),
        ("conftest.py File", check_conftest_exists),
        ("conftest.py Validity", check_conftest_valid),
        ("Test Runner", check_test_runner_exists),
        ("Property Test Files", check_property_test_files),
        ("Documentation Files", check_documentation_exists),
        ("Hypothesis Profiles", check_hypothesis_profiles),
        ("Pytest Markers", check_pytest_markers),
        ("Hypothesis Database", check_hypothesis_database),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 70)
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error during check: {e}")
            results.append((check_name, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nChecks Passed: {passed}/{total}")
    print()
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {check_name}")
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print("🎉 ALL VALIDATION CHECKS PASSED!")
        print("✅ Hypothesis framework is properly configured")
        print("\nNext Steps:")
        print("1. Run property tests: python backend/run_all_property_tests.py")
        print("2. Read quick start: backend/QUICK_START_PROPERTY_TESTS.md")
        print("3. Read full guide: backend/HYPOTHESIS_TESTING_GUIDE.md")
        return 0
    else:
        print("⚠️  SOME VALIDATION CHECKS FAILED")
        print("❌ Please review the errors above and fix them")
        print("\nCommon Solutions:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Check file paths and permissions")
        print("- Review error messages for specific issues")
        return 1


if __name__ == "__main__":
    sys.exit(run_validation())
