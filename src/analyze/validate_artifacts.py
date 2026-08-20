"""Validate extraction parquets: spans exist, statuses legal, ids join to relevant."""

from __future__ import annotations

from src.analyze.schema import EXTRACTION_COLUMNS, EXTRACTORS
from src.analyze.validate import locate_span
from src.qualify.config import ROOT


def main() -> int:
    import pyarrow.parquet as pq

    relevant = pq.read_table(ROOT / "data" / "processed" / "relevant.parquet")
    by_id = {str(row["record_id"]): str(row["text"] or "") for row in relevant.to_pylist()}
    problems = 0
    for extractor in EXTRACTORS:
        path = ROOT / "data" / "extractions" / f"{extractor}s.parquet"
        table = pq.read_table(path)
        missing_cols = [name for name in EXTRACTION_COLUMNS if name not in table.column_names]
        if missing_cols:
            print("FAIL columns", path.name, missing_cols)
            problems += 1
            continue
        rows = table.to_pylist()
        bad_span = 0
        bad_status = 0
        orphan = 0
        empty_span = 0
        for row in rows:
            span = str(row.get("evidence_span") or "")
            record_id = str(row.get("record_id") or "")
            text = by_id.get(record_id)
            if text is None:
                orphan += 1
            elif not span:
                empty_span += 1
            elif not locate_span(text, span):
                bad_span += 1
            if row.get("status") not in {"observed_evidence", "hypothesis"}:
                bad_status += 1
        print(
            path.name,
            "rows",
            len(rows),
            "bad_span",
            bad_span,
            "empty_span",
            empty_span,
            "orphan",
            orphan,
            "bad_status",
            bad_status,
        )
        problems += bad_span + empty_span + orphan + bad_status
    print("validation_problems", problems)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
