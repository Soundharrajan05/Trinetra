"""
TRINETRA AI - Trade Fraud Intelligence System
Main Application Entry Point

This module orchestrates the complete system startup process:
1. Load and validate dataset
2. Run feature engineering pipeline  
3. Train or load ML model
4. Score all transactions
5. Start FastAPI server in background thread
6. Launch Streamlit dashboard
7. Handle graceful shutdown
8. Implement comprehensive logging

Usage:
    python main.py

Author: TRINETRA AI Team
Date: 2024
"""

import os
import sys
import time
import logging
import threading
import signal
import subprocess
from pathlib import Path
from typing import Optional
import pandas as pd

# Add backend directory to Python path for imports
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import backend modules
try:
    from data_loader import load_dataset, validate_schema, get_dataset_stats
    from feature_engineering import engineer_features
    from model import train_model, save_model, load_model
    from fraud_detection import score_transactions, classify_risk
    from ai_explainer import initialize_gemini, test_fallback_system
    from api import app as fastapi_app
except ImportError as e:
    print(f"❌ Error importing backend modules: {e}")
    print("Please ensure all backend modules are properly installed")
    sys.exit(1)

# Configuration
DATASET_PATH = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
MODEL_PATH = "models/isolation_forest.pkl"
API_HOST = "0.0.0.0"
API_PORT = 8000
DASHBOARD_PORT = 8505
LOG_LEVEL = logging.INFO

# Global variables for process management
fastapi_process: Optional[subprocess.Popen] = None
streamlit_process: Optional[subprocess.Popen] = None
shutdown_event = threading.Event()

