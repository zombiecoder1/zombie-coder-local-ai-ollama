import sys
import time
import json
import argparse
from typing import Any, Dict, List, Tuple

try:
    import requests
except Exception:
    print("requests module is required. Try: pip install requests", file=sys.stderr)
    sys.exit(1)


def safe_get(url: str, timeout: float = 5.0) -> Tuple[int, Any, float]:
    t0 = time.time()
    try:
        r = requests.get(url, timeout=timeout)
        latency = (time.time() - t0) * 1000.0
        ctype = r.headers.get("Content-Type", "")
        payload: Any
        if "application/json" in ctype:
            try:
                payload = r.json()
            except Exception:
                payload = r.text
        else:
            payload = r.text
        return r.status_code, payload, latency
    except Exception as e:
        return 0, str(e), (time.time() - t0) * 1000.0


def safe_post(url: str, json_body: Dict[str, Any], timeout: float = 15.0) -> Tuple[int, Any, float]:
    t0 = time.time()
    try:
        r = requests.post(url, json=json_body, timeout=timeout)
        latency = (time.time() - t0) * 1000.0
        ctype = r.headers.get("Content-Type", "")
        payload: Any
        if "application/json" in ctype:
            try:
                payload = r.json()
            except Exception:
                payload = r.text
        else:
            payload = r.text
        return r.status_code, payload, latency
    except Exception as e:
        return 0, str(e), (time.time() - t0) * 1000.0


def parse_log_stats(log_text: str) -> Dict[str, Any]:
    # Best-effort extraction: counts per model and avg latency
    import re

    model_re = re.compile(r'"model"\s*:\s*"([^"]+)"')
    lat_re = re.compile(r'"latency_ms"\s*:\s*(\d+)')

    model_counts: Dict[str, int] = {}
    for m in model_re.findall(log_text):
        model_counts[m] = model_counts.get(m, 0) + 1

    latencies = [int(x) for x in lat_re.findall(log_text)]
    avg_latency = int(sum(latencies) / len(latencies)) if latencies else 0

    return {"counts": model_counts, "avg_latency": avg_latency, "total": len(latencies)}


def fmt_ms(ms: float) -> str:
    return f"{int(ms)} ms"


def print_section(title: str):
    print("\n" + title)
    print("-" * len(title))


