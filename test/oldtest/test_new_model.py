#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the newly downloaded Qwen2.5-7B-Instruct-GGUF model
"""

import requests
import json

def test_model():
    """Test the new model with various prompts"""
    api_url = "http://localhost:8007/api/generate"
    
    # Test 1: Bangla language test
    print("🧪 Testing Bangla language support...")
    bangla_prompt = {
        "model": "qwen2.5-7b-instruct-gguf",
        "prompt": "বাংলায় ২ লাইনের সারাংশ লিখুন: আজ আকাশে অনেক মেঘ।",
        "stream": False,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=bangla_prompt)
        if response.status_code == 200:
            result = response.json()
            content = result.get("runtime_response", {}).get("content", "")
            print(f"✅ Bangla test response: {content}")
        else:
            print(f"❌ Bangla test failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Bangla test error: {e}")
    
    # Test 2: JSON validity test
    print("\n🧪 Testing JSON generation...")
    json_prompt = {
        "model": "qwen2.5-7b-instruct-gguf",
        "prompt": "Return ONLY valid JSON. Create a todo list with 3 items.",
        "stream": False,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=json_prompt)
        if response.status_code == 200:
            result = response.json()
            content = result.get("runtime_response", {}).get("content", "")
            print(f"✅ JSON test response: {content}")
            
            # Try to parse as JSON
            try:
                parsed = json.loads(content)
                print("✅ JSON is valid")
            except json.JSONDecodeError:
                print("❌ JSON is invalid")
        else:
            print(f"❌ JSON test failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ JSON test error: {e}")
    
    # Test 3: Code generation test
    print("\n🧪 Testing code generation...")
    code_prompt = {
        "model": "qwen2.5-7b-instruct-gguf",
        "prompt": "Write a python function that returns fib(10). Only return the function, no explanation.",
        "stream": False,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=code_prompt)
        if response.status_code == 200:
            result = response.json()
            content = result.get("runtime_response", {}).get("content", "")
            print(f"✅ Code test response: {content}")
            
            # Check if it contains function definition
            if "def" in content and "fib" in content:
                print("✅ Code generation passed")
            else:
                print("❌ Code generation failed")
        else:
            print(f"❌ Code test failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Code test error: {e}")

if __name__ == "__main__":
    test_model()