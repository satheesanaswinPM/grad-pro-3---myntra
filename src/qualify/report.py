"""Write Phase 0 artifacts. Never writes into data/raw/."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join("" if c is None else str(c) for c in row) + " |" for row in rows]
    return "\n".join([line, sep, *body]) if rows else line + "\n" + sep + "\n| _(empty)_ |"


def write_schema_catalog(path: Path, files: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    catalog = {
        "generated_at": summary["generated_at"],
        "raw_root": "data/raw/",
        "note": "Phase 0 inspects raw files in place. Raw data is never overwritten.",
        "file_count": summary["file_count"],
        "record_count": summary["record_count"],
        "files": [
            {
                "relative_path": f["relative_path"],
                "format": f["format"],
                "bytes": f["bytes"],
                "record_count": f["record_count"],
                "source_guess": f["source_guess"],
                "roles": f["roles"],
                "error": f["error"],
                "fields": f["fields"],
            }
            for f in files
        ],
    }
    path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_source_coverage(path: Path, summary: dict[str, Any]) -> None:
    rows = summary.get("source_coverage") or []
    fieldnames = [
        "source",
        "files",
        "records",
        "pct_of_records",
        "unique_text",
        "duplicate_text_extras",
        "missing_text_pct",
        "date_min",
        "date_max",
        "myntra_records",
        "broader_fashion_records",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def write_quality_report(
    path: Path,
    summary: dict[str, Any],
    files: list[dict[str, Any]],
    raw_dir: Path,
    raw_file_count: int,
) -> None:
    n = summary["record_count"]
    denom = n or 1
    missing = summary.get("missing_by_role") or {}
    present = summary.get("present_by_role") or {}
    languages = summary.get("language") or {}
    scope = summary.get("corpus_scope") or {}
    errors = summary.get("load_errors") or []

    field_rows = []
    for role in (
        "text",
        "source",
        "date",
        "rating",
        "product_or_category",
        "user_key",
        "url",
    ):
        have = present.get(role, 0)
        miss = missing.get(role, 0)
        field_rows.append(
            [role, have, miss, round(100.0 * miss / denom, 2) if n else "n/a"]
        )

    file_rows = [
        [
            f["relative_path"],
            f["format"],
            f["bytes"],
            f["record_count"],
            f["source_guess"],
            f["error"] or "",
        ]
        for f in files
    ]

    lang_rows = [[k, v, round(100.0 * v / denom, 2)] for k, v in languages.items()]
    source_rows = [
        [
            r["source"],
            r["records"],
            r["pct_of_records"],
            r["unique_text"],
            r["missing_text_pct"],
        ]
        for r in summary.get("source_coverage") or []
    ]

    blocker = ""
    if raw_file_count == 0:
        blocker = (
            "\n**Blocker:** `data/raw/` has no scrape files yet. Drop the original dataset "
            "into `data/raw/` (do not overwrite later) and re-run `python -m src.qualify`.\n"
        )

    error_section = "None."
    if errors:
        error_section = _md_table(
            ["File", "Error"],
            [[e["path"], e["error"]] for e in errors],
        )

    body = f"""# Data quality report — Phase 0

Generated: {summary["generated_at"]}  
Raw root: `{raw_dir.as_posix()}` (read-only)  
Records inspected: **{n}** across **{summary["file_count"]}** file(s)
{blocker}
This report inventories the scrape before any cleaning, LLM extraction, or modelling.
Original files were not modified.

## 1. Files and folders

{_md_table(["Relative path", "Format", "Bytes", "Records", "Source guess", "Load error"], file_rows) if file_rows else "_No inspectable files under data/raw/._"}

## 2. Formats and schemas

Per-file field names, inferred CanonicalFeedback roles, dtypes, and missingness are in [`schema_catalog.json`](schema_catalog.json).

Inferred roles are name-based heuristics (e.g. `review_text` → `text`). They are not ground truth.

## 3. Available fields (CanonicalFeedback mapping)

{_md_table(["Role", "Non-empty records", "Missing", "Missing %"], field_rows)}

Population for missing %: all inspected records (n = {n}).

## 4. Record count

- Files walked: {raw_file_count}
- Files parsed into the catalog: {summary["file_count"]}
- Total records: {n}

## 5. Duplicates

- Extra copies of the same **full row**: {summary.get("duplicate_full_row_extras", 0)}
- Extra copies of the same **text** (case-insensitive SHA-256, empty text excluded): {summary.get("duplicate_text_extras", 0)}
- Unique non-empty texts: {summary.get("unique_text", 0)}
- Empty text records: {summary.get("empty_text", 0)}

Duplicates are counted, not removed. Deduplication is Phase 1.

## 6. Missing values

See the role table above and per-field `missing_pct` in the schema catalog.

## 7. Language distribution

Heuristic script + token tagging only (not an LLM). Labels include `en`, `hi`, `hinglish`, other Indic scripts, `latin-other`, `empty`, `unknown`.

{_md_table(["Language", "Records", "% of records"], lang_rows) if lang_rows else "_No text to tag._"}

Population: all inspected records (n = {n}). Non-English rows are **not** dropped in Phase 0.

## 8. Source distribution

Folder/file names supply `source_guess` when a `source` column is absent. Full breakdown: [`source_coverage.csv`](source_coverage.csv).

{_md_table(["Source", "Records", "%", "Unique text", "Missing text %"], source_rows) if source_rows else "_No records._"}

Population: all inspected records (n = {n}).

## 9. Myntra vs broader fashion shopping

{scope.get("overall", "n/a")}

- Myntra signal (mentions in path, source, or text): {scope.get("pct_myntra_signal", 0)}%
- Other-retailer signal: {scope.get("pct_broader_signal", 0)}%
- Unlabeled: {scope.get("pct_unlabeled", 0)}%
- Label counts: `{json.dumps(scope.get("counts") or {})}`

This is corpus coverage, not a claim about why wishlists fail to convert.

## 10. Date span

- Min date string (raw, unparsed): {summary.get("date_min") or "n/a"}
- Max date string (raw, unparsed): {summary.get("date_max") or "n/a"}

## Load errors

{error_section}

## What Phase 0 did not do

- No writes under `data/raw/`
- No LLM extraction, sentiment, or topic modelling
- No assumption that price, size, reviews, or discounts are the user problem
- No processed/canonical dataset (that is Phase 1)

## Exit gate

- Quality report: this file
- Schema catalog: `reports/schema_catalog.json`
- Source coverage: `reports/source_coverage.csv`
- Raw files untouched: yes

Re-run after adding or replacing files in `data/raw/`:

```bash
python -m src.qualify
```
"""
    path.write_text(body, encoding="utf-8")
