#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Local AI Framework - API Test Script
Tests all API endpoints as a regular user
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class ZombieCoderAPITester:
    def __init__(self, base_url: str = "http://localhost:8008"):
        self.base_url = base_url
        self.results = {
            "test_timestamp": datetime.now().isoformat(),
            "server_url": base_url,
            "api_tests": {},
            "chat_tests": {},
            "performance_metrics": {},
            "summary": {}
        }
    
    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test health endpoint"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            end_time = time.time()
            
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_time": round(end_time - start_time, 3),
                "response_data": response.json() if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}"
            }
        except Exception as e:
            return {
                "status": "error",
                "status_code": None,
                "response_time": None,
                "response_data": None,
                "error": str(e)
            }
    
    def test_models_installed(self) -> Dict[str, Any]:
        """Test models installed endpoint"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/models/installed", timeout=10)
            end_time = time.time()
            
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_time": round(end_time - start_time, 3),
                "response_data": response.json() if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}"
            }
        except Exception as e:
            return {
                "status": "error",
                "status_code": None,
                "response_time": None,
                "response_data": None,
                "error": str(e)
            }
    
    def test_system_info(self) -> Dict[str, Any]:
        """Test system info endpoint"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/system/info", timeout=10)
            end_time = time.time()
            
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_time": round(end_time - start_time, 3),
                "response_data": response.json() if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}"
            }
        except Exception as e:
            return {
                "status": "error",
                "status_code": None,
                "response_time": None,
                "response_data": None,
                "error": str(e)
            }
    
    def test_runtime_status(self) -> Dict[str, Any]:
        """Test runtime status endpoint"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/runtime/status", timeout=10)
            end_time = time.time()
            
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_time": round(end_time - start_time, 3),
                "response_data": response.json() if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}"
            }
        except Exception as e:
            return {
                "status": "error",
                "status_code": None,
                "response_time": None,
                "response_data": None,
                "error": str(e)
            }
    
    def test_generate_api(self, model: str, prompt: str, max_tokens: int = 50) -> Dict[str, Any]:
        """Test generate API endpoint"""
        start_time = time.time()
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "max_tokens": max_tokens
            }
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            end_time = time.time()
            
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_time": round(end_time - start_time, 3),
                "response_data": response.json() if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}",
                "prompt": prompt,
                "model": model
            }
        except Exception as e:
            return {
                "status": "error",
                "status_code": None,
                "response_time": None,
                "response_data": None,
                "error": str(e),
                "prompt": prompt,
                "model": model
            }
    
    def test_chat_api(self, model: str, messages: List[Dict[str, str]], max_tokens: int = 50) -> Dict[str, Any]:
        """Test chat API endpoint"""
        start_time = time.time()
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens
            }
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            end_time = time.time()
            
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_time": round(end_time - start_time, 3),
                "response_data": response.json() if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}",
                "messages": messages,
                "model": model
            }
        except Exception as e:
            return {
                "status": "error",
                "status_code": None,
                "response_time": None,
                "response_data": None,
                "error": str(e),
                "messages": messages,
                "model": model
            }
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting ZombieCoder Local AI Framework API Tests...")
        
        # Test basic endpoints
        print("\n📡 Testing Basic Endpoints...")
        self.results["api_tests"]["health"] = self.test_health_endpoint()
        self.results["api_tests"]["models_installed"] = self.test_models_installed()
        self.results["api_tests"]["system_info"] = self.test_system_info()
        self.results["api_tests"]["runtime_status"] = self.test_runtime_status()
        
        # Test generate API with different questions
        print("\n🤖 Testing Generate API...")
        test_questions = [
            "What is artificial intelligence?",
            "Explain machine learning in simple terms.",
            "Write a Python function to calculate the sum of two numbers.",
            "What is the capital of Bangladesh?",
            "How does photosynthesis work?"
        ]
        
        for i, question in enumerate(test_questions):
            print(f"  Question {i+1}: {question[:50]}...")
            result = self.test_generate_api("phi-2-gguf", question, 60)
            self.results["api_tests"][f"generate_question_{i+1}"] = result
        
        # Test chat API
        print("\n💬 Testing Chat API...")
        chat_scenarios = [
            [{"role": "user", "content": "Hello! How are you today?"}],
            [{"role": "user", "content": "Can you help me with a math problem? What is 15 * 8?"}],
            [{"role": "user", "content": "Tell me about the weather in Bangladesh."}]
        ]
        
        for i, messages in enumerate(chat_scenarios):
            print(f"  Chat Scenario {i+1}: {messages[0]['content'][:50]}...")
            result = self.test_chat_api("phi-2-gguf", messages, 50)
            self.results["chat_tests"][f"chat_scenario_{i+1}"] = result
        
        # Calculate performance metrics
        self.calculate_performance_metrics()
        
        # Generate summary
        self.generate_summary()
        
        print("\n✅ All tests completed!")
        return self.results
    
    def calculate_performance_metrics(self):
        """Calculate performance metrics"""
        response_times = []
        success_count = 0
        total_count = 0
        
        # Collect metrics from API tests
        for test_name, result in self.results["api_tests"].items():
            if result["response_time"] is not None:
                response_times.append(result["response_time"])
            if result["status"] == "success":
                success_count += 1
            total_count += 1
        
        # Collect metrics from chat tests
        for test_name, result in self.results["chat_tests"].items():
            if result["response_time"] is not None:
                response_times.append(result["response_time"])
            if result["status"] == "success":
                success_count += 1
            total_count += 1
        
        self.results["performance_metrics"] = {
            "total_tests": total_count,
            "successful_tests": success_count,
            "failed_tests": total_count - success_count,
            "success_rate": round((success_count / total_count) * 100, 2) if total_count > 0 else 0,
            "average_response_time": round(sum(response_times) / len(response_times), 3) if response_times else 0,
            "min_response_time": round(min(response_times), 3) if response_times else 0,
            "max_response_time": round(max(response_times), 3) if response_times else 0
        }
    
    def generate_summary(self):
        """Generate test summary"""
        metrics = self.results["performance_metrics"]
        
        self.results["summary"] = {
            "overall_status": "PASS" if metrics["success_rate"] >= 80 else "FAIL",
            "total_tests_run": metrics["total_tests"],
            "tests_passed": metrics["successful_tests"],
            "tests_failed": metrics["failed_tests"],
            "success_percentage": metrics["success_rate"],
            "average_response_time_seconds": metrics["average_response_time"],
            "fastest_response_seconds": metrics["min_response_time"],
            "slowest_response_seconds": metrics["max_response_time"],
            "recommendations": self.get_recommendations()
        }
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations based on test results"""
        recommendations = []
        metrics = self.results["performance_metrics"]
        
        if metrics["success_rate"] < 90:
            recommendations.append("Some API endpoints are failing. Check server logs for errors.")
        
        if metrics["average_response_time"] > 20:
            recommendations.append("Response times are slow. Consider optimizing model performance.")
        
        if metrics["max_response_time"] > 60:
            recommendations.append("Some requests are taking too long. Check for timeout issues.")
        
        if metrics["success_rate"] >= 95 and metrics["average_response_time"] < 15:
            recommendations.append("Excellent performance! System is working optimally.")
        
        return recommendations
    
    def export_results(self, filename: str = "api_test_results.json"):
        """Export results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Results exported to: {filename}")
        return filename

def main():
    """Main function to run tests"""
    tester = ZombieCoderAPITester()
    results = tester.run_all_tests()
    
    # Export results
    filename = tester.export_results()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    summary = results["summary"]
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Tests Run: {summary['total_tests_run']}")
    print(f"Tests Passed: {summary['tests_passed']}")
    print(f"Tests Failed: {summary['tests_failed']}")
    print(f"Success Rate: {summary['success_percentage']}%")
    print(f"Average Response Time: {summary['average_response_time_seconds']}s")
    print(f"Fastest Response: {summary['fastest_response_seconds']}s")
    print(f"Slowest Response: {summary['slowest_response_seconds']}s")
    
    if summary["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in summary["recommendations"]:
            print(f"  • {rec}")
    
    print(f"\n📄 Detailed results saved to: {filename}")

if __name__ == "__main__":
    main()
