#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
from shutil import which
import threading
import subprocess
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class DownloadJob:
    def __init__(self, repo_id: str, target_dir: Path, revision: Optional[str] = None) -> None:
        self.repo_id = repo_id
        self.target_dir = target_dir
        self.revision = revision
        self.started_at = datetime.now().isoformat()
        self.ended_at: Optional[str] = None
        self.returncode: Optional[int] = None
        self.error: Optional[str] = None
        self.log_file = target_dir / ".." / f"download_{target_dir.name}.log"
        self.log_file = self.log_file.resolve()
        self.proc: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None

    def to_dict(self) -> Dict:
        return {
            "repo_id": self.repo_id,
            "target_dir": str(self.target_dir),
            "revision": self.revision,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "returncode": self.returncode,
            "error": self.error,
            "pid": self.proc.pid if self.proc else None,
            "log_file": str(self.log_file),
            "running": self.is_running(),
        }

    def is_running(self) -> bool:
        alive = self.thread.is_alive() if self.thread else False
        return (self.proc is not None and self.proc.poll() is None) or alive


class HFDownloader:
    """Downloader using huggingface_hub CLI to ensure real output and logs."""

    def __init__(self) -> None:
        self.jobs: Dict[str, DownloadJob] = {}

    def _resolve_cli(self) -> str:
        """Find huggingface-cli binary; fallback to module runner."""
        # 1) PATH
        exe = which("huggingface-cli")
        if exe:
            return exe
        # 2) Common per-user Scripts path on Windows
        candidates = []
        appdata = os.getenv("APPDATA")
        if appdata:
            candidates.append(os.path.join(appdata, "Python", f"Python{sys.version_info.major}{sys.version_info.minor}", "Scripts", "huggingface-cli.exe"))
        home = os.path.expanduser("~")
        candidates.append(os.path.join(home, "AppData", "Roaming", "Python", f"Python{sys.version_info.major}{sys.version_info.minor}", "Scripts", "huggingface-cli.exe"))
        for c in candidates:
            if os.path.exists(c):
                return c
        # 3) Fallback to module runner
        return None

    def start(self, model_name: str, repo_id: str, target_root: Path, revision: Optional[str] = None) -> Dict:
        if model_name in self.jobs and self.jobs[model_name].is_running():
            return {"status": "busy", "message": "download already running", "job": self.jobs[model_name].to_dict()}

        target_dir = target_root / model_name
        target_dir.mkdir(parents=True, exist_ok=True)
        job = DownloadJob(repo_id=repo_id, target_dir=target_dir, revision=revision)
        self.jobs[model_name] = job

        # Build CLI command
        cli = self._resolve_cli()
        env = os.environ.copy()
        # pass HF token to subprocess if present
        for key in ("HUGGINGFACE_HUB_TOKEN", "HF_TOKEN"):
            if os.getenv(key):
                env[key] = os.getenv(key)

        if cli:
            cmd = [
                cli, "download", repo_id,
                "--local-dir", str(target_dir),
                "--local-dir-use-symlinks", "False",
            ]
        else:
            cmd = [
                sys.executable, "-m", "huggingface_hub", "download",
                repo_id,
                "--local-dir", str(target_dir),
                "--local-dir-use-symlinks", "False",
            ]
        if revision:
            cmd += ["--revision", revision]

        # Start subprocess and stream logs to file (real output)
        def _runner():
            with open(job.log_file, "a", encoding="utf-8", errors="ignore") as lf:
                lf.write(f"# START {datetime.now().isoformat()} | repo={repo_id} | model={model_name} | rev={revision}\n")
                try:
                    # Try CLI first if available
                    if cli:
                        job.proc = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            bufsize=1,
                            universal_newlines=True,
                            cwd=str(target_root),
                            env=env,
                        )
                        assert job.proc.stdout is not None
                        for line in job.proc.stdout:
                            lf.write(line)
                        job.proc.wait()
                        job.returncode = job.proc.returncode

                    # If CLI missing or failed, fallback to Python API
                    if (not cli) or (job.returncode and job.returncode != 0):
                        lf.write("# Fallback: huggingface_hub.snapshot_download\n")
                        try:
                            from huggingface_hub import snapshot_download
                            local_path = snapshot_download(
                                repo_id=repo_id,
                                revision=revision,
                                local_dir=str(job.target_dir),
                                local_dir_use_symlinks=False,
                                allow_patterns=["*.gguf", "*.safetensors", "*.bin", "*.json", "tokenizer*", "config*"],
                                ignore_patterns=["*.onnx", "*.safetensors.index.json"],
                                token=env.get("HUGGINGFACE_HUB_TOKEN") or env.get("HF_TOKEN"),
                            )
                            lf.write(f"# snapshot_download_ok: {local_path}\n")
                            job.returncode = 0
                        except Exception as e:
                            job.error = f"fallback_error: {e}"
                            job.returncode = -2
                except Exception as e:
                    job.error = str(e)
                    job.returncode = -1
                finally:
                    job.ended_at = datetime.now().isoformat()
                    lf.write(f"# END {job.ended_at} rc={job.returncode} err={job.error}\n")

        job.thread = threading.Thread(target=_runner, daemon=True)
        job.thread.start()
        return {"status": "started", "job": job.to_dict(), "cmd": " ".join(cmd)}

    def status(self, model_name: str) -> Dict:
        job = self.jobs.get(model_name)
        if not job:
            return {"status": "absent"}
        return {"status": "running" if job.is_running() else "finished", "job": job.to_dict()}

    def cancel(self, model_name: str) -> Dict:
        job = self.jobs.get(model_name)
        if not job or not job.is_running():
            return {"status": "noop"}
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(job.proc.pid), "/F"], capture_output=True)
            else:
                job.proc.terminate()
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "cancelled", "pid": job.proc.pid}


DOWNLOADER = HFDownloader()


