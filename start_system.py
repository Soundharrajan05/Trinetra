"""
TRINETRA AI System Startup Script

This script helps start the complete TRINETRA AI fraud detection system
with the updated quota management features.

Usage:
    python start_system.py

Author: TRINETRA AI Team
Date: 2024
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'pandas', 
        'scikit-learn', 'plotly', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_data_files():
    """Check if required data files exist."""
    required_files = [
        'backend/ai_explainer.py',
        'backend/api.py', 
        'frontend/dashboard.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    return True

def start_api_server():
    """Start the FastAPI backend server."""
    print("🚀 Starting TRINETRA AI API Server...")
    
    try:
        # Start the API server
        api_process = subprocess.Popen([
            sys.executable, 'backend/api.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if it's still running
        if api_process.poll() is None:
            print("✅ API Server started successfully on http://localhost:8000")
            return api_process
        else:
            stdout, stderr = api_process.communicate()
            print(f"❌ API Server failed to start:")
            print(f"Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start API server: {str(e)}")
        return None

def start_dashboard():
    """Start the Streamlit dashboard."""
    print("🎨 Starting TRINETRA AI Dashboard...")
    
    try:
        # Start the dashboard
        dashboard_process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'frontend/dashboard.py',
            '--server.port', '8501',
            '--server.headless', 'true'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it a moment to start
        time.sleep(5)
        
        # Check if it's still running
        if dashboard_process.poll() is None:
            print("✅ Dashboard started successfully on http://localhost:8501")
            return dashboard_process
        else:
            stdout, stderr = dashboard_process.communicate()
            print(f"❌ Dashboard failed to start:")
            print(f"Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start dashboard: {str(e)}")
        return None

def main():
    """Main startup function."""
    print("🛡️ TRINETRA AI - Trade Fraud Intelligence System")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Check required files
    print("📁 Checking required files...")
    if not check_data_files():
        sys.exit(1)
    
    print("✅ All prerequisites met!")
    print()
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Cannot start system without API server")
        sys.exit(1)
    
    # Start dashboard
    dashboard_process = start_dashboard()
    if not dashboard_process:
        print("❌ Cannot start dashboard")
        if api_process:
            api_process.terminate()
        sys.exit(1)
    
    print()
    print("🎉 TRINETRA AI System Started Successfully!")
    print("=" * 50)
    print("📊 Dashboard: http://localhost:8501")
    print("🔌 API Docs: http://localhost:8000/docs")
    print()
    print("💡 Quota Management Features:")
    print("   • Max 3 AI explanations per session")
    print("   • Fallback explanations always available")
    print("   • Caching prevents repeated API calls")
    print("   • Session reset available when quota exhausted")
    print()
    print("🔧 Usage Tips:")
    print("   • Use 'Get Fallback Explanation' for most investigations")
    print("   • Use 'Get AI Explanation' only when you need advanced analysis")
    print("   • Monitor quota usage in the dashboard")
    print("   • Reset session to get new quota when needed")
    print()
    print("Press Ctrl+C to stop the system...")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
                
            if dashboard_process.poll() is not None:
                print("❌ Dashboard stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down TRINETRA AI System...")
        
        # Terminate processes
        if api_process:
            api_process.terminate()
            print("✅ API server stopped")
            
        if dashboard_process:
            dashboard_process.terminate()
            print("✅ Dashboard stopped")
        
        print("👋 TRINETRA AI System shutdown complete")

if __name__ == "__main__":
    main()