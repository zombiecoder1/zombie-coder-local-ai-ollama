#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
import time

import requests


def wait_ready(base: str, model: str, timeout: int = 30) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            s = requests.get(f"{base}/runtime/status", timeout=10).json()
        except Exception:
            time.sleep(1)
            continue
        for m in s.get("models", []) if isinstance(s, dict) else []:
            if m.get("model") == model and m.get("status") == "ready":
                return True
        time.sleep(1)
    return False


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--prompt", default="Hello from lifecycle test")
    p.add_argument("--host", default="http://127.0.0.1:8155")
    args = p.parse_args()

    base = args.host.rstrip("/")
    out = {"ok": True, "steps": []}

    # Load
    r = requests.post(f"{base}/runtime/load/{args.model}?threads=4", timeout=60)
    out["steps"].append({"load": {"code": r.status_code, "data": r.json()}})
    if r.status_code != 200:
        print(json.dumps(out, indent=2))
        return 1

    # Wait ready
    if not wait_ready(base, args.model, timeout=40):
        out["ok"] = False
        out["steps"].append({"ready": False})
        print(json.dumps(out, indent=2))
        return 1

    # Generate
    g = requests.post(f"{base}/api/generate", json={"model": args.model, "prompt": args.prompt}, timeout=200)
    out["steps"].append({"generate": {"code": g.status_code, "data": (g.json() if g.headers.get('content-type','').startswith('application/json') else g.text)}})
    if g.status_code != 200:
        out["ok"] = False

    # Unload
    u = requests.post(f"{base}/runtime/unload/{args.model}", timeout=30)
    out["steps"].append({"unload": {"code": u.status_code, "data": u.json()}})
    if u.status_code != 200:
        out["ok"] = False

    print(json.dumps(out, indent=2))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())


