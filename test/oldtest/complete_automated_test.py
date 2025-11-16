#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Local AI Framework - Complete Automated Test System
Automatically stops processes, starts server, loads models, and runs all tests
"""

import subprocess
import requests
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import signal

class ZombieCoderAutomatedTester:
    def __init__(self, base_url: str = "http://localhost:8007"):
        self.base_url = base_url
        self.results = {
            "test_timestamp": datetime.now().isoformat(),
            "server_url": base_url,
            "system_status": {},
            "api_tests": {},
            "chat_tests": {},
            "performance_metrics": {},
            "summary": {}
        }
        self.server_process = None
    
    def stop_existing_processes(self):
        """Stop all existing Python processes"""
        print("🛑 Stopping existing Python processes...")
        try:
            # Windows
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                            capture_output=True, text=True)
                subprocess.run(['taskkill', '/F', '/IM', 'uvicorn.exe'], 
                            capture_output=True, text=True)
            else:
                # Linux/Mac
                subprocess.run(['pkill', '-f', 'python'], 
                            capture_output=True, text=True)
                subprocess.run(['pkill', '-f', 'uvicorn'], 
                            capture_output=True, text=True)
            
            print("✅ Existing processes stopped")
            time.sleep(3)  # Wait for processes to stop
        except Exception as e:
            print(f"⚠️ Warning: Could not stop all processes: {e}")
    
    def start_server(self):
        """Start the server using uvicorn"""
        print("🚀 Starting ZombieCoder server...")
        try:
            # Start server in background
            self.server_process = subprocess.Popen([
                'uvicorn', 'model_server:app', 
                '--host', '0.0.0.0', 
                '--port', '8007'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ Server started successfully!")
                        return True
                except:
                    pass
                time.sleep(1)
                print(f"   Waiting... ({i+1}/30)")
            
            print("❌ Server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def check_authentication(self):
        """Check server authentication and basic endpoints"""
        print("🔐 Checking server authentication...")
        
        endpoints_to_check = [
            "/health",
            "/models/installed", 
            "/system/info",
            "/runtime/status"
        ]
        
        auth_results = {}
        
        for endpoint in endpoints_to_check:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                auth_results[endpoint] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "status_code": response.status_code,
                    "response_time": round(end_time - start_time, 3),
                    "response_data": response.json() if response.status_code == 200 else None
                }
                
                status_icon = "✅" if response.status_code == 200 else "❌"
                print(f"   {status_icon} {endpoint}: {response.status_code} ({end_time - start_time:.2f}s)")
                
            except Exception as e:
                auth_results[endpoint] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"   ❌ {endpoint}: Error - {e}")
        
        self.results["system_status"]["authentication"] = auth_results
        return auth_results
    
    def load_models(self):
        """Load available models"""
        print("🤖 Loading models...")
        
        # Get available models
        try:
            response = requests.get(f"{self.base_url}/models/installed", timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model["name"] for model in models_data.get("models", [])]
                print(f"   Available models: {available_models}")
                
                # Load models
                load_results = {}
                for model_name in available_models:
                    if "gguf" in model_name.lower():  # Only load GGUF models
                        print(f"   Loading {model_name}...")
                        try:
                            load_response = requests.post(
                                f"{self.base_url}/runtime/load/{model_name}",
                                timeout=60
                            )
                            
                            if load_response.status_code == 200:
                                load_data = load_response.json()
                                load_results[model_name] = {
                                    "status": "success",
                                    "data": load_data
                                }
                                print(f"   ✅ {model_name} loaded successfully")
                            else:
                                load_results[model_name] = {
                                    "status": "failed",
                                    "error": f"HTTP {load_response.status_code}"
                                }
                                print(f"   ❌ {model_name} failed to load")
                                
                        except Exception as e:
                            load_results[model_name] = {
                                "status": "error",
                                "error": str(e)
                            }
                            print(f"   ❌ {model_name} error: {e}")
                
                self.results["system_status"]["model_loading"] = load_results
                return load_results
            else:
                print("❌ Could not get available models")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting models: {e}")
            return {}
    
    def run_api_tests(self):
        """Run API tests using the existing chat.py"""
        print("📡 Running API tests...")
        
        try:
            # Import and run the API test
            sys.path.append(os.path.join(os.getcwd(), 'test'))
            from chat import ZombieCoderAPITester
            
            tester = ZombieCoderAPITester(self.base_url)
            api_results = tester.run_all_tests()
            
            self.results["api_tests"] = api_results["api_tests"]
            self.results["performance_metrics"]["api"] = api_results["performance_metrics"]
            
            print("✅ API tests completed")
            return api_results
            
        except Exception as e:
            print(f"❌ Error running API tests: {e}")
            return {}
    
    def run_chat_tests(self):
        """Run chat tests using the existing js.py"""
        print("💬 Running chat tests...")
        
        try:
            # Import and run the chat test
            sys.path.append(os.path.join(os.getcwd(), 'test'))
            from js import ZombieCoderChatTester
            
            tester = ZombieCoderChatTester(self.base_url)
            chat_results = tester.run_conversation_tests()
            
            self.results["chat_tests"] = chat_results["chat_conversations"]
            self.results["performance_metrics"]["chat"] = chat_results["performance_metrics"]
            
            print("✅ Chat tests completed")
            return chat_results
            
        except Exception as e:
            print(f"❌ Error running chat tests: {e}")
            return {}
    
    def show_realtime_status(self):
        """Show real-time system status"""
        print("\n" + "="*60)
        print("📊 REAL-TIME SYSTEM STATUS")
        print("="*60)
        
        try:
            # Health check
            health_response = requests.get(f"{self.base_url}/health", timeout=5)
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"🟢 Server Status: {health_data.get('status', 'Unknown')}")
                print(f"📅 Uptime: {health_data.get('uptime_sec', 0)} seconds")
            
            # Runtime status
            runtime_response = requests.get(f"{self.base_url}/runtime/status", timeout=5)
            if runtime_response.status_code == 200:
                runtime_data = runtime_response.json()
                models = runtime_data.get("models", [])
                print(f"🤖 Loaded Models: {len(models)}")
                for model in models:
                    print(f"   • {model.get('model', 'Unknown')}: {model.get('status', 'Unknown')} (PID: {model.get('pid', 'N/A')})")
            
            # System info
            system_response = requests.get(f"{self.base_url}/system/info", timeout=5)
            if system_response.status_code == 200:
                system_data = system_response.json()
                print(f"💾 RAM: {system_data.get('total_ram_gb', 0)} GB")
                print(f"🖥️ CPU: {system_data.get('cpu_model', 'Unknown')}")
                print(f"🎮 GPU: {system_data.get('gpu_info', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error getting real-time status: {e}")
    
    def generate_final_summary(self):
        """Generate final test summary"""
        print("\n" + "="*60)
        print("📋 FINAL TEST SUMMARY")
        print("="*60)
        
        # Calculate overall metrics
        total_tests = 0
        successful_tests = 0
        
        # Count API tests
        if "api_tests" in self.results:
            for test_name, result in self.results["api_tests"].items():
                total_tests += 1
                if result.get("status") == "success":
                    successful_tests += 1
        
        # Count chat tests
        if "chat_tests" in self.results:
            for test_name, result in self.results["chat_tests"].items():
                total_tests += 1
                if result.get("result", {}).get("status") == "success":
                    successful_tests += 1
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.results["summary"] = {
            "overall_status": "PASS" if success_rate >= 80 else "FAIL",
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": round(success_rate, 2),
            "test_timestamp": self.results["test_timestamp"],
            "server_url": self.base_url
        }
        
        print(f"Overall Status: {self.results['summary']['overall_status']}")
        print(f"Total Tests: {self.results['summary']['total_tests']}")
        print(f"Successful: {self.results['summary']['successful_tests']}")
        print(f"Failed: {self.results['summary']['failed_tests']}")
        print(f"Success Rate: {self.results['summary']['success_rate']}%")
        
        return self.results["summary"]
    
    def export_results(self, filename: str = "complete_test_results.json"):
        """Export all results to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Complete results exported to: {filename}")
        return filename
    
    def run_complete_test_suite(self):
        """Run the complete automated test suite"""
        print("🚀 Starting ZombieCoder Complete Automated Test Suite")
        print("="*60)
        
        try:
            # Step 1: Stop existing processes
            self.stop_existing_processes()
            
            # Step 2: Start server
            if not self.start_server():
                print("❌ Failed to start server. Exiting.")
                return False
            
            # Step 3: Check authentication
            self.check_authentication()
            
            # Step 4: Load models
            self.load_models()
            
            # Step 5: Run API tests
            self.run_api_tests()
            
            # Step 6: Run chat tests
            self.run_chat_tests()
            
            # Step 7: Show real-time status
            self.show_realtime_status()
            
            # Step 8: Generate summary
            self.generate_final_summary()
            
            # Step 9: Export results
            self.export_results()
            
            print("\n🎉 Complete test suite finished successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            return False
        
        finally:
            # Cleanup
            if self.server_process:
                try:
                    self.server_process.terminate()
                except:
                    pass

def main():
    """Main function"""
    tester = ZombieCoderAutomatedTester()
    success = tester.run_complete_test_suite()
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("🔍 Check the exported JSON file for detailed results.")
    else:
        print("\n❌ Some tests failed. Check the logs above.")
    
    return success

if __name__ == "__main__":
    main()
