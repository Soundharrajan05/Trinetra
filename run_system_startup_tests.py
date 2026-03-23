#!/usr/bin/env python3
"""
TRINETRA AI - System Startup and Shutdown Test Runner
Execute comprehensive tests for system startup and shutdown functionality

**Validates: System Integration Tests (section 10.2)**

This runner executes:
1. Basic startup sequence tests
2. Error handling tests (missing dataset, port conflicts, etc.)
3. Graceful shutdown tests (SIGINT, SIGTERM)
4. Child process cleanup verification
5. Property-based tests for startup robustness
6. Environment variable configuration tests

Success Criteria:
- System runs with single command: `python main.py`
- All components start successfully
- Graceful shutdown handling works
- Comprehensive logging during startup/shutdown
"""

import subprocess
import sys
import os
import time
from pathlib import Path


def run_command(command: str, description: str, timeout: int = 120) -> bool:
    """Run a test command and return success status."""
    print(f"Running: {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path.cwd()
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMED OUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False
    finally:
        print("=" * 60)
        print()


def check_prerequisites() -> bool:
    """Check if all prerequisites are available for testing."""
    print("🔍 Checking prerequisites...")
    
    # Check if main.py exists
    if not Path("main.py").exists():
        print("❌ main.py not found")
        return False
    
    # Check if dataset exists
    dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    if not Path(dataset_path).exists():
        print(f"⚠️  Dataset not found: {dataset_path}")
        print("Some tests will be skipped")
    
    # Check if backend modules exist
    backend_modules = [
        "backend/data_loader.py",
        "backend/feature_engineering.py", 
        "backend/model.py",
        "backend/fraud_detection.py",
        "backend/ai_explainer.py",
        "backend/api.py"
    ]
    
    missing_modules = []
    for module in backend_modules:
        if not Path(module).exists():
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing backend modules: {missing_modules}")
        return False
    
    # Check if frontend exists
    if not Path("frontend/dashboard.py").exists():
        print("❌ frontend/dashboard.py not found")
        return False
    
    print("✅ Prerequisites check passed")
    return True


def main():
    """Run all system startup and shutdown tests."""
    print("🚀 TRINETRA AI - System Startup and Shutdown Test Suite")
    print("=" * 60)
    print("Testing System Integration (section 10.2)")
    print("=" * 60)
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please ensure all required files are present.")
        return 1
    
    # Define test cases
    test_cases = [
        {
            "command": "python -m pytest test_system_startup_shutdown.py::TestSystemStartup::test_basic_startup_sequence -v --tb=short -s",
            "description": "Basic System Startup Sequence Test",
            "timeout": 120
        },
        {
            "command": "python -m pytest test_system_startup_shutdown.py::TestSystemStartup::test_startup_with_missing_dataset -v --tb=short -s",
            "description": "Startup with Missing Dataset Test",
            "timeout": 60
        },
        {
            "command": "python -m pytest test_system_startup_shutdown.py::TestSystemStartup::test_startup_with_invalid_dataset -v --tb=short -s",
            "description": "Startup with Invalid Dataset Test",
            "timeout": 60
        },
        {
            "command": "python -m pytest test_system_startup_shutdown.py::TestSystemStartup::test_port_conflict_handling -v --tb=short -s",
            "description": "Port Conflict Handling Test",
            "timeout": 60
        },
        {
            "command": "python -m pytest test_system_startup_shutdown.py::TestSystemStartup::test_environment_validation -v --tb=short -s",
            "description": "Environment Validation Test",
            "timeout": 60
        },
        {
            "command": "python -m pytest test_system_startup_shutdown.py::TestSystemStartup::test_logging_functionality -v --tb=short -s",
            "description": "Logging Functionality Test",
            "timeout": 60
        },
        {
            "command": "python -m pytest test_system_startup_shutdown.py::TestSystemShutdown::test_graceful_shutdown_sigint -v --tb=short -s",
            "description": "Graceful Shutdown (SIGINT) Test",
            "timeout": 120
        },
        {
            "command": "python -m pytest test_system_startup_shutdown.py::TestSystemShutdown::test_graceful_shutdown_sigterm -v --tb=short -s",
            "description": "Graceful Shutdown (SIGTERM) Test",
            "timeout": 120
        },
        {
            "command": "python -m pytest test_system_startup_shutdown.py::TestSystemShutdown::test_child_process_cleanup -v --tb=short -s",
            "description": "Child Process Cleanup Test",
            "timeout": 120
        },
        {
            "command": "python -m pytest test_system_startup_shutdown.py::TestSystemStartupProperties::test_startup_timing_robustness -v --tb=short -s --hypothesis-show-statistics",
            "description": "Startup Timing Robustness Property Test",
            "timeout": 180
        },
        {
            "command": "python -m pytest test_system_startup_shutdown.py::TestSystemStartupProperties::test_environment_variable_robustness -v --tb=short -s --hypothesis-show-statistics",
            "description": "Environment Variable Robustness Property Test",
            "timeout": 180
        }
    ]
    
    # Run tests
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Running Test {i}/{total_tests}...")
        print(f"Test: {test_case['description']}")
        print()
        
        success = run_command(
            test_case["command"], 
            test_case["description"],
            test_case.get("timeout", 120)
        )
        
        if success:
            passed_tests += 1
        
        # Add delay between tests to avoid port conflicts
        if i < total_tests:
            print("⏳ Waiting 5 seconds before next test...")
            time.sleep(5)
    
    # Summary
    print("=" * 60)
    print("📋 System Startup and Shutdown Test Summary")
    print("=" * 60)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print()
    
    if passed_tests == total_tests:
        print("🎉 ALL SYSTEM STARTUP AND SHUTDOWN TESTS PASSED!")
        print()
        print("✅ System Integration Tests (section 10.2) Validated")
        print("✅ Requirements: System runs with single command: python main.py")
        print("✅ Requirements: All components start successfully")
        print("✅ Requirements: Graceful shutdown handling works")
        print("✅ Requirements: Comprehensive logging during startup/shutdown")
        print("✅ Test Strategy: Comprehensive integration testing successful")
        print()
        print("🚀 TRINETRA AI system startup and shutdown functionality is working correctly!")
        return 0
    else:
        print("⚠️  SOME SYSTEM STARTUP AND SHUTDOWN TESTS FAILED")
        print()
        print("❌ System integration validation incomplete")
        print(f"❌ {total_tests - passed_tests} test(s) failed")
        print()
        print("Please review the failed tests and fix any issues before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())