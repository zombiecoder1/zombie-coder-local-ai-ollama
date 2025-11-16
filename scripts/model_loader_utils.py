#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Loader Utilities for ZombieCoder Provider Ecosystem
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, Any

class ModelLoaderUtils:
    def __init__(self, base_url: str = "http://localhost:8007"):
        """Initialize the model loader utilities"""
        self.base_url = base_url
        self.base_dir = Path.cwd()
        self.registry_dir = self.base_dir / "registry"
        
    def get_models_index(self) -> Dict[str, Any]:
        """Get the current models index"""
        index_file = self.registry_dir / "models_index.json"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"models": []}
    
    def update_models_index(self, models_index: Dict[str, Any]):
        """Update the models index file"""
        index_file = self.registry_dir / "models_index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(models_index, f, indent=2, ensure_ascii=False)
    
    def lazy_load_model(self, model_name: str) -> bool:
        """
        Lazy load a model - if not loaded, auto-load it
        Returns True if model is ready, False if failed
        """
        try:
            # Check if model is already loaded
            response = requests.get(f"{self.base_url}/models/installed")
            if response.status_code == 200:
                installed_models = response.json()
                for model in installed_models:
                    if model.get("model") == model_name and model.get("status") == "ready":
                        print(f"✅ Model {model_name} is already loaded")
                        return True
            
            # Model not loaded, load it
            print(f"🔄 Loading model: {model_name}")
            response = requests.post(f"{self.base_url}/runtime/load/{model_name}")
            if response.status_code == 200:
                print(f"✅ Model {model_name} loaded successfully")
                return True
            else:
                print(f"❌ Failed to load model {model_name}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error loading model {model_name}: {e}")
            return False
    
    def update_model_status(self, model_name: str, status: str):
        """Update model status in the index"""
        models_index = self.get_models_index()
        for model in models_index["models"]:
            if model["name"] == model_name:
                model["status"] = status
                model["last_used_ts"] = time.time()
                break
        self.update_models_index(models_index)
    
    def ensure_model_resident(self, model_name: str):
        """Ensure model stays resident in memory (sleep mode)"""
        # This would be implemented in the server side
        # For now, we just update the status
        self.update_model_status(model_name, "loaded")
        print(f"💤 Model {model_name} set to sleep/resident mode")
    
    def get_provider_endpoints_status(self) -> Dict[str, bool]:
        """Check status of all provider endpoints"""
        endpoints = {
            "/api/tags": False,
            "/api/generate": False,
            "/api/chat": False,
            "/runtime/load/{model}": False,
            "/models/installed": False
        }
        
        try:
            # Test /api/tags
            response = requests.get(f"{self.base_url}/api/tags")
            endpoints["/api/tags"] = response.status_code == 200
            
            # Test /models/installed
            response = requests.get(f"{self.base_url}/models/installed")
            endpoints["/models/installed"] = response.status_code == 200
            
            # Test /runtime/load/{model} (with a simple model)
            response = requests.post(f"{self.base_url}/runtime/load/phi-2")
            endpoints["/runtime/load/{model}"] = response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error testing endpoints: {e}")
        
        return endpoints

def main():
    """Main function for testing"""
    loader = ModelLoaderUtils()
    
    print("🤖 ZombieCoder Model Loader Utilities")
    print("=====================================")
    
    # Check provider endpoints
    print("\n🔍 Checking provider endpoints...")
    endpoints = loader.get_provider_endpoints_status()
    for endpoint, status in endpoints.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {endpoint}")
    
    # Test lazy loading
    print("\n🔄 Testing lazy load...")
    loader.lazy_load_model("phi-2")
    
    print("\n✅ Model loader utilities ready")

if __name__ == "__main__":
    main()