#!/usr/bin/env python3
"""
Fallback run.py for Render deployment
This file is used when render.yaml is not recognized
"""

import os
import sys
import subprocess

def main():
    # Determine which service to run based on environment or default to API
    service_type = os.environ.get('SERVICE_TYPE', 'api')
    port = int(os.environ.get('PORT', 8000))
    
    print(f"TRINETRA AI - Starting {service_type} service on port {port}")
    
    if service_type == 'dashboard':
        # Run dashboard
        print("Starting TRINETRA AI Dashboard...")
        try:
            # Set API_BASE_URL if not set
            if 'API_BASE_URL' not in os.environ:
                os.environ['API_BASE_URL'] = 'https://trinetra-ai-api.onrender.com'
            
            subprocess.run([sys.executable, 'deploy_dashboard_html.py'], check=True)
        except FileNotFoundError:
            print("Error: deploy_dashboard_html.py not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error starting dashboard: {e}")
            sys.exit(1)
    else:
        # Run API (default)
        print("Starting TRINETRA AI API...")
        try:
            subprocess.run([sys.executable, 'deploy_api_ultra_minimal.py'], check=True)
        except FileNotFoundError:
            print("Error: deploy_api_ultra_minimal.py not found, trying deploy_api_minimal.py")
            try:
                subprocess.run([sys.executable, 'deploy_api_minimal.py'], check=True)
            except FileNotFoundError:
                print("Error: No API deployment file found")
                sys.exit(1)
        except Exception as e:
            print(f"Error starting API: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()