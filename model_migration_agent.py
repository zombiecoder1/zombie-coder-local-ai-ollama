#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Model Migration Agent
Automated model directory scanning, analysis, and migration assistant
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

class ModelMigrationAgent:
    def __init__(self):
        """Initialize the agent with the current working directory as base"""
        self.base_dir = Path.cwd()
        self.models_dir = self.base_dir / "models"
        self.found_models = []
        self.incompatible_models = []
        self.low_power_models = []
        self.safe_to_delete = []
        self.recommended_model = None
        
    def scan_model_directory(self) -> Dict[str, Any]:
        """Step 1: Scan the model directory automatically"""
        print("🔍 Scanning model directory...")
        
        if not self.models_dir.exists():
            print(f"❌ Models directory not found at {self.models_dir}")
            return {
                "found_models": [],
                "incompatible": [],
                "low_power": [],
                "safe_to_delete": []
            }
        
        print(f"✅ Found models directory at {self.models_dir}")
        
        # Scan all subdirectories in models folder
        for item in self.models_dir.iterdir():
            if item.is_dir():
                model_info = self._analyze_model_directory(item)
                if model_info:
                    self.found_models.append(model_info)
        
        # Also check for loose .gguf or .safetensors files
        for pattern in ["*.gguf", "*.safetensors"]:
            for file in self.models_dir.glob(pattern):
                model_info = {
                    "name": file.name,
                    "path": str(file),
                    "format": "gguf" if file.suffix == ".gguf" else "safetensors",
                    "size_mb": file.stat().st_size / (1024 * 1024),
                    "type": "standalone_file"
                }
                self.found_models.append(model_info)
        
        print(f"📊 Found {len(self.found_models)} models/directories")
        return {
            "found_models": self.found_models,
            "incompatible": self.incompatible_models,
            "low_power": self.low_power_models,
            "safe_to_delete": self.safe_to_delete
        }
    
    def _analyze_model_directory(self, model_dir: Path) -> Dict[str, Any]:
        """Analyze a single model directory"""
        model_info = {
            "name": model_dir.name,
            "path": str(model_dir),
            "gguf_files": [],
            "safetensors_files": [],
            "size_mb": 0,
            "format": "unknown"
        }
        
        # Check for GGUF files
        gguf_files = list(model_dir.glob("*.gguf"))
        model_info["gguf_files"] = [str(f.name) for f in gguf_files]
        
        # Check for safetensors files
        safetensors_files = list(model_dir.glob("*.safetensors"))
        model_info["safetensors_files"] = [str(f.name) for f in safetensors_files]
        
        # Calculate total size
        total_size = 0
        file_count = 0
        for file in model_dir.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
                file_count += 1
        
        model_info["size_mb"] = total_size / (1024 * 1024)
        model_info["file_count"] = file_count
        
        # Determine format
        if gguf_files:
            model_info["format"] = "gguf"
        elif safetensors_files:
            model_info["format"] = "safetensors"
        else:
            model_info["format"] = "unknown"
        
        # Check for model-info.json or config.json
        metadata_files = []
        for meta_file in ["model-info.json", "config.json"]:
            meta_path = model_dir / meta_file
            if meta_path.exists():
                metadata_files.append(meta_file)
        model_info["metadata_files"] = metadata_files
        
        # Categorize model
        if model_info["format"] == "safetensors":
            self.incompatible_models.append(model_info["name"])
            self.safe_to_delete.append(model_info["name"])
        elif "0.5b" in model_info["name"].lower() or "tiny" in model_info["name"].lower():
            self.low_power_models.append(model_info["name"])
            self.safe_to_delete.append(model_info["name"])
        
        return model_info
    
    def recommend_new_model(self) -> Dict[str, Any]:
        """Step 3: Recommend new model installation"""
        print("💡 Recommending new model...")
        
        # Determine save location
        target_dir = self.models_dir / "qwen2.5-7b-instruct-gguf"
        
        recommendation = {
            "recommended_model": "Qwen2.5-7B-Instruct-GGUF",
            "download_url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF",
            "target_save_location": str(target_dir),
            "quant_choice": "Q4_K_M",
            "estimated_size_gb": "4.5-6",
            "download_command": f"huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF --local-dir {target_dir} --local-dir-use-symlinks False"
        }
        
        self.recommended_model = recommendation
        return recommendation
    
    def suggest_config_updates(self) -> Dict[str, Any]:
        """Step 4: Suggest config updates"""
        print("⚙️  Suggesting config updates...")
        
        # Find the recommended model path
        model_path = ""
        if self.recommended_model:
            model_path = f"{self.recommended_model['target_save_location']}/qwen2.5-7b-instruct-q4_k_m.gguf"
        
        config_suggestion = {
            "update_config": {
                "model_path": model_path,
                "context": 4096,
                "gpu_layers": "auto",
                "lazyload": True,
                "low_vram": True
            }
        }
        
        return config_suggestion
    
    def prepare_safe_delete_list(self) -> Dict[str, List[str]]:
        """Step 7: Prepare safe-to-delete list"""
        print("🗑️  Preparing safe-to-delete list...")
        
        return {
            "safe_to_delete": self.safe_to_delete
        }
    
    def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics"""
        print("📋 Running diagnostics...")
        
        # Scan models
        scan_results = self.scan_model_directory()
        
        # Recommend new model
        recommendation = self.recommend_new_model()
        
        # Suggest config updates
        config_updates = self.suggest_config_updates()
        
        # Prepare safe delete list
        delete_list = self.prepare_safe_delete_list()
        
        # Compile full report
        report = {
            "scan_results": scan_results,
            "recommendation": recommendation,
            "config_updates": config_updates,
            "delete_list": delete_list
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any]) -> str:
        """Save the report to a JSON file"""
        report_file = self.base_dir / "model_migration_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return str(report_file)
    
    def main(self):
        """Main execution function"""
        print("🤖 ZombieCoder Model Migration Agent")
        print("=" * 50)
        
        # Run diagnostics
        report = self.run_diagnostics()
        
        # Save report
        report_path = self.save_report(report)
        print(f"✅ Report saved to {report_path}")
        
        # Print summary
        print("\n📋 Summary:")
        print(f"  Found models: {len(report['scan_results']['found_models'])}")
        print(f"  Incompatible models: {len(report['scan_results']['incompatible'])}")
        print(f"  Low-power models: {len(report['scan_results']['low_power'])}")
        print(f"  Safe to delete: {len(report['delete_list']['safe_to_delete'])}")
        print(f"  Recommended model: {report['recommendation']['recommended_model']}")
        
        return report

if __name__ == "__main__":
    agent = ModelMigrationAgent()
    agent.main()