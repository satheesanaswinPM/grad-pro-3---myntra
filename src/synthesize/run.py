"""Phase 4: themes, segments, and numbered patterns. Never writes to data/raw/."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from src.ingest.env import load_dotenv
from src.qualify.config import LOGS_DIR, ROOT
from src.synthesize.cluster import apply_segment_mix, cluster_themes
from src.synthesize.io import (
    SYNTHESIS,
    load_extractions,
    load_relevant,
    relevant_index,
    required_inputs,
    write_rows,
)
from src.synthesize.quantify import category_counts, category_diffs, metrics
from src.synthesize.schema import (
    CATEGORY_DIFF_COLUMNS,
    CATEGORY_DIFF_TYPES,
    METRIC_COLUMNS,
    METRIC_TYPES,
    MIN_RECURRING_RECORDS,
    SEGMENT_COLUMNS,
    SEGMENT_TYPES,
    SMALL_N_CATEGORY,
    THEME_COLUMNS,
    THEME_TYPES,
)
from src.synthesize.segments import form_segments, record_segment_map

MANIFEST = SYNTHESIS / "manifest.json"


def _logger() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("phase4")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(LOGS_DIR / "synthesize.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


def run() -> dict[str, Any]:
    load_dotenv()
    logger = _logger()
    missing = [path for path in required_inputs() if not path.exists()]
    if missing:
        names = ", ".join(str(path.relative_to(ROOT)).replace("\\", "/") for path in missing)
        raise FileNotFoundError(f"Missing Phase 3/2 inputs: {names}. Run python -m src.process and python -m src.analyze first.")

    relevant_rows = load_relevant()
    if not relevant_rows:
        raise RuntimeError("data/processed/relevant.parquet is empty. Re-run python -m src.process.")
    relevant_by_id = relevant_index(relevant_rows)
    extractions = load_extractions()
    n_relevant = len(relevant_rows)
    extracted_ids = {row["record_id"] for row in extractions if row["record_id"] in relevant_by_id}
    orphan = sum(1 for row in extractions if row["record_id"] not in relevant_by_id)
    extractions = [row for row in extractions if row["record_id"] in relevant_by_id]

    logger.info(
        "Phase 4 starting. relevant=%s extracted_records=%s extraction_rows=%s orphans=%s",
        n_relevant,
        len(extracted_ids),
        len(extractions),
        orphan,
    )

    themes = cluster_themes(extractions, relevant_by_id, n_relevant)
    segments, skipped_segments = form_segments(extractions, relevant_by_id, n_relevant)
    apply_segment_mix(themes, record_segment_map(segments))
    n_by_category = category_counts(relevant_rows)
    diffs = category_diffs(extractions, relevant_by_id, n_by_category)
    metric_rows = metrics(relevant_rows, relevant_by_id, extractions, themes, segments, n_by_category)

    write_rows(themes, SYNTHESIS / "themes.parquet", THEME_COLUMNS, THEME_TYPES)
    write_rows(segments, SYNTHESIS / "segments.parquet", SEGMENT_COLUMNS, SEGMENT_TYPES)
    write_rows(diffs, SYNTHESIS / "category_diffs.parquet", CATEGORY_DIFF_COLUMNS, CATEGORY_DIFF_TYPES)
    write_rows(metric_rows, SYNTHESIS / "metrics.parquet", METRIC_COLUMNS, METRIC_TYPES)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest = {
        "generated_at": generated_at,
        "n_relevant": n_relevant,
        "n_extracted_records": len(extracted_ids),
        "n_extraction_rows": len(extractions),
        "orphan_extractions": orphan,
        "extraction_coverage_pct": round(100.0 * len(extracted_ids) / n_relevant, 4) if n_relevant else 0,
        "n_themes": len(themes),
        "n_themes_observed": sum(1 for row in themes if row["status"] == "observed_evidence"),
        "n_segments": len(segments),
        "skipped_segments": skipped_segments,
        "n_category_diffs": len(diffs),
        "n_metrics": len(metric_rows),
        "min_recurring_records": MIN_RECURRING_RECORDS,
        "small_n_category": SMALL_N_CATEGORY,
        "outputs": {
            "themes": "data/synthesis/themes.parquet",
            "segments": "data/synthesis/segments.parquet",
            "category_diffs": "data/synthesis/category_diffs.parquet",
            "metrics": "data/synthesis/metrics.parquet",
        },
        "notes": [
            "Percentages use the named denominator on each row. pct_relevant is unique_records / relevant.",
            "Theme frequency is not purchase causality. scrape_has_purchase_outcomes is hypothesis.",
            "Segments are omitted until they have recurring observed evidence; they are not invented personas.",
            "Category cuts with n_small=true are not robust.",
        ],
    }
    SYNTHESIS.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info(
        "Phase 4 done. themes=%s (observed=%s) segments=%s category_diffs=%s metrics=%s",
        len(themes),
        manifest["n_themes_observed"],
        len(segments),
        len(diffs),
        len(metric_rows),
    )
    return manifest


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
