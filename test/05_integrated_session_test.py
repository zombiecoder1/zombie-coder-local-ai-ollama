import json, sys, time, requests

BASE = 'http://127.0.0.1:8155'


def req(method, path, **kw):
    if 'timeout' not in kw:
        kw['timeout'] = 60
    r = requests.request(method, BASE + path, **kw)
    return r.status_code, (r.json() if 'application/json' in r.headers.get('Content-Type', '') else r.text)


def main():
    out = {"ok": True, "steps": []}

    # start session
    code, sess = req('POST', '/api/session/start', json={})
    if code != 200 or not isinstance(sess, dict):
        out["ok"] = False
        print(json.dumps(out, indent=2)); sys.exit(1)
    sid = sess.get('session_id')
    out['steps'].append({'session_start': sess})

    # load model (use GGUF model)
    model_name = 'tinyllama-gguf'
    code, load = req('POST', f'/runtime/load/{model_name}?threads=4')
    out['steps'].append({'load': load})
    if code != 200:
        out['ok'] = False; print(json.dumps(out, indent=2)); sys.exit(1)

    # wait ready
    deadline = time.time() + 40
    while time.time() < deadline:
        code, rt = req('GET', '/runtime/status', timeout=5)
        if isinstance(rt, dict):
            for m in rt.get('models', []):
                if m.get('model') == model_name and m.get('status') == 'ready':
                    break
            else:
                time.sleep(1); continue
            break
        time.sleep(1)

    # generate with session
    payload = {"model":model_name,"prompt":"ping","options":{"session_id": sid}}
    code, gen = req('POST', '/api/generate', json=payload, timeout=200)
    out['steps'].append({'generate': gen})
    if code != 200:
        out['ok'] = False; print(json.dumps(out, indent=2)); sys.exit(1)

    # verify session
    code, sst = req('GET', f'/api/session/status/{sid}')
    out['steps'].append({'session_status': sst})
    if code != 200 or (isinstance(sst, dict) and sst.get('session',{}).get('last_model') != model_name):
        out['ok'] = False; print(json.dumps(out, indent=2)); sys.exit(1)

    # unload
    code, un = req('POST', f'/runtime/unload/{model_name}')
    out['steps'].append({'unload': un})
    if code != 200:
        out['ok'] = False; print(json.dumps(out, indent=2)); sys.exit(1)

    print(json.dumps(out, indent=2)); sys.exit(0)


if __name__ == '__main__':
    main()


