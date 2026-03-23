#!/usr/bin/env python3
"""
Debug Transactions Response Format

Quick test to see what the transactions endpoint is actually returning.
"""

import sys
import os
from fastapi.testclient import TestClient

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.api import app, initialize_system
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def main():
    print("🔍 Debugging Transactions Response Format")
    print("=" * 50)
    
    # Initialize system
    print("Initializing system...")
    try:
        initialize_system()
        client = TestClient(app)
        print("✅ System initialized")
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return
    
    # Test transactions endpoint
    print("\nTesting /transactions endpoint...")
    try:
        response = client.get("/transactions?limit=3")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            print(f"Status: {data.get('status')}")
            print(f"Data type: {type(data.get('data'))}")
            
            if 'data' in data:
                transactions_data = data['data']
                print(f"Data content type: {type(transactions_data)}")
                
                if isinstance(transactions_data, list):
                    print(f"List length: {len(transactions_data)}")
                    if transactions_data:
                        print(f"First item type: {type(transactions_data[0])}")
                        print(f"First item keys: {list(transactions_data[0].keys()) if isinstance(transactions_data[0], dict) else 'Not a dict'}")
                elif isinstance(transactions_data, dict):
                    print(f"Dict keys: {list(transactions_data.keys())}")
                else:
                    print(f"Unexpected data type: {type(transactions_data)}")
                    print(f"Data content: {str(transactions_data)[:200]}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing transactions endpoint: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()