#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Local AI Framework - Minimal Server (per plan.md)
Role: API Gateway + Static UI
Port: 8001 (API Gateway)
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
import time
import requests

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from system_detector import detect_system_info
from db_manager import load_registry, save_registry, scan_models_directory
from router import (
    get_status as runtime_status,
    load_model as runtime_load,
    unload_model as runtime_unload,
    check_runtime_available,
    start_idle_killer,
    stop_all_running,
    mark_access,
)
from downloader import DOWNLOADER as DL
from pydantic import BaseModel
from runtime_db import upsert_model_state, delete_model_state, get_all_states
import requests as httpx
import threading
import os


ROOT_DIR = Path(__file__).parent
MODELS_DIR = Path(os.getenv("MODELS_DIR", str(ROOT_DIR / "models")))
REGISTRY_FILE = MODELS_DIR / "models_registry.json"
PORT = int(os.getenv("MODEL_SERVER_PORT", 8155))  # uncommon default port
START_TIME = time.time()
DB_PATH = ROOT_DIR / "data" / "runtime.db"

# Provider meta (from user)
PROVIDER_INFO = {
    "product": "ZombieCoder Local AI",
    "tagline": "যেখানে কোড ও কথা বলে",
    "owner": "Sahon Srabon",
    "company": "Developer Zone",
    "contact": "+880 1323-626282",
    "address": "235 south pirarbag, Amtala Bazar, Mirpur -60 feet",
    "planning_ideals": "chatgpt",
    "website": "https://zombiecoder.my.id/",
    "email": "infi@zombiecoder.my.id",
}


def ensure_models_dir() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title="ZombieCoder Local AI Framework",
    description="Lightweight, lazy-load ready local AI server (skeleton)",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],   # Allow all headers
)

# Static UI
static_dir = ROOT_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Simple in-memory + file request log (real events)
REQUEST_LOG: deque = deque(maxlen=200)
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
SERVER_LOG = LOG_DIR / "server.log"


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        t0 = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - t0) * 1000)
        try:
            REQUEST_LOG.append({
                "ts": datetime.now().isoformat(),
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
            })
            # Append JSON line to file log
            with open(SERVER_LOG, "a", encoding="utf-8", errors="ignore") as lf:
                lf.write(
                    f"{datetime.now().isoformat()}\t{request.method}\t{request.url.path}\t{response.status_code}\t{duration_ms}ms\n"
                )
        except Exception:
            pass
        return response


app.add_middleware(RequestLoggerMiddleware)


@app.on_event("startup")
async def on_startup():
    ensure_models_dir()
    scanned = scan_models_directory(MODELS_DIR)
    registry = load_registry(REGISTRY_FILE)
    registry["models"] = scanned
    registry["last_updated"] = datetime.now().isoformat()
    save_registry(REGISTRY_FILE, registry)
    # Start idle killer (10 minutes)
    start_idle_killer(timeout_sec=600, check_interval_sec=30)
    # Kick off background auto-download of smallest GGUF if missing
    def _auto_download_worker():
        try:
            model_dir = MODELS_DIR / "qwen0_5b"
            need = True
            if model_dir.exists():
                ggufs = list(model_dir.glob("*.gguf"))
                if ggufs:
                    need = False
            if need:
                try:
                    DL.start("qwen0_5b", "Qwen/Qwen-0.5B-Chat-GGUF", MODELS_DIR)
                except Exception:
                    return
            # Poll a short while to refresh registry if download is quick
            t0 = time.time()
            while time.time() - t0 < 120:
                try:
                    status = DL.status("qwen0_5b")
                    if isinstance(status, dict) and status.get("state") in ("done", "error", "cancelled"):
                        break
                except Exception:
                    break
                time.sleep(2)
            # refresh registry
            scanned2 = scan_models_directory(MODELS_DIR)
            reg2 = load_registry(REGISTRY_FILE)
            reg2["models"] = scanned2
            reg2["last_updated"] = datetime.now().isoformat()
            save_registry(REGISTRY_FILE, reg2)
        except Exception:
            pass

    threading.Thread(target=_auto_download_worker, daemon=True).start()


