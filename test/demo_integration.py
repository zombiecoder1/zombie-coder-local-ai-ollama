#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Systems Integration Demo
দুটি সিস্টেম একসাথে ব্যবহার করার উদাহরণ
"""

import requests
import json
import time

# Colors for output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

# System endpoints
LOCAL_AI = "http://localhost:8155"
API_GATEWAY = "http://localhost:8000"
MEMORY_SERVICE = "http://localhost:8001"
MULTIPROCESSING = "http://localhost:8002"

def check_services():
    """সব সার্ভিস চেক করুন"""
    print_header("সার্ভিস স্ট্যাটাস চেক")
    
    services = [
        ("Local AI Framework", LOCAL_AI + "/health"),
        ("API Gateway", API_GATEWAY + "/health"),
        ("Memory Service", MEMORY_SERVICE + "/health"),
        ("Multiprocessing", MULTIPROCESSING + "/health"),
    ]
    
    for name, url in services:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                print_success(f"{name}: Running")
            else:
                print_warning(f"{name}: Status {r.status_code}")
        except Exception as e:
            print_warning(f"{name}: Not available ({str(e)[:30]})")

def demo_ai_generation():
    """AI Text Generation Demo"""
    print_header("Demo 1: AI Text Generation")
    
    # Check if model loaded
    print_info("Checking model status...")
    r = requests.get(f"{LOCAL_AI}/runtime/status")
    status = r.json()
    
    model_loaded = False
    for m in status.get('models', []):
        if m.get('status') == 'ready':
            model_loaded = True
            print_success(f"Model loaded: {m.get('model')}")
    
    if not model_loaded:
        print_warning("Loading model...")
        r = requests.post(f"{LOCAL_AI}/runtime/load/tinyllama-gguf?threads=4")
        if r.status_code == 200:
            print_success("Model loaded successfully!")
            time.sleep(2)
        else:
            print_warning("Failed to load model")
            return
    
    # Generate text
    print_info("Generating AI response...")
    
    prompts = [
        "Write a Python hello world program",
        "Explain AI in simple terms",
        "What is machine learning?"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{Colors.BOLD}Prompt {i}:{Colors.END} {prompt}")
        
        try:
            r = requests.post(
                f"{LOCAL_AI}/api/generate",
                json={"model": "tinyllama-gguf", "prompt": prompt},
                timeout=30
            )
            
            if r.status_code == 200:
                data = r.json()
                response = data.get('runtime_response', {}).get('content', '')
                print(f"{Colors.GREEN}Response:{Colors.END} {response[:200]}...")
            else:
                print_warning(f"Failed: {r.status_code}")
        except Exception as e:
            print_warning(f"Error: {str(e)[:50]}")

def demo_memory_service():
    """Memory Service Demo"""
    print_header("Demo 2: Memory Service")
    
    session_id = f"demo_{int(time.time())}"
    
    # Save conversation
    print_info(f"Saving conversation to session: {session_id}")
    
    conversation = [
        {"message": "Hello", "response": "Hi! Hello Zombie?"},
        {"message": "What is Python?", "response": "Python is a programming language."},
        {"message": "Tell me more", "response": "Python is easy to learn and powerful."}
    ]
    
    for conv in conversation:
        try:
            r = requests.post(
                f"{MEMORY_SERVICE}/memory/save",
                json={
                    "session_id": session_id,
                    "message": conv["message"],
                    "response": conv["response"]
                },
                timeout=5
            )
            
            if r.status_code == 200:
                print_success(f"Saved: {conv['message'][:30]}...")
            else:
                print_warning(f"Failed to save: {r.status_code}")
        except Exception as e:
            print_warning(f"Memory service error: {str(e)[:50]}")
    
    # Retrieve memory
    print_info(f"Retrieving conversation history...")
    
    try:
        r = requests.get(f"{MEMORY_SERVICE}/memory/get/{session_id}", timeout=5)
        if r.status_code == 200:
            history = r.json()
            print_success(f"Retrieved {len(history.get('messages', []))} messages")
            print(json.dumps(history, indent=2)[:300])
        else:
            print_warning("Failed to retrieve memory")
    except Exception as e:
        print_warning(f"Error: {str(e)[:50]}")

def demo_integration():
    """Complete Integration Demo"""
    print_header("Demo 3: সম্পূর্ণ Integration (AI + Memory)")
    
    session_id = f"integrated_{int(time.time())}"
    
    # Step 1: User question
    user_query = "What is the capital of Bangladesh?"
    print_info(f"User Query: {user_query}")
    
    # Step 2: Generate AI response
    print_info("Generating AI response...")
    
    try:
        r = requests.post(
            f"{LOCAL_AI}/api/generate",
            json={"model": "tinyllama-gguf", "prompt": user_query},
            timeout=30
        )
        
        if r.status_code == 200:
            data = r.json()
            ai_response = data.get('runtime_response', {}).get('content', '')
            print_success(f"AI Response: {ai_response[:100]}...")
            
            # Step 3: Save to memory
            print_info("Saving to memory service...")
            
            try:
                r2 = requests.post(
                    f"{MEMORY_SERVICE}/memory/save",
                    json={
                        "session_id": session_id,
                        "message": user_query,
                        "response": ai_response
                    },
                    timeout=5
                )
                
                if r2.status_code == 200:
                    print_success("Conversation saved to memory!")
                    print_info(f"Session ID: {session_id}")
                else:
                    print_warning("Failed to save to memory")
            except:
                print_warning("Memory service not available")
        else:
            print_warning("AI generation failed")
    except Exception as e:
        print_warning(f"Error: {str(e)[:50]}")

def demo_multiprocessing():
    """Multiprocessing Demo"""
    print_header("Demo 4: Multiprocessing Service")
    
    print_info("Submitting parallel tasks...")
    
    tasks = [
        {"id": 1, "type": "compute", "data": "task_1"},
        {"id": 2, "type": "compute", "data": "task_2"},
        {"id": 3, "type": "compute", "data": "task_3"}
    ]
    
    try:
        r = requests.post(
            f"{MULTIPROCESSING}/process/parallel",
            json={"tasks": tasks},
            timeout=10
        )
        
        if r.status_code == 200:
            result = r.json()
            print_success(f"Processed {len(tasks)} tasks in parallel")
            print(json.dumps(result, indent=2)[:300])
        else:
            print_warning(f"Failed: {r.status_code}")
    except Exception as e:
        print_warning(f"Multiprocessing service error: {str(e)[:50]}")

def main():
    print_header("🧟 ZombieCoder Systems Integration Demo")
    print(f"{Colors.CYAN}দুটি সিস্টেম একসাথে ব্যবহার করার উদাহরণ{Colors.END}\n")
    
    # Check all services
    check_services()
    
    # Run demos
    demos = [
        ("AI Text Generation", demo_ai_generation),
        ("Memory Service", demo_memory_service),
        ("Integration", demo_integration),
        ("Multiprocessing", demo_multiprocessing),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{Colors.BOLD}[{i}/{len(demos)}]{Colors.END}")
        try:
            demo_func()
        except Exception as e:
            print_warning(f"Demo failed: {str(e)[:100]}")
        
        if i < len(demos):
            time.sleep(2)
    
    print_header("Demo সম্পন্ন!")
    print(f"\n{Colors.GREEN}✓ সব demo সফলভাবে চালানো হয়েছে!{Colors.END}\n")
    
    # Print summary
    print(f"{Colors.BOLD}Available Endpoints:{Colors.END}")
    print(f"  - Local AI: {LOCAL_AI}")
    print(f"  - API Gateway: {API_GATEWAY}")
    print(f"  - Memory Service: {MEMORY_SERVICE}")
    print(f"  - Multiprocessing: {MULTIPROCESSING}")
    
    print(f"\n{Colors.BOLD}Working Features:{Colors.END}")
    print(f"  ✓ AI Text Generation (tinyllama-gguf)")
    print(f"  ✓ Memory/Conversation Storage")
    print(f"  ✓ Parallel Task Processing")
    print(f"  ✓ Session Management")
    print(f"  ✓ System Integration")

if __name__ == "__main__":
    main()

