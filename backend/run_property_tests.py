#!/usr/bin/env python3
"""
Property-Based Test Runner for TRINETRA AI Data Integrity
Executes the CP-1 data integrity property tests
"""

import sys
import subprocess
import os

def run_property_tests():
    """Run the property-based tests for data integrity (CP-1)."""
    print("=" * 60)
    print("TRINETRA AI - Property-Based Test Execution")
    print("Testing Data Integrity (CP-1)")
    print("=" * 60)
    
    # Change to the project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Run the specific property-based tests
    test_commands = [
        [
            "python", "-m", "pytest", 
            "backend/test_data_integrity_property.py::TestDataIntegrityProperty::test_data_integrity_random_rows",
            "-v", "--tb=short"
        ],
        [
            "python", "-m", "pytest", 
            "backend/test_data_integrity_property.py::TestDataIntegrityProperty::test_data_integrity_sample_validation",
            "-v", "--tb=short"
        ]
    ]
    
    all_passed = True
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n🧪 Running Property Test {i}/{len(test_commands)}...")
        print(f"Command: {' '.join(cmd)}")
        print("-" * 40)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ Property Test {i} PASSED")
                print("Key validation points:")
                print("  - Random row indices generated successfully")
                print("  - transaction_id, date, fraud_label verified as non-null")
                print("  - Data integrity maintained across samples")
            else:
                print(f"❌ Property Test {i} FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                all_passed = False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Property Test {i} TIMED OUT")
            all_passed = False
        except Exception as e:
            print(f"💥 Property Test {i} ERROR: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL PROPERTY TESTS PASSED!")
        print("✅ Data Integrity (CP-1) Property Validated")
        print("✅ Requirements: All loaded transactions have valid transaction_id, date, and fraud_label")
        print("✅ Test Strategy: Property-based testing with random row indices successful")
        return 0
    else:
        print("⚠️  SOME PROPERTY TESTS FAILED")
        print("❌ Data integrity validation incomplete")
        return 1

if __name__ == "__main__":
    sys.exit(run_property_tests())