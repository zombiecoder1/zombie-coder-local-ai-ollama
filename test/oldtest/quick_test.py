#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Model Test for Bengali Language
"""

import requests
import json
import time

def quick_test():
    """Quick test of one model with Bengali text"""
    print("Quick Bengali Language Model Test")
    print("=" * 40)
    
    # Test with phi-2-gguf model
    model_name = "phi-2-gguf"
    prompt = "আপনি কেমন আছেন?"  # "How are you?" in Bengali
    
    url = "http://localhost:8007/api/chat"
    
    messages = [{"role": "user", "content": prompt}]
    
    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    print(f"Testing model: {model_name}")
    print(f"Prompt: {prompt}")
    print("Sending request...")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=30)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"Response time: {response_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print("Response received successfully!")
            
            # Extract the response content
            response_text = ""
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice:
                    response_text = choice["message"]["content"]
                elif "delta" in choice:
                    response_text = choice["delta"].get("content", "")
            
            print(f"Model response: {response_text}")
            
            # Save to file
            result = {
                "model": model_name,
                "prompt": prompt,
                "response": response_text,
                "response_time": response_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open("quick_test_result.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print("Result saved to quick_test_result.json")
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_test()