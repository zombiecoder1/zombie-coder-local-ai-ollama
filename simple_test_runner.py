#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Simple Test Runner
"""

import subprocess
import requests
import json
import time
import os

def stop_processes():
    print("🛑 Stopping existing processes...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
        subprocess.run(['taskkill', '/F', '/IM', 'uvicorn.exe'], capture_output=True)
        print("✅ Processes stopped")
        time.sleep(3)
    except:
        print("⚠️ Some processes couldn't be stopped")

def start_server():
    print("🚀 Starting server...")
    try:
        # Start server in background
        process = subprocess.Popen([
            'uvicorn', 'model_server:app', '--host', '0.0.0.0', '--port', '8007'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server
        for i in range(30):
            try:
                response = requests.get("http://localhost:8007/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Server started!")
                    return True
            except:
                pass
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ Server failed to start")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def load_models():
    print("🤖 Loading models...")
    try:
        response = requests.post("http://localhost:8007/runtime/load/phi-2-gguf", timeout=60)
        if response.status_code == 200:
            print("✅ Phi-2-gguf loaded")
        else:
            print("❌ Failed to load phi-2-gguf")
    except Exception as e:
        print(f"❌ Error loading models: {e}")

def test_api():
    print("📡 Testing API...")
    try:
        # Test generate
        payload = {
            "model": "phi-2-gguf",
            "prompt": "Hello, how are you?",
            "max_tokens": 30
        }
        response = requests.post("http://localhost:8007/api/generate", json=payload, timeout=30)
        if response.status_code == 200:
            print("✅ Generate API works")
            data = response.json()
            print(f"   Response: {data['runtime_response']['content'][:50]}...")
        else:
            print(f"❌ Generate API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API test error: {e}")

def test_chat():
    print("💬 Testing Chat...")
    try:
        # Test chat
        payload = {
            "model": "phi-2-gguf",
            "messages": [{"role": "user", "content": "আপনি কেমন আছেন?"}],
            "max_tokens": 30
        }
        response = requests.post("http://localhost:8007/api/chat", json=payload, timeout=30)
        if response.status_code == 200:
            print("✅ Chat API works")
            data = response.json()
            print(f"   Response: {data['runtime_response']['content'][:50]}...")
        else:
            print(f"❌ Chat API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat test error: {e}")

def show_status():
    print("\n📊 Real-time Status:")
    try:
        # Health
        health = requests.get("http://localhost:8007/health", timeout=5)
        if health.status_code == 200:
            print(f"🟢 Server: {health.json().get('status', 'Unknown')}")
        
        # Runtime
        runtime = requests.get("http://localhost:8007/runtime/status", timeout=5)
        if runtime.status_code == 200:
            models = runtime.json().get("models", [])
            print(f"🤖 Models: {len(models)} loaded")
            for model in models:
                print(f"   • {model.get('model', 'Unknown')}: {model.get('status', 'Unknown')}")
        
        # System
        system = requests.get("http://localhost:8007/system/info", timeout=5)
        if system.status_code == 200:
            sys_data = system.json()
            print(f"💾 RAM: {sys_data.get('total_ram_gb', 0)} GB")
            print(f"🖥️ CPU: {sys_data.get('cpu_model', 'Unknown')[:50]}...")
            
    except Exception as e:
        print(f"❌ Status error: {e}")

def main():
    print("🚀 ZombieCoder Simple Test Runner")
    print("="*40)
    
    # Step 1: Stop processes
    stop_processes()
    
    # Step 2: Start server
    if not start_server():
        return
    
    # Step 3: Load models
    load_models()
    
    # Step 4: Test API
    test_api()
    
    # Step 5: Test Chat
    test_chat()
    
    # Step 6: Show status
    show_status()
    
    print("\n✅ All tests completed!")
    print("🔍 Server is running at: http://localhost:8007")

if __name__ == "__main__":
    main()
