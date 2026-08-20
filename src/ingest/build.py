"""Phase 1: normalize data/raw into CanonicalFeedback. Never writes to data/raw/."""

from __future__ import annotations

import json
import logging
import sys
from collections import Counter
from pathlib import Path

from src.ingest.adapters import ADAPTERS
from src.ingest.adapters.base import CanonicalFeedback, utc_now
from src.ingest.env import load_dotenv
from src.qualify.config import LOGS_DIR, RAW_DIR, ROOT
from src.qualify.loaders import iter_loaded

PROCESSED_DIR = ROOT / "data" / "processed"
CANONICAL_PARQUET = PROCESSED_DIR / "canonical.parquet"
MANIFEST_PATH = PROCESSED_DIR / "ingest_manifest.json"

SOURCE_RANK = {
    "google_play": 0,
    "app_store": 1,
    "reddit": 2,
    "myntra_reviews": 3,
    "product_reviews": 4,
    "youtube": 5,
    "social": 6,
    "product_qa": 7,
    "myntra_catalog": 8,
    "other": 9,
}


def _setup_log() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("phase1")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(LOGS_DIR / "ingest.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


def choose_adapter(relative_path: str):
    for adapter in ADAPTERS:
        if adapter.matches(relative_path):
            return adapter
    raise RuntimeError(f"No adapter for {relative_path}")


def dedupe(records: list[CanonicalFeedback]) -> tuple[list[CanonicalFeedback], int]:
    records.sort(key=lambda row: (SOURCE_RANK.get(row.source, 99), row.raw_ref))
    seen_hash: set[str] = set()
    seen_id: set[str] = set()
    kept: list[CanonicalFeedback] = []
    dropped = 0
    for row in records:
        if row.content_hash in seen_hash:
            dropped += 1
            continue
        record_id = row.record_id
        if record_id in seen_id:
            row.record_id = f"{record_id}:{row.content_hash[:8]}"
        seen_hash.add(row.content_hash)
        seen_id.add(row.record_id)
        kept.append(row)
    return kept, dropped


def write_parquet(rows: list[CanonicalFeedback], path: Path) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Phase 1 needs pyarrow to write canonical.parquet. pip install pyarrow") from exc

    payload = [row.as_dict() for row in rows]
    table = pa.Table.from_pylist(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path, compression="zstd")


def run(raw_dir: Path | None = None) -> dict:
    load_dotenv()
    logger = _setup_log()
    raw = raw_dir or RAW_DIR
    ingest_at = utc_now()
    logger.info("Phase 1 ingest starting. raw=%s", raw)

    mapped: list[CanonicalFeedback] = []
    skipped_empty = 0
    adapter_counts: Counter[str] = Counter()
    file_counts: Counter[str] = Counter()
    load_errors: list[dict[str, str]] = []

    for path, _fmt, records, error in iter_loaded(raw):
        relative = path.relative_to(raw).as_posix()
        if error:
            load_errors.append({"path": relative, "error": error})
            logger.warning("Skip %s: %s", relative, error)
            continue
        adapter = choose_adapter(relative)
        kept_in_file = 0
        for line_no, record in enumerate(records, start=1):
            converted = adapter.convert(
                record,
                relative_path=relative,
                line_no=line_no,
                ingest_at=ingest_at,
            )
            if converted is None:
                skipped_empty += 1
                continue
            mapped.append(converted)
            kept_in_file += 1
        adapter_counts[adapter.name] += kept_in_file
        file_counts[relative] = kept_in_file
        logger.info("%s -> %s (%s records)", relative, adapter.name, kept_in_file)

    canonical, dropped_dupes = dedupe(mapped)
    write_parquet(canonical, CANONICAL_PARQUET)

    source_counts = Counter(row.source for row in canonical)
    manifest = {
        "ingest_at": ingest_at,
        "raw_root": "data/raw/",
        "output": "data/processed/canonical.parquet",
        "mapped": len(mapped),
        "canonical": len(canonical),
        "dropped_empty_text": skipped_empty,
        "dropped_duplicate_text": dropped_dupes,
        "adapter_counts": dict(adapter_counts),
        "source_counts": dict(source_counts),
        "files": dict(file_counts),
        "load_errors": load_errors,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info(
        "Phase 1 done. canonical=%s dropped_dupes=%s empty=%s path=%s",
        len(canonical),
        dropped_dupes,
        skipped_empty,
        CANONICAL_PARQUET,
    )
    return manifest


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
