#!/usr/bin/env python3
"""
Comprehensive Property-Based Test Runner for TRINETRA AI
=========================================================

This script runs all 5 correctness property tests defined in the requirements:
- CP-1: Data Integrity
- CP-2: Risk Score Consistency
- CP-3: Feature Engineering Correctness
- CP-4: API Response Validity
- CP-5: Alert Trigger Accuracy

Usage:
    python backend/run_all_property_tests.py [--profile PROFILE] [--verbose]

Profiles:
    - trinetra_default: Standard testing (50 examples, 30s deadline)
    - trinetra_quick: Fast testing (10 examples, 10s deadline)
    - trinetra_thorough: Comprehensive testing (200 examples, 60s deadline)
    - ci: Continuous integration (20 examples, 20s deadline)
"""

import sys
import subprocess
import os
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import time


class PropertyTestRunner:
    """Runner for all property-based tests."""
    
    def __init__(self, profile: str = "trinetra_default", verbose: bool = False):
        """
        Initialize the test runner.
        
        Args:
            profile: Hypothesis profile to use
            verbose: Whether to show verbose output
        """
        self.profile = profile
        self.verbose = verbose
        self.project_root = Path(__file__).parent.parent
        self.results: Dict[str, Dict] = {}
        
    def run_test_file(self, test_file: str, property_name: str, property_id: str) -> Tuple[bool, float]:
        """
        Run a single property test file.
        
        Args:
            test_file: Path to test file relative to project root
            property_name: Human-readable property name
            property_id: Property identifier (CP-1, CP-2, etc.)
        
        Returns:
            Tuple of (success: bool, duration: float)
        """
        print(f"\n{'=' * 70}")
        print(f"Testing {property_id}: {property_name}")
        print(f"{'=' * 70}")
        print(f"Test File: {test_file}")
        print(f"Profile: {self.profile}")
        print("-" * 70)
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            test_file,
            "-v" if self.verbose else "-q",
            "--tb=short",
            f"-m={property_id.lower().replace('-', '')}",
            "--disable-warnings"
        ]
        
        # Set environment variable for hypothesis profile
        env = os.environ.copy()
        env["HYPOTHESIS_PROFILE"] = self.profile
        
        # Run the test
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env
            )
            duration = time.time() - start_time
            
            success = result.returncode == 0
            
            if success:
                print(f"✅ {property_id} PASSED ({duration:.2f}s)")
            else:
                print(f"❌ {property_id} FAILED ({duration:.2f}s)")
                if self.verbose:
                    print("\nSTDOUT:")
                    print(result.stdout)
                    print("\nSTDERR:")
                    print(result.stderr)
            
            self.results[property_id] = {
                "name": property_name,
                "success": success,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            return success, duration
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"⏰ {property_id} TIMED OUT ({duration:.2f}s)")
            self.results[property_id] = {
                "name": property_name,
                "success": False,
                "duration": duration,
                "error": "Timeout"
            }
            return False, duration
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {property_id} ERROR: {e} ({duration:.2f}s)")
            self.results[property_id] = {
                "name": property_name,
                "success": False,
                "duration": duration,
                "error": str(e)
            }
            return False, duration
    
    def run_all_tests(self) -> bool:
        """
        Run all property-based tests.
        
        Returns:
            True if all tests passed, False otherwise
        """
        print("\n" + "=" * 70)
        print("TRINETRA AI - Comprehensive Property-Based Testing")
        print("=" * 70)
        print(f"Hypothesis Profile: {self.profile}")
        print(f"Verbose Mode: {self.verbose}")
        print("=" * 70)
        
        # Define all property tests
        tests = [
            {
                "file": "backend/test_data_integrity_property.py",
                "name": "Data Integrity",
                "id": "CP-1",
                "description": "All loaded transactions must have valid transaction_id, date, and fraud_label"
            },
            {
                "file": "backend/test_risk_score_consistency_property.py",
                "name": "Risk Score Consistency",
                "id": "CP-2",
                "description": "Risk scores must be monotonically related to risk categories (SAFE < SUSPICIOUS < FRAUD)"
            },
            {
                "file": "backend/test_feature_correctness_property.py",
                "name": "Feature Engineering Correctness",
                "id": "CP-3",
                "description": "Engineered features must be mathematically correct and within expected ranges"
            },
            {
                "file": "backend/test_api_response_validity_property.py",
                "name": "API Response Validity",
                "id": "CP-4",
                "description": "All API endpoints must return valid JSON with expected schema"
            },
            {
                "file": "backend/test_alert_trigger_property.py",
                "name": "Alert Trigger Accuracy",
                "id": "CP-5",
                "description": "Alerts must be triggered if and only if threshold conditions are met"
            }
        ]
        
        # Run each test
        total_duration = 0
        all_passed = True
        
        for test in tests:
            # Check if test file exists
            test_path = self.project_root / test["file"]
            if not test_path.exists():
                print(f"\n⚠️  Test file not found: {test['file']}")
                print(f"   Skipping {test['id']}: {test['name']}")
                self.results[test["id"]] = {
                    "name": test["name"],
                    "success": False,
                    "duration": 0,
                    "error": "Test file not found"
                }
                all_passed = False
                continue
            
            success, duration = self.run_test_file(
                test["file"],
                test["name"],
                test["id"]
            )
            
            total_duration += duration
            if not success:
                all_passed = False
        
        # Print summary
        self.print_summary(total_duration)
        
        return all_passed
    
    def print_summary(self, total_duration: float):
        """
        Print test summary.
        
        Args:
            total_duration: Total time taken for all tests
        """
        print("\n" + "=" * 70)
        print("PROPERTY-BASED TESTING SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for r in self.results.values() if r.get("success", False))
        total = len(self.results)
        
        print(f"\nResults: {passed}/{total} properties validated")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Profile: {self.profile}")
        
        print("\nDetailed Results:")
        print("-" * 70)
        
        for prop_id in ["CP-1", "CP-2", "CP-3", "CP-4", "CP-5"]:
            if prop_id in self.results:
                result = self.results[prop_id]
                status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
                duration = result.get("duration", 0)
                name = result.get("name", "Unknown")
                
                print(f"{status} | {prop_id}: {name} ({duration:.2f}s)")
                
                if "error" in result:
                    print(f"       Error: {result['error']}")
            else:
                print(f"⚠️  SKIP | {prop_id}: Not executed")
        
        print("\n" + "=" * 70)
        
        if passed == total:
            print("🎉 ALL CORRECTNESS PROPERTIES VALIDATED!")
            print("✅ System meets all formal specifications")
        else:
            print("⚠️  SOME PROPERTIES FAILED VALIDATION")
            print("❌ System does not meet all formal specifications")
        
        print("=" * 70 + "\n")
    
    def generate_report(self, output_file: str = "property_test_report.md"):
        """
        Generate a markdown report of test results.
        
        Args:
            output_file: Path to output markdown file
        """
        report_path = self.project_root / output_file
        
        with open(report_path, 'w') as f:
            f.write("# TRINETRA AI - Property-Based Testing Report\n\n")
            f.write(f"**Profile:** {self.profile}\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            passed = sum(1 for r in self.results.values() if r.get("success", False))
            total = len(self.results)
            f.write(f"- **Total Properties:** {total}\n")
            f.write(f"- **Passed:** {passed}\n")
            f.write(f"- **Failed:** {total - passed}\n\n")
            
            f.write("## Correctness Properties\n\n")
            
            for prop_id in ["CP-1", "CP-2", "CP-3", "CP-4", "CP-5"]:
                if prop_id in self.results:
                    result = self.results[prop_id]
                    status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
                    name = result.get("name", "Unknown")
                    duration = result.get("duration", 0)
                    
                    f.write(f"### {prop_id}: {name}\n\n")
                    f.write(f"- **Status:** {status}\n")
                    f.write(f"- **Duration:** {duration:.2f}s\n")
                    
                    if "error" in result:
                        f.write(f"- **Error:** {result['error']}\n")
                    
                    f.write("\n")
        
        print(f"📄 Report generated: {report_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run all property-based tests for TRINETRA AI"
    )
    parser.add_argument(
        "--profile",
        choices=["trinetra_default", "trinetra_quick", "trinetra_thorough", "ci"],
        default="trinetra_default",
        help="Hypothesis profile to use"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate markdown report"
    )
    
    args = parser.parse_args()
    
    # Create and run test runner
    runner = PropertyTestRunner(profile=args.profile, verbose=args.verbose)
    success = runner.run_all_tests()
    
    # Generate report if requested
    if args.report:
        runner.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
