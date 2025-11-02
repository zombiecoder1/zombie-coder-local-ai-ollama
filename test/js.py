#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Local AI Framework - Chat Test Script
Tests chat functionality as a regular user with Bengali and English questions
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class ZombieCoderChatTester:
    def __init__(self, base_url: str = "http://localhost:8008"):
        self.base_url = base_url
        self.results = {
            "test_timestamp": datetime.now().isoformat(),
            "server_url": base_url,
            "chat_conversations": [],
            "performance_metrics": {},
            "summary": {}
        }
    
    def send_chat_message(self, model: str, messages: List[Dict[str, str]], max_tokens: int = 60) -> Dict[str, Any]:
        """Send a chat message and get response"""
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
    
    def run_conversation_tests(self):
        """Run various conversation tests"""
        print("🚀 Starting ZombieCoder Chat Tests...")
        
        # Test 1: Bengali Greeting
        print("\n🇧🇩 Test 1: Bengali Greeting")
        messages = [{"role": "user", "content": "আপনি কেমন আছেন? আমি ভালো আছি।"}]
        result = self.send_chat_message("phi-2-gguf", messages, 50)
        self.results["chat_conversations"].append({
            "test_name": "Bengali Greeting",
            "language": "Bengali",
            "question": messages[0]["content"],
            "result": result
        })
        
        # Test 2: Family Health Check
        print("\n👨‍👩‍👧‍👦 Test 2: Family Health Check")
        messages = [{"role": "user", "content": "বাসার সবাই কেমন? মন ভালো আছে? আমার পরিবারের সবাই ভালো আছে।"}]
        result = self.send_chat_message("phi-2-gguf", messages, 60)
        self.results["chat_conversations"].append({
            "test_name": "Family Health Check",
            "language": "Bengali",
            "question": messages[0]["content"],
            "result": result
        })
        
        # Test 3: Mathematical Question
        print("\n🔢 Test 3: Mathematical Question")
        messages = [{"role": "user", "content": "Can you solve this math problem: (25 + 15) * 3 - 10 = ?"}]
        result = self.send_chat_message("phi-2-gguf", messages, 50)
        self.results["chat_conversations"].append({
            "test_name": "Mathematical Question",
            "language": "English",
            "question": messages[0]["content"],
            "result": result
        })
        
        # Test 4: Mixed Language Question
        print("\n🌍 Test 4: Mixed Language Question")
        messages = [{"role": "user", "content": "আমি একজন student। I want to learn programming. Can you help me?"}]
        result = self.send_chat_message("phi-2-gguf", messages, 70)
        self.results["chat_conversations"].append({
            "test_name": "Mixed Language Question",
            "language": "Bengali + English",
            "question": messages[0]["content"],
            "result": result
        })
        
        # Test 5: Weather Question in Bengali
        print("\n🌤️ Test 5: Weather Question")
        messages = [{"role": "user", "content": "আজকের আবহাওয়া কেমন? Is it raining today?"}]
        result = self.send_chat_message("phi-2-gguf", messages, 60)
        self.results["chat_conversations"].append({
            "test_name": "Weather Question",
            "language": "Bengali + English",
            "question": messages[0]["content"],
            "result": result
        })
        
        # Test 6: Programming Help
        print("\n💻 Test 6: Programming Help")
        messages = [{"role": "user", "content": "I need help with Python. How do I create a list and add items to it?"}]
        result = self.send_chat_message("phi-2-gguf", messages, 80)
        self.results["chat_conversations"].append({
            "test_name": "Programming Help",
            "language": "English",
            "question": messages[0]["content"],
            "result": result
        })
        
        # Test 7: Bengali Food Question
        print("\n🍛 Test 7: Bengali Food Question")
        messages = [{"role": "user", "content": "আপনি কি খেতে পছন্দ করেন? আমি ভাত খেতে ভালোবাসি।"}]
        result = self.send_chat_message("phi-2-gguf", messages, 50)
        self.results["chat_conversations"].append({
            "test_name": "Bengali Food Question",
            "language": "Bengali",
            "question": messages[0]["content"],
            "result": result
        })
        
        # Test 8: Multi-turn Conversation
        print("\n💬 Test 8: Multi-turn Conversation")
        conversation = [
            {"role": "user", "content": "Hello! How are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you! How can I help you today?"},
            {"role": "user", "content": "Can you tell me about Bangladesh?"}
        ]
        result = self.send_chat_message("phi-2-gguf", conversation, 80)
        self.results["chat_conversations"].append({
            "test_name": "Multi-turn Conversation",
            "language": "English",
            "question": "Multi-turn conversation about Bangladesh",
            "conversation": conversation,
            "result": result
        })
        
        # Test 9: Bengali Cultural Question
        print("\n🎭 Test 9: Bengali Cultural Question")
        messages = [{"role": "user", "content": "বাংলাদেশের সংস্কৃতি সম্পর্কে বলুন। What is special about Bengali culture?"}]
        result = self.send_chat_message("phi-2-gguf", messages, 90)
        self.results["chat_conversations"].append({
            "test_name": "Bengali Cultural Question",
            "language": "Bengali + English",
            "question": messages[0]["content"],
            "result": result
        })
        
        # Test 10: Technical Question
        print("\n🔧 Test 10: Technical Question")
        messages = [{"role": "user", "content": "What is the difference between AI and Machine Learning? Explain in simple terms."}]
        result = self.send_chat_message("phi-2-gguf", messages, 100)
        self.results["chat_conversations"].append({
            "test_name": "Technical Question",
            "language": "English",
            "question": messages[0]["content"],
            "result": result
        })
        
        # Calculate performance metrics
        self.calculate_performance_metrics()
        
        # Generate summary
        self.generate_summary()
        
        print("\n✅ All chat tests completed!")
        return self.results
    
    def calculate_performance_metrics(self):
        """Calculate performance metrics"""
        response_times = []
        success_count = 0
        total_count = len(self.results["chat_conversations"])
        
        for conversation in self.results["chat_conversations"]:
            result = conversation["result"]
            if result["response_time"] is not None:
                response_times.append(result["response_time"])
            if result["status"] == "success":
                success_count += 1
        
        self.results["performance_metrics"] = {
            "total_conversations": total_count,
            "successful_conversations": success_count,
            "failed_conversations": total_count - success_count,
            "success_rate": round((success_count / total_count) * 100, 2) if total_count > 0 else 0,
            "average_response_time": round(sum(response_times) / len(response_times), 3) if response_times else 0,
            "min_response_time": round(min(response_times), 3) if response_times else 0,
            "max_response_time": round(max(response_times), 3) if response_times else 0
        }
    
    def generate_summary(self):
        """Generate test summary"""
        metrics = self.results["performance_metrics"]
        
        # Analyze language support
        bengali_tests = [c for c in self.results["chat_conversations"] if "Bengali" in c["language"]]
        english_tests = [c for c in self.results["chat_conversations"] if "English" in c["language"]]
        mixed_tests = [c for c in self.results["chat_conversations"] if "+" in c["language"]]
        
        self.results["summary"] = {
            "overall_status": "PASS" if metrics["success_rate"] >= 80 else "FAIL",
            "total_conversations": metrics["total_conversations"],
            "successful_conversations": metrics["successful_conversations"],
            "failed_conversations": metrics["failed_conversations"],
            "success_percentage": metrics["success_rate"],
            "average_response_time_seconds": metrics["average_response_time"],
            "fastest_response_seconds": metrics["min_response_time"],
            "slowest_response_seconds": metrics["max_response_time"],
            "language_support": {
                "bengali_tests": len(bengali_tests),
                "english_tests": len(english_tests),
                "mixed_language_tests": len(mixed_tests)
            },
            "recommendations": self.get_recommendations()
        }
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations based on test results"""
        recommendations = []
        metrics = self.results["performance_metrics"]
        
        if metrics["success_rate"] < 90:
            recommendations.append("Some chat conversations failed. Check server logs for errors.")
        
        if metrics["average_response_time"] > 30:
            recommendations.append("Chat response times are slow. Consider optimizing model performance.")
        
        if metrics["max_response_time"] > 60:
            recommendations.append("Some chat requests are taking too long. Check for timeout issues.")
        
        if metrics["success_rate"] >= 95 and metrics["average_response_time"] < 20:
            recommendations.append("Excellent chat performance! System is working optimally.")
        
        return recommendations
    
    def export_results(self, filename: str = "chat_test_results.json"):
        """Export results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Results exported to: {filename}")
        return filename

def main():
    """Main function to run chat tests"""
    tester = ZombieCoderChatTester()
    results = tester.run_conversation_tests()
    
    # Export results
    filename = tester.export_results()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 CHAT TEST SUMMARY")
    print("="*60)
    summary = results["summary"]
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Total Conversations: {summary['total_conversations']}")
    print(f"Successful Conversations: {summary['successful_conversations']}")
    print(f"Failed Conversations: {summary['failed_conversations']}")
    print(f"Success Rate: {summary['success_percentage']}%")
    print(f"Average Response Time: {summary['average_response_time_seconds']}s")
    print(f"Fastest Response: {summary['fastest_response_seconds']}s")
    print(f"Slowest Response: {summary['slowest_response_seconds']}s")
    
    print(f"\n🌍 Language Support:")
    lang_support = summary["language_support"]
    print(f"  Bengali Tests: {lang_support['bengali_tests']}")
    print(f"  English Tests: {lang_support['english_tests']}")
    print(f"  Mixed Language Tests: {lang_support['mixed_language_tests']}")
    
    if summary["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in summary["recommendations"]:
            print(f"  • {rec}")
    
    print(f"\n📄 Detailed results saved to: {filename}")

if __name__ == "__main__":
    main()
