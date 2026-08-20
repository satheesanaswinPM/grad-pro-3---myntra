"""Duplicate, missingness, and source-coverage metrics for Phase 0."""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from src.qualify.corpus_scope import classify_record, corpus_scope
from src.qualify.language import language_distribution
from src.qualify.schema import is_missing, role_map


def _cell(value: Any) -> str:
    if is_missing(value):
        return ""
    return str(value).strip()


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def inspect_records(
    files: list[dict[str, Any]],
) -> dict[str, Any]:
    all_rows: list[dict[str, Any]] = []
    load_errors: list[dict[str, str]] = []
    for file_info in files:
        if file_info.get("error"):
            load_errors.append(
                {"path": file_info["relative_path"], "error": file_info["error"]}
            )
        for record in file_info.get("records", []):
            all_rows.append(
                {
                    "path": file_info["relative_path"],
                    "source_guess": file_info.get("source_guess"),
                    "record": record,
                    "roles": file_info.get("roles") or {},
                }
            )

    texts: list[str] = []
    sources: list[str] = []
    dates: list[str] = []
    row_hashes: list[str] = []
    text_hashes: list[str] = []
    scope_labels: list[str] = []
    missing_by_role: dict[str, int] = defaultdict(int)
    present_by_role: dict[str, int] = defaultdict(int)

    for row in all_rows:
        record = row["record"]
        roles: dict[str, str] = row["roles"]
        text = _cell(record.get(roles.get("text", ""), record.get("text", "")))
        if not text:
            for key, value in record.items():
                if isinstance(value, str) and len(value.strip()) >= 20:
                    text = value.strip()
                    break
        source = _cell(record.get(roles.get("source", ""), "")) or row["source_guess"] or "unknown"
        date = _cell(record.get(roles.get("date", ""), ""))
        rating = _cell(record.get(roles.get("rating", ""), ""))
        category = _cell(record.get(roles.get("product_or_category", ""), ""))
        user = _cell(record.get(roles.get("user_key", ""), ""))
        url = _cell(record.get(roles.get("url", ""), ""))

        for role, value in (
            ("text", text),
            ("source", source if source != "unknown" else ""),
            ("date", date),
            ("rating", rating),
            ("product_or_category", category),
            ("user_key", user),
            ("url", url),
        ):
            if value:
                present_by_role[role] += 1
            else:
                missing_by_role[role] += 1

        texts.append(text)
        sources.append(source)
        dates.append(date)
        text_hashes.append(content_hash(text.lower()) if text else "")
        canonical = "||".join(f"{k}={_cell(record.get(k))}" for k in sorted(record))
        row_hashes.append(content_hash(canonical))
        scope_labels.append(classify_record(Path(row["path"]), source, text))

    n = len(all_rows)
    nonempty_text_hashes = [h for h in text_hashes if h]
    text_dupes = 0
    if nonempty_text_hashes:
        counts = Counter(nonempty_text_hashes)
        text_dupes = sum(v - 1 for v in counts.values() if v > 1)
    row_counts = Counter(row_hashes)
    row_dupes = sum(v - 1 for v in row_counts.values() if v > 1)

    dated = [d for d in dates if d]
    source_counts = Counter(sources)

    per_source: list[dict[str, Any]] = []
    for source, count in source_counts.most_common():
        idxs = [i for i, s in enumerate(sources) if s == source]
        src_texts = [texts[i] for i in idxs]
        src_hashes = [text_hashes[i] for i in idxs if text_hashes[i]]
        src_dates = [dates[i] for i in idxs if dates[i]]
        hash_counts = Counter(src_hashes)
        per_source.append(
            {
                "source": source,
                "files": len({all_rows[i]["path"] for i in idxs}),
                "records": count,
                "pct_of_records": round(100.0 * count / n, 2) if n else 0.0,
                "unique_text": len(set(src_hashes)),
                "duplicate_text_extras": sum(v - 1 for v in hash_counts.values() if v > 1),
                "missing_text_pct": round(
                    100.0 * sum(1 for t in src_texts if not t) / count, 2
                )
                if count
                else 0.0,
                "date_min": min(src_dates) if src_dates else "",
                "date_max": max(src_dates) if src_dates else "",
                "myntra_records": sum(1 for i in idxs if scope_labels[i] in {"myntra", "mixed"}),
                "broader_fashion_records": sum(
                    1 for i in idxs if scope_labels[i] in {"broader_fashion", "mixed"}
                ),
            }
        )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "record_count": n,
        "file_count": len(files),
        "load_errors": load_errors,
        "duplicate_full_row_extras": row_dupes,
        "duplicate_text_extras": text_dupes,
        "unique_text": len(set(nonempty_text_hashes)),
        "empty_text": sum(1 for t in texts if not t),
        "language": language_distribution(texts),
        "source_counts": dict(source_counts),
        "source_coverage": per_source,
        "missing_by_role": dict(missing_by_role),
        "present_by_role": dict(present_by_role),
        "date_min": min(dated) if dated else "",
        "date_max": max(dated) if dated else "",
        "corpus_scope": corpus_scope(scope_labels) if n else corpus_scope([]),
    }


def guess_source_from_path(relative: str) -> str:
    lower = relative.lower()
    rules = (
        ("play", "google_play"),
        ("google", "google_play"),
        ("appstore", "app_store"),
        ("app_store", "app_store"),
        ("apple", "app_store"),
        ("reddit", "reddit"),
        ("youtube", "youtube"),
        ("instagram", "instagram"),
        ("twitter", "social"),
        ("facebook", "social"),
        ("q&a", "product_qa"),
        ("qa", "product_qa"),
        ("review", "product_reviews"),
    )
    for needle, label in rules:
        if needle in lower:
            return label
    parent = Path(relative).parts[0] if Path(relative).parts else "unknown"
    return parent if parent not in {".", ""} else "unknown"


def attach_file_meta(
    relative: str,
    fmt: str,
    size: int,
    records: list[dict[str, Any]],
    fields: list[dict[str, Any]],
    error: str | None,
) -> dict[str, Any]:
    roles = role_map(fields)
    return {
        "relative_path": relative,
        "format": fmt,
        "bytes": size,
        "record_count": len(records),
        "fields": fields,
        "roles": roles,
        "source_guess": guess_source_from_path(relative),
        "error": error,
        "records": records,
    }
