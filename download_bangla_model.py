#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to download Qwen2.5:3b model for Bangla language support
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path to import project modules
sys.path.append(str(Path(__file__).parent))

from downloader import HFDownloader

def download_bangla_model():
    """Download the Qwen2.5:3b model for Bangla language support"""
    print("Starting download of Qwen2.5:3b model for Bangla language support...")
    
    # Initialize the downloader
    downloader = HFDownloader()
    
    # Model details
    model_name = "qwen2.5-3b-bangla"
    repo_id = "Qwen/Qwen2.5-3B"  # Using the base Qwen2.5-3B model
    target_root = Path(__file__).parent / "models"
    
    # Create target directory
    target_root.mkdir(parents=True, exist_ok=True)
    
    # Start download
    print(f"Downloading model: {model_name}")
    print(f"Repository ID: {repo_id}")
    print(f"Target directory: {target_root}")
    
    result = downloader.start(
        model_name=model_name,
        repo_id=repo_id,
        target_root=target_root
    )
    
    print(f"Download started with result: {result}")
    
    # Monitor download progress
    import time
    while True:
        status = downloader.status(model_name)
        print(f"Download status: {status}")
        
        # Check if download is finished
        if status.get("status") in ["finished", "error"]:
            break
            
        time.sleep(5)  # Check every 5 seconds
    
    print("Download process completed.")
    return status

if __name__ == "__main__":
    download_bangla_model()