#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
সিস্টেম যাচাইকরণ স্ক্রিপ্ট
- লগ বিশ্লেষণ
- এন্ডপয়েন্ট যাচাই
- Ollama সার্ভার চেক
- মডেল লিস্ট ও লোড টেস্ট (30-40 সেকেন্ড টাইমআউট)
"""

import requests
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:8155"
TIMEOUT = 40  # 40 সেকেন্ড টাইমআউট

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

def analyze_logs():
    """লগ ফাইল বিশ্লেষণ করে সমস্যা চিহ্নিত করে"""
    print_header("লগ বিশ্লেষণ (Log Analysis)")
    
    log_file = Path("C:/model/logs/server.log")
    if not log_file.exists():
        print_warning("সার্ভার লগ ফাইল পাওয়া যায়নি")
        return
    
    # শেষ 100 লাইন পড়ুন
    lines = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()[-100:]
    
    # বিশ্লেষণ
    errors = []
    warnings = []
    success_count = 0
    error_404_count = 0
    error_500_count = 0
    
    for line in lines:
        if "\t200\t" in line:
            success_count += 1
        elif "\t404\t" in line:
            error_404_count += 1
            errors.append(line)
        elif "\t500\t" in line or "\t502\t" in line or "\t503\t" in line:
            error_500_count += 1
            errors.append(line)
    
    print_info(f"মোট সফল রিকোয়েস্ট: {success_count}")
    print_info(f"404 এরর: {error_404_count}")
    print_info(f"5xx এরর: {error_500_count}")
    
    if error_404_count > 0:
        print_warning("404 এরর পাওয়া গেছে:")
        for err in errors[:5]:  # প্রথম 5টি দেখান
            parts = err.split('\t')
            if len(parts) >= 3:
                print(f"  - {parts[2]} → {parts[3]}")
    
    if error_500_count > 0:
        print_error("5xx সার্ভার এরর পাওয়া গেছে:")
        for err in errors[:5]:
            print(f"  - {err}")

def check_endpoint(path: str, method: str = "GET", data: Dict = None) -> bool:
    """একটি এন্ডপয়েন্ট চেক করে"""
    try:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, json=data, timeout=10)
        
        if r.status_code == 200:
            print_success(f"{method} {path} → 200 OK")
            return True
        else:
            print_warning(f"{method} {path} → {r.status_code}")
            return False
    except Exception as e:
        print_error(f"{method} {path} → {str(e)}")
        return False

def check_all_endpoints():
    """সব এন্ডপয়েন্ট যাচাই করে"""
    print_header("এন্ডপয়েন্ট যাচাই (Endpoint Verification)")
    
    endpoints = [
        ("/health", "GET"),
        ("/system/info", "GET"),
        ("/models/installed", "GET"),
        ("/models/available", "GET"),
        ("/runtime/status", "GET"),
        ("/runtime/config", "GET"),
        ("/api/tags", "GET"),
        ("/monitoring/summary", "GET"),
        ("/performance/snapshot", "GET"),
        ("/provider/about", "GET"),
        ("/logs/recent", "GET"),
        ("/auth/status", "GET"),
    ]
    
    success = 0
    total = len(endpoints)
    
    for path, method in endpoints:
        if check_endpoint(path, method):
            success += 1
        time.sleep(0.1)
    
    print_info(f"\nমোট: {success}/{total} এন্ডপয়েন্ট সফল")
    return success == total

def check_ollama_compatibility():
    """Ollama সার্ভার compatibility চেক করে"""
    print_header("Ollama সামঞ্জস্যতা যাচাই (Ollama Compatibility)")
    
    try:
        # Check if /api/tags works (Ollama endpoint)
        r = requests.get(f"{BASE_URL}/api/tags", timeout=10)
        if r.status_code == 200:
            data = r.json()
            models = data.get("models", [])
            print_success(f"Ollama API সক্রিয়: {len(models)} মডেল পাওয়া গেছে")
            
            if models:
                print_info("মডেল তালিকা:")
                for m in models:
                    name = m.get("name", "Unknown")
                    size_mb = m.get("size", 0) / (1024 * 1024)
                    status = m.get("runtime_status", "stopped")
                    fmt = m.get("format", "unknown")
                    quant = m.get("quantization", "N/A")
                    print(f"  - {name}: {size_mb:.1f} MB, {fmt}, {quant}, status={status}")
            return True
        else:
            print_error(f"/api/tags এরর: {r.status_code}")
            return False
    except Exception as e:
        print_error(f"Ollama API চেক ব্যর্থ: {str(e)}")
        return False

def get_installed_models() -> List[Dict]:
    """ইনস্টল করা মডেল লিস্ট পায়"""
    try:
        r = requests.get(f"{BASE_URL}/models/installed", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("models", [])
        return []
    except:
        return []

def test_model_load(model_name: str, timeout: int = TIMEOUT) -> bool:
    """মডেল লোড টেস্ট করে (টাইমআউট সহ)"""
    print_header(f"মডেল লোড টেস্ট: {model_name}")
    
    # প্রথমে চেক করুন মডেল আছে কিনা
    models = get_installed_models()
    if not any(m["name"] == model_name for m in models):
        print_error(f"মডেল '{model_name}' ইনস্টল করা নেই")
        return False
    
    print_info(f"মডেল লোড শুরু... (টাইমআউট: {timeout} সেকেন্ড)")
    
    try:
        # Load model
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
            port = data.get("port", "N/A")
            
            print_success(f"মডেল লোড সফল! সময়: {elapsed:.1f}s")
            print_info(f"স্ট্যাটাস: {status}, পোর্ট: {port}")
            
            # Wait a bit for model to be fully ready
            print_info("মডেল সম্পূর্ণ প্রস্তুত হওয়ার জন্য অপেক্ষা করছি...")
            time.sleep(5)
            
            # Check runtime status
            r2 = requests.get(f"{BASE_URL}/runtime/status", timeout=10)
            if r2.status_code == 200:
                rt_data = r2.json()
                for m in rt_data.get("models", []):
                    if m.get("model") == model_name:
                        print_info(f"Runtime স্ট্যাটাস: {m.get('status')}")
            
            return True
        else:
            print_error(f"লোড ব্যর্থ: {r.status_code} - {r.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print_error(f"টাইমআউট! {elapsed:.1f}s পরে প্রতিক্রিয়া পাওয়া যায়নি")
        return False
    except Exception as e:
        print_error(f"এরর: {str(e)}")
        return False

def test_model_inference(model_name: str, timeout: int = TIMEOUT) -> bool:
    """মডেল inference টেস্ট করে"""
    print_header(f"মডেল Inference টেস্ট: {model_name}")
    
    try:
        payload = {
            "model": model_name,
            "prompt": "Hello, how are you?",
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
                print_info(f"প্রতিক্রিয়া: {content[:100]}...")
            
            return True
        else:
            print_warning(f"Inference ব্যর্থ: {r.status_code} - {r.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error(f"টাইমআউট! {timeout}s এর মধ্যে inference সম্পন্ন হয়নি")
        return False
    except Exception as e:
        print_error(f"এরর: {str(e)}")
        return False

def test_model_unload(model_name: str) -> bool:
    """মডেল আনলোড টেস্ট করে"""
    print_header(f"মডেল আনলোড টেস্ট: {model_name}")
    
    try:
        r = requests.post(f"{BASE_URL}/runtime/unload/{model_name}", timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            print_success(f"মডেল আনলোড সফল! স্ট্যাটাস: {data.get('status')}")
            return True
        else:
            print_warning(f"আনলোড ব্যর্থ: {r.status_code} - {r.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"এরর: {str(e)}")
        return False

def main():
    print_header("ZombieCoder Local AI - সিস্টেম যাচাইকরণ")
    print_info(f"সার্ভার: {BASE_URL}")
    print_info(f"টাইমআউট: {TIMEOUT} সেকেন্ড")
    print_info(f"সময়: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. লগ বিশ্লেষণ
    analyze_logs()
    
    # 2. এন্ডপয়েন্ট যাচাই
    check_all_endpoints()
    
    # 3. Ollama compatibility
    check_ollama_compatibility()
    
    # 4. মডেল লিস্ট
    print_header("ইনস্টল করা মডেল")
    models = get_installed_models()
    if models:
        print_success(f"{len(models)} মডেল পাওয়া গেছে:")
        for m in models:
            name = m.get("name", "Unknown")
            size = m.get("size_mb", 0)
            print(f"  - {name}: {size:.1f} MB")
    else:
        print_warning("কোনো মডেল পাওয়া যায়নি")
    
    # 5. মডেল লোড/আনলোড টেস্ট
    if models:
        # প্রথম GGUF মডেল খুঁজুন
        test_model = None
        for m in models:
            name = m.get("name")
            # Check if it's a GGUF model
            model_path = Path(f"C:/model/models/{name}")
            if model_path.exists() and list(model_path.glob("*.gguf")):
                test_model = name
                break
        
        if test_model:
            print_info(f"\nটেস্ট মডেল নির্বাচিত: {test_model}")
            
            # Load test
            if test_model_load(test_model, timeout=TIMEOUT):
                time.sleep(2)
                
                # Inference test
                test_model_inference(test_model, timeout=TIMEOUT)
                time.sleep(2)
                
                # Unload test
                test_model_unload(test_model)
        else:
            print_warning("টেস্টের জন্য কোনো GGUF মডেল পাওয়া যায়নি")
    
    print_header("যাচাইকরণ সম্পূর্ণ")
    print_success("সব টেস্ট সম্পন্ন হয়েছে!")

if __name__ == "__main__":
    main()

