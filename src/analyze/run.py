"""Phase 3 extraction engine. Never writes to data/raw/. Never resends cached texts."""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from src.analyze.cache import connect, get as cache_get, put as cache_put
from src.analyze.llm import chat_json, llm_config, wait_seconds
from src.analyze.local import extract_text as local_extract
from src.analyze.prompts import PROMPT_VERSION as LLM_PROMPT_VERSION
from src.analyze.prompts import request_body
from src.analyze.schema import EXTRACTION_COLUMNS, EXTRACTORS, PROMPT_VERSION_LOCAL
from src.analyze.validate import make_extraction_id, sanitize_payload
from src.ingest.env import load_dotenv
from src.process.io import write_parquet
from src.qualify.config import LOGS_DIR, ROOT

PROCESSED = ROOT / "data" / "processed"
RELEVANT = PROCESSED / "relevant.parquet"
OUT_DIR = ROOT / "data" / "extractions"
FAILURES = LOGS_DIR / "ai_failures.log"
MANIFEST = OUT_DIR / "manifest.json"

BATCH_SIZE = 2
TEXT_LIMIT = 2500


def _logger() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("phase3")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(LOGS_DIR / "analyze.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


def _log_failure(record_ids: list[str], error: str) -> None:
    FAILURES.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(
        {
            "at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "record_ids": record_ids,
            "error": error[:1000],
        },
        ensure_ascii=False,
    )
    with FAILURES.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _limit(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw = os.environ.get("EXTRACT_LIMIT", "").strip()
    if not raw:
        return rows
    return rows[: max(0, int(raw))]


def records_by_id(parsed: Any, batch: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Map LLM output to batch rows. Never reuse the whole batch payload for a miss."""
    records: list[Any] = []
    if isinstance(parsed, dict):
        raw_records = parsed.get("records") or parsed.get("items") or parsed.get("results")
        if isinstance(raw_records, list):
            records = raw_records
        elif isinstance(raw_records, dict):
            records = [raw_records]
        elif parsed.get("record_id") is not None:
            records = [parsed]
        elif len(batch) == 1 and any(
            parsed.get(key) for key in ("intents", "barriers", "needs", "behaviors", "intent", "barrier")
        ):
            records = [parsed]
    elif isinstance(parsed, list):
        records = parsed

    by_id: dict[str, dict[str, Any]] = {}
    for item in records:
        if isinstance(item, dict) and item.get("record_id") is not None:
            by_id[str(item["record_id"])] = item
    if len(records) == len(batch):
        for row, item in zip(batch, records):
            rid = str(row["record_id"])
            if rid not in by_id and isinstance(item, dict):
                by_id[rid] = item
    return by_id


def _json_mode_default(base_url: str, model: str) -> bool:
    raw = os.environ.get("EXTRACT_JSON_MODE", "").strip().lower()
    if raw in {"0", "false", "no"}:
        return False
    if raw in {"1", "true", "yes"}:
        return True
    # Groq gpt-oss often returns json_validate_failed with an empty body.
    if "groq.com" in base_url and "gpt-oss" in model:
        return False
    return True


def _batch_size() -> int:
    raw = os.environ.get("EXTRACT_BATCH_SIZE", "").strip()
    if raw:
        return max(1, int(raw))
    return BATCH_SIZE


def alias_batch(batch: list[dict[str, Any]]) -> tuple[list[dict[str, str]], dict[str, dict[str, Any]]]:
    items: list[dict[str, str]] = []
    lookup: dict[str, dict[str, Any]] = {}
    for i, row in enumerate(batch, start=1):
        alias = f"r{i}"
        lookup[alias] = row
        items.append({"record_id": alias, "text": str(row["text"])[:TEXT_LIMIT]})
    return items, lookup


def payloads_from_parsed(
    parsed: Any,
    lookup: dict[str, dict[str, Any]],
    prompt_version: str,
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    alias_rows = [{"record_id": alias} for alias in lookup]
    by_id = records_by_id(parsed, alias_rows)
    out: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for alias, row in lookup.items():
        raw = by_id.get(alias)
        if not isinstance(raw, dict):
            continue
        out[row["content_hash"]] = sanitize_payload(str(row["text"]), raw, prompt_version, row["content_hash"])
    return out


def flatten_rows(
    record_id: str,
    content_hash: str,
    payload: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for extractor in EXTRACTORS:
        for item in payload.get(extractor) or []:
            span = item["evidence_span"]
            label = item["label"]
            rows.append(
                {
                    "extraction_id": make_extraction_id(record_id, extractor, label, span),
                    "record_id": record_id,
                    "extractor": extractor,
                    "label": label,
                    "evidence_span": span,
                    "confidence": item["confidence"],
                    "prompt_version": item["prompt_version"],
                    "status": item["status"],
                    "ai_interpretation": item.get("ai_interpretation") or "",
                    "content_hash": content_hash,
                }
            )
    return rows


def _choose_backend() -> tuple[dict[str, str] | None, str]:
    mode = (os.environ.get("EXTRACT_BACKEND") or "auto").strip().lower()
    cfg = llm_config()
    if mode == "local":
        return None, "local"
    if mode == "llm":
        if not cfg:
            raise RuntimeError("EXTRACT_BACKEND=llm requires GROQ_API_KEY")
        return cfg, "llm"
    if mode not in {"", "auto"}:
        raise RuntimeError(f"Unknown EXTRACT_BACKEND={mode}. Use auto, local, or llm.")
    return cfg, ("llm" if cfg else "local")


def extract_unique(
    unique_rows: list[dict[str, Any]],
    conn: sqlite3.Connection,
    logger: logging.Logger,
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Map content_hash -> sanitized extractor payload. Cache-first. No duplicate LLM sends."""
    cfg, backend = _choose_backend()
    prompt_version = LLM_PROMPT_VERSION if cfg else PROMPT_VERSION_LOCAL
    logger.info("Phase 3 backend=%s prompt_version=%s unique_texts=%s", backend, prompt_version, len(unique_rows))

    results: dict[str, dict[str, list[dict[str, Any]]]] = {}
    missing: list[dict[str, Any]] = []
    cache_hits = 0
    for row in unique_rows:
        digest = row["content_hash"]
        cached = cache_get(conn, digest, prompt_version)
        if cached is not None:
            results[digest] = cached
            cache_hits += 1
        else:
            missing.append(row)
    logger.info("cache hits=%s misses=%s", cache_hits, len(missing))

    if not cfg:
        for row in missing:
            payload = local_extract(str(row["text"]), row["content_hash"])
            cache_put(conn, row["content_hash"], prompt_version, payload)
            results[row["content_hash"]] = payload
        return results

    size = _batch_size()
    n_batches = (len(missing) + size - 1) // size or 1
    pace = os.environ.get("EXTRACT_PACE_SECS", "").strip()
    groq = "groq.com" in cfg["base_url"]
    pace_secs = 22.0 if groq else 0.0
    if pace:
        requested = max(0.0, float(pace))
        pace_secs = max(pace_secs, requested) if groq else requested
    if pace_secs:
        logger.info("LLM pace=%.1f s between calls (EXTRACT_PACE_SECS)", pace_secs)
    json_mode = _json_mode_default(cfg["base_url"], cfg["model"])
    logger.info("LLM json_mode=%s batch_size=%s", json_mode, size)

    def local_fallback(batch_rows: list[dict[str, Any]], reason: str) -> None:
        logger.warning("%s — local fallback, not cached", reason)
        for row in batch_rows:
            if row["content_hash"] in results:
                continue
            results[row["content_hash"]] = local_extract(str(row["text"]), row["content_hash"])

    def send(batch_rows: list[dict[str, Any]], json_mode: bool) -> None:
        items, lookup = alias_batch(batch_rows)
        parsed = chat_json(request_body(items, cfg["model"], json_mode=json_mode))
        mapped = payloads_from_parsed(parsed, lookup, prompt_version)
        for digest, payload in mapped.items():
            cache_put(conn, digest, prompt_version, payload)
            results[digest] = payload
        if pace_secs:
            time.sleep(pace_secs)

    def extract_batch(batch_rows: list[dict[str, Any]]) -> None:
        pending = [row for row in batch_rows if row["content_hash"] not in results]
        if not pending:
            return
        ids = [str(row["record_id"]) for row in pending]
        try:
            send(pending, json_mode=json_mode)
        except Exception as exc:  # noqa: BLE001
            err = str(exc)
            if "429" in err:
                delay = wait_seconds(err, 4)
                logger.warning("rate limited, sleeping %.1fs then retrying", delay)
                time.sleep(delay)
                try:
                    send(pending, json_mode=json_mode)
                except Exception as exc2:  # noqa: BLE001
                    logger.warning("LLM call failed after 429 retry (%s): %s", ids[:3], exc2)
                    _log_failure(ids, str(exc2))
            else:
                logger.warning("LLM call failed (%s): %s", ids[:3], exc)
                _log_failure(ids, str(exc))
        pending = [row for row in pending if row["content_hash"] not in results]
        other_mode = not json_mode
        skip_json_object = other_mode and "gpt-oss" in cfg["model"]
        if pending and not skip_json_object:
            try:
                send(pending, json_mode=other_mode)
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM retry failed (%s): %s", ids[:3], exc)
                _log_failure(ids, str(exc))
        pending = [row for row in pending if row["content_hash"] not in results]
        if len(pending) > 1:
            for row in pending:
                extract_batch([row])
            return
        if pending:
            local_fallback(pending, f"LLM missing/invalid payload for {ids[0]}")

    for start in range(0, len(missing), size):
        batch = missing[start : start + size]
        batch_no = start // size + 1
        if batch_no == 1 or batch_no % 25 == 0 or batch_no == n_batches:
            logger.info("LLM batch %s/%s", batch_no, n_batches)
        extract_batch(batch)
    return results


def run() -> dict[str, Any]:
    load_dotenv()
    logger = _logger()
    if not RELEVANT.exists():
        raise FileNotFoundError("Missing data/processed/relevant.parquet. Run python -m src.process first.")

    import pyarrow.parquet as pq

    rows = pq.read_table(RELEVANT).to_pylist()
    before_limit = len(rows)
    rows = _limit(rows)
    logger.info(
        "relevant_rows=%s after_EXTRACT_LIMIT=%s limit=%s",
        before_limit,
        len(rows),
        os.environ.get("EXTRACT_LIMIT", "").strip() or "(none)",
    )
    # One LLM/local call per unique text.
    by_hash: dict[str, dict[str, Any]] = {}
    hash_to_ids: dict[str, list[str]] = {}
    for row in rows:
        digest = str(row["content_hash"])
        hash_to_ids.setdefault(digest, []).append(str(row["record_id"]))
        by_hash.setdefault(digest, row)

    unique_rows = list(by_hash.values())
    conn = connect()
    try:
        payloads = extract_unique(unique_rows, conn, logger)
    finally:
        conn.close()

    buckets: dict[str, list[dict[str, Any]]] = {name: [] for name in EXTRACTORS}
    skipped = 0
    for digest, record_ids in hash_to_ids.items():
        payload = payloads.get(digest)
        if not payload:
            skipped += 1
            continue
        for record_id in record_ids:
            for item in flatten_rows(record_id, digest, payload):
                buckets[item["extractor"]].append(item)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = {}
    for extractor, items in buckets.items():
        path = OUT_DIR / f"{extractor}s.parquet"
        if items:
            write_parquet(items, path)
        else:
            import pyarrow as pa
            import pyarrow.parquet as pq

            schema = pa.schema([(name, pa.string()) for name in EXTRACTION_COLUMNS])
            pq.write_table(pa.Table.from_pylist([], schema=schema), path)
        written[extractor] = {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "rows": len(items)}
        logger.info("wrote %s (%s rows)", path.name, len(items))

    label_counts = {
        extractor: dict(Counter(item["label"] for item in items).most_common(20))
        for extractor, items in buckets.items()
    }
    status_counts = {
        extractor: dict(Counter(item["status"] for item in items))
        for extractor, items in buckets.items()
    }
    _, backend = _choose_backend()
    manifest = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "backend": backend,
        "prompt_version": LLM_PROMPT_VERSION if backend == "llm" else PROMPT_VERSION_LOCAL,
        "extract_backend": (os.environ.get("EXTRACT_BACKEND") or "auto").strip() or "auto",
        "n_relevant": len(rows),
        "n_unique_texts": len(unique_rows),
        "skipped_hashes": skipped,
        "written": written,
        "top_labels": label_counts,
        "status_counts": status_counts,
        "note": "Labels are not findings until Phase 4–5. observed_evidence vs hypothesis is per extraction row.",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info("Phase 3 done. unique_texts=%s", len(unique_rows))
    return manifest


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
