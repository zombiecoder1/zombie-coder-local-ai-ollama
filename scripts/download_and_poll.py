#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
import time
from pathlib import Path

import requests


def main() -> int:
    parser = argparse.ArgumentParser(description="Start HF GGUF download via API and poll status")
    parser.add_argument("--model", required=True, help="Local model folder name under models/")
    parser.add_argument("--repo", required=True, help="Hugging Face repo id")
    parser.add_argument("--host", default="http://127.0.0.1:8155", help="Model server host")
    parser.add_argument("--timeout", type=int, default=900, help="Max seconds to wait")
    args = parser.parse_args()

    base = args.host.rstrip("/")
    # Start download
    try:
        r = requests.post(f"{base}/download/start", json={"model_name": args.model, "repo_id": args.repo}, timeout=30)
        r.raise_for_status()
        start_resp = r.json()
    except Exception as e:
        print(json.dumps({"status": "error", "stage": "start", "message": str(e)}))
        return 2

    # Poll status
    t0 = time.time()
    last_status = None
    while time.time() - t0 < args.timeout:
        try:
            s = requests.get(f"{base}/download/status/{args.model}", timeout=15)
            s.raise_for_status()
            last_status = s.json()
        except Exception as e:
            last_status = {"status": "error", "message": str(e)}
        # Print heartbeat to keep logs moving
        sys.stdout.write("." )
        sys.stdout.flush()
        if isinstance(last_status, dict) and last_status.get("status") == "finished":
            break
        time.sleep(2)
    sys.stdout.write("\n")

    # Inspect filesystem for gguf presence
    models_dir = Path(__file__).resolve().parent.parent / "models" / args.model
    ggufs = sorted(models_dir.glob("*.gguf"))
    result = {
        "start": start_resp,
        "final_status": last_status,
        "gguf_files": [str(p) for p in ggufs],
        "gguf_count": len(ggufs),
        "models_dir": str(models_dir),
    }
    print(json.dumps(result, indent=2))
    # Success if any gguf present
    return 0 if ggufs else 1


if __name__ == "__main__":
    sys.exit(main())



