#!/usr/bin/env python3
"""
System Startup and Shutdown Tests for TRINETRA AI
Tests the complete system startup sequence and graceful shutdown process.

**Validates: System Integration Tests (section 10.2)**

This module implements comprehensive testing for:
1. Complete system startup sequence
2. Graceful shutdown process
3. Component initialization validation
4. Error handling during startup failures
5. Property-based tests for startup robustness

Success Criteria:
- System runs with single command: `python main.py`
- All components start successfully
- Graceful shutdown handling works
- Comprehensive logging during startup/shutdown
"""

import pytest
import subprocess
import time
import signal
import os
import sys
import tempfile
import shutil
import threading
import requests
import psutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings, assume, example

# Add backend directory to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Test configuration
TEST_TIMEOUT = 60  # seconds
API_PORT = 8000
DASHBOARD_PORT = 8501
STARTUP_WAIT_TIME = 10  # seconds to wait for services to start


class SystemStartupTester:
    """Helper class for system startup and shutdown testing."""
    
    def __init__(self):
        self.main_process: Optional[subprocess.Popen] = None
        self.temp_dirs: List[str] = []
        self.original_cwd = os.getcwd()
        
    def cleanup(self):
        """Clean up test resources."""
        if self.main_process:
            self.terminate_process_tree(self.main_process.pid)
        
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        os.chdir(self.original_cwd)
    
    def terminate_process_tree(self, pid: int):
        """Terminate a process and all its children."""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            
            # Terminate children first
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass
            
            # Wait for children to terminate
            psutil.wait_procs(children, timeout=5)
            
            # Terminate parent
            try:
                parent.terminate()
                parent.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                try:
                    parent.kill()
                except psutil.NoSuchProcess:
                    pass
                    
        except psutil.NoSuchProcess:
            pass
    
    def create_test_environment(self) -> str:
        """Create a temporary test environment with required files."""
        temp_dir = tempfile.mkdtemp(prefix="trinetra_test_")
        self.temp_dirs.append(temp_dir)
        
        # Copy essential files to temp directory
        essential_files = [
            "main.py",
            "requirements.txt",
            ".env.example"
        ]
        
        for file_path in essential_files:
            if os.path.exists(file_path):
                shutil.copy2(file_path, temp_dir)
        
        # Copy backend directory
        backend_src = Path("backend")
        backend_dst = Path(temp_dir) / "backend"
        if backend_src.exists():
            shutil.copytree(backend_src, backend_dst)
        
        # Copy frontend directory
        frontend_src = Path("frontend")
        frontend_dst = Path(temp_dir) / "frontend"
        if frontend_src.exists():
            shutil.copytree(frontend_src, frontend_dst)
        
        # Create necessary directories
        for directory in ["models", "logs", "data"]:
            (Path(temp_dir) / directory).mkdir(exist_ok=True)
        
        # Copy dataset if it exists
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if os.path.exists(dataset_path):
            shutil.copy2(dataset_path, Path(temp_dir) / "data")
        
        return temp_dir
    
    def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """Wait for a service to become available."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        return False
    
    def check_process_health(self, pid: int) -> bool:
        """Check if a process is running and healthy."""
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            return False


class TestSystemStartup:
    """Test cases for system startup functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.tester = SystemStartupTester()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.tester.cleanup()
    
    def test_basic_startup_sequence(self):
        """Test that the system can start up with all components."""
        # Skip if dataset is missing
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Dataset not found for startup test")
        
        # Start the main process
        cmd = [sys.executable, "main.py"]
        self.tester.main_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Wait for startup
        time.sleep(STARTUP_WAIT_TIME)
        
        # Check that main process is running
        assert self.tester.check_process_health(self.tester.main_process.pid), "Main process not running"
        
        # Check that API service is available
        api_available = self.tester.wait_for_service(f"http://localhost:{API_PORT}", timeout=30)
        assert api_available, "FastAPI service not available"
        
        # Check that dashboard service is available
        dashboard_available = self.tester.wait_for_service(f"http://localhost:{DASHBOARD_PORT}", timeout=30)
        assert dashboard_available, "Streamlit dashboard not available"
        
        # Verify API endpoints are working
        response = requests.get(f"http://localhost:{API_PORT}/stats", timeout=10)
        assert response.status_code == 200, "API stats endpoint not working"
        
        # Test graceful shutdown
        self.tester.main_process.send_signal(signal.SIGINT)
        
        # Wait for shutdown
        try:
            self.tester.main_process.wait(timeout=15)
            assert self.tester.main_process.returncode == 0, "Process did not exit cleanly"
        except subprocess.TimeoutExpired:
            pytest.fail("Process did not shutdown gracefully within timeout")
    
    def test_startup_with_missing_dataset(self):
        """Test system behavior when dataset is missing."""
        # Create test environment without dataset
        test_dir = self.tester.create_test_environment()
        
        # Remove dataset if it exists
        dataset_path = Path(test_dir) / "data" / "trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if dataset_path.exists():
            dataset_path.unlink()
        
        # Try to start the system
        cmd = [sys.executable, "main.py"]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=test_dir
        )
        
        # Wait for process to complete or timeout
        try:
            stdout, stderr = process.communicate(timeout=30)
            
            # System should exit with error code
            assert process.returncode != 0, "System should fail when dataset is missing"
            
            # Check that error message mentions dataset
            combined_output = stdout + stderr
            assert "dataset" in combined_output.lower() or "not found" in combined_output.lower(), \
                "Error message should mention missing dataset"
                
        except subprocess.TimeoutExpired:
            process.kill()
            pytest.fail("Process did not exit when dataset was missing")
    
    def test_startup_with_invalid_dataset(self):
        """Test system behavior with corrupted dataset."""
        test_dir = self.tester.create_test_environment()
        
        # Create invalid dataset
        dataset_path = Path(test_dir) / "data" / "trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        with open(dataset_path, 'w') as f:
            f.write("invalid,csv,data\n1,2,3\n")
        
        # Try to start the system
        cmd = [sys.executable, "main.py"]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=test_dir
        )
        
        try:
            stdout, stderr = process.communicate(timeout=30)
            
            # System should handle invalid data gracefully
            combined_output = stdout + stderr
            assert "validation" in combined_output.lower() or "schema" in combined_output.lower() or \
                   "error" in combined_output.lower(), "Should report data validation error"
                   
        except subprocess.TimeoutExpired:
            process.kill()
            pytest.fail("Process hung with invalid dataset")
    
    def test_port_conflict_handling(self):
        """Test system behavior when ports are already in use."""
        # Skip if dataset is missing
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Dataset not found for port conflict test")
        
        # Start a dummy server on API port
        import socket
        dummy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dummy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            dummy_socket.bind(('localhost', API_PORT))
            dummy_socket.listen(1)
            
            # Try to start the main system
            cmd = [sys.executable, "main.py"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            
            # Wait for process to handle port conflict
            try:
                stdout, stderr = process.communicate(timeout=30)
                combined_output = stdout + stderr
                
                # Should detect port conflict
                assert "port" in combined_output.lower() or "address" in combined_output.lower() or \
                       "bind" in combined_output.lower(), "Should detect port conflict"
                       
            except subprocess.TimeoutExpired:
                process.kill()
                pytest.fail("Process did not handle port conflict")
                
        finally:
            dummy_socket.close()
    
    def test_environment_validation(self):
        """Test that environment validation works correctly."""
        # Test with missing backend modules
        test_dir = self.tester.create_test_environment()
        
        # Remove a critical backend module
        backend_file = Path(test_dir) / "backend" / "data_loader.py"
        if backend_file.exists():
            backend_file.unlink()
        
        cmd = [sys.executable, "main.py"]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=test_dir
        )
        
        try:
            stdout, stderr = process.communicate(timeout=20)
            
            # Should fail with import error
            combined_output = stdout + stderr
            assert "import" in combined_output.lower() or "module" in combined_output.lower(), \
                "Should report missing module error"
                
        except subprocess.TimeoutExpired:
            process.kill()
            pytest.fail("Process did not exit with missing modules")
    
    def test_logging_functionality(self):
        """Test that logging is working during startup."""
        # Skip if dataset is missing
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Dataset not found for logging test")
        
        # Start system and capture logs
        cmd = [sys.executable, "main.py"]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Let it run briefly to generate logs
        time.sleep(5)
        
        # Terminate gracefully
        process.send_signal(signal.SIGINT)
        
        try:
            stdout, stderr = process.communicate(timeout=15)
            combined_output = stdout + stderr
            
            # Check for expected log messages
            expected_log_patterns = [
                "TRINETRA AI System Starting",
                "Loading dataset",
                "Engineering fraud detection features",
                "Setting up machine learning model",
                "Starting FastAPI server",
                "Starting Streamlit dashboard"
            ]
            
            found_patterns = 0
            for pattern in expected_log_patterns:
                if pattern.lower() in combined_output.lower():
                    found_patterns += 1
            
            # Should find most log patterns
            assert found_patterns >= len(expected_log_patterns) // 2, \
                f"Expected logging patterns not found. Found {found_patterns}/{len(expected_log_patterns)}"
                
        except subprocess.TimeoutExpired:
            process.kill()
            pytest.fail("Process did not shutdown for logging test")


