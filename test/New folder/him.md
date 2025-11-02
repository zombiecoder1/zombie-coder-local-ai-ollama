### ZombieCoder Local Test Plan — Documentation

- **Author**: ZombieCoder Assistant (GPT-5)
- **Digital Signature**: ZC-ASSISTANT-GPT5-LOCAL-2025-10-29
- **Scope**: Non-invasive verification only. No system config changes.
- **Targets**:
  - `C:\model` (Local API server at 127.0.0.1:8007)
  - `C:\Users\sahon\Desktop\ZombieCoder Main Server` (Launcher/orchestrator)

### What tests we will perform
- **Environment & Ports**: Verify Python/venv, PowerShell, and ports 8007/8155/12346 status.
- **Health**: `GET /health` on 8007.
- **Models**: `GET /models/installed` on 8007.
- **Generate (JSON API)**: `POST /api/generate` with a simple prompt.
- **Chat (headers/JSON)**: `POST /api/chat` with a simple user message.

### Expected results (success criteria)
- **Environment & Ports**: 8007 LISTENING, 8155 LISTENING, 12346 LISTENING (if main server is up).
- **Health**: 200 with a JSON body containing status ok/healthy.
- **Models**: 200 with a list/array containing at least `phi-2-gguf` or installed models.
- **Generate**: 200 with coherent text output in `data`/`text` field.
- **Chat**: 200 with coherent content; latency may be high on CPU.

### Current observed state (from provided logs)
- `start_zombie_system.ps1`: Model Server failed readiness; Hello Zombie Server OK.
- `run.py` (1st run): API healthy, model ready, Chat and Generate failed (timeout/race).
- `run.py` (2nd run): API/model OK; Chat 200 (~37s), Generate 200 (~28s); outputs returned.

### Action plan
1) Run scripted checks from `C:\model\test\New folder` and store outputs into `.log` files.
2) Compare actual responses vs expected success criteria.
3) If failures occur, identify whether it’s startup race, schema mismatch, or port/service down.

### Pass conditions (per test)
- Env/Ports: All expected listeners present or clearly documented if intentionally absent.
- Health: HTTP 200 and JSON body.
- Models: HTTP 200 and JSON list or object of models.
- Generate: HTTP 200 and non-empty model text.
- Chat: HTTP 200 and non-empty model text.

### Notes
- Tests are read-only; no configuration is altered.
- Latency on CPU may be 20–40s per request; treated as acceptable if responses are successful.
