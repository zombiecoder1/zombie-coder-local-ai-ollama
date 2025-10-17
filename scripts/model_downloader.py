#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Local AI - GGUF Model Downloader
Downloads GGUF models from HuggingFace Hub
"""

import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download, login
from typing import Optional, Dict
import json


def download_model(repo_id: str, filename: str, dest_dir: str = "./models", token: Optional[str] = None) -> Dict:
    """
    Download GGUF model from HuggingFace Hub
    
    Args:
        repo_id: HuggingFace repo ID (e.g., "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF")
        filename: GGUF filename (e.g., "tinyllama-1.1b-chat-v1.0.Q2_K.gguf")
        dest_dir: Destination directory
        token: HuggingFace token (optional)
    
    Returns:
        Dict with download info
    """
    try:
        # Login if token provided
        if token:
            login(token=token)
        
        # Create destination directory
        os.makedirs(dest_dir, exist_ok=True)
        
        print(f"🔄 Downloading: {repo_id}/{filename}")
        print(f"📂 Destination: {dest_dir}")
        
        # Download file
        file_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=dest_dir,
            local_dir_use_symlinks=False
        )
        
        print(f"✅ Downloaded: {file_path}")
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return {
            "status": "success",
            "repo_id": repo_id,
            "filename": filename,
            "file_path": file_path,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return {
            "status": "failed",
            "repo_id": repo_id,
            "filename": filename,
            "error": str(e)
        }


def get_gguf_files(repo_id: str, token: Optional[str] = None) -> list:
    """
    List all GGUF files in a HuggingFace repo
    
    Args:
        repo_id: HuggingFace repo ID
        token: HuggingFace token (optional)
    
    Returns:
        List of GGUF filenames
    """
    try:
        from huggingface_hub import list_repo_files
        
        if token:
            login(token=token)
        
        files = list_repo_files(repo_id=repo_id)
        gguf_files = [f for f in files if f.endswith('.gguf')]
        
        return gguf_files
        
    except Exception as e:
        print(f"❌ Failed to list files: {e}")
        return []


if __name__ == "__main__":
    # Example: Download TinyLlama GGUF
    if len(sys.argv) > 2:
        repo_id = sys.argv[1]
        filename = sys.argv[2]
        dest_dir = sys.argv[3] if len(sys.argv) > 3 else "./models"
    else:
        # Default example
        repo_id = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
        filename = "tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
        dest_dir = "./models"
    
    result = download_model(repo_id, filename, dest_dir)
    print(json.dumps(result, indent=2))