def run_once(base8007: str, base8155: str, base12346: str, quick_probe: bool) -> None:
    # Health checks
    h8007 = safe_get(f"{base8007}/health")
    h8155 = safe_get(f"{base8155}/health")
    h12346 = safe_get(f"{base12346}/health")

    print_section("Health")
    print(f"8007 /health: {h8007[0]} | {fmt_ms(h8007[2])}")
    print(f"8155 /health: {h8155[0]} | {fmt_ms(h8155[2])}")
    print(f"12346 /health: {h12346[0]} | {fmt_ms(h12346[2])}")

    # Service signatures (best-effort from /health JSON)
    try:
        if isinstance(h8007[1], dict):
            svc = h8007[1].get('service')
            ver = h8007[1].get('version')
            if svc:
                print(f"8007 service: {svc}{(' v'+ver) if ver else ''}")
    except Exception:
        pass
    try:
        if isinstance(h8155[1], dict):
            svc = h8155[1].get('service')
            ver = h8155[1].get('version')
            if svc:
                print(f"8155 service: {svc}{(' v'+ver) if ver else ''}")
    except Exception:
        pass

    # Provider/About and Monitoring (best-effort)
    pa = safe_get(f"{base8155}/provider/about")
    ms = safe_get(f"{base8155}/monitoring/summary")

    print_section("Provider / About (8155)")
    if pa[0] == 200:
        try:
            text = json.dumps(pa[1], ensure_ascii=False, indent=2)[:800]
            print(text)
        except Exception:
            # Fallback to ASCII-safe
            text = json.dumps(pa[1], ensure_ascii=True, indent=2)[:800]
            print(text)
    else:
        print(f"status: {pa[0]} | {fmt_ms(pa[2])}")

    print_section("Monitoring Summary (8155)")
    if ms[0] == 200:
        try:
            text = json.dumps(ms[1], ensure_ascii=False, indent=2)[:800]
            print(text)
        except Exception:
            text = json.dumps(ms[1], ensure_ascii=True, indent=2)[:800]
            print(text)
    else:
        print(f"status: {ms[0]} | {fmt_ms(ms[2])}")

    # Models installed
    mi = safe_get(f"{base8007}/models/installed")
    models: List[Dict[str, Any]] = []
    count = 0
    total_mb = 0.0
    if mi[0] == 200 and isinstance(mi[1], dict):
        models = mi[1].get("models", [])
        count = mi[1].get("count", len(models))
        total_mb = float(mi[1].get("total_size_mb", 0.0))

    print_section("Models Installed (8007)")
    print(f"count: {count} | total_size: {total_mb/1024:.2f} GB | fetch: {fmt_ms(mi[2])}")
    for m in models:
        print(f"- {m.get('name')} | {m.get('path')} | {m.get('size_mb')/1024:.2f} GB")

    # Runtime status (loaded models)
    rt = safe_get(f"{base8155}/runtime/status")
    loaded_names: List[str] = []
    if rt[0] == 200 and isinstance(rt[1], dict):
        loaded_names = [x.get("model") for x in rt[1].get("models", []) if x.get("model")]

    print_section("Runtime (8155) Loaded Models")
    print(
        (", ".join(loaded_names) if loaded_names else "None") + f" | fetch: {fmt_ms(rt[2])}"
    )

    # Logs (for per-model counts + average latency)
    lg = safe_get(f"{base8007}/logs/server")
    counts = {}
    avg_lat = 0
    total_lat = 0
    if lg[0] == 200 and isinstance(lg[1], str):
        stats = parse_log_stats(lg[1])
        counts = stats["counts"]
        avg_lat = stats["avg_latency"]
        total_lat = stats["total"]

    print_section("Recent Inference (from 8007 logs)")
    print(f"avg_latency: {avg_lat} ms | samples: {total_lat}")
    if counts:
        for k, v in counts.items():
            print(f"- {k}: {v} req")
    else:
        print("- no recent entries")

    # Quick probe (optional) using default/first model
    if quick_probe and models:
        probe_model = models[0].get("name")
        status, payload, lat = safe_post(f"{base8007}/api/generate", {"model": probe_model, "prompt": "hi", "stream": False}, timeout=60.0)
        print_section("Quick Probe /api/generate")
        print(f"model: {probe_model} | status: {status} | latency: {fmt_ms(lat)}")
        if isinstance(payload, dict):
            snippet = json.dumps(payload)[:240]
        else:
            snippet = str(payload)[:240]
        print(snippet + ("..." if len(snippet) == 240 else ""))


def main():
    parser = argparse.ArgumentParser(description="ZombieCoder realtime monitor (local)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=float, default=5.0, help="Refresh interval seconds")
    parser.add_argument("--no-probe", action="store_true", help="Skip quick inference probe")
    parser.add_argument("--base8007", default="http://127.0.0.1:8007")
    parser.add_argument("--base8155", default="http://127.0.0.1:8155")
    parser.add_argument("--base12346", default="http://127.0.0.1:12346")
    args = parser.parse_args()

    if args.once:
        run_once(args.base8007, args.base8155, args.base12346, quick_probe=(not args.no_probe))
        return

    try:
        while True:
            print("\x1bc", end="")  # clear screen
            print("ZombieCoder Realtime Monitor — Local Providers\n")
            run_once(args.base8007, args.base8155, args.base12346, quick_probe=False)
            print("\nPress Ctrl+C to exit | next refresh in", args.interval, "sec")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nExit")


if __name__ == "__main__":
    main()


