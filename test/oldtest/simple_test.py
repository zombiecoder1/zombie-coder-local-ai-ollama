#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for the Qwen model
"""

import requests
import json

def test_model():
    """Test the Qwen model with a simple prompt"""
    print("Testing Qwen2.5-0.5B-Instruct-GGUF model...")
    
    # Test data
    data = {
        "model": "qwen2.5-0.5b-instruct-gguf",
        "prompt": "Hello, how are you?",
        "stream": False,
        "max_tokens": 50
    }
    
    try:
        # Send request to generate endpoint
        response = requests.post(
            "http://localhost:8007/api/generate",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=60
        )
        
        print(f"Status code: {response.status_code}")
        
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
    test_model()