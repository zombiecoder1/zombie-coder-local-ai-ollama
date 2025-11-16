#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Chat Test Script
"""

import requests
import json
import time

def test_chat():
    url = "http://localhost:8007/api/chat"
    
    # Test 1: Simple English
    print("Test 1: English Question")
    payload = {
        "model": "phi-2-gguf",
        "messages": [{"role": "user", "content": "Hello, how are you?"}],
        "max_tokens": 30
    }
    
    try:
        start = time.time()
        response = requests.post(url, json=payload, timeout=30)
        end = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Time: {end - start:.2f}s")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['runtime_response']['content']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Bengali
    print("Test 2: Bengali Question")
    payload = {
        "model": "phi-2-gguf",
        "messages": [{"role": "user", "content": "আপনি কেমন আছেন?"}],
        "max_tokens": 30
    }
    
    try:
        start = time.time()
        response = requests.post(url, json=payload, timeout=30)
        end = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Time: {end - start:.2f}s")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['runtime_response']['content']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Math Question
    print("Test 3: Math Question")
    payload = {
        "model": "phi-2-gguf",
        "messages": [{"role": "user", "content": "What is 5 + 3?"}],
        "max_tokens": 30
    }
    
    try:
        start = time.time()
        response = requests.post(url, json=payload, timeout=30)
        end = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Time: {end - start:.2f}s")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['runtime_response']['content']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_chat()
