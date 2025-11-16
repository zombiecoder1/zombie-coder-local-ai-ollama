#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for ZombieCoder Local AI Framework models
"""

import requests
import json

def test_phi2_model():
    """Test the phi-2 model"""
    print("Testing phi-2 model...")
    
    # Test data
    data = {
        "model": "phi-2",
        "prompt": "Hello, how are you?",
        "stream": False
    }
    
    try:
        # Send request to generate endpoint
        response = requests.post(
            "http://localhost:8007/api/generate",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=120
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("Model response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    test_phi2_model()