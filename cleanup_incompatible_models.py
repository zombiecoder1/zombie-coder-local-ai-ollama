#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to clean up incompatible and low-power models
"""

import os
import shutil
from pathlib import Path

def cleanup_models():
    """Delete the incompatible and low-power models"""
    base_dir = Path.cwd()
    models_dir = base_dir / "models"
    
    # Models to delete based on migration report
    models_to_delete = [
        "qwen2.5-0.5b-instruct-gguf",  # Low-power model
        "qwen2.5-3b-bangla"            # Incompatible safetensors model
    ]
    
    print("🗑️  Cleaning up incompatible and low-power models...")
    
    for model_name in models_to_delete:
        model_path = models_dir / model_name
        if model_path.exists():
            try:
                if model_path.is_dir():
                    shutil.rmtree(model_path)
                    print(f"✅ Deleted directory: {model_name}")
                else:
                    model_path.unlink()
                    print(f"✅ Deleted file: {model_name}")
            except Exception as e:
                print(f"❌ Error deleting {model_name}: {e}")
        else:
            print(f"⚠️  Model not found: {model_name}")
    
    # Also delete associated log files
    log_files_to_delete = [
        "download_qwen2.5-0.5b-instruct-gguf.log",
        "download_qwen2.5-3b-bangla.log"
    ]
    
    for log_file in log_files_to_delete:
        log_path = models_dir / log_file
        if log_path.exists():
            try:
                log_path.unlink()
                print(f"✅ Deleted log file: {log_file}")
            except Exception as e:
                print(f"❌ Error deleting log {log_file}: {e}")
    
    print("✅ Cleanup completed!")

if __name__ == "__main__":
    cleanup_models()