"""Phase 4 table contracts. Every metric names its denominator. Segments require recurring evidence."""

from __future__ import annotations

from typing import Any

MIN_RECURRING_RECORDS = 3
SMALL_N_CATEGORY = 30
# Architecture: keep evidence IDs on every cluster. Do not truncate.
EVIDENCE_ID_CAP: int | None = None

# Category cuts named in the architecture. Rows may also include unlabeled / other buckets from Phase 2.
ARCHITECTURE_CATEGORIES = (
    "Clothing",
    "Footwear",
    "Accessories",
    "Beauty",
    "Ethnic wear",
    "Western wear",
    "Sportswear",
)

THEME_COLUMNS = (
    "theme_id",
    "label",
    "extractor",
    "mention_count",
    "unique_records",
    "observed_records",
    "hypothesis_records",
    "pct_relevant",
    "denominator",
    "denominator_label",
    "mean_confidence",
    "source_mix",
    "category_mix",
    "segment_mix",
    "evidence_record_ids",
    "extraction_ids",
    "status",
)

SEGMENT_COLUMNS = (
    "segment_id",
    "label",
    "definition",
    "unique_records",
    "observed_records",
    "pct_relevant",
    "denominator",
    "denominator_label",
    "dominant_barriers",
    "dominant_needs",
    "evidence_record_ids",
    "status",
)

CATEGORY_DIFF_COLUMNS = (
    "category",
    "theme_or_barrier",
    "extractor",
    "unique_records",
    "pct_in_category",
    "denominator",
    "denominator_label",
    "n_small",
    "evidence_record_ids",
    "status",
)

METRIC_COLUMNS = (
    "metric_id",
    "name",
    "value",
    "numerator",
    "denominator",
    "denominator_label",
    "slice_source",
    "slice_segment",
    "slice_category",
    "n",
    "status",
)

THEME_TYPES = {
    "theme_id": "string",
    "label": "string",
    "extractor": "string",
    "mention_count": "int",
    "unique_records": "int",
    "observed_records": "int",
    "hypothesis_records": "int",
    "pct_relevant": "float",
    "denominator": "int",
    "denominator_label": "string",
    "mean_confidence": "float",
    "source_mix": "string",
    "category_mix": "string",
    "segment_mix": "string",
    "evidence_record_ids": "string",
    "extraction_ids": "string",
    "status": "string",
}

SEGMENT_TYPES = {
    "segment_id": "string",
    "label": "string",
    "definition": "string",
    "unique_records": "int",
    "observed_records": "int",
    "pct_relevant": "float",
    "denominator": "int",
    "denominator_label": "string",
    "dominant_barriers": "string",
    "dominant_needs": "string",
    "evidence_record_ids": "string",
    "status": "string",
}

CATEGORY_DIFF_TYPES = {
    "category": "string",
    "theme_or_barrier": "string",
    "extractor": "string",
    "unique_records": "int",
    "pct_in_category": "float",
    "denominator": "int",
    "denominator_label": "string",
    "n_small": "bool",
    "evidence_record_ids": "string",
    "status": "string",
}

METRIC_TYPES = {
    "metric_id": "string",
    "name": "string",
    "value": "float",
    "numerator": "float",
    "denominator": "float",
    "denominator_label": "string",
    "slice_source": "string",
    "slice_segment": "string",
    "slice_category": "string",
    "n": "int",
    "status": "string",
}


def empty_row(columns: tuple[str, ...]) -> dict[str, Any]:
    return {name: None for name in columns}


def normalize_label(label: str) -> str:
    return str(label or "").strip().lower().replace(" ", "_")


def pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(100.0 * numerator / denominator, 4)
