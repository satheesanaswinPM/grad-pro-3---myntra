"""Load Phase 3 extractions and write Phase 4 tables. Never writes to data/raw/."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.analyze.schema import EXTRACTORS
from src.qualify.config import ROOT
from src.synthesize.schema import EVIDENCE_ID_CAP, normalize_label

RELEVANT = ROOT / "data" / "processed" / "relevant.parquet"
EXTRACTIONS = ROOT / "data" / "extractions"
SYNTHESIS = ROOT / "data" / "synthesis"

RELEVANT_KEEP = (
    "record_id",
    "source",
    "authored_at",
    "language",
    "fashion_category",
    "journey_stage",
    "inclusion_rules",
    "external_destinations",
)


def extraction_path(extractor: str) -> Path:
    return EXTRACTIONS / f"{extractor}s.parquet"


def required_inputs() -> list[Path]:
    return [RELEVANT, *[extraction_path(name) for name in EXTRACTORS]]


def load_parquet(path: Path) -> list[dict[str, Any]]:
    import pyarrow.parquet as pq

    if not path.exists():
        raise FileNotFoundError(path)
    return pq.read_table(path).to_pylist()


def load_relevant() -> list[dict[str, Any]]:
    rows = []
    for row in load_parquet(RELEVANT):
        rows.append({key: row.get(key) for key in RELEVANT_KEEP})
    return rows


def load_extractions() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for extractor in EXTRACTORS:
        path = extraction_path(extractor)
        for row in load_parquet(path):
            label = normalize_label(str(row.get("label") or ""))
            record_id = str(row.get("record_id") or "")
            extraction_id = str(row.get("extraction_id") or "")
            if not label or not record_id or not extraction_id:
                continue
            status = str(row.get("status") or "")
            if status not in {"observed_evidence", "hypothesis"}:
                continue
            try:
                confidence = float(row.get("confidence") or 0)
            except (TypeError, ValueError):
                confidence = 0.0
            rows.append(
                {
                    "extraction_id": extraction_id,
                    "record_id": record_id,
                    "extractor": str(row.get("extractor") or extractor),
                    "label": label,
                    "status": status,
                    "confidence": max(0.0, min(1.0, confidence)),
                    "evidence_span": str(row.get("evidence_span") or ""),
                }
            )
    return rows


def relevant_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["record_id"]): row for row in rows if row.get("record_id")}


def join_ids(values: list[str] | set[str], cap: int | None = EVIDENCE_ID_CAP) -> str:
    ordered = sorted({str(value) for value in values if value})
    if cap is not None:
        ordered = ordered[:cap]
    return "|".join(ordered)


def mix_json(counter: dict[str, int]) -> str:
    clean = {str(key): int(value) for key, value in sorted(counter.items()) if key}
    return json.dumps(clean, ensure_ascii=False, sort_keys=True)


def _arrow_type(kind: str):
    import pyarrow as pa

    return {
        "string": pa.string(),
        "int": pa.int64(),
        "float": pa.float64(),
        "bool": pa.bool_(),
    }[kind]


def _coerce(value: Any, kind: str) -> Any:
    if kind == "string":
        return "" if value is None else str(value)
    if kind == "int":
        return 0 if value is None else int(value)
    if kind == "float":
        return 0.0 if value is None else float(value)
    if kind == "bool":
        return bool(value)
    return value


def write_rows(rows: list[dict[str, Any]], path: Path, columns: tuple[str, ...], types: dict[str, str]) -> None:
    import pyarrow as pa
    import pyarrow.parquet as pq

    schema = pa.schema([(name, _arrow_type(types[name])) for name in columns])
    payload = [{name: _coerce(row.get(name), types[name]) for name in columns} for row in rows]
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(payload, schema=schema) if payload else pa.Table.from_pylist([], schema=schema)
    pq.write_table(table, path, compression="zstd")
