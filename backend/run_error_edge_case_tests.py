#!/usr/bin/env python3
"""
Test Runner for Error Conditions and Edge Cases

This script runs all error condition and edge case tests for the TRINETRA AI system.
It provides comprehensive testing of boundary conditions, error handling, and system resilience.

Usage:
    python run_error_edge_case_tests.py [--verbose] [--fast] [--coverage]

Options:
    --verbose: Enable verbose output
    --fast: Skip slow/performance tests
    --coverage: Generate coverage report
    --module: Run tests for specific module only

Author: TRINETRA AI Team
Date: 2024
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_test_suite(test_file, verbose=False, fast=False):
    """
    Run a specific test suite.
    
    Args:
        test_file (str): Path to test file
        verbose (bool): Enable verbose output
        fast (bool): Skip slow tests
        
    Returns:
        tuple: (success, output)
    """
    cmd = ["python", "-m", "pytest", test_file]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if fast:
        cmd.extend(["-m", "not slow"])
    
    cmd.extend(["--tb=short", "--maxfail=10"])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Test suite timed out after 5 minutes"
    except Exception as e:
        return False, f"Error running test suite: {str(e)}"


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run TRINETRA AI error condition and edge case tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--fast", "-f", action="store_true", help="Skip slow/performance tests")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--module", "-m", help="Run tests for specific module only")
    
    args = parser.parse_args()
    
    # Define test suites
    test_suites = [
        ("Error Conditions & Edge Cases", "test_error_conditions_edge_cases.py"),
        ("Data Corruption Scenarios", "test_data_corruption_scenarios.py"),
        ("Performance & Stress Tests", "test_performance_stress.py")
    ]
    
    # Filter by module if specified
    if args.module:
        test_suites = [(name, file) for name, file in test_suites 
                      if args.module.lower() in name.lower() or args.module.lower() in file.lower()]
        
        if not test_suites:
            print(f"No test suites found matching '{args.module}'")
            return 1
    
    print("=" * 80)
    print("TRINETRA AI - ERROR CONDITIONS & EDGE CASES TEST SUITE")
    print("=" * 80)
    print(f"Running {len(test_suites)} test suite(s)")
    print(f"Verbose: {args.verbose}")
    print(f"Fast mode: {args.fast}")
    print(f"Coverage: {args.coverage}")
    print("=" * 80)
    
    total_start_time = time.time()
    results = []
    
    for suite_name, test_file in test_suites:
        print(f"\n🧪 Running {suite_name}...")
        print(f"   File: {test_file}")
        
        if not os.path.exists(test_file):
            print(f"   ❌ Test file not found: {test_file}")
            results.append((suite_name, False, "Test file not found"))
            continue
        
        start_time = time.time()
        success, output = run_test_suite(test_file, args.verbose, args.fast)
        duration = time.time() - start_time
        
        if success:
            print(f"   ✅ PASSED ({duration:.2f}s)")
        else:
            print(f"   ❌ FAILED ({duration:.2f}s)")
            if args.verbose:
                print(f"   Output:\n{output}")
        
        results.append((suite_name, success, output))
    
    total_duration = time.time() - total_start_time
    
    # Generate summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed
    
    for suite_name, success, output in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {suite_name}")
        
        if not success and not args.verbose:
            # Show brief error info
            lines = output.split('\n')
            error_lines = [line for line in lines if 'FAILED' in line or 'ERROR' in line]
            if error_lines:
                print(f"         {error_lines[0][:100]}...")
    
    print("=" * 80)
    print(f"Total: {len(results)} suites, {passed} passed, {failed} failed")
    print(f"Duration: {total_duration:.2f} seconds")
    
    if args.coverage:
        print("\n📊 Generating coverage report...")
        try:
            # Run coverage analysis
            coverage_cmd = [
                "python", "-m", "pytest", 
                "--cov=.", 
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing"
            ] + [file for _, file in test_suites if os.path.exists(file)]
            
            subprocess.run(coverage_cmd, check=True)
            print("   ✅ Coverage report generated in htmlcov/")
        except subprocess.CalledProcessError:
            print("   ❌ Coverage report generation failed")
        except FileNotFoundError:
            print("   ❌ pytest-cov not installed. Install with: pip install pytest-cov")
    
    # Return appropriate exit code
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)