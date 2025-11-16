#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model cleanup script for ZombieCoder Local AI Framework
"""

import os
import shutil
from pathlib import Path

def cleanup_models():
    """Remove all model directories except phi-2 as requested"""
    models_dir = Path(__file__).parent / "models"
    
    if not models_dir.exists():
        print("Models directory not found")
        return
    
    # List of models to keep (phi-2 only)
    keep_models = ["phi-2"]
    
    # Iterate through model directories
    for item in models_dir.iterdir():
        if item.is_dir() and item.name not in keep_models:
            print(f"Removing model directory: {item.name}")
            try:
                shutil.rmtree(item)
                print(f"Successfully removed {item.name}")
            except Exception as e:
                print(f"Error removing {item.name}: {e}")
    
    # Update registry to reflect only kept models
    registry_file = models_dir / "models_registry.json"
    if registry_file.exists():
        import json
        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            # Filter models in registry
            filtered_models = [m for m in registry.get("models", []) if m.get("name") in keep_models]
            registry["models"] = filtered_models
            
            # Save updated registry
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
            
            print("Registry updated to reflect only kept models")
        except Exception as e:
            print(f"Error updating registry: {e}")

if __name__ == "__main__":
    cleanup_models()