#!/usr/bin/env python3
"""
Test the explanation endpoint
"""

import requests
import json

def test_explanation():
    try:
        # Test explanation endpoint
        response = requests.post(
            'http://127.0.0.1:8000/explain/TXN00100', 
            json={}, 
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Status: {data['status']}")
            print(f"Message: {data['message']}")
            
            if data['status'] == 'success':
                explanation_data = data['data']
                print(f"Transaction ID: {explanation_data['transaction_id']}")
                print(f"Explanation Type: {explanation_data['explanation_type']}")
                print(f"Explanation Preview: {explanation_data['explanation'][:100]}...")
                print("✅ Explanation endpoint working!")
            else:
                print(f"❌ API Error: {data['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_explanation()