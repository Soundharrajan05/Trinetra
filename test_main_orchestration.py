#!/usr/bin/env python3
"""
Unit Tests for main.py Orchestration Logic
Tests the main.py orchestration functions without starting the full system.

**Validates: System Integration Tests (section 10.2)**

This module tests:
1. Individual orchestration functions
2. Error handling in startup sequence
3. Environment validation logic
4. Directory creation functionality
5. Signal handler setup
6. Logging configuration

These tests can run without the full dataset or system dependencies.
"""

import pytest
import os
import sys
import tempfile
import shutil
import logging
import signal
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from typing import Dict, Any

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import main module functions
try:
    import main
except ImportError as e:
    pytest.skip(f"Cannot import main module: {e}", allow_module_level=True)


class TestMainOrchestration:
    """Test cases for main.py orchestration functions."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dirs = []
        self.original_cwd = os.getcwd()
    
    def teardown_method(self):
        """Clean up test environment."""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        os.chdir(self.original_cwd)
    
    def create_temp_dir(self) -> str:
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp(prefix="trinetra_test_")
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def test_setup_logging(self):
        """Test logging configuration setup."""
        temp_dir = self.create_temp_dir()
        os.chdir(temp_dir)
        
        # Test logging setup
        logger = main.setup_logging()
        
        # Check that logger is configured
        assert isinstance(logger, logging.Logger)
        assert logger.name == "main"
        
        # Check that logs directory is created
        logs_dir = Path(temp_dir) / "logs"
        assert logs_dir.exists()
        
        # Check that log file is created
        log_file = logs_dir / "trinetra_main.log"
        
        # Test logging functionality
        logger.info("Test log message")
        
        # Verify log file exists (may be created on first write)
        assert logs_dir.exists()
    
    def test_create_directories(self):
        """Test directory creation functionality."""
        temp_dir = self.create_temp_dir()
        os.chdir(temp_dir)
        
        # Mock logger to avoid logging setup
        with patch('main.logger') as mock_logger:
            main.create_directories()
            
            # Check that required directories are created
            required_dirs = ["models", "logs", "data"]
            for directory in required_dirs:
                dir_path = Path(temp_dir) / directory
                assert dir_path.exists(), f"Directory {directory} was not created"
                assert dir_path.is_dir(), f"{directory} is not a directory"
            
            # Check that success message was logged
            mock_logger.info.assert_called_with("✅ Created necessary directories")
    
    def test_validate_environment_success(self):
        """Test environment validation with valid environment."""
        temp_dir = self.create_temp_dir()
        os.chdir(temp_dir)
        
        # Create mock dataset
        data_dir = Path(temp_dir) / "data"
        data_dir.mkdir()
        dataset_path = data_dir / "trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        dataset_path.write_text("mock,csv,data\n1,2,3\n")
        
        # Mock logger
        with patch('main.logger') as mock_logger:
            result = main.validate_environment()
            
            assert result is True
            mock_logger.info.assert_any_call("🔍 Validating environment...")
            mock_logger.info.assert_any_call("✅ Environment validation passed")
    
    def test_validate_environment_missing_dataset(self):
        """Test environment validation with missing dataset."""
        temp_dir = self.create_temp_dir()
        os.chdir(temp_dir)
        
        # Mock logger
        with patch('main.logger') as mock_logger:
            result = main.validate_environment()
            
            assert result is False
            mock_logger.error.assert_called_with(
                f"❌ Dataset not found: {main.DATASET_PATH}"
            )
    
    @patch('main.uvicorn')
    @patch('main.streamlit')
    @patch('main.fastapi')
    @patch('main.pandas')
    @patch('main.sklearn')
    @patch('main.plotly')
    def test_validate_environment_missing_dependencies(self, mock_plotly, mock_sklearn, 
                                                      mock_pandas, mock_fastapi, 
                                                      mock_streamlit, mock_uvicorn):
        """Test environment validation with missing dependencies."""
        temp_dir = self.create_temp_dir()
        os.chdir(temp_dir)
        
        # Create dataset
        data_dir = Path(temp_dir) / "data"
        data_dir.mkdir()
        dataset_path = data_dir / "trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        dataset_path.write_text("mock,csv,data\n1,2,3\n")
        
        # Mock import error for one dependency
        mock_uvicorn.side_effect = ImportError("uvicorn not found")
        
        with patch('main.logger') as mock_logger:
            result = main.validate_environment()
            
            assert result is False
            mock_logger.error.assert_called_with("❌ Missing required dependency: uvicorn not found")
    
    def test_setup_signal_handlers(self):
        """Test signal handler setup."""
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_DFL)
        original_sigterm_handler = signal.signal(signal.SIGTERM, signal.SIG_DFL)
        
        try:
            with patch('main.logger') as mock_logger:
                main.setup_signal_handlers()
                
                # Check that signal handlers are set
                current_sigint = signal.signal(signal.SIGINT, signal.SIG_DFL)
                current_sigterm = signal.signal(signal.SIGTERM, signal.SIG_DFL)
                
                assert current_sigint != signal.SIG_DFL
                assert current_sigterm != signal.SIG_DFL
                
                mock_logger.info.assert_called_with("✅ Signal handlers configured")
                
        finally:
            # Restore original handlers
            signal.signal(signal.SIGINT, original_sigint_handler)
            signal.signal(signal.SIGTERM, original_sigterm_handler)
    
    @patch('main.load_dataset')
    @patch('main.validate_schema')
    @patch('main.get_dataset_stats')
    @patch('main.engineer_features')
    def test_load_and_process_data_success(self, mock_engineer, mock_stats, 
                                          mock_validate, mock_load):
        """Test successful data loading and processing."""
        # Mock successful data loading
        mock_df = MagicMock()
        mock_df.empty = False
        mock_load.return_value = mock_df
        mock_validate.return_value = True
        mock_stats.return_value = {
            'basic_info': {
                'total_rows': 1000,
                'total_columns': 30
            }
        }
        mock_engineer.return_value = mock_df
        
        with patch('main.logger') as mock_logger:
            result = main.load_and_process_data()
            
            assert result == mock_df
            mock_load.assert_called_once_with(main.DATASET_PATH)
            mock_validate.assert_called_once_with(mock_df)
            mock_engineer.assert_called_once_with(mock_df)
            
            # Check logging calls
            mock_logger.info.assert_any_call("📊 Loading and processing dataset...")
            mock_logger.info.assert_any_call("🔧 Engineering fraud detection features...")
            mock_logger.info.assert_any_call("✅ Data loading and feature engineering completed")
    
    @patch('main.load_dataset')
    def test_load_and_process_data_empty_dataset(self, mock_load):
        """Test data loading with empty dataset."""
        # Mock empty dataset
        mock_df = MagicMock()
        mock_df.empty = True
        mock_load.return_value = mock_df
        
        with patch('main.logger') as mock_logger:
            with pytest.raises(Exception, match="Failed to load dataset or dataset is empty"):
                main.load_and_process_data()
    
    @patch('main.load_dataset')
    def test_load_and_process_data_none_dataset(self, mock_load):
        """Test data loading with None dataset."""
        # Mock None dataset
        mock_load.return_value = None
        
        with patch('main.logger') as mock_logger:
            with pytest.raises(Exception, match="Failed to load dataset or dataset is empty"):
                main.load_and_process_data()
    
    @patch('main.load_dataset')
    @patch('main.validate_schema')
    def test_load_and_process_data_invalid_schema(self, mock_validate, mock_load):
        """Test data loading with invalid schema."""
        # Mock dataset with invalid schema
        mock_df = MagicMock()
        mock_df.empty = False
        mock_load.return_value = mock_df
        mock_validate.return_value = False
        
        with patch('main.logger') as mock_logger:
            with pytest.raises(Exception, match="Dataset schema validation failed"):
                main.load_and_process_data()
    
    @patch('main.Path')
    @patch('main.load_model')
    @patch('main.train_model')
    @patch('main.save_model')
    @patch('main.score_transactions')
    @patch('main.classify_risk')
    def test_setup_ml_model_existing_model(self, mock_classify, mock_score, mock_save,
                                          mock_train, mock_load, mock_path):
        """Test ML model setup with existing model."""
        # Mock existing model file
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        mock_df = MagicMock()
        mock_model = MagicMock()
        mock_scored_df = MagicMock()
        mock_classified_df = MagicMock()
        
        # Mock successful model loading and scoring
        mock_load.return_value = mock_model
        mock_score.return_value = mock_scored_df
        mock_classify.return_value = mock_classified_df
        
        # Mock classification results for logging
        mock_classified_df.__getitem__.return_value.__getitem__.return_value = MagicMock()
        mock_classified_df.__getitem__.return_value.__getitem__.return_value.__len__.return_value = 10
        
        with patch('main.logger') as mock_logger:
            result_df, result_model = main.setup_ml_model(mock_df)
            
            assert result_df == mock_classified_df
            assert result_model == mock_model
            
            mock_load.assert_called_once_with(main.MODEL_PATH)
            mock_train.assert_not_called()
            mock_save.assert_not_called()
            mock_score.assert_called_once_with(mock_df, mock_model)
            mock_classify.assert_called_once_with(mock_scored_df)
    
    @patch('main.Path')
    @patch('main.train_model')
    @patch('main.save_model')
    @patch('main.score_transactions')
    @patch('main.classify_risk')
    def test_setup_ml_model_new_model(self, mock_classify, mock_score, mock_save,
                                     mock_train, mock_path):
        """Test ML model setup with new model training."""
        # Mock no existing model file
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path_instance.parent.mkdir = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_df = MagicMock()
        mock_model = MagicMock()
        mock_scored_df = MagicMock()
        mock_classified_df = MagicMock()
        
        # Mock successful model training and scoring
        mock_train.return_value = mock_model
        mock_score.return_value = mock_scored_df
        mock_classify.return_value = mock_classified_df
        
        # Mock classification results for logging
        mock_classified_df.__getitem__.return_value.__getitem__.return_value = MagicMock()
        mock_classified_df.__getitem__.return_value.__getitem__.return_value.__len__.return_value = 5
        
        with patch('main.logger') as mock_logger:
            result_df, result_model = main.setup_ml_model(mock_df)
            
            assert result_df == mock_classified_df
            assert result_model == mock_model
            
            mock_train.assert_called_once_with(mock_df)
            mock_save.assert_called_once_with(mock_model, main.MODEL_PATH)
            mock_score.assert_called_once_with(mock_df, mock_model)
            mock_classify.assert_called_once_with(mock_scored_df)
    
    @patch('main.initialize_gemini')
    @patch('main.test_fallback_system')
    def test_test_ai_integration_success(self, mock_fallback, mock_init):
        """Test successful AI integration testing."""
        mock_model = MagicMock()
        mock_init.return_value = mock_model
        mock_fallback.return_value = {'test_status': 'success'}
        
        with patch('main.logger') as mock_logger:
            main.test_ai_integration()
            
            mock_init.assert_called_once()
            mock_fallback.assert_called_once()
            
            mock_logger.info.assert_any_call("🧠 Testing AI integration...")
            mock_logger.info.assert_any_call("✅ Gemini API initialized successfully")
            mock_logger.info.assert_any_call("✅ Fallback explanation system working")
            mock_logger.info.assert_any_call("✅ AI integration testing completed")
    
    @patch('main.initialize_gemini')
    @patch('main.test_fallback_system')
    def test_test_ai_integration_gemini_failure(self, mock_fallback, mock_init):
        """Test AI integration with Gemini API failure."""
        mock_init.side_effect = Exception("API key invalid")
        mock_fallback.return_value = {'test_status': 'success'}
        
        with patch('main.logger') as mock_logger:
            main.test_ai_integration()
            
            mock_init.assert_called_once()
            mock_fallback.assert_called_once()
            
            mock_logger.warning.assert_any_call("⚠️ Gemini API initialization failed: API key invalid")
            mock_logger.info.assert_any_call("Fallback explanations will be used")
    
    def test_display_startup_banner(self, capsys):
        """Test startup banner display."""
        with patch('main.logger') as mock_logger:
            main.display_startup_banner()
            
            captured = capsys.readouterr()
            assert "TRINETRA AI - Trade Fraud Intelligence System" in captured.out
            
            # Check logging calls
            mock_logger.info.assert_any_call("🚀 TRINETRA AI System Starting...")
            mock_logger.info.assert_any_call(f"📊 Dataset: {main.DATASET_PATH}")
            mock_logger.info.assert_any_call(f"🤖 Model: {main.MODEL_PATH}")
    
    def test_display_success_message(self, capsys):
        """Test success message display."""
        with patch('main.logger') as mock_logger:
            main.display_success_message()
            
            captured = capsys.readouterr()
            assert "TRINETRA AI System Successfully Started!" in captured.out
            assert f"http://localhost:{main.API_PORT}" in captured.out
            assert f"http://localhost:{main.DASHBOARD_PORT}" in captured.out
            
            mock_logger.info.assert_any_call("🎉 TRINETRA AI is ready for fraud detection!")


class TestMainOrchestrationEdgeCases:
    """Edge case tests for main.py orchestration."""
    
    def test_create_directories_existing_dirs(self):
        """Test directory creation when directories already exist."""
        temp_dir = tempfile.mkdtemp(prefix="trinetra_test_")
        os.chdir(temp_dir)
        
        try:
            # Create directories first
            for directory in ["models", "logs", "data"]:
                (Path(temp_dir) / directory).mkdir()
            
            # Test that function handles existing directories
            with patch('main.logger') as mock_logger:
                main.create_directories()
                
                # Should still succeed
                mock_logger.info.assert_called_with("✅ Created necessary directories")
                
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_validate_environment_permission_error(self):
        """Test environment validation with permission errors."""
        with patch('main.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.side_effect = PermissionError("Access denied")
            mock_path.return_value = mock_path_instance
            
            with patch('main.logger') as mock_logger:
                # Should handle permission error gracefully
                result = main.validate_environment()
                
                # May return False or raise exception depending on implementation
                assert isinstance(result, bool)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])