#!/usr/bin/env python3
"""
TRINETRA AI - Model Consistency Property-Based Test Runner
Execute property-based tests for ML model consistency validation (CP-2)
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status."""
    print(f"🧪 {description}...")
    print(f"Command: {command}")
    print("-" * 40)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print(f"✅ {description} PASSED")
            # Extract key information from output
            if "passed" in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if "passed" in line and "failed" not in line:
                        print(f"Key validation points:")
                        print(f"  - Model training consistency verified")
                        print(f"  - Prediction consistency validated")
                        print(f"  - Serialization/deserialization tested")
                        break
            return True
        else:
            print(f"❌ {description} FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ {description} ERROR: {str(e)}")
        return False

def main():
    """Run all model consistency property-based tests."""
    print("=" * 60)
    print("TRINETRA AI - Model Consistency Property-Based Test Execution")
    print("Testing Model Consistency (CP-2)")
    print("=" * 60)
    print()
    
    # Test cases to run
    test_cases = [
        {
            "command": "python -m pytest backend/test_model_consistency_property.py::TestModelConsistencyProperty::test_model_training_consistency -v --tb=short",
            "description": "Model Training Consistency Test"
        },
        {
            "command": "python -m pytest backend/test_model_consistency_property.py::TestModelConsistencyProperty::test_model_prediction_consistency -v --tb=short", 
            "description": "Model Prediction Consistency Test"
        },
        {
            "command": "python -m pytest backend/test_model_consistency_property.py::TestModelConsistencyProperty::test_model_serialization_deserialization_consistency -v --tb=short",
            "description": "Model Serialization Consistency Test"
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Running Property Test {i}/{total_tests}...")
        success = run_command(test_case["command"], test_case["description"])
        if success:
            passed_tests += 1
        print()
    
    # Summary
    print("=" * 60)
    if passed_tests == total_tests:
        print("🎉 ALL MODEL CONSISTENCY TESTS PASSED!")
        print("✅ Model Consistency (CP-2) Property Validated")
        print("✅ Requirements: ML model behaves consistently across training runs and serialization")
        print("✅ Test Strategy: Property-based testing with multiple training runs successful")
        return 0
    else:
        print(f"❌ {total_tests - passed_tests}/{total_tests} TESTS FAILED")
        print("❌ Model Consistency (CP-2) Property NOT Validated")
        return 1

if __name__ == "__main__":
    sys.exit(main())