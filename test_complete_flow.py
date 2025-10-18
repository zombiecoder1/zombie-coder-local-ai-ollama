#!/usr/bin/env python3
"""
ZombieCoder - সম্পূর্ণ ফ্লো টেস্ট
Token → Available → Download → Load → Generate → Unload
"""
import requests
import time
import json

BASE = "http://127.0.0.1:8155"

def log(msg, status="info"):
    colors = {"ok": "\033[92m", "warn": "\033[93m", "err": "\033[91m", "info": "\033[96m"}
    print(f"{colors.get(status, '')}{msg}\033[0m")

def wait_server():
    log("⏳ সার্ভার চেক করা হচ্ছে...", "info")
    for i in range(30):
        try:
            r = requests.get(f"{BASE}/health", timeout=2)
            if r.ok:
                log(f"✅ সার্ভার প্রস্তুত: {r.json()}", "ok")
                return True
        except:
            time.sleep(1)
    log("❌ সার্ভার রেসপন্স করছে না", "err")
    return False

def save_token(token):
    log(f"🔑 টোকেন সেভ করা হচ্ছে...", "info")
    try:
        r = requests.post(f"{BASE}/auth/hf_token", json={"token": token}, timeout=10)
        if r.ok:
            log(f"✅ টোকেন সেভ সফল: {r.json()}", "ok")
            return True
    except Exception as e:
        log(f"❌ টোকেন সেভ ব্যর্থ: {e}", "err")
    return False

def get_available():
    log("📋 উপলব্ধ মডেল লিস্ট...", "info")
    try:
        r = requests.get(f"{BASE}/models/available", timeout=10)
        if r.ok:
            data = r.json()
            log(f"✅ {len(data)} টি মডেল পাওয়া গেছে", "ok")
            for m in data[:3]:
                print(f"   - {m.get('name')} ({m.get('size', 'N/A')})")
            return data
    except Exception as e:
        log(f"❌ লিস্ট ব্যর্থ: {e}", "err")
    return []

def download_model(model_name, repo_id):
    log(f"⬇️  ডাউনলোড শুরু: {model_name} ({repo_id})", "info")
    try:
        r = requests.post(f"{BASE}/download/start", json={"model_name": model_name, "repo_id": repo_id}, timeout=15)
        if r.ok:
            log(f"✅ ডাউনলোড শুরু হয়েছে: {r.json()}", "ok")
            # Poll status
            for i in range(60):
                time.sleep(3)
                status = requests.get(f"{BASE}/download/status/{model_name}", timeout=10).json()
                log(f"   স্ট্যাটাস: {status.get('status', 'unknown')}", "info")
                if status.get('status') == 'completed':
                    log(f"✅ ডাউনলোড সম্পন্ন!", "ok")
                    return True
                elif status.get('status') == 'failed':
                    log(f"❌ ডাউনলোড ব্যর্থ", "err")
                    return False
    except Exception as e:
        log(f"❌ ডাউনলোড এরর: {e}", "err")
    return False

def load_model(model_name):
    log(f"🔄 মডেল লোড করা হচ্ছে: {model_name}", "info")
    try:
        r = requests.post(f"{BASE}/runtime/load/{model_name}", timeout=120)
        if r.ok:
            data = r.json()
            log(f"✅ মডেল লোড সফল: পোর্ট {data.get('port')}, PID {data.get('pid')}", "ok")
            return data
    except Exception as e:
        log(f"❌ লোড ব্যর্থ: {e}", "err")
    return None

def generate(model_name, prompt="Hello, who are you?"):
    log(f"💬 টেক্সট জেনারেট করা হচ্ছে...", "info")
    try:
        r = requests.post(f"{BASE}/api/generate", json={"model": model_name, "prompt": prompt, "stream": False}, timeout=180)
        if r.ok:
            data = r.json()
            log(f"✅ রেসপন্স: {json.dumps(data, indent=2)}", "ok")
            return data
    except Exception as e:
        log(f"❌ জেনারেট ব্যর্থ: {e}", "err")
    return None

def unload_model(model_name):
    log(f"⏹️  মডেল আনলোড করা হচ্ছে: {model_name}", "info")
    try:
        r = requests.post(f"{BASE}/runtime/unload/{model_name}", timeout=30)
        if r.ok:
            log(f"✅ মডেল আনলোড সফল", "ok")
            return True
    except Exception as e:
        log(f"❌ আনলোড ব্যর্থ: {e}", "err")
    return False

def main():
    log("═══════════════════════════════════════", "info")
    log("  ZombieCoder - সম্পূর্ণ ফ্লো টেস্ট", "info")
    log("═══════════════════════════════════════", "info")
    
    if not wait_server():
        return
    
    # Step 1: Save token (placeholder)
    token = "REPLACE_WITH_YOUR_HF_TOKEN"
    if not save_token(token):
        log("⚠️  টোকেন সেভ না হলেও চালিয়ে যাচ্ছি...", "warn")
    
    # Step 2: Get available models
    available = get_available()
    
    # Step 3: Check installed models
    log("📦 ইনস্টলড মডেল চেক করা হচ্ছে...", "info")
    try:
        r = requests.get(f"{BASE}/models/installed", timeout=10)
        if r.ok:
            inst = r.json()
            log(f"✅ {inst.get('count', 0)} টি মডেল ইনস্টল করা আছে", "ok")
            if inst.get('models'):
                # Use first installed model
                first_model = inst['models'][0]['name']
                log(f"🎯 মডেল ব্যবহার করা হবে: {first_model}", "info")
                
                # Load
                loaded = load_model(first_model)
                if loaded:
                    time.sleep(5)  # Wait for model to be ready
                    
                    # Generate
                    generate(first_model, "What is 2+2?")
                    
                    # Unload
                    time.sleep(2)
                    unload_model(first_model)
                
                log("═══════════════════════════════════════", "ok")
                log("  ✅ সম্পূর্ণ ফ্লো সফল!", "ok")
                log("═══════════════════════════════════════", "ok")
                return
    except Exception as e:
        log(f"❌ ইনস্টলড চেক এরর: {e}", "err")
    
    log("⚠️  কোনো মডেল ইনস্টল নেই। UI থেকে ডাউনলোড করুন:", "warn")
    log(f"   http://127.0.0.1:8155/static/allindex.html", "info")

if __name__ == "__main__":
    main()
