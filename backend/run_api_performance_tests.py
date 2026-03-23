"""
Script to run API performance tests with automatic server management.

This script:
1. Starts the FastAPI server in the background
2. Waits for the server to be ready
3. Runs the performance tests
4. Stops the server
5. Generates a performance report

Usage:
    python backend/run_api_performance_tests.py
"""

import subprocess
import time
import sys
import os
import requests
import signal
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def is_server_ready(url: str = "http://localhost:8000", max_attempts: int = 30) -> bool:
    """
    Check if the API server is ready to accept requests.
    
    Args:
        url: Base URL of the API server
        max_attempts: Maximum number of attempts to check
        
    Returns:
        True if server is ready, False otherwise
    """
    logger.info(f"Checking if server is ready at {url}...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{url}/", timeout=2)
            if response.status_code == 200:
                logger.info(f"✅ Server is ready (attempt {attempt + 1}/{max_attempts})")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_attempts - 1:
            logger.info(f"Server not ready yet, waiting... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(2)
    
    logger.error(f"❌ Server did not become ready after {max_attempts} attempts")
    return False


def start_api_server():
    """
    Start the FastAPI server in the background.
    
    Returns:
        subprocess.Popen object for the server process
    """
    logger.info("Starting FastAPI server...")
    
    # Start the server using uvicorn
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    logger.info(f"Server process started with PID: {server_process.pid}")
    
    return server_process


def stop_api_server(server_process):
    """
    Stop the API server gracefully.
    
    Args:
        server_process: subprocess.Popen object for the server
    """
    logger.info("Stopping API server...")
    
    try:
        # Try graceful termination first
        server_process.terminate()
        
        # Wait up to 5 seconds for graceful shutdown
        try:
            server_process.wait(timeout=5)
            logger.info("✅ Server stopped gracefully")
        except subprocess.TimeoutExpired:
            # Force kill if graceful shutdown fails
            logger.warning("Server did not stop gracefully, forcing shutdown...")
            server_process.kill()
            server_process.wait()
            logger.info("✅ Server stopped forcefully")
    
    except Exception as e:
        logger.error(f"Error stopping server: {e}")


def run_performance_tests():
    """
    Run the API performance tests using pytest.
    
    Returns:
        Exit code from pytest
    """
    logger.info("Running API performance tests...")
    
    # Run pytest with verbose output
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "backend/test_api_performance.py", "-v", "-s", "--tb=short"],
        capture_output=False
    )
    
    return result.returncode


def main():
    """Main execution function."""
    logger.info("="*80)
    logger.info("API PERFORMANCE TEST RUNNER")
    logger.info("="*80)
    
    server_process = None
    exit_code = 1
    
    try:
        # Step 1: Start the API server
        server_process = start_api_server()
        
        # Step 2: Wait for server to be ready
        if not is_server_ready():
            logger.error("❌ Failed to start API server")
            return 1
        
        # Small delay to ensure server is fully initialized
        time.sleep(2)
        
        # Step 3: Run performance tests
        exit_code = run_performance_tests()
        
        # Step 4: Report results
        if exit_code == 0:
            logger.info("="*80)
            logger.info("✅ ALL PERFORMANCE TESTS PASSED")
            logger.info("="*80)
        else:
            logger.error("="*80)
            logger.error("❌ SOME PERFORMANCE TESTS FAILED")
            logger.error("="*80)
    
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Test run interrupted by user")
        exit_code = 130
    
    except Exception as e:
        logger.error(f"❌ Error during test execution: {e}")
        exit_code = 1
    
    finally:
        # Step 5: Always stop the server
        if server_process:
            stop_api_server(server_process)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
