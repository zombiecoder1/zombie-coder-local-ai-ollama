#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for qwen2.5-3b-bangla model
This model is in safetensors format and needs to be converted to GGUF for llama.cpp
"""

import requests
import json
import os
from pathlib import Path

def check_model_availability():
    """Check if the qwen2.5-3b-bangla model is available in GGUF format"""
    print("Checking qwen2.5-3b-bangla model availability...")
    
    # Check if model directory exists
    model_dir = Path("models/qwen2.5-3b-bangla")
    if not model_dir.exists():
        print("Model directory not found")
        return False
    
    # Check for GGUF files
    gguf_files = list(model_dir.glob("*.gguf"))
    if gguf_files:
        print(f"Found GGUF files: {[f.name for f in gguf_files]}")
        return True
    else:
        print("No GGUF files found in model directory")
        print("Model is in safetensors format which is not compatible with llama.cpp")
        return False

def check_installed_models():
    """Check what models are installed"""
    try:
        response = requests.get("http://localhost:8007/models/installed")
        if response.status_code == 200:
            data = response.json()
            print("Installed models:")
            for model in data["models"]:
                print(f"  - {model['name']} ({model['size_mb']:.2f} MB)")
            return data["models"]
        else:
            print(f"HTTP Error checking installed models: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error checking installed models: {e}")
        return []

def check_loaded_models():
    """Check what models are currently loaded"""
    try:
        response = requests.get("http://localhost:8007/runtime/status")
        if response.status_code == 200:
            data = response.json()
            print("Loaded models:")
            loaded_count = 0
            for model in data["models"]:
                if model["status"] == "ready":
                    print(f"  - {model['model']} (port: {model['port']})")
                    loaded_count += 1
            print(f"Total loaded models: {loaded_count}")
            return data["models"]
        else:
            print(f"HTTP Error checking loaded models: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error checking loaded models: {e}")
        return []

def attempt_model_load(model_name):
    """Attempt to load the model"""
    print(f"Attempting to load {model_name}...")
    
    try:
        # Try to load the model with default parameters
        data = {
            "threads": 4
        }
        
        response = requests.post(
            f"http://localhost:8007/runtime/load/{model_name}",
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Model load result: {result['status']}")
            if result['status'] == 'ready':
                print(f"Model successfully loaded on port {result['port']}")
                return True
            else:
                print(f"Model load failed: {result.get('reason', 'Unknown error')}")
                return False
        else:
            print(f"HTTP Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Exception during model load: {e}")
        return False

def test_model_response(model_name):
    """Test the model with a simple prompt"""
    print(f"Testing {model_name} response...")
    
    try:
        data = {
            "model": model_name,
            "prompt": "Hello, how are you?",
            "stream": False,
            "max_tokens": 50
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
            print(f"Model response: {content[:100]}...")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Exception during model test: {e}")
        return False

def main():
    """Main test function"""
    print("Testing qwen2.5-3b-bangla model")
    print("=" * 40)
    
    # Check model availability
    model_available = check_model_availability()
    
    # Check installed models
    installed_models = check_installed_models()
    
    # Check loaded models
    loaded_models = check_loaded_models()
    
    # Check if qwen2.5-3b-bangla is installed
    qwen_installed = any(model["name"] == "qwen2.5-3b-bangla" for model in installed_models)
    
    if not qwen_installed:
        print("\nqwen2.5-3b-bangla model is not installed")
        return
    
    # Check if qwen2.5-3b-bangla is loaded
    qwen_loaded = any(model["model"] == "qwen2.5-3b-bangla" and model["status"] == "ready" for model in loaded_models)
    
    if not qwen_loaded and model_available:
        # Attempt to load the model
        load_success = attempt_model_load("qwen2.5-3b-bangla")
        if load_success:
            # Test model response
            test_model_response("qwen2.5-3b-bangla")
    elif qwen_loaded:
        # Test model response
        test_model_response("qwen2.5-3b-bangla")
    else:
        print("\nCannot load qwen2.5-3b-bangla model because it's not in GGUF format")
        print("The model is in safetensors format which is incompatible with llama.cpp")
        print("\nRecommendation:")
        print("1. Use the qwen2.5-0.5b-instruct-gguf model which is already working")
        print("2. Or convert the safetensors model to GGUF format using llama.cpp tools")
        
        # Test the working GGUF model instead
        print("\nTesting the working qwen2.5-0.5b-instruct-gguf model instead:")
        test_model_response("qwen2.5-0.5b-instruct-gguf")

if __name__ == "__main__":
    main()