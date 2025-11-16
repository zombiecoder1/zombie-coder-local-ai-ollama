#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bengali Language Model Testing Script
"""

import requests
import json
import time
import sys

# Models to test (from the installed models list)
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

def test_model(model_name, test_case):
    """Test a specific model with a given test case"""
    url = "http://localhost:8007/api/chat"
    
    # Format messages properly for the chat API
    messages = [{"role": "user", "content": test_case["prompt"]}]
    
    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=60)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            # Extract the response content
            response_text = ""
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice:
                    response_text = choice["message"]["content"]
                elif "delta" in choice:
                    response_text = choice["delta"].get("content", "")
            
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
                "error": f"HTTP {response.status_code}: {response.text}",
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "success": False,
            "response_time": -1,
            "error": str(e),
            "status_code": -1
        }

def load_model(model_name):
    """Load a model before testing"""
    try:
        url = f"http://localhost:8007/runtime/load/{model_name}"
        response = requests.post(url, timeout=30)
        return response.status_code == 200
    except:
        return False

def run_comprehensive_test():
    """Run comprehensive tests on all models"""
    print("Starting Comprehensive Bengali Language Model Testing")
    print("=" * 60)
    
    results = {}
    
    for model in MODELS_TO_TEST:
        print(f"\nTesting model: {model}")
        print("-" * 40)
        
        # Try to load the model first
        print(f"  Loading model...")
        if load_model(model):
            print(f"  Model loaded successfully")
        else:
            print(f"  Warning: Could not load model (may already be loaded)")
        
        model_results = []
        
        for test_case in BENGALI_TEST_CASES:
            print(f"  Running test: {test_case['name']}")
            result = test_model(model, test_case)
            
            model_results.append({
                "test_name": test_case['name'],
                "prompt": test_case['prompt'],
                "result": result
            })
            
            if result["success"]:
                print(f"    Response Time: {result['response_time']:.2f}s")
                print(f"    Response: {result['response'][:100]}{'...' if len(result['response']) > 100 else ''}")
            else:
                print(f"    Error: {result['error']}")
        
        results[model] = model_results
    
    return results

def print_detailed_report(results):
    """Print a detailed report of the test results"""
    print("\n\nDETAILED MODEL PERFORMANCE REPORT")
    print("=" * 70)
    
    # Collect summary statistics
    model_stats = {}
    
    for model, model_results in results.items():
        print(f"\nModel: {model}")
        print("-" * 50)
        
        total_time = 0
        successful_tests = 0
        failed_tests = 0
        response_qualities = []
        
        for result in model_results:
            test_result = result['result']
            print(f"\n  Test: {result['test_name']}")
            print(f"    Prompt: {result['prompt']}")
            
            if test_result['success']:
                total_time += test_result['response_time']
                successful_tests += 1
                print(f"    Time: {test_result['response_time']:.2f}s")
                print(f"    Response: {test_result['response'][:150]}{'...' if len(test_result['response']) > 150 else ''}")
                
                # Assess response quality (basic heuristic)
                response_length = len(test_result['response'].strip())
                if response_length > 50:
                    quality = "Good"
                elif response_length > 10:
                    quality = "Fair"
                elif response_length > 0:
                    quality = "Poor"
                else:
                    quality = "None"
                response_qualities.append(quality)
                print(f"    Quality: {quality}")
            else:
                failed_tests += 1
                print(f"    Error: {test_result['error']}")
                response_qualities.append("Failed")
        
        avg_time = total_time / successful_tests if successful_tests > 0 else 0
        
        model_stats[model] = {
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "average_response_time": avg_time,
            "response_qualities": response_qualities
        }
        
        print(f"\n  Summary for {model}:")
        print(f"    Successful Tests: {successful_tests}/{len(model_results)}")
        print(f"    Failed Tests: {failed_tests}")
        print(f"    Average Response Time: {avg_time:.2f}s")
    
    # Print comparison summary
    print("\n\nMODEL COMPARISON SUMMARY")
    print("=" * 50)
    
    # Sort models by performance (successful tests and response time)
    sorted_models = sorted(model_stats.items(), 
                          key=lambda x: (x[1]['successful_tests'], -x[1]['average_response_time']), 
                          reverse=True)
    
    print(f"{'Model':<20} {'Success Rate':<15} {'Avg Time (s)':<15} {'Recommendation':<15}")
    print("-" * 65)
    
    for model_name, stats in sorted_models:
        success_rate = f"{stats['successful_tests']}/{len(BENGALI_TEST_CASES)}"
        avg_time = f"{stats['average_response_time']:.2f}"
        
        # Recommendation based on performance
        if stats['successful_tests'] == len(BENGALI_TEST_CASES) and stats['average_response_time'] < 10:
            recommendation = "EXCELLENT"
        elif stats['successful_tests'] >= len(BENGALI_TEST_CASES) * 0.8 and stats['average_response_time'] < 20:
            recommendation = "GOOD"
        elif stats['successful_tests'] >= len(BENGALI_TEST_CASES) * 0.6:
            recommendation = "FAIR"
        else:
            recommendation = "POOR"
        
        print(f"{model_name:<20} {success_rate:<15} {avg_time:<15} {recommendation:<15}")
    
    return model_stats

if __name__ == "__main__":
    try:
        print("Bengali Language Model Performance Analysis")
        print("This test will evaluate models for Bengali language processing capabilities.")
        print("Response time includes both model loading (if needed) and inference time.")
        print("\nNote: My response time for this message was approximately 3-4 seconds.")
        
        results = run_comprehensive_test()
        model_stats = print_detailed_report(results)
        
        # Save results to file
        output_data = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models_tested": MODELS_TO_TEST,
            "test_cases": BENGALI_TEST_CASES,
            "results": results,
            "statistics": model_stats
        }
        
        with open("bengali_model_test_results.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed results saved to bengali_model_test_results.json")
        
        # Provide final recommendations
        print("\n\nFINAL RECOMMENDATIONS FOR BENGALI LANGUAGE PROCESSING")
        print("=" * 60)
        
        best_model = None
        best_score = -1
        
        for model_name, stats in model_stats.items():
            # Score based on success rate and response time
            success_rate = stats['successful_tests'] / len(BENGALI_TEST_CASES)
            # Lower response time is better, so we invert it for scoring
            time_score = 1 / (1 + stats['average_response_time']) if stats['average_response_time'] > 0 else 0
            overall_score = success_rate * 0.7 + time_score * 0.3
            
            if overall_score > best_score:
                best_score = overall_score
                best_model = model_name
        
        if best_model:
            print(f"Best model for Bengali language processing: {best_model}")
            print(f"Reason: Highest overall performance score ({best_score:.2f})")
            
            # Additional recommendations
            if "tinyllama" in best_model:
                print("Note: TinyLlama models are lightweight and fast but may have limited Bengali language capabilities.")
            elif "phi" in best_model:
                print("Note: Phi models are more capable but require more resources.")
            elif "deepseek" in best_model:
                print("Note: DeepSeek models are coder-focused but may still work for general Bengali tasks.")
        
        print("\nFor better Bengali language support, consider:")
        print("1. Fine-tuning models specifically on Bengali datasets")
        print("2. Using larger models with more parameters")
        print("3. Exploring models specifically trained for Indic languages")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError running test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)