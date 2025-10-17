import sys, json, requests

BASE = 'http://127.0.0.1:8155'

def main():
    out = {"ok": True, "checks": {}}
    try:
        sysinfo = requests.get(f"{BASE}/system/info", timeout=10).json()
        avail = requests.get(f"{BASE}/models/available", timeout=10).json()
        runtime = requests.get(f"{BASE}/runtime/status", timeout=10).json()
        installed = requests.get(f"{BASE}/models/installed", timeout=10).json()
        out["checks"]["system_ok"] = all(k in sysinfo for k in ("total_ram_gb","cpu_model","tier"))
        out["checks"]["available_ok"] = isinstance(avail, list)
        out["checks"]["runtime_ok"] = isinstance(runtime, dict) and "models" in runtime
        out["checks"]["installed_ok"] = isinstance(installed, dict) and "models" in installed
        out["checks"]["summary"] = {"system":sysinfo,"available_len":len(avail),"installed_len":len(installed.get('models',[]))}
        if not all(out["checks"][k] for k in ("system_ok","available_ok","runtime_ok","installed_ok")):
            out["ok"] = False
    except Exception as e:
        out["ok"] = False
        out["checks"]["error"] = str(e)

    print(json.dumps(out, indent=2))
    sys.exit(0 if out["ok"] else 1)

if __name__ == '__main__':
    main()


