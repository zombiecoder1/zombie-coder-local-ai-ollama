#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Local AI - HuggingFace Models API
Real-time model discovery from HuggingFace Hub
"""

from typing import Optional, List, Dict
from huggingface_hub import HfApi, list_models
from huggingface_hub.hf_api import ModelInfo


class HuggingFaceModelsAPI:
    """API for discovering models from HuggingFace Hub"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.api = HfApi(token=token) if token else HfApi()
    
    def search_gguf_models(
        self,
        search: str = "GGUF",
        limit: int = 25,
        sort: str = "downloads",
        author: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for GGUF models on HuggingFace
        
        Args:
            search: Search query
            limit: Maximum results
            sort: Sort by (downloads, likes, trending, updated)
            author: Filter by author (e.g., "TheBloke")
        
        Returns:
            List of model info dicts
        """
        try:
            models = list_models(
                search=search,
                limit=limit,
                sort=sort,
                author=author,
                token=self.token
            )
            
            results = []
            for model in models:
                # Filter for GGUF models
                if any(tag in model.tags for tag in ['gguf', 'GGUF']) or 'GGUF' in model.modelId.upper():
                    results.append({
                        "model_id": model.modelId,
                        "author": model.author,
                        "model_name": model.modelId.split('/')[-1],
                        "downloads": getattr(model, 'downloads', 0),
                        "likes": getattr(model, 'likes', 0),
                        "tags": model.tags,
                        "last_modified": str(model.lastModified) if hasattr(model, 'lastModified') else None,
                        "private": getattr(model, 'private', False)
                    })
            
            return results
        
        except Exception as e:
            return {"error": str(e), "models": []}
    
    def get_model_files(self, repo_id: str) -> List[Dict]:
        """
        Get all files from a model repository
        
        Args:
            repo_id: HuggingFace repo ID
        
        Returns:
            List of file info dicts
        """
        try:
            files = self.api.list_repo_files(repo_id=repo_id)
            
            # Filter and categorize files
            result = {
                "gguf_files": [],
                "safetensors_files": [],
                "other_files": []
            }
            
            for file in files:
                file_info = {
                    "filename": file,
                    "size": None  # Size not available from list_repo_files
                }
                
                if file.endswith('.gguf'):
                    result["gguf_files"].append(file_info)
                elif file.endswith('.safetensors'):
                    result["safetensors_files"].append(file_info)
                else:
                    result["other_files"].append(file_info)
            
            return result
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_popular_gguf_models(self, limit: int = 10) -> List[Dict]:
        """Get popular GGUF models (pre-curated list + dynamic)"""
        
        # Curated popular models
        popular = [
            {"author": "TheBloke", "search": "TinyLlama GGUF"},
            {"author": "TheBloke", "search": "phi-2 GGUF"},
            {"author": "bartowski", "search": "Llama-3.2 GGUF"},
            {"author": "TheBloke", "search": "Mistral GGUF"},
            {"author": "Qwen", "search": "Qwen2.5 GGUF"},
        ]
        
        results = []
        for item in popular[:limit]:
            try:
                models = self.search_gguf_models(
                    search=item["search"],
                    author=item["author"],
                    limit=3
                )
                if isinstance(models, list):
                    results.extend(models[:1])  # Take top 1 from each search
            except:
                pass
        
        return results[:limit]
    
    def search_by_size(self, max_size_gb: float = 3.0) -> List[Dict]:
        """Search for small GGUF models suitable for low-end hardware"""
        
        # Keywords for small models
        small_model_keywords = [
            "TinyLlama GGUF Q2",
            "TinyLlama GGUF Q4",
            "phi-2 GGUF Q4",
            "Qwen-1.5B GGUF"
        ]
        
        results = []
        for keyword in small_model_keywords:
            models = self.search_gguf_models(search=keyword, limit=5)
            if isinstance(models, list):
                results.extend(models)
        
        return results[:10]


if __name__ == "__main__":
    # Test HuggingFace Models API
    api = HuggingFaceModelsAPI()
    
    print("🔍 Searching for GGUF models...")
    models = api.search_gguf_models(search="TinyLlama GGUF", limit=5)
    
    print(f"\n✅ Found {len(models)} models:")
    for i, model in enumerate(models, 1):
        print(f"\n{i}. {model['model_id']}")
        print(f"   Downloads: {model.get('downloads', 'N/A')}")
        print(f"   Likes: {model.get('likes', 'N/A')}")
    
    if models:
        print(f"\n📂 Getting files for {models[0]['model_id']}...")
        files = api.get_model_files(models[0]['model_id'])
        print(f"   GGUF files: {len(files.get('gguf_files', []))}")
        if files.get('gguf_files'):
            for f in files['gguf_files'][:3]:
                print(f"   - {f['filename']}")

