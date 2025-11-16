#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple verification script for the working qwen model
"""

import requests
import json

def test_working_model():
    """Test the working qwen2.5-0.5b-instruct-gguf model"""
    print("Testing qwen2.5-0.5b-instruct-gguf model (GGUF format)...")
    
    try:
        data = {
            "model": "qwen2.5-0.5b-instruct-gguf",
            "prompt": "Translate to Bengali: Hello, how are you?",
            "stream": False,
            "max_tokens": 100
        }
        
        response = requests.post(
            "http://localhost:8007/api/generate",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("runtime_response", {}).get("content", "")
            print("Model response:")
            print(content)
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Exception during model test: {e}")
        return False

if __name__ == "__main__":
    test_working_model()