#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for ZombieCoder Provider Ecosystem endpoints
"""

import requests
import json

def test_provider_endpoints():
    """Test the provider endpoints"""
    base_url = "http://localhost:8007"
    
    print("🧪 Testing ZombieCoder Provider Endpoints")
    print("========================================")
    
    # Test 1: GET /api/tags
    print("\n1. Testing GET /api/tags")
    try:
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code == 200:
            print("✅ /api/tags endpoint is working")
            tags = response.json()
            print(f"   Found {len(tags.get('models', []))} models")
        else:
            print(f"❌ /api/tags returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing /api/tags: {e}")
    
    # Test 2: GET /models/installed
    print("\n2. Testing GET /models/installed")
    try:
        response = requests.get(f"{base_url}/models/installed")
        if response.status_code == 200:
            print("✅ /models/installed endpoint is working")
        else:
            print(f"❌ /models/installed returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing /models/installed: {e}")
    
    # Test 3: POST /runtime/load/{model}
    print("\n3. Testing POST /runtime/load/phi-2")
    try:
        response = requests.post(f"{base_url}/runtime/load/phi-2")
        if response.status_code == 200:
            print("✅ /runtime/load/phi-2 endpoint is working")
        else:
            print(f"❌ /runtime/load/phi-2 returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing /runtime/load/phi-2: {e}")
    
    # Test 4: POST /api/generate
    print("\n4. Testing POST /api/generate")
    try:
        payload = {
            "model": "phi-2",
            "prompt": "Say hello in one word",
            "stream": False,
            "max_tokens": 10
        }
        response = requests.post(
            f"{base_url}/api/generate",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        if response.status_code == 200:
            print("✅ /api/generate endpoint is working")
            result = response.json()
            content = result.get("runtime_response", {}).get("content", "")
            print(f"   Response: {content}")
        else:
            print(f"❌ /api/generate returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing /api/generate: {e}")
    
    print("\n✅ Provider endpoint tests completed")

if __name__ == "__main__":
    test_provider_endpoints()