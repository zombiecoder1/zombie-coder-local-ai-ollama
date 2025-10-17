#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Local AI - GGUF Model Loader
Loads GGUF models using llama.cpp backend
"""

import subprocess
import os
import sys
from pathlib import Path
import time
import requests
from typing import Optional, Dict


def find_llama_cpp_server() -> Optional[Path]:
    """
    Find llama.cpp server executable
    
    Returns:
        Path to server executable or None
    """
    possible_paths = [
        Path("config/llama.cpp/server.exe"),
        Path("../config/llama.cpp/server.exe"),
        Path("C:/model/config/llama.cpp/server.exe"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path.resolve()
    
    return None


def load_model(
    model_path: str,
    port: int = 8080,
    threads: int = 4,
    gpu_layers: int = 0,
    context_size: int = 2048,
    background: bool = True
) -> Dict:
    """
    Load GGUF model using llama.cpp server
    
    Args:
        model_path: Path to GGUF model file
        port: Server port
        threads: Number of CPU threads
        gpu_layers: Number of GPU layers (0 for CPU-only)
        context_size: Context size
        background: Run in background
    
    Returns:
        Dict with process info
    """
    # Find llama.cpp server
    llama_bin = find_llama_cpp_server()
    if not llama_bin:
        raise FileNotFoundError("❌ llama.cpp server not found!")
    
    # Check if model exists
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"❌ Model not found: {model_path}")
    
    print(f"🚀 Loading model: {model_path}")
    print(f"📦 Server: {llama_bin}")
    print(f"🔌 Port: {port}")
    print(f"🧵 Threads: {threads}")
    print(f"🎮 GPU Layers: {gpu_layers}")
    
    # Build command
    cmd = [
        str(llama_bin),
        "--model", str(model_path),
        "--port", str(port),
        "--threads", str(threads),
        "--ctx-size", str(context_size),
    ]
    
    if gpu_layers > 0:
        cmd.extend(["--n-gpu-layers", str(gpu_layers)])
    
    # Start process
    if background:
        # Run in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        print(f"✅ Model loading (PID: {process.pid})")
        
        # Wait for server to be ready
        max_wait = 30
        for i in range(max_wait):
            try:
                response = requests.get(f"http://127.0.0.1:{port}/health", timeout=1)
                if response.status_code == 200:
                    print(f"✅ Model ready on port {port}")
                    break
            except:
                pass
            time.sleep(1)
        else:
            print(f"⚠️ Server may still be loading...")
        
        return {
            "status": "loading",
            "pid": process.pid,
            "port": port,
            "model_path": str(model_path),
            "command": " ".join(cmd)
        }
    else:
        # Run in foreground (blocking)
        subprocess.run(cmd)
        return {
            "status": "completed",
            "port": port,
            "model_path": str(model_path)
        }


def check_model_status(port: int = 8080) -> Dict:
    """
    Check if model is ready on given port
    
    Args:
        port: Server port
    
    Returns:
        Dict with status info
    """
    try:
        response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
        if response.status_code == 200:
            return {"status": "ready", "port": port}
    except:
        pass
    
    return {"status": "not_ready", "port": port}


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
        threads = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    else:
        # Default example
        model_path = "./models/tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
        port = 8080
        threads = 4
    
    try:
        result = load_model(model_path, port=port, threads=threads)
        print(f"\n📊 Status: {result}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

