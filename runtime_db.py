#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List
from datetime import datetime


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runtime_models (
            model TEXT PRIMARY KEY,
            status TEXT,
            port INTEGER,
            pid INTEGER,
            updated_at TEXT
        )
        """
    )
    return conn


def upsert_model_state(db_path: Path, model: str, status: str, port: int | None, pid: int | None) -> None:
    conn = _connect(db_path)
    with conn:
        conn.execute(
            """
            INSERT INTO runtime_models(model, status, port, pid, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(model) DO UPDATE SET
              status=excluded.status,
              port=excluded.port,
              pid=excluded.pid,
              updated_at=excluded.updated_at
            """,
            (model, status, port, pid, datetime.now().isoformat()),
        )
    conn.close()


def delete_model_state(db_path: Path, model: str) -> None:
    conn = _connect(db_path)
    with conn:
        conn.execute("DELETE FROM runtime_models WHERE model=?", (model,))
    conn.close()


def get_all_states(db_path: Path) -> List[Dict]:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT model, status, port, pid, updated_at FROM runtime_models")
    rows = cur.fetchall()
    conn.close()
    return [
        {"model": r[0], "status": r[1], "port": r[2], "pid": r[3], "updated_at": r[4]}
        for r in rows
    ]