@app.get("/", response_class=HTMLResponse)
async def root():
    index_file = static_dir / "allindex.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>ZombieCoder Local AI Framework</h1><p>UI not found.</p>")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ZombieCoder Local AI Framework",
        "version": "0.1.0",
        "models_dir": str(MODELS_DIR),
        "port": PORT,
        "timestamp": datetime.now().isoformat(),
        "uptime_sec": int(time.time() - START_TIME),
    }


@app.get("/system/info")
async def system_info():
    return detect_system_info()


@app.get("/models/installed")
async def models_installed():
    registry = load_registry(REGISTRY_FILE)
    scanned = scan_models_directory(MODELS_DIR)
    registry["models"] = scanned
    save_registry(REGISTRY_FILE, registry)
    total_size_mb = sum(m.get("size_mb", 0.0) for m in scanned)
    return {"models": scanned, "count": len(scanned), "total_size_mb": total_size_mb}


# Recommended/available models (curated minimal set) and compatibility
MODELS_DATABASE = {
    "entry_level": [
        {
            "name": "TinyLlama-1.1B",
            "size": "1.1B",
            "ram_required": "2-3 GB",
            "vram_required": "Optional",
            "description": "সবচেয়ে হালকা, সাধারণ টেক্সট ও চ্যাট",
            "huggingface_id": "TheBloke/TinyLlama-1.1B-Chat-GGUF",
            "recommended": True,
            "compatibility": "recommended",
        },
        {
            "name": "Phi-2",
            "size": "2.7B",
            "ram_required": "3-4 GB",
            "vram_required": "Optional",
            "description": "কোডিং ও সাধারণ কাজের জন্য",
            "huggingface_id": "microsoft/phi-2",
            "recommended": True,
            "compatibility": "recommended",
        },
    ],
    "mid_range": [
        {
            "name": "Llama-3.2-3B",
            "size": "3B",
            "ram_required": "4-6 GB",
            "vram_required": "Optional",
            "description": "General purpose",
            "huggingface_id": "meta-llama/Llama-3.2-3B-Instruct",
            "recommended": True,
            "compatibility": "recommended",
        }
    ],
}


@app.get("/models/available")
async def models_available():
    sys = detect_system_info()
    tier = sys.get("tier", "entry_level")
    tier_order = ["entry_level", "mid_range", "good", "high_end", "enthusiast"]
    current_idx = tier_order.index(tier) if tier in tier_order else 0

    all_models: list[dict] = []
    for idx, t in enumerate(tier_order):
        for m in MODELS_DATABASE.get(t, []):
            mc = dict(m)
            if idx <= current_idx:
                mc["compatibility"] = "recommended"
                mc["recommended"] = True
            elif idx == current_idx + 1:
                mc["compatibility"] = "compatible"
                mc["recommended"] = False
            else:
                mc["compatibility"] = "not_recommended"
                mc["recommended"] = False
            all_models.append(mc)
    return all_models


# Monitoring / Performance / Provider / Logs endpoints

@app.get("/monitoring/summary")
async def monitoring_summary():
    registry = load_registry(REGISTRY_FILE)
    sysinfo = detect_system_info()
    return {
        "uptime_sec": int(time.time() - START_TIME),
        "system": sysinfo,
        "models_indexed": len(registry.get("models", [])),
        "runtime": runtime_status(),
    }


