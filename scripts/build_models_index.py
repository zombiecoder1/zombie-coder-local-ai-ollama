#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build models index JSON for the ZombieCoder Provider Ecosystem
"""

import json
import os
from pathlib import Path

def build_models_index():
    """Scan models directory and build index JSON"""
    base_dir = Path.cwd()
    models_dir = base_dir / "models"
    registry_dir = base_dir / "registry"
    
    # Create registry directory if it doesn't exist
    registry_dir.mkdir(exist_ok=True)
    
    # Scan for GGUF models
    models_index = {
        "models": []
    }
    
    if models_dir.exists():
        for model_folder in models_dir.iterdir():
            if model_folder.is_dir():
                # Look for GGUF files in the model folder
                gguf_files = list(model_folder.glob("*.gguf"))
                
                for gguf_file in gguf_files:
                    model_info = {
                        "name": model_folder.name,
                        "path": str(gguf_file.relative_to(base_dir)),
                        "size_bytes": gguf_file.stat().st_size,
                        "status": "unloaded",
                        "keep_loaded": True
                    }
                    models_index["models"].append(model_info)
    
    # Save the models index
    index_file = registry_dir / "models_index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(models_index, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Models index saved to: {index_file}")
    print(f"Found {len(models_index['models'])} models")
    
    # Print model details
    for model in models_index["models"]:
        print(f"  - {model['name']}: {model['path']} ({model['size_bytes']} bytes)")
    
    return models_index

if __name__ == "__main__":
    build_models_index()