def setup_logging():
    """Set up comprehensive logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging with both file and console handlers
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'trinetra_main.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific log levels for different modules
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('streamlit').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


def create_directories():
    """Create necessary directories for the application."""
    directories = ["models", "logs", "data"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        
    logger.info("✅ Created necessary directories")


def validate_environment():
    """Validate that all required files and dependencies are available."""
    logger.info("🔍 Validating environment...")
    
    # Check if dataset exists
    if not Path(DATASET_PATH).exists():
        logger.error(f"❌ Dataset not found: {DATASET_PATH}")
        return False
    
    # Check if backend modules are accessible
    try:
        import uvicorn
        import streamlit
        import fastapi
        import pandas
        import sklearn
        import plotly
    except ImportError as e:
        logger.error(f"❌ Missing required dependency: {e}")
        return False
    
    logger.info("✅ Environment validation passed")
    return True
def load_and_process_data():
    """Load dataset and run feature engineering pipeline."""
    logger.info("📊 Loading and processing dataset...")
    
    try:
        # Load and validate dataset
        logger.info(f"Loading dataset from: {DATASET_PATH}")
        df = load_dataset(DATASET_PATH)
        
        if df is None or df.empty:
            raise Exception("Failed to load dataset or dataset is empty")
        
        # Validate schema
        if not validate_schema(df):
            raise Exception("Dataset schema validation failed")
        
        # Log dataset statistics
        stats = get_dataset_stats(df)
        logger.info(f"Dataset loaded: {stats['basic_info']['total_rows']} rows, {stats['basic_info']['total_columns']} columns")
        
        # Engineer features
        logger.info("🔧 Engineering fraud detection features...")
        df_engineered = engineer_features(df)
        
        logger.info("✅ Data loading and feature engineering completed")
        return df_engineered
        
    except Exception as e:
        logger.error(f"❌ Data processing failed: {str(e)}")
        raise


def setup_ml_model(df: pd.DataFrame):
    """Train or load ML model and score transactions."""
    logger.info("🤖 Setting up machine learning model...")
    
    try:
        # Check if trained model exists
        if Path(MODEL_PATH).exists():
            logger.info(f"Loading existing model from: {MODEL_PATH}")
            model = load_model(MODEL_PATH)
        else:
            logger.info("Training new model...")
            model = train_model(df)
            
            # Create models directory and save model
            Path(MODEL_PATH).parent.mkdir(exist_ok=True)
            save_model(model, MODEL_PATH)
            logger.info(f"Model saved to: {MODEL_PATH}")
        
        # Score all transactions
        logger.info("📈 Scoring transactions for fraud risk...")
        df_scored = score_transactions(df, model)
        df_classified = classify_risk(df_scored)
        
        # Log scoring results
        fraud_count = len(df_classified[df_classified['risk_category'] == 'FRAUD'])
        suspicious_count = len(df_classified[df_classified['risk_category'] == 'SUSPICIOUS'])
        safe_count = len(df_classified[df_classified['risk_category'] == 'SAFE'])
        
        logger.info(f"Scoring completed: {fraud_count} fraud, {suspicious_count} suspicious, {safe_count} safe")
        logger.info("✅ ML model setup completed")
        
        return df_classified, model
        
    except Exception as e:
        logger.error(f"❌ ML model setup failed: {str(e)}")
        raise
def test_ai_integration():
    """Test AI integration and fallback systems."""
    logger.info("🧠 Testing AI integration...")
    
    try:
        # Test Gemini API initialization
        try:
            model = initialize_gemini()
            logger.info("✅ Gemini API initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Gemini API initialization failed: {e}")
            logger.info("Fallback explanations will be used")
        
        # Test fallback system
        fallback_results = test_fallback_system()
        if fallback_results.get('test_status') == 'success':
            logger.info("✅ Fallback explanation system working")
        else:
            logger.warning("⚠️ Fallback system test failed")
        
        logger.info("✅ AI integration testing completed")
        
    except Exception as e:
        logger.error(f"❌ AI integration test failed: {str(e)}")
        # Don't raise - AI is optional, system can work with fallbacks


def start_fastapi_server():
    """Start FastAPI server in background process."""
    global fastapi_process
    
    logger.info("🚀 Starting FastAPI server...")
    
    try:
        # Start FastAPI server using uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            "backend.api:app",
            "--host", API_HOST,
            "--port", str(API_PORT),
            "--reload",
            "--log-level", "warning"
        ]
        
        fastapi_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path.cwd()
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running
        if fastapi_process.poll() is None:
            logger.info(f"✅ FastAPI server started on http://{API_HOST}:{API_PORT}")
            return True
        else:
            stdout, stderr = fastapi_process.communicate()
            logger.error(f"❌ FastAPI server failed to start")
            logger.error(f"STDOUT: {stdout.decode()}")
            logger.error(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to start FastAPI server: {str(e)}")
        return False
def start_streamlit_dashboard():
    """Start Streamlit dashboard in background process."""
    global streamlit_process
    
    logger.info("📊 Starting Streamlit dashboard...")
    
    try:
        # Start Streamlit dashboard
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "frontend/dashboard.py",
            "--server.port", str(DASHBOARD_PORT),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--logger.level", "warning"
        ]
        
        streamlit_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path.cwd()
        )
        
        # Wait a moment for dashboard to start
        time.sleep(5)
        
        # Check if process is still running
        if streamlit_process.poll() is None:
            logger.info(f"✅ Streamlit dashboard started on http://localhost:{DASHBOARD_PORT}")
            return True
        else:
            stdout, stderr = streamlit_process.communicate()
            logger.error(f"❌ Streamlit dashboard failed to start")
            logger.error(f"STDOUT: {stdout.decode()}")
            logger.error(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to start Streamlit dashboard: {str(e)}")
        return False


def wait_for_services():
    """Wait for services to be ready and test connectivity."""
    logger.info("⏳ Waiting for services to be ready...")
    
    # Test API connectivity
    max_retries = 10
    for i in range(max_retries):
        try:
            import requests
            response = requests.get(f"http://localhost:{API_PORT}/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ FastAPI server is responding")
                break
        except Exception:
            if i < max_retries - 1:
                logger.info(f"Waiting for API server... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                logger.warning("⚠️ API server not responding, but continuing...")
    
    # Test dashboard connectivity
    for i in range(max_retries):
        try:
            import requests
            response = requests.get(f"http://localhost:{DASHBOARD_PORT}/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Streamlit dashboard is responding")
                break
        except Exception:
            if i < max_retries - 1:
                logger.info(f"Waiting for dashboard... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                logger.warning("⚠️ Dashboard not responding, but continuing...")
    
    logger.info("✅ Service readiness check completed")
def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
        shutdown_event.set()
        shutdown_system()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("✅ Signal handlers configured")


def shutdown_system():
    """Gracefully shutdown all services."""
    global fastapi_process, streamlit_process
    
    logger.info("🛑 Shutting down TRINETRA AI system...")
    
    # Shutdown FastAPI server
    if fastapi_process and fastapi_process.poll() is None:
        logger.info("Stopping FastAPI server...")
        fastapi_process.terminate()
        try:
            fastapi_process.wait(timeout=10)
            logger.info("✅ FastAPI server stopped")
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ FastAPI server did not stop gracefully, forcing...")
            fastapi_process.kill()
    
    # Shutdown Streamlit dashboard
    if streamlit_process and streamlit_process.poll() is None:
        logger.info("Stopping Streamlit dashboard...")
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=10)
            logger.info("✅ Streamlit dashboard stopped")
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Streamlit dashboard did not stop gracefully, forcing...")
            streamlit_process.kill()
    
    logger.info("✅ System shutdown completed")


def display_startup_banner():
    """Display startup banner with system information."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  🛡️  TRINETRA AI - Trade Fraud Intelligence System  🛡️      ║
    ║                                                              ║
    ║  AI-Powered Trade Fraud Detection and Analysis Platform     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    
    logger.info("🚀 TRINETRA AI System Starting...")
    logger.info(f"📊 Dataset: {DATASET_PATH}")
    logger.info(f"🤖 Model: {MODEL_PATH}")
    logger.info(f"🌐 API Server: http://localhost:{API_PORT}")
    logger.info(f"📱 Dashboard: http://localhost:{DASHBOARD_PORT}")


