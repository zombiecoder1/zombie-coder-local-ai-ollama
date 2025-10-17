#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Local AI - Transformers Runner
Python-based runtime for SafeTensors models
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 64
    temperature: float = 0.8
    top_p: float = 0.95
    stream: bool = False


class TransformersRunner:
    """Run SafeTensors models using transformers library"""
    
    def __init__(self, model_path: str, device: str = "auto"):
        self.model_path = Path(model_path)
        self.device = device
        self.model = None
        self.tokenizer = None
        self.generator = None
        
        print(f"🔄 Loading model from: {self.model_path}")
        self._load_model()
    
    def _load_model(self):
        """Load model and tokenizer"""
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_path),
                local_files_only=True,
                trust_remote_code=True
            )
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                str(self.model_path),
                local_files_only=True,
                trust_remote_code=True,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map=self.device,
                low_cpu_mem_usage=True
            )
            
            # Create generator
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map=self.device
            )
            
            print(f"✅ Model loaded successfully")
            print(f"   Device: {self.device}")
            print(f"   Model size: {self.model.num_parameters() / 1e9:.2f}B parameters")
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 64,
        temperature: float = 0.8,
        top_p: float = 0.95
    ) -> str:
        """Generate text"""
        try:
            result = self.generator(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                return_full_text=False
            )
            
            return result[0]['generated_text']
            
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            return f"Error: {str(e)}"


def create_server(runner: TransformersRunner, port: int = 8080):
    """Create FastAPI server for transformers runner"""
    
    app = FastAPI(title="Transformers Runner")
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "runtime": "transformers",
            "model": str(runner.model_path.name)
        }
    
    @app.post("/completion")
    async def completion(req: GenerateRequest):
        """Generate completion (llama.cpp compatible endpoint)"""
        generated = runner.generate(
            prompt=req.prompt,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            top_p=req.top_p
        )
        
        return {
            "content": generated,
            "stop": True,
            "model": str(runner.model_path.name),
            "tokens_predicted": req.max_tokens,
            "tokens_evaluated": len(runner.tokenizer.encode(req.prompt))
        }
    
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transformers Runner")
    parser.add_argument("--model", "-m", required=True, help="Path to model directory")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Server port")
    parser.add_argument("--device", "-d", default="auto", help="Device (auto/cpu/cuda)")
    
    args = parser.parse_args()
    
    # Create runner
    runner = TransformersRunner(args.model, device=args.device)
    
    # Create and run server
    app = create_server(runner, args.port)
    
    print(f"\n🚀 Starting Transformers Runner on port {args.port}")
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="info")

