#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GGUF মডেল দিয়ে সম্পূর্ণ টেস্ট
- TinyLlama GGUF ডাউনলোড
- মডেল লোড (৩০-৪০ সেকেন্ড টাইমআউট)
- Inference টেস্ট
- আনলোড
"""

import requests
import time
import json
from typing import Optional

BASE_URL = "http://localhost:8155"
TIMEOUT = 40

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def download_gguf_model(model_name: str, repo_id: str, timeout: int = 300) -> bool:
    """GGUF মডেল ডাউনলোড করে"""
    print_header(f"মডেল ডাউনলোড: {model_name}")
    
    try:
        # Start download
        payload = {
            "model_name": model_name,
            "repo_id": repo_id
        }
        
        print_info(f"ডাউনলোড শুরু: {repo_id}")
        r = requests.post(f"{BASE_URL}/download/start", json=payload, timeout=10)
        
        if r.status_code != 200:
            print_error(f"ডাউনলোড শুরু ব্যর্থ: {r.status_code} - {r.text[:200]}")
            return False
        
        print_success("ডাউনলোড শুরু হয়েছে")
        
        # Poll status
        start_time = time.time()
        last_progress = -1
        
        while time.time() - start_time < timeout:
            try:
                r2 = requests.get(f"{BASE_URL}/download/status/{model_name}", timeout=5)
                if r2.status_code == 200:
                    status = r2.json()
                    state = status.get("state", "unknown")
                    progress = status.get("progress", 0)
                    
                    # Show progress if changed
                    if progress != last_progress:
                        print_info(f"অগ্রগতি: {progress:.1f}% [{state}]")
                        last_progress = progress
                    
                    if state == "done":
                        elapsed = time.time() - start_time
                        print_success(f"ডাউনলোড সম্পন্ন! সময়: {elapsed:.1f}s")
                        return True
                    elif state == "error":
                        error_msg = status.get("error", "Unknown error")
                        print_error(f"ডাউনলোড এরর: {error_msg}")
                        return False
                    elif state == "cancelled":
                        print_warning("ডাউনলোড বাতিল করা হয়েছে")
                        return False
                    
                time.sleep(2)
            except Exception as e:
                print_warning(f"স্ট্যাটাস চেক এরর: {str(e)}")
                time.sleep(2)
        
        print_error(f"টাইমআউট! {timeout}s এর মধ্যে ডাউনলোড সম্পন্ন হয়নি")
        return False
        
    except Exception as e:
        print_error(f"ডাউনলোড এরর: {str(e)}")
        return False

def load_model(model_name: str, timeout: int = TIMEOUT) -> Optional[int]:
    """মডেল লোড করে এবং port ফেরত দেয়"""
    print_header(f"মডেল লোড: {model_name}")
    
    try:
        print_info(f"লোড করা হচ্ছে... (টাইমআউট: {timeout}s)")
        start_time = time.time()
        
        r = requests.post(
            f"{BASE_URL}/runtime/load/{model_name}",
            params={"threads": 4},
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        
        if r.status_code == 200:
            data = r.json()
            status = data.get("status", "unknown")
            port = data.get("port")
            
            print_success(f"মডেল লোড সফল! সময়: {elapsed:.1f}s")
            print_info(f"স্ট্যাটাস: {status}, পোর্ট: {port}")
            
            # Wait for model to be fully ready
            print_info("মডেল প্রস্তুত হওয়ার জন্য অপেক্ষা...")
            time.sleep(5)
            
            return port
        else:
            print_error(f"লোড ব্যর্থ: {r.status_code} - {r.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        print_error(f"টাইমআউট! {timeout}s এর মধ্যে লোড সম্পন্ন হয়নি")
        return None
    except Exception as e:
        print_error(f"এরর: {str(e)}")
        return None

def test_inference(model_name: str, timeout: int = TIMEOUT) -> bool:
    """মডেল inference টেস্ট করে"""
    print_header(f"Inference টেস্ট: {model_name}")
    
    try:
        payload = {
            "model": model_name,
            "prompt": "What is 2+2?",
            "stream": False
        }
        
        print_info("Inference রিকোয়েস্ট পাঠানো হচ্ছে...")
        start_time = time.time()
        
        r = requests.post(
            f"{BASE_URL}/api/generate",
            json=payload,
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        
        if r.status_code == 200:
            data = r.json()
            print_success(f"Inference সফল! সময়: {elapsed:.1f}s")
            
            # Show response
            runtime_resp = data.get("runtime_response", {})
            content = runtime_resp.get("content", "")
            if content:
                print_info(f"প্রতিক্রিয়া: {content[:200]}")
            else:
                print_warning("কোনো প্রতিক্রিয়া পাওয়া যায়নি")
            
            return True
        else:
            print_error(f"Inference ব্যর্থ: {r.status_code} - {r.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error(f"টাইমআউট! {timeout}s এর মধ্যে inference সম্পন্ন হয়নি")
        return False
    except Exception as e:
        print_error(f"এরর: {str(e)}")
        return False

def unload_model(model_name: str) -> bool:
    """মডেল আনলোড করে"""
    print_header(f"মডেল আনলোড: {model_name}")
    
    try:
        r = requests.post(f"{BASE_URL}/runtime/unload/{model_name}", timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            print_success(f"মডেল আনলোড সফল! স্ট্যাটাস: {data.get('status')}")
            return True
        else:
            print_warning(f"আনলোড ব্যর্থ: {r.status_code}")
            return False
            
    except Exception as e:
        print_error(f"এরর: {str(e)}")
        return False

def check_installed_models():
    """ইনস্টল করা মডেল চেক করে"""
    print_header("ইনস্টল করা মডেল")
    
    try:
        r = requests.get(f"{BASE_URL}/models/installed", timeout=10)
        if r.status_code == 200:
            data = r.json()
            models = data.get("models", [])
            
            if models:
                print_success(f"{len(models)} মডেল পাওয়া গেছে:")
                for m in models:
                    name = m.get("name", "Unknown")
                    size = m.get("size_mb", 0)
                    print(f"  - {name}: {size:.1f} MB")
                return models
            else:
                print_warning("কোনো মডেল পাওয়া যায়নি")
                return []
        else:
            print_error(f"মডেল লিস্ট পেতে ব্যর্থ: {r.status_code}")
            return []
    except Exception as e:
        print_error(f"এরর: {str(e)}")
        return []

def main():
    print_header("GGUF মডেল টেস্ট - ZombieCoder Local AI")
    
    # Check current models
    models = check_installed_models()
    
    # Model to test
    model_name = "tinyllama-gguf"
    repo_id = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    
    # Check if already installed
    if not any(m.get("name") == model_name for m in models):
        print_info(f"'{model_name}' ইনস্টল নেই, ডাউনলোড করা হচ্ছে...")
        
        if not download_gguf_model(model_name, repo_id, timeout=600):
            print_error("ডাউনলোড ব্যর্থ হয়েছে। প্রক্রিয়া বন্ধ করা হচ্ছে।")
            return
        
        # Refresh model list
        time.sleep(2)
        models = check_installed_models()
    
    # Load model
    port = load_model(model_name, timeout=TIMEOUT)
    if not port:
        print_error("মডেল লোড ব্যর্থ। প্রক্রিয়া বন্ধ করা হচ্ছে।")
        return
    
    # Test inference
    time.sleep(2)
    test_inference(model_name, timeout=TIMEOUT)
    
    # Unload
    time.sleep(2)
    unload_model(model_name)
    
    print_header("টেস্ট সম্পূর্ণ")
    print_success("সব কাজ সফলভাবে সম্পন্ন হয়েছে!")

if __name__ == "__main__":
    main()

