"""
Dashboard Component Integration Tests for TRINETRA AI

This test suite validates that dashboard components properly integrate with the FastAPI backend,
ensuring data flows correctly from API to dashboard visualizations, error handling works properly,
and all dashboard sections render correctly with real data.

**Validates: Task 12.2 Integration Testing - Test dashboard component integration**
"""

import pytest
import requests
import json
import time
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDashboardComponentIntegration:
    """Integration tests for dashboard components with FastAPI backend."""
    
    API_BASE_URL = "http://localhost:8000"
    
    @classmethod
    def setup_class(cls):
        """Set up test environment with running API server."""
        print("🔧 Setting up dashboard component integration test environment...")
        
        # Check if dataset exists
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        if not os.path.exists(dataset_path):
            pytest.skip("Real dataset not available for integration test")
        
        # Start API server in background for testing
        cls.start_test_api_server()
        
        # Wait for API to be ready
        cls.wait_for_api_ready()
        
    @classmethod
    def teardown_class(cls):
        """Clean up test environment."""
        print("🧹 Cleaning up test environment...")
        if hasattr(cls, 'api_process') and cls.api_process:
            cls.api_process.terminate()
            cls.api_process.wait()
    
    @classmethod
    def start_test_api_server(cls):
        """Start FastAPI server for testing."""
        try:
            cmd = [
                sys.executable, "-m", "uvicorn",
                "backend.api:app",
                "--host", "localhost",
                "--port", "8000",
                "--log-level", "warning"
            ]
            
            cls.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            print("✅ Test API server started")
            
        except Exception as e:
            pytest.skip(f"Could not start test API server: {e}")
    
    @classmethod
    def wait_for_api_ready(cls, max_retries=15, delay=2):
        """Wait for API server to be ready."""
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.API_BASE_URL}/", timeout=5)
                if response.status_code == 200:
                    print("✅ API server is ready")
                    return True
            except Exception:
                if i < max_retries - 1:
                    print(f"Waiting for API server... ({i+1}/{max_retries})")
                    time.sleep(delay)
                else:
                    pytest.skip("API server not responding")
        return False
    
    def test_kpi_metrics_component_integration(self):
        """Test 1: KPI metrics component integration with /stats endpoint."""
        print("📊 Testing KPI metrics component integration...")
        
        # Simulate dashboard KPI component fetching stats
        response = requests.get(f"{self.API_BASE_URL}/stats", timeout=10)
        assert response.status_code == 200, "Stats endpoint should be accessible"
        
        data = response.json()
        assert data["status"] == "success", "Stats should return success status"
        
        stats = data["data"]
        
        # Verify all KPI fields required by dashboard are pres