#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Benchmark Script for Bengali Language Processing
"""

import requests
import json
import time
import sys

# Models to test
MODELS_TO_TEST = [
    "phi-2-gguf",
    "tinyllama-gguf",
    "deepseek-coder-1.3b"
]

# Test cases in Bengali
BENGALI_TEST_CASES = [
    {"name": "Basic Greeting", "prompt": "আপনি কেমন আছেন?"},
    {"name": "Simple Question", "prompt": "আজকের তারিখ কি?"},
    {"name": "Complex Query", "prompt": "বাংলাদেশের মুক্তিযুদ্ধ কবে শুরু হয়েছিল?"},
    {"name": "Translation Request", "prompt": "Translate 'Good morning' to English"},
    {"name": "Math Problem", "prompt": "১০ + ৫ = কত?"}
]

def test_model(model_name, prompt):
    """Test a specific model with a given prompt"""
    url = "http://localhost:8007/api/chat"
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=60)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "success": True,
                "response_time": response_time,
                "response": response_text,
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "response_time": response_time,
                "error": f"HTTP {response.status_code}",
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "success": False,
            "response_time": -1,
            "error": str(e),
            "status_code": -1
        }

def run_benchmark():
    """Run benchmark tests on all models"""
    print("Starting Model Benchmark for Bengali Language Processing")
    print("=" * 60)
    
    results = {}
    
    for model in MODELS_TO_TEST:
        print(f"\nTesting model: {model}")
        print("-" * 40)
        
        model_results = []
        
        for test_case in BENGALI_TEST_CASES:
            print(f"  Running test: {test_case['name']}")
            result = test_model(model, test_case['prompt'])
            
            model_results.append({
                "test_name": test_case['name'],
                "prompt": test_case['prompt'],
                "result": result
            })
            
            if result["success"]:
                print(f"    Response Time: {result['response_time']:.2f}s")
                print(f"    Response: {result['response'][:100]}...")
            else:
                print(f"    Error: {result['error']}")
        
        results[model] = model_results
    
    return results

def print_summary(results):
    """Print a summary of the benchmark results"""
    print("\n\nBENCHMARK SUMMARY")
    print("=" * 60)
    
    for model, model_results in results.items():
        print(f"\nModel: {model}")
        print("-" * 30)
        
        total_time = 0
        successful_tests = 0
        failed_tests = 0
        
        for result in model_results:
            test_result = result['result']
            if test_result['success']:
                total_time += test_result['response_time']
                successful_tests += 1
            else:
                failed_tests += 1
        
        avg_time = total_time / successful_tests if successful_tests > 0 else 0
        
        print(f"  Successful Tests: {successful_tests}/{len(model_results)}")
        print(f"  Failed Tests: {failed_tests}")
        print(f"  Average Response Time: {avg_time:.2f}s")

if __name__ == "__main__":
    try:
        results = run_benchmark()
        print_summary(results)
        
        # Save results to file
        with open("benchmark_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed results saved to benchmark_results.json")
        
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
    except Exception as e:
        print(f"\nError running benchmark: {e}")
        sys.exit(1)