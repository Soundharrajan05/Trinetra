"""
Simple startup script for TRINETRA AI
Starts both FastAPI and Streamlit without reload
"""

import subprocess
import sys
import time
from pathlib import Path

def start_fastapi():
    """Start FastAPI server"""
    print("🚀 Starting FastAPI server...")
    cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.api:app",
        "--host", "127.0.0.1",
        "--port", "8001",
        "--log-level", "info"
    ]
    
    return subprocess.Popen(cmd, cwd=Path.cwd())

def start_streamlit():
    """Start Streamlit dashboard"""
    print("📊 Starting Streamlit dashboard...")
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "frontend/dashboard.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    return subprocess.Popen(cmd, cwd=Path.cwd())

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  🛡️  TRINETRA AI - Trade Fraud Intelligence System  🛡️      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Start FastAPI
    fastapi_process = start_fastapi()
    time.sleep(5)  # Wait for FastAPI to start
    
    # Start Streamlit
    streamlit_process = start_streamlit()
    time.sleep(5)  # Wait for Streamlit to start
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  ✅ TRINETRA AI System Started!                             ║
    ║                                                              ║
    ║  🌐 API Server:    http://localhost:8001                    ║
    ║  📱 Dashboard:     http://localhost:8501                   ║
    ║                                                              ║
    ║  Press Ctrl+C to stop the system                            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Keep running
        while True:
            time.sleep(1)
            
            # Check if processes died
            if fastapi_process.poll() is not None:
                print("❌ FastAPI process died")
                break
            if streamlit_process.poll() is not None:
                print("❌ Streamlit process died")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        fastapi_process.terminate()
        streamlit_process.terminate()
        fastapi_process.wait()
        streamlit_process.wait()
        print("✅ Shutdown complete")
