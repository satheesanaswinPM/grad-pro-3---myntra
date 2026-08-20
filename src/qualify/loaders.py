"""Read raw scrape files into record dicts. Never writes to data/raw/."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterator

from src.qualify.config import SKIP_NAMES, SKIP_SUFFIXES

MAX_EXAMPLE_LEN = 180
MAX_JSON_BYTES = 200 * 1024 * 1024


def iter_raw_files(raw_dir: Path) -> list[Path]:
    if not raw_dir.exists():
        return []
    files: list[Path] = []
    for path in sorted(raw_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name.lower() in SKIP_NAMES:
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        files.append(path)
    return files


def flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, dict):
                out.update(flatten(value, name))
            elif isinstance(value, list):
                if value and all(isinstance(x, dict) for x in value):
                    continue
                out[name] = "; ".join(_stringify(x) for x in value[:8])
            else:
                out[name] = value
        return out
    return {prefix or "value": obj}


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)[:MAX_EXAMPLE_LEN]
    return str(value)


def _looks_like_record(item: Any) -> bool:
    if not isinstance(item, dict) or not item:
        return False
    string_fields = 0
    long_string = False
    for value in item.values():
        if isinstance(value, str):
            string_fields += 1
            if len(value.strip()) >= 20:
                long_string = True
    return string_fields >= 1 and (long_string or len(item) >= 2)


def extract_record_lists(obj: Any, found: list[list[dict]] | None = None) -> list[list[dict]]:
    if found is None:
        found = []
    if isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj):
        if sum(1 for x in obj[:50] if _looks_like_record(x)) >= max(1, min(3, len(obj[:50]) // 2)):
            found.append(obj)
        for item in obj[:20]:
            extract_record_lists(item, found)
    elif isinstance(obj, dict):
        for value in obj.values():
            extract_record_lists(value, found)
    return found


def records_from_json_obj(obj: Any) -> list[dict[str, Any]]:
    if isinstance(obj, list):
        if obj and all(isinstance(x, str) for x in obj):
            return [{"text": x} for x in obj]
        if obj and all(isinstance(x, dict) for x in obj):
            return [flatten(x) for x in obj]
        records: list[dict[str, Any]] = []
        for item in obj:
            records.extend(records_from_json_obj(item))
        return records
    if isinstance(obj, dict):
        lists = extract_record_lists(obj)
        if lists:
            best = max(lists, key=len)
            return [flatten(x) for x in best]
        return [flatten(obj)]
    if isinstance(obj, str) and obj.strip():
        return [{"text": obj}]
    return []


def load_json(path: Path) -> list[dict[str, Any]]:
    size = path.stat().st_size
    if size > MAX_JSON_BYTES:
        raise RuntimeError(f"JSON file exceeds {MAX_JSON_BYTES} bytes; split or convert to JSONL")
    text = path.read_text(encoding="utf-8", errors="replace")
    stripped = text.lstrip()
    if not stripped:
        return []
    if stripped[0] not in "{[":
        records: list[dict[str, Any]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            records.extend(records_from_json_obj(json.loads(line)))
        return records
    return records_from_json_obj(json.loads(text))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if isinstance(obj, dict):
                records.append(flatten(obj))
            else:
                records.extend(records_from_json_obj(obj))
    return records


def load_csv(path: Path, delimiter: str) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        reader: csv.DictReader
        if delimiter == "\t":
            reader = csv.DictReader(handle, delimiter="\t")
        else:
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",\t|;")
                reader = csv.DictReader(handle, dialect=dialect)
            except csv.Error:
                reader = csv.DictReader(handle, delimiter=delimiter)
        rows = []
        for row in reader:
            rows.append({str(k): v for k, v in row.items() if k is not None})
        return rows


def load_txt(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            records.append({"text": line})
    return records


def load_parquet(path: Path) -> list[dict[str, Any]]:
    try:
        import pyarrow.parquet as pq  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install pyarrow to inspect .parquet files") from exc
    table = pq.read_table(path)
    return [{str(k): v for k, v in row.items()} for row in table.to_pylist()]


def load_xlsx(path: Path) -> list[dict[str, Any]]:
    try:
        import openpyxl  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install openpyxl to inspect .xlsx files") from exc
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    records: list[dict[str, Any]] = []
    for sheet in workbook.worksheets:
        rows = sheet.iter_rows(values_only=True)
        try:
            header = next(rows)
        except StopIteration:
            continue
        names = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(header)]
        for row in rows:
            records.append({names[i]: row[i] if i < len(row) else None for i in range(len(names))})
    return records


def load_file(path: Path) -> tuple[str, list[dict[str, Any]], str | None]:
    suffix = path.suffix.lower()
    try:
        if suffix == ".json":
            return "json", load_json(path), None
        if suffix in {".jsonl", ".ndjson"}:
            return "jsonl", load_jsonl(path), None
        if suffix == ".csv":
            return "csv", load_csv(path, ","), None
        if suffix == ".tsv":
            return "tsv", load_csv(path, "\t"), None
        if suffix == ".txt":
            return "txt", load_txt(path), None
        if suffix == ".parquet":
            return "parquet", load_parquet(path), None
        if suffix in {".xlsx", ".xls"}:
            return "xlsx", load_xlsx(path), None
    except Exception as exc:  # noqa: BLE001 — inspection must continue across files
        return suffix.lstrip(".") or "unknown", [], str(exc)
    return suffix.lstrip(".") or "unknown", [], f"Unsupported format: {suffix or 'no extension'}"


def iter_loaded(raw_dir: Path) -> Iterator[tuple[Path, str, list[dict[str, Any]], str | None]]:
    for path in iter_raw_files(raw_dir):
        fmt, records, error = load_file(path)
        yield path, fmt, records, error