def display_success_message():
    """Display success message with access URLs."""
    success_message = f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  ✅ TRINETRA AI System Successfully Started!                ║
    ║                                                              ║
    ║  🌐 API Server:    http://localhost:{API_PORT}                    ║
    ║  📱 Dashboard:     http://localhost:{DASHBOARD_PORT}                   ║
    ║                                                              ║
    ║  Press Ctrl+C to stop the system                            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(success_message)
    logger.info("🎉 TRINETRA AI is ready for fraud detection!")
    logger.info("Access the dashboard to start investigating suspicious transactions")
def main():
    """Main application entry point."""
    global logger
    
    try:
        # Initialize logging
        logger = setup_logging()
        
        # Display startup banner
        display_startup_banner()
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers()
        
        # Create necessary directories
        create_directories()
        
        # Validate environment
        if not validate_environment():
            logger.error("❌ Environment validation failed")
            sys.exit(1)
        
        # Load and process data
        df_processed = load_and_process_data()
        
        # Setup ML model and score transactions
        df_final, model = setup_ml_model(df_processed)
        
        # Test AI integration
        test_ai_integration()
        
        # Start FastAPI server
        if not start_fastapi_server():
            logger.error("❌ Failed to start FastAPI server")
            sys.exit(1)
        
        # Start Streamlit dashboard
        if not start_streamlit_dashboard():
            logger.error("❌ Failed to start Streamlit dashboard")
            shutdown_system()
            sys.exit(1)
        
        # Wait for services to be ready
        wait_for_services()
        
        # Display success message
        display_success_message()
        
        # Keep the main process running
        try:
            while not shutdown_event.is_set():
                time.sleep(1)
                
                # Check if processes are still running
                if fastapi_process and fastapi_process.poll() is not None:
                    logger.error("❌ FastAPI server process died unexpectedly")
                    break
                    
                if streamlit_process and streamlit_process.poll() is not None:
                    logger.error("❌ Streamlit dashboard process died unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            logger.info("🛑 Keyboard interrupt received")
        
    except Exception as e:
        logger.error(f"❌ System startup failed: {str(e)}")
        sys.exit(1)
    
    finally:
        # Ensure cleanup happens
        shutdown_system()


if __name__ == "__main__":
    main()