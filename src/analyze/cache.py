"""SQLite cache for LLM (and local) extraction keyed by content_hash + prompt_version."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.qualify.config import ROOT

CACHE_PATH = ROOT / "data" / "cache" / "llm.sqlite"


def connect(path: Path | None = None) -> sqlite3.Connection:
    cache = path or CACHE_PATH
    cache.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(cache)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS llm_cache (
            cache_key TEXT PRIMARY KEY,
            content_hash TEXT NOT NULL,
            prompt_version TEXT NOT NULL,
            response_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_llm_cache_hash ON llm_cache(content_hash, prompt_version)"
    )
    conn.commit()
    return conn


def cache_key(content_hash: str, prompt_version: str) -> str:
    return f"{prompt_version}:{content_hash}"


def get(conn: sqlite3.Connection, content_hash: str, prompt_version: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT response_json FROM llm_cache WHERE cache_key = ?",
        (cache_key(content_hash, prompt_version),),
    ).fetchone()
    if not row:
        return None
    return json.loads(row[0])


def put(
    conn: sqlite3.Connection,
    content_hash: str,
    prompt_version: str,
    payload: dict[str, Any],
) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO llm_cache (cache_key, content_hash, prompt_version, response_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            cache_key(content_hash, prompt_version),
            content_hash,
            prompt_version,
            json.dumps(payload, ensure_ascii=False),
            datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        ),
    )
    conn.commit()
