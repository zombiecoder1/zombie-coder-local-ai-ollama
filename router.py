#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import socket
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import subprocess
import time
import socket
from system_detector import detect_system_info


class RuntimeState:
    """In-memory runtime state for models (placeholder until real subprocess)."""

    def __init__(self) -> None:
        self.model_to_port: Dict[str, int] = {}
        self.model_to_status: Dict[str, str] = {}  # stopped|loading|ready|error
        self.model_to_pid: Dict[str, int] = {}
        self.model_to_last_access: Dict[str, float] = {}
        self.model_to_runtime: Dict[str, str] = {}  # gguf|safetensors
        self._idle_thread_started: bool = False


STATE = RuntimeState()


def load_runtime_config(root: Path) -> Dict:
    """Load runtime configuration"""
    config_file = root / "config" / "runtime_config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Default config if file doesn't exist
    return {
        "runtime_rules": {
            "gguf": {
                "engine": "llama.cpp",
                "command": "config/llama.cpp/server.exe"
            },
            "safetensors": {
                "engine": "transformers",
                "command": "python"
            }
        }
    }


def detect_model_format(model_path: Path) -> Tuple[str, Optional[Path]]:
    """
    Detect model format and return (format_type, model_file)
    
    Returns:
        ("gguf", gguf_file_path) or ("safetensors", safetensors_dir)
    """
    # Check for GGUF files
    gguf_files = list(model_path.glob("*.gguf"))
    if gguf_files:
        return ("gguf", gguf_files[0])
    
    # Check for SafeTensors files
    safetensors_files = list(model_path.glob("*.safetensors"))
    if safetensors_files:
        return ("safetensors", model_path)
    
    # Check for PyTorch bins
    bin_files = list(model_path.glob("*.bin"))
    if bin_files:
        return ("safetensors", model_path)  # treat as safetensors-compatible
    
    return ("unknown", None)


def find_free_port(start: int = 8080, end: int = 8100) -> Optional[int]:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return None


def llama_server_path(root: Path) -> Path:
    """Resolve llama.cpp HTTP server binary path.
    Prefer 'server(.exe)'; if absent on Windows, try 'llama-server.exe'.
    """
    base = root / "config" / "llama.cpp"
    if os.name == "nt":
        p1 = base / "server.exe"
        if p1.exists():
            return p1
        p2 = base / "llama-server.exe"
        return p2
    else:
        return base / "server"


def check_runtime_available(root: Path) -> Dict:
    path = llama_server_path(root)
    exists = path.exists()
    return {
        "exists": exists,
        "path": str(path),
        "message": None if exists else "llama.cpp server binary not found. Place it at the path above.",
    }


def _port_open(host: str, port: int, timeout_sec: int = 1) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout_sec):
            return True
    except OSError:
        return False


def get_status() -> Dict:
    return {
        "models": [
            {
                "model": m,
                "status": STATE.model_to_status.get(m, "stopped"),
                "port": STATE.model_to_port.get(m),
                "pid": STATE.model_to_pid.get(m),
                "runtime": STATE.model_to_runtime.get(m, "unknown"),
                "last_access_ts": STATE.model_to_last_access.get(m),
            }
            for m in sorted(set(list(STATE.model_to_status.keys()) + list(STATE.model_to_port.keys())))
        ]
    }