@app.get("/performance/snapshot")
async def performance_snapshot():
    import psutil
    cpu_percent = psutil.cpu_percent(interval=0.2)
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage(str(Path.cwd().anchor))
    net = psutil.net_io_counters()
    proc = psutil.Process()
    with proc.oneshot():
        mem_info = proc.memory_info()
        num_threads = proc.num_threads()
        open_files = len(proc.open_files()) if hasattr(proc, 'open_files') else None
    return {
        "cpu_percent": cpu_percent,
        "memory": {
            "total_gb": round(vm.total / 1024**3, 2),
            "used_gb": round(vm.used / 1024**3, 2),
            "percent": vm.percent,
        },
        "disk": {
            "total_gb": round(disk.total / 1024**3, 2),
            "used_gb": round(disk.used / 1024**3, 2),
            "percent": disk.percent,
        },
        "network": {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
        },
        "process": {
            "rss_mb": round(mem_info.rss / 1024**2, 1),
            "threads": num_threads,
            "open_files": open_files,
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/provider/about")
async def provider_about():
    return PROVIDER_INFO


@app.get("/logs/recent")
async def logs_recent():
    return {"events": list(REQUEST_LOG)}


@app.get("/logs/server")
async def logs_server(limit: int = 200):
    try:
        lines = SERVER_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
        return {"path": str(SERVER_LOG), "tail": lines[-limit:]}
    except FileNotFoundError:
        return {"path": str(SERVER_LOG), "tail": []}


# ------------------------
# Downloader endpoints
# ------------------------

class DownloadRequest(BaseModel):
    model_name: str
    repo_id: str
    revision: str | None = None


@app.post("/download/start")
async def download_start(req: DownloadRequest):
    return DL.start(req.model_name, req.repo_id, MODELS_DIR, revision=req.revision)


@app.get("/download/status/{model}")
async def download_status(model: str):
    return DL.status(model)


@app.post("/download/cancel/{model}")
async def download_cancel(model: str):
    return DL.cancel(model)


# ------------------------
# HuggingFace Auth endpoints
# ------------------------

class HFToken(BaseModel):
    token: str


@app.post("/auth/hf_token")
async def set_hf_token(t: HFToken):
    # Store in environment so downloader subprocess and hub API can use it
    os.environ["HUGGINGFACE_HUB_TOKEN"] = t.token.strip()
    os.environ["HF_TOKEN"] = t.token.strip()
    return {"ok": True, "token_set": True}


@app.get("/auth/status")
async def auth_status():
    token_present = bool(os.getenv("HUGGINGFACE_HUB_TOKEN") or os.getenv("HF_TOKEN"))
    return {"token_set": token_present}


# Runtime control (lazy-loader stubs)

@app.get("/runtime/status")
async def runtime_get_status():
    status = runtime_status()
    # merge with persisted states (for unloaded models info)
    persisted = get_all_states(DB_PATH)
    status["persisted"] = persisted
    return status


@app.post("/runtime/load/{model}")
async def runtime_load_model(model: str, threads: int = 4):
    # Resolve model path (restrict to GGUF to avoid incompatible formats)
    model_dir = MODELS_DIR / model
    model_path = None
    candidates = list(model_dir.glob("*.gguf"))
    if candidates:
        model_path = candidates[0]
    if not model_path:
        raise HTTPException(status_code=404, detail=f"GGUF weights not found under {model_dir}")
    res = runtime_load(ROOT_DIR, model, model_path, threads=threads)
    try:
        upsert_model_state(DB_PATH, model, res.get("status","unknown"), res.get("port"), res.get("pid"))
    except Exception:
        pass
    return res


@app.post("/runtime/unload/{model}")
async def runtime_unload_model(model: str):
    res = runtime_unload(model)
    try:
        upsert_model_state(DB_PATH, model, res.get("status","stopped"), None, None)
    except Exception:
        pass
    return res


@app.get("/runtime/config")
async def runtime_config():
    return check_runtime_available(ROOT_DIR)


# Ollama-compatible minimal endpoints (placeholders)

@app.get("/api/tags")
async def api_tags():
    """Return installed models in Ollama-like shape."""
    scanned = scan_models_directory(MODELS_DIR)
    rt = runtime_status()
    models_list: List[Dict] = []
    for m in scanned:
        name = m["name"]
        # determine format and quantization
        fmt = "gguf" if any(str(name).lower().endswith(".gguf") for name in []) else (
            "gguf" if any(str(p).lower().endswith(".gguf") for p in []) else ("safetensors" if any(str(name).lower().endswith(".safetensors") for name in []) else "unknown")
        )
        # parse quant from any gguf filename under folder
        quant = "N/A"
        model_dir = MODELS_DIR / name
        ggufs = list(model_dir.glob("*.gguf"))
        if ggufs:
            fname = ggufs[0].name
            parts = fname.split("-")
            for p in parts:
                if p.lower().startswith("q") and any(ch.isdigit() for ch in p):
                    quant = p
                    break
            fmt = "gguf"
        elif list(model_dir.glob("*.safetensors")):
            fmt = "safetensors"

        # runtime status
        rstatus = "stopped"
        for rm in rt.get("models", []):
            if rm.get("model") == name:
                rstatus = rm.get("status", "stopped")
                break

        models_list.append({
            "name": name,
            "model": name,
            "modified_at": m.get("detected_at", datetime.now().isoformat()),
            "size": int(m.get("size_mb", 0) * 1024 * 1024),
            "digest": "local",
            "status": "installed",
            "runtime_status": rstatus,
            "format": fmt,
            "quantization": quant,
            "details": {
                "parent_model": "",
                "format": fmt,
                "family": "unknown",
                "families": ["unknown"],
                "parameter_size": "unknown",
                "quantization_level": quant,
            },
        })
    return {"models": models_list}


class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: bool = False
    options: Optional[Dict] = None
    session_id: Optional[str] = None
    system: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 100
    stream: bool = False
    options: Optional[Dict] = None


@app.post("/api/generate")
async def api_generate(req: GenerateRequest):
    # Verify installed
    scanned = scan_models_directory(MODELS_DIR)
    if not any(m["name"] == req.model for m in scanned):
        raise HTTPException(status_code=404, detail=f"Model '{req.model}' not found")
    # Find running port for this model
    rt = runtime_status()
    port = None
    for m in rt.get("models", []):
        if m.get("model") == req.model and m.get("status") == "ready":
            port = m.get("port")
            break
    if not port:
        raise HTTPException(status_code=409, detail="Model is not running. Load it via /runtime/load/{model} first.")
    # Proxy to llama.cpp server completion endpoint
    try:
        url = f"http://127.0.0.1:{port}/completion"
        # Build prompt with system context if provided
        system_prompt = req.system or """You are ZombieCoder Local AI Assistant, powered by local models running on user's own machine. 
Provider: ZombieCoder Local AI Framework
Location: Running locally on user's computer (C:\\model)
Cost: Free - 100% offline, no API costs
You are here to help users with coding, questions, and tasks."""
        
        full_prompt = f"{system_prompt}\n\nUser: {req.prompt}\nAssistant:"
        # Force non-streaming single JSON response and limit tokens for low latency
        payload = {"prompt": full_prompt, "stream": False, "n_predict": 64}
        # Try up to ~60s to allow runtime to finish loading the model
        deadline = time.time() + 60
        last_resp = None
        while True:
            r = httpx.post(url, json=payload, timeout=180)
            last_resp = r
            if r.status_code == 200:
                break
            # llama.cpp may return 503 while still "Loading model"
            if r.status_code == 503 and ("Loading model" in r.text or "loading" in r.text.lower()):
                if time.time() < deadline:
                    time.sleep(1.0)
                    continue
            # Any other non-200 or timeout → error
            raise HTTPException(status_code=502, detail=f"Runtime error {r.status_code}: {r.text[:200]}")
        data = last_resp.json() if last_resp is not None else {}
        # mark last access for idle killer
        try:
            mark_access(req.model)
        except Exception:
            pass
        # update session if provided
        sid = req.session_id or (req.options or {}).get("session_id") if req.options else None
        if sid:
            _session_touch(sid, last_model=req.model)
        return {"model": req.model, "runtime_port": port, "runtime_response": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Proxy error: {e}")


# Simple in-memory sessions
SESSIONS: Dict[str, Dict] = {}


def _session_touch(session_id: str, last_model: Optional[str] = None) -> None:
    now = datetime.now().isoformat()
    s = SESSIONS.get(session_id) or {"session_id": session_id, "created_at": now}
    s["last_seen_at"] = now
    if last_model:
        s["last_model"] = last_model
    SESSIONS[session_id] = s


class StartSessionRequest(BaseModel):
    session_id: Optional[str] = None


@app.post("/api/session/start")
async def api_session_start(req: StartSessionRequest):
    sid = req.session_id or f"sess-{int(time.time())}"
    _session_touch(sid)
    return {"session_id": sid, "status": "active"}


@app.get("/api/session/status/{session_id}")
async def api_session_status(session_id: str):
    s = SESSIONS.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    return {"session": s, "status": "active"}


@app.post("/api/session/end/{session_id}")
async def api_session_end(session_id: str):
    if session_id in SESSIONS:
        SESSIONS.pop(session_id, None)
        return {"session_id": session_id, "status": "ended"}
    return {"session_id": session_id, "status": "not_found"}


@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    scanned = scan_models_directory(MODELS_DIR)
    if not any(m["name"] == req.model for m in scanned):
        raise HTTPException(status_code=404, detail=f"Model '{req.model}' not found")
    
    # Find running port for this model
    rt = runtime_status()
    port = None
    for m in rt.get("models", []):
        if m.get("model") == req.model and m.get("status") == "ready":
            port = m.get("port")
            break
    if not port:
        raise HTTPException(status_code=409, detail="Model is not running. Load it via /runtime/load/{model} first.")
    
    # Convert chat messages to prompt format
    system_prompt = """You are ZombieCoder Local AI Assistant, powered by local models running on user's own machine. 
Provider: ZombieCoder Local AI Framework
Location: Running locally on user's computer (C:\\model)
Cost: Free - 100% offline, no API costs
You are here to help users with coding, questions, and tasks."""
    
    # Build conversation prompt
    conversation = system_prompt + "\n\n"
    for message in req.messages:
        role = message.role
        content = message.content
        if role == "user":
            conversation += f"User: {content}\n"
        elif role == "assistant":
            conversation += f"Assistant: {content}\n"
    
    conversation += "Assistant:"
    
    # Proxy to llama.cpp server completion endpoint
    try:
        url = f"http://127.0.0.1:{port}/completion"
        payload = {
            "prompt": conversation,
            "stream": False,
            "n_predict": req.max_tokens or 100
        }

        # More tolerant waiting with 503 handling like generate()
        deadline = time.time() + 90
        last_resp = None
        while True:
            try:
                resp = requests.post(url, json=payload, timeout=20)
                last_resp = resp
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                    except ValueError:
                        # malformed json; try again until deadline
                        data = None
                    if isinstance(data, dict):
                        # Try several shapes to extract content
                        content = None
                        if isinstance(data.get("content"), str):
                            content = data.get("content")
                        elif isinstance(data.get("choices"), list) and data["choices"]:
                            first = data["choices"][0]
                            if isinstance(first, dict):
                                content = first.get("text") or first.get("content")
                        elif isinstance(data.get("response"), str):
                            content = data.get("response")

                        if isinstance(content, str):
                            return {
                                "model": req.model,
                                "runtime_port": port,
                                "runtime_response": {
                                    "index": 0,
                                    "content": content,
                                },
                            }

                # llama.cpp may return 503 while still loading
                if resp.status_code == 503 and ("loading" in resp.text.lower() or "model" in resp.text.lower()):
                    if time.time() < deadline:
                        time.sleep(1.0)
                        continue
                # For other non-200s, retry until deadline
            except requests.exceptions.RequestException:
                # transient network/timeouts; keep trying until deadline
                pass

            if time.time() > deadline:
                break
            time.sleep(1)

        # If we get here, the model didn't respond successfully in time
        if last_resp is not None:
            raise HTTPException(status_code=500, detail=f"Model runtime error: {last_resp.status_code}")
        raise HTTPException(status_code=500, detail="Model runtime not responding")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    try:
        # ensure idle killer is active on direct run
        start_idle_killer(timeout_sec=600, check_interval_sec=30)
        uvicorn.run("model_server:app", host="0.0.0.0", port=PORT, reload=True, log_level="info")
    finally:
        # graceful shutdown of all runtimes
        try:
            stop_all_running()
        except Exception:
            pass