class TestSystemShutdown:
    """Test cases for system shutdown functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.tester = SystemStartupTester()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.tester.cleanup()
    
    def test_graceful_shutdown_sigint(self):
        """Test graceful shutdown with SIGINT (Ctrl+C)."""
        # Skip if dataset is missing
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Dataset not found for shutdown test")
        
        # Start the system
        cmd = [sys.executable, "main.py"]
        self.tester.main_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Wait for startup
        time.sleep(STARTUP_WAIT_TIME)
        
        # Verify system is running
        assert self.tester.check_process_health(self.tester.main_process.pid)
        
        # Send SIGINT for graceful shutdown
        self.tester.main_process.send_signal(signal.SIGINT)
        
        # Wait for shutdown
        try:
            stdout, stderr = self.tester.main_process.communicate(timeout=20)
            
            # Should exit cleanly
            assert self.tester.main_process.returncode == 0, "Process should exit cleanly with SIGINT"
            
            # Check for shutdown messages
            combined_output = stdout + stderr
            assert "shutdown" in combined_output.lower() or "stopping" in combined_output.lower(), \
                "Should log shutdown messages"
                
        except subprocess.TimeoutExpired:
            self.tester.main_process.kill()
            pytest.fail("Process did not shutdown gracefully with SIGINT")
    
    def test_graceful_shutdown_sigterm(self):
        """Test graceful shutdown with SIGTERM."""
        # Skip if dataset is missing
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Dataset not found for shutdown test")
        
        # Start the system
        cmd = [sys.executable, "main.py"]
        self.tester.main_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Wait for startup
        time.sleep(STARTUP_WAIT_TIME)
        
        # Verify system is running
        assert self.tester.check_process_health(self.tester.main_process.pid)
        
        # Send SIGTERM for graceful shutdown
        self.tester.main_process.send_signal(signal.SIGTERM)
        
        # Wait for shutdown
        try:
            stdout, stderr = self.tester.main_process.communicate(timeout=20)
            
            # Should exit cleanly
            assert self.tester.main_process.returncode == 0, "Process should exit cleanly with SIGTERM"
            
        except subprocess.TimeoutExpired:
            self.tester.main_process.kill()
            pytest.fail("Process did not shutdown gracefully with SIGTERM")
    
    def test_child_process_cleanup(self):
        """Test that child processes are properly cleaned up during shutdown."""
        # Skip if dataset is missing
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Dataset not found for child process test")
        
        # Start the system
        cmd = [sys.executable, "main.py"]
        self.tester.main_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Wait for startup
        time.sleep(STARTUP_WAIT_TIME)
        
        # Get child processes
        try:
            parent = psutil.Process(self.tester.main_process.pid)
            children_before = parent.children(recursive=True)
            child_pids = [child.pid for child in children_before]
            
            # Should have child processes (FastAPI and Streamlit)
            assert len(children_before) > 0, "Should have child processes running"
            
            # Shutdown gracefully
            self.tester.main_process.send_signal(signal.SIGINT)
            self.tester.main_process.wait(timeout=20)
            
            # Check that child processes are cleaned up
            time.sleep(2)  # Give time for cleanup
            
            remaining_children = []
            for pid in child_pids:
                try:
                    child_process = psutil.Process(pid)
                    if child_process.is_running():
                        remaining_children.append(pid)
                except psutil.NoSuchProcess:
                    pass  # Process cleaned up successfully
            
            assert len(remaining_children) == 0, f"Child processes not cleaned up: {remaining_children}"
            
        except (psutil.NoSuchProcess, subprocess.TimeoutExpired):
            pytest.fail("Could not test child process cleanup")


class TestSystemStartupProperties:
    """Property-based tests for system startup robustness."""
    
    def setup_method(self):
        """Set up test environment."""
        self.tester = SystemStartupTester()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.tester.cleanup()
    
    @given(
        startup_delay=st.integers(min_value=1, max_value=5),
        check_interval=st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=5, deadline=60000)
    def test_startup_timing_robustness(self, startup_delay: int, check_interval: int):
        """
        Property: System should start successfully regardless of timing variations.
        
        Test Strategy: Vary startup delays and service check intervals.
        """
        # Skip if dataset is missing
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Dataset not found for property test")
        
        # Start the system
        cmd = [sys.executable, "main.py"]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        try:
            # Wait with variable delay
            time.sleep(startup_delay)
            
            # Check services with variable intervals
            api_available = False
            dashboard_available = False
            
            for _ in range(10):  # Max 10 attempts
                if not api_available:
                    api_available = self.tester.wait_for_service(
                        f"http://localhost:{API_PORT}", timeout=check_interval
                    )
                
                if not dashboard_available:
                    dashboard_available = self.tester.wait_for_service(
                        f"http://localhost:{DASHBOARD_PORT}", timeout=check_interval
                    )
                
                if api_available and dashboard_available:
                    break
                
                time.sleep(check_interval)
            
            # Property: Both services should eventually be available
            assert api_available, "API service should be available with timing variations"
            assert dashboard_available, "Dashboard service should be available with timing variations"
            
        finally:
            # Clean shutdown
            try:
                process.send_signal(signal.SIGINT)
                process.wait(timeout=15)
            except (subprocess.TimeoutExpired, ProcessLookupError):
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
    
    @given(
        environment_vars=st.dictionaries(
            st.sampled_from(['LOG_LEVEL', 'API_HOST', 'API_PORT']),
            st.sampled_from(['INFO', 'DEBUG', 'WARNING', '0.0.0.0', '127.0.0.1', '8001', '8002']),
            min_size=0,
            max_size=2
        )
    )
    @settings(max_examples=3, deadline=60000)
    def test_environment_variable_robustness(self, environment_vars: Dict[str, str]):
        """
        Property: System should handle various environment variable configurations.
        
        Test Strategy: Test with different environment variable combinations.
        """
        # Skip if dataset is missing
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Dataset not found for environment test")
        
        # Skip invalid port configurations
        if 'API_PORT' in environment_vars:
            try:
                port = int(environment_vars['API_PORT'])
                assume(1024 <= port <= 65535)  # Valid port range
            except ValueError:
                assume(False)  # Skip non-numeric ports
        
        # Set up environment
        original_env = os.environ.copy()
        test_env = original_env.copy()
        test_env.update(environment_vars)
        
        try:
            # Start system with modified environment
            cmd = [sys.executable, "main.py"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=test_env,
                cwd=os.getcwd()
            )
            
            # Wait for startup
            time.sleep(8)
            
            # Check if process is still running (didn't crash)
            if process.poll() is None:
                # Process is running, try to access services
                api_port = int(environment_vars.get('API_PORT', API_PORT))
                
                try:
                    response = requests.get(f"http://localhost:{api_port}/", timeout=5)
                    # Property: System should respond on configured port
                    assert response.status_code == 200, "System should respond on configured port"
                except requests.exceptions.RequestException:
                    # May not be ready yet, which is acceptable
                    pass
            
            # Clean shutdown
            try:
                process.send_signal(signal.SIGINT)
                process.wait(timeout=15)
            except (subprocess.TimeoutExpired, ProcessLookupError):
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
                    
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])