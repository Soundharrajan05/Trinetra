#!/usr/bin/env python3
"""
TRINETRA AI - Risk Score Consistency Property-Based Test Runner
Execute property-based tests for risk score consistency validation (CP-2)
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def run_risk_score_consistency_tests():
    """
    Execute property-based tests for risk score consistency (CP-2).
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("=" * 60)
    print("TRINETRA AI - Risk Score Consistency Property-Based Test Execution")
    print("Testing Risk Score Consistency (CP-2)")
    print("=" * 60)
    print()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Test configuration
    test_file = "test_risk_score_consistency_property.py"
    
    # Check if test file exists
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return 1
    
    print(f"📋 Running property-based tests from: {test_file}")
    print(f"🎯 Target Property: Risk scores must be monotonically related to risk categories")
    print(f"📊 Test Strategy: Property-based testing with hypothesis library")
    print()
    
    # Run the tests
    start_time = time.time()
    
    try:
        # Execute pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_file,
            "-v",
            "--tb=short",
            "--hypothesis-show-statistics"
        ], capture_output=True, text=True, timeout=300)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print("📊 TEST EXECUTION RESULTS")
        print("=" * 40)
        print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
        print()
        
        # Print test output
        if result.stdout:
            print("📋 Test Output:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print(result.stderr)
        
        print()
        print("=" * 60)
        
        # Analyze results
        if result.returncode == 0:
            # Count passed tests from output
            output_lines = result.stdout.split('\n')
            passed_tests = 0
            total_tests = 0
            skipped_tests = 0
            
            for line in output_lines:
                if 'PASSED' in line:
                    passed_tests += 1
                    total_tests += 1
                elif 'FAILED' in line:
                    total_tests += 1
                elif 'SKIPPED' in line:
                    skipped_tests += 1
                    total_tests += 1
            
            print("🎉 ALL RISK SCORE CONSISTENCY TESTS PASSED!")
            print("✅ Risk Score Consistency (CP-2) Property Validated")
            print()
            print("✅ Requirements: Risk scores are monotonically related to risk categories (SAFE < SUSPICIOUS < FRAUD)")
            print("✅ Test Strategy: Property-based testing with various risk score ranges successful")
            print()
            print(f"📊 Test Summary:")
            print(f"   • Passed: {passed_tests}")
            print(f"   • Skipped: {skipped_tests}")
            print(f"   • Total: {total_tests}")
            print()
            print("🔍 Validated Properties:")
            print("   • Monotonic relationship between scores and categories")
            print("   • Correct boundary threshold implementation (-0.2, 0.2)")
            print("   • Consistency across generated and real data")
            print("   • Proper handling of edge cases and boundary values")
            
            return 0
        else:
            print(f"❌ {total_tests - passed_tests}/{total_tests} TESTS FAILED")
            print("❌ Risk Score Consistency (CP-2) Property NOT Validated")
            print()
            print("🔧 Possible Issues:")
            print("   • Risk classification thresholds may be incorrect")
            print("   • Monotonic relationship violation detected")
            print("   • Boundary condition handling issues")
            print("   • Implementation inconsistency in get_risk_category()")
            
            return 1
            
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 5 minutes")
        print("🔧 Consider reducing test complexity or increasing timeout")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected error running tests: {e}")
        return 1

def main():
    """Main entry point for the test runner."""
    print("🚀 Starting TRINETRA AI Risk Score Consistency Property Tests")
    print()
    
    exit_code = run_risk_score_consistency_tests()
    
    if exit_code == 0:
        print()
        print("🎯 PROPERTY VALIDATION COMPLETE")
        print("✅ Risk Score Consistency (CP-2) requirements satisfied")
        print("🔒 System ready for fraud detection with validated risk classification")
    else:
        print()
        print("❌ PROPERTY VALIDATION FAILED")
        print("🔧 Please review and fix the risk classification implementation")
        print("📋 Check the test output above for specific failure details")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())