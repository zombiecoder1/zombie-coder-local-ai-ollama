#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Local AI - Model Registry Manager
Manages model_registry.json for installed and available models
"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class ModelRegistry:
    """Manage model registry JSON file"""
    
    def __init__(self, registry_path: str = "models/model_registry.json"):
        self.registry_path = Path(registry_path)
        self.ensure_registry()
    
    def ensure_registry(self):
        """Create registry file if it doesn't exist"""
        if not self.registry_path.exists():
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            default_registry = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "models": {},
                "available": {}
            }
            self.save(default_registry)
    
    def load(self) -> Dict:
        """Load registry from file"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "models": {},
                "available": {}
            }
    
    def save(self, data: Dict):
        """Save registry to file"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_installed_model(
        self,
        model_name: str,
        repo_id: str,
        filename: str,
        location: str,
        size_mb: float,
        format: str = "gguf"
    ):
        """Add or update an installed model"""
        registry = self.load()
        
        registry["models"][model_name] = {
            "repo_id": repo_id,
            "filename": filename,
            "format": format,
            "status": "installed",
            "location": location,
            "size_mb": size_mb,
            "installed_at": datetime.now().isoformat()
        }
        
        self.save(registry)
    
    def remove_installed_model(self, model_name: str):
        """Remove an installed model from registry"""
        registry = self.load()
        
        if model_name in registry["models"]:
            del registry["models"][model_name]
            self.save(registry)
    
    def get_installed_model(self, model_name: str) -> Optional[Dict]:
        """Get info about an installed model"""
        registry = self.load()
        return registry["models"].get(model_name)
    
    def list_installed_models(self) -> Dict:
        """List all installed models"""
        registry = self.load()
        return registry["models"]
    
    def add_available_model(
        self,
        model_name: str,
        repo_id: str,
        filename: str,
        size_estimate_mb: int,
        description: str,
        format: str = "gguf"
    ):
        """Add a model to available list"""
        registry = self.load()
        
        if "available" not in registry:
            registry["available"] = {}
        
        registry["available"][model_name] = {
            "repo_id": repo_id,
            "filename": filename,
            "format": format,
            "status": "available",
            "size_estimate_mb": size_estimate_mb,
            "description": description
        }
        
        self.save(registry)
    
    def list_available_models(self) -> Dict:
        """List all available models"""
        registry = self.load()
        return registry.get("available", {})
    
    def is_gguf_format(self, filename: str) -> bool:
        """Check if file is GGUF format"""
        return filename.lower().endswith('.gguf')
    
    def validate_model_format(self, model_path: Path) -> Dict:
        """
        Validate model format and return info
        
        Returns:
            Dict with format info and validation status
        """
        gguf_files = list(model_path.glob("*.gguf"))
        safetensor_files = list(model_path.glob("*.safetensors"))
        
        if gguf_files:
            return {
                "format": "gguf",
                "valid": True,
                "files": [f.name for f in gguf_files],
                "message": "GGUF format detected - compatible with llama.cpp"
            }
        elif safetensor_files:
            return {
                "format": "safetensors",
                "valid": False,
                "files": [f.name for f in safetensor_files],
                "message": "SafeTensors format detected - NOT compatible with current runtime. Please download GGUF version."
            }
        else:
            return {
                "format": "unknown",
                "valid": False,
                "files": [],
                "message": "No supported model files found"
            }


if __name__ == "__main__":
    # Example usage
    registry = ModelRegistry("../models/model_registry.json")
    
    # Test add installed model
    registry.add_installed_model(
        model_name="test-model",
        repo_id="TheBloke/Test-GGUF",
        filename="test.Q4_K_M.gguf",
        location="./models/test-model/test.Q4_K_M.gguf",
        size_mb=1500.5
    )
    
    print("Installed models:", registry.list_installed_models())