def load_model(root: Path, model_name: str, model_path: Path, threads: int = 4) -> Dict:
    """Load model with automatic runtime selection based on format"""
    
    # Detect model format
    format_type, detected_path = detect_model_format(model_path)
    
    if format_type == "unknown":
        return {
            "status": "error",
            "reason": "unsupported_format",
            "message": f"No supported model files found in {model_path}",
            "suggestion": "Model must contain .gguf or .safetensors files"
        }
    
    # Load runtime config
    config = load_runtime_config(root)
    runtime_config = config["runtime_rules"].get(format_type)
    
    if not runtime_config:
        return {
            "status": "error",
            "reason": "no_runtime_config",
            "format": format_type,
            "message": f"No runtime configured for {format_type} format"
        }
    
    port = find_free_port()
    if port is None:
        return {"status": "error", "reason": "no_free_port", "message": "No free port in 8080-8100"}

    # Initialize variables
    gpu_layers = 0
    
    # Build command based on format
    if format_type == "gguf":
        # GGUF - use llama.cpp
        server_bin = llama_server_path(root)
        if not server_bin.exists():
            return {
                "status": "error",
                "reason": "runtime_missing",
                "format": format_type,
                "message": f"llama.cpp server not found at {server_bin}"
            }
        
        # GPU layers heuristic
        sysinfo = detect_system_info()
        vram_mb = sysinfo.get("vram_mb") or 0
        gpu_layers = 0
        if vram_mb >= 6144:
            gpu_layers = 40
        elif vram_mb >= 4096:
            gpu_layers = 28
        elif vram_mb >= 2048:
            gpu_layers = 16
        
        # llama.cpp command variants
        base_a = [str(server_bin), "-m", str(detected_path), "-p", str(port), "-t", str(threads)]
        base_b = [str(server_bin), "--model", str(detected_path), "--port", str(port), "--threads", str(threads)]
        if gpu_layers > 0:
            base_a += ["-ngl", str(gpu_layers)]
            base_b += ["--gpu-layers", str(gpu_layers)]
        cmd_variants = [base_b, base_a]
    
    elif format_type == "safetensors":
        # SafeTensors - use transformers runner
        cmd_variants = [[
            "python",
            str(root / "scripts" / "transformers_runner.py"),
            "--model", str(detected_path),
            "--port", str(port),
            "--device", "auto"
        ]]
    
    else:
        return {
            "status": "error",
            "reason": "unsupported_format",
            "format": format_type
        }
    # Log stdout/stderr to file for diagnostics
    logs_dir = root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    runtime_log = logs_dir / f"runtime_{model_name}.log"
    proc = None
    used_cmd = None
    for cmd in cmd_variants:
        try:
            f = open(runtime_log, "a", encoding="utf-8", errors="ignore")
            f.write(f"# START {time.time()} cmd={' '.join(cmd)}\n")
            proc = subprocess.Popen(
                cmd,
                stdout=f,
                stderr=subprocess.STDOUT,
                creationflags=(subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0),
            )
            used_cmd = cmd
        except FileNotFoundError:
            return {"status": "error", "reason": "bin_not_found", "path": str(server_bin)}
        except Exception as e:
            return {"status": "error", "reason": "spawn_failed", "message": str(e)}
        # Quick check: if exits immediately non-zero, try next variant
        time.sleep(0.8)
        if proc.poll() is not None and proc.returncode != 0:
            f.write(f"# EARLY_EXIT rc={proc.returncode}\n")
            f.flush()
            continue
        break
    if proc is None:
        return {"status": "error", "reason": "spawn_failed", "message": "no command executed"}

    STATE.model_to_port[model_name] = port
    STATE.model_to_pid[model_name] = proc.pid
    STATE.model_to_status[model_name] = "loading"
    STATE.model_to_last_access[model_name] = time.time()
    STATE.model_to_runtime[model_name] = format_type  # Track runtime type

    # Wait briefly for port to open
    t0 = time.time()
    ready = False
    while time.time() - t0 < 20:
        if _port_open("127.0.0.1", port, 1):
            ready = True
            break
        # If process exited early mark error
        if proc.poll() is not None:
            STATE.model_to_status[model_name] = "error"
            return {
                "status": "error",
                "reason": "early_exit",
                "code": proc.returncode,
                "log": str(runtime_log),
            }
        time.sleep(0.5)

    STATE.model_to_status[model_name] = "ready" if ready else "loading"
    
    # Build response
    response = {
        "status": STATE.model_to_status[model_name],
        "model": model_name,
        "port": port,
        "pid": proc.pid,
        "command": " ".join(used_cmd) if used_cmd else None,
        "log": str(runtime_log),
        "format": format_type,
        "runtime": runtime_config.get("engine", "unknown")
    }
    
    # Add GPU layers info for GGUF only
    if format_type == "gguf":
        response["gpu_layers"] = gpu_layers
    
    return response


def unload_model(model_name: str) -> Dict:
    pid = STATE.model_to_pid.get(model_name)
    if not pid:
        STATE.model_to_status[model_name] = "stopped"
        STATE.model_to_port.pop(model_name, None)
        return {"status": "noop", "message": "No PID", "model": model_name}
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
        else:
            os.kill(pid, 15)
    except Exception:
        pass
    STATE.model_to_status[model_name] = "stopped"
    STATE.model_to_port.pop(model_name, None)
    STATE.model_to_pid.pop(model_name, None)
    STATE.model_to_last_access.pop(model_name, None)
    return {"status": "stopped", "model": model_name}
def mark_access(model_name: str) -> None:
    STATE.model_to_last_access[model_name] = time.time()


def _idle_killer_loop(timeout_sec: int = 600, check_interval_sec: int = 30) -> None:
    while True:
        now = time.time()
        try:
            for model, last_ts in list(STATE.model_to_last_access.items()):
                status = STATE.model_to_status.get(model)
                if status != "ready":
                    continue
                if last_ts is None:
                    continue
                if now - last_ts >= timeout_sec:
                    try:
                        unload_model(model)
                    except Exception:
                        pass
        except Exception:
            pass
        time.sleep(check_interval_sec)


def start_idle_killer(timeout_sec: int = 600, check_interval_sec: int = 30) -> None:
    if STATE._idle_thread_started:
        return
    t = subprocess  # placeholder to keep import usage consistent
    import threading
    th = threading.Thread(target=_idle_killer_loop, kwargs={"timeout_sec": timeout_sec, "check_interval_sec": check_interval_sec}, daemon=True)
    th.start()
    STATE._idle_thread_started = True


def stop_all_running() -> None:
    for model, status in list(STATE.model_to_status.items()):
        if status in ("loading", "ready"):
            try:
                unload_model(model)
            except Exception:
                pass



