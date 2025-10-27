#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
import time
import json
import socket
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


ROOT = Path(__file__).parent.resolve()
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    print(msg, flush=True)


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _find_pids_by_port_windows(port: int) -> List[int]:
    try:
        out = subprocess.run(
            ["cmd", "/C", f"netstat -ano -p TCP | findstr :{port}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode not in (0, 1):
            return []
        pids: List[int] = []
        for line in (out.stdout or "").splitlines():
            line = line.strip()
            if not line:
                continue
            # Example: TCP    0.0.0.0:8007         0.0.0.0:0              LISTENING       12345
            parts = [p for p in line.split() if p]
            if len(parts) >= 5 and parts[-2].upper() == "LISTENING":
                try:
                    pids.append(int(parts[-1]))
                except ValueError:
                    pass
        return sorted(set(pids))
    except Exception:
        return []


def _find_pids_by_port_posix(port: int) -> List[int]:
    # Prefer lsof, fallback to fuser
    try:
        out = subprocess.run(
            ["bash", "-lc", f"lsof -i :{port} -t"], capture_output=True, text=True, timeout=5
        )
        if out.returncode == 0:
            return sorted({int(x) for x in (out.stdout or "").split() if x.strip().isdigit()})
    except Exception:
        pass
    try:
        out = subprocess.run(
            ["bash", "-lc", f"fuser -n tcp {port} 2>/dev/null"], capture_output=True, text=True, timeout=5
        )
        if out.returncode == 0:
            return sorted({int(x) for x in (out.stdout or "").split() if x.strip().isdigit()})
    except Exception:
        pass
    return []


def find_pids_by_port(port: int) -> List[int]:
    if os.name == "nt":
        return _find_pids_by_port_windows(port)
    return _find_pids_by_port_posix(port)


def kill_pid(pid: int) -> None:
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True, timeout=5)
        else:
            subprocess.run(["kill", "-9", str(pid)], capture_output=True, timeout=5)
    except Exception:
        pass


def ensure_port_free(port: int) -> None:
    pids = find_pids_by_port(port)
    if not pids and not is_port_open("127.0.0.1", port):
        return
    log(f"🔧 Port {port} is in use; attempting to stop existing process(es): {pids or 'unknown'}")
    for pid in pids:
        kill_pid(pid)
    # Wait until closed (best-effort)
    deadline = time.time() + 8
    while time.time() < deadline:
        if not is_port_open("127.0.0.1", port):
            break
        time.sleep(0.5)


def start_server(port: int) -> Tuple[Optional[subprocess.Popen], str]:
    env = os.environ.copy()
    env["MODEL_SERVER_PORT"] = str(port)
    uvicorn_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "model_server:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
        "--log-level",
        "info",
        # Note: reload adds watcher processes; avoid for runner simplicity
    ]

    runtime_log = LOGS_DIR / "runner_uvicorn.log"
    log(f"🚀 Starting API server on http://127.0.0.1:{port}")
    try:
        f = open(runtime_log, "a", encoding="utf-8", errors="ignore")
        f.write(f"# START {time.time()} {' '.join(uvicorn_cmd)}\n")
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NO_WINDOW
        proc = subprocess.Popen(
            uvicorn_cmd,
            stdout=f,
            stderr=subprocess.STDOUT,
            env=env,
            creationflags=creationflags,
            cwd=str(ROOT),
        )
        return proc, str(runtime_log)
    except Exception as e:
        log(f"❌ Failed to start server: {e}")
        return None, str(runtime_log)


def wait_server_ready(base_url: str, timeout_sec: int = 40) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        try:
            r = requests.get(f"{base_url}/health", timeout=3)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def choose_model(base_url: str) -> Optional[str]:
    try:
        r = requests.get(f"{base_url}/models/installed", timeout=10)
        if r.status_code != 200:
            return None
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        models = [m.get("name") for m in data.get("models", [])]
        preferred = [
            "phi-2-gguf",
            "tinyllama-gguf",
            "qwen0_5b",
        ]
        for p in preferred:
            if p in models:
                return p
        return models[0] if models else None
    except Exception:
        return None


def compute_threads() -> int:
    try:
        cpu = os.cpu_count() or 4
        return max(2, min(cpu, 8))
    except Exception:
        return 4


def load_model(base_url: str, model: str, threads: int) -> Dict:
    try:
        r = requests.post(f"{base_url}/runtime/load/{model}", params={"threads": threads}, timeout=120)
        if r.status_code == 200:
            return {"ok": True, "data": r.json()}
        return {"ok": False, "code": r.status_code, "text": r.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def wait_model_ready(base_url: str, model: str, timeout_sec: int = 60) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        try:
            s = requests.get(f"{base_url}/runtime/status", timeout=5)
            if s.status_code == 200:
                js = s.json()
                for m in js.get("models", []):
                    if m.get("model") == model and m.get("status") == "ready":
                        return True
        except Exception:
            pass
        time.sleep(1)
    return False


def run_chat_test(base_url: str, model: str) -> Dict:
    headers = {
        "X-App-Name": "ZombieRunner",
        "X-Test": "chat",
        "X-Lang": "bn-BD",
        "Accept": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "বাংলায় একটা ছোট্ট শুভেচ্ছা দিন।"}],
        "max_tokens": 48,
    }
    try:
        r = requests.post(f"{base_url}/api/chat", headers=headers, json=payload, timeout=40)
        ok = r.status_code == 200 and r.headers.get("content-type", "").startswith("application/json")
        data = r.json() if ok else {"status": r.status_code, "text": r.text[:200]}
        return {"ok": ok, "response": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def run_generate_test(base_url: str, model: str) -> Dict:
    headers = {
        "X-App-Name": "ZombieRunner",
        "X-Test": "json-generate",
        "Accept": "application/json",
    }
    payload = {
        "model": model,
        "prompt": "Say hello in one short line.",
        "stream": False,
    }
    try:
        r = requests.post(f"{base_url}/api/generate", headers=headers, json=payload, timeout=60)
        ok = r.status_code == 200 and r.headers.get("content-type", "").startswith("application/json")
        data = r.json() if ok else {"status": r.status_code, "text": r.text[:200]}
        return {"ok": ok, "response": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def tail_logs(base_url: str, seconds: int = 10) -> None:
    log("\n📜 Real-time server log tail:")
    t0 = time.time()
    last_print = 0.0
    while time.time() - t0 < seconds:
        try:
            r = requests.get(f"{base_url}/logs/server", params={"limit": 15}, timeout=4)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/json"):
                data = r.json()
                tail = data.get("tail", [])
                # Print the last 3 fresh lines per second
                if tail:
                    to_show = tail[-3:]
                    for ln in to_show:
                        log(f"   {ln}")
            time.sleep(max(0.2, 1.0 - (time.time() - last_print)))
            last_print = time.time()
        except Exception:
            time.sleep(0.5)


def unload_model(base_url: str, model: str) -> None:
    try:
        requests.post(f"{base_url}/runtime/unload/{model}", timeout=10)
    except Exception:
        pass


def main() -> int:
    # Configuration
    port = int(os.getenv("MODEL_SERVER_PORT", "8007"))  # align with local tests
    base = f"http://127.0.0.1:{port}"

    log("🚀 ZombieCoder Runner: start")
    log("1) Preflight: dependency and port checks")

    # Preflight: port safety
    ensure_port_free(port)

    # Launch server
    proc, uvicorn_log = start_server(port)
    if proc is None or proc.poll() is not None:
        log("❌ Server process failed to spawn.")
        return 1

    # Wait server ready
    log("2) Waiting for server /health ...")
    if not wait_server_ready(base, timeout_sec=40):
        log("❌ Server didn't become healthy in time.")
        return 1
    log("✅ Server is healthy.")

    # Model selection and loading
    log("3) Selecting and loading model ...")
    model = choose_model(base)
    if not model:
        log("⚠️ No local models found. Skipping load/tests.")
        tail_logs(base, seconds=6)
        log("ℹ️ You can place a GGUF model under models/ then rerun.")
        return 0

    threads = compute_threads()
    log(f"   → Model: {model} | Threads: {threads}")
    load_res = load_model(base, model, threads)
    if not load_res.get("ok"):
        log(f"❌ Load failed: {json.dumps(load_res)[:300]}")
        return 1

    # Wait model ready
    if not wait_model_ready(base, model, timeout_sec=90):
        log("❌ Model didn't become ready in time.")
        return 1
    log("✅ Model is ready.")

    # Tests
    log("4) Running Chat test (with headers) ...")
    chat_res = run_chat_test(base, model)
    log(f"   Chat: {'OK' if chat_res.get('ok') else 'FAIL'}")
    if chat_res.get("ok"):
        try:
            content = chat_res["response"]["runtime_response"]["content"]
            log(f"   ↳ {content[:120]}{'…' if len(content) > 120 else ''}")
        except Exception:
            pass

    log("5) Running JSON API generate test ...")
    gen_res = run_generate_test(base, model)
    log(f"   Generate: {'OK' if gen_res.get('ok') else 'FAIL'}")
    if gen_res.get("ok"):
        try:
            content = gen_res["response"]["runtime_response"].get("content", "")
            log(f"   ↳ {content[:120]}{'…' if len(content) > 120 else ''}")
        except Exception:
            pass

    # Live logs tail
    log("6) Tailing server logs (live 10s) ...")
    tail_logs(base, seconds=10)

    # Optional: minimal CRUD self-check (unload)
    log("7) Unloading model (CRUD: Delete) ...")
    unload_model(base, model)
    log("✅ Runner completed.")
    log(f"🔎 Uvicorn log: {uvicorn_log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


