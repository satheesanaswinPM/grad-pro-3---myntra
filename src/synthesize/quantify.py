"""Quantify mentions, % of relevant, source/category mix, co-occurrence, and time trend."""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from typing import Any

from src.synthesize.io import join_ids
from src.synthesize.schema import (
    ARCHITECTURE_CATEGORIES,
    MIN_RECURRING_RECORDS,
    SMALL_N_CATEGORY,
    pct,
)


def month_key(value: Any) -> str:
    raw = str(value or "").strip()
    if len(raw) >= 7 and raw[4] == "-" and raw[:4].isdigit() and raw[5:7].isdigit():
        return raw[:7]
    return ""


def category_counts(relevant_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter(str(row.get("fashion_category") or "unlabeled") for row in relevant_rows)
    for name in ARCHITECTURE_CATEGORIES:
        counts.setdefault(name, 0)
    return dict(counts)


def category_diffs(
    extractions: list[dict[str, Any]],
    relevant_by_id: dict[str, dict[str, Any]],
    n_by_category: dict[str, int],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in extractions:
        if row["extractor"] != "barrier":
            continue
        linked = relevant_by_id.get(row["record_id"])
        if not linked:
            continue
        category = str(linked.get("fashion_category") or "unlabeled")
        grouped[(category, row["label"])].add(row["record_id"])

    diffs: list[dict[str, Any]] = []
    for (category, label), record_ids in grouped.items():
        denom = int(n_by_category.get(category) or 0)
        unique_n = len(record_ids)
        small = denom < SMALL_N_CATEGORY
        recurring = unique_n >= MIN_RECURRING_RECORDS and not small
        diffs.append(
            {
                "category": category,
                "theme_or_barrier": label,
                "extractor": "barrier",
                "unique_records": unique_n,
                "pct_in_category": pct(unique_n, denom),
                "denominator": denom,
                "denominator_label": f"relevant in category {category}",
                "n_small": small,
                "evidence_record_ids": join_ids(record_ids),
                "status": "observed_evidence" if recurring else "hypothesis",
            }
        )
    diffs.sort(key=lambda row: (bool(row["n_small"]), -int(row["unique_records"]), row["category"], row["theme_or_barrier"]))
    return diffs


def _metric(
    name: str,
    numerator: float,
    denominator: float,
    denominator_label: str,
    status: str,
    slice_source: str = "",
    slice_segment: str = "",
    slice_category: str = "",
) -> dict[str, Any]:
    value = round(float(numerator) / float(denominator), 6) if denominator else 0.0
    metric_id = "metric:" + "|".join(part for part in (name, slice_source, slice_segment, slice_category) if part)
    return {
        "metric_id": metric_id,
        "name": name,
        "value": value,
        "numerator": float(numerator),
        "denominator": float(denominator),
        "denominator_label": denominator_label,
        "slice_source": slice_source,
        "slice_segment": slice_segment,
        "slice_category": slice_category,
        "n": int(denominator),
        "status": status,
    }


def _cooccurrence(extractions: list[dict[str, Any]], n_extracted: int) -> list[dict[str, Any]]:
    by_record: dict[str, set[str]] = defaultdict(set)
    for row in extractions:
        by_record[row["record_id"]].add(f"{row['extractor']}:{row['label']}")
    pair_records: dict[tuple[str, str], set[str]] = defaultdict(set)
    for record_id, labels in by_record.items():
        for left, right in combinations(sorted(labels), 2):
            pair_records[(left, right)].add(record_id)
    rows: list[dict[str, Any]] = []
    for (left, right), record_ids in pair_records.items():
        unique_n = len(record_ids)
        if unique_n < 2:
            continue
        status = "observed_evidence" if unique_n >= MIN_RECURRING_RECORDS else "hypothesis"
        rows.append(
            _metric(
                f"cooccur:{left}|{right}",
                unique_n,
                n_extracted or 1,
                "extracted records",
                status,
            )
        )
    rows.sort(key=lambda row: (-row["numerator"], row["name"]))
    return rows


def metrics(
    relevant_rows: list[dict[str, Any]],
    relevant_by_id: dict[str, dict[str, Any]],
    extractions: list[dict[str, Any]],
    themes: list[dict[str, Any]],
    segments: list[dict[str, Any]],
    n_by_category: dict[str, int],
) -> list[dict[str, Any]]:
    n_relevant = len(relevant_rows)
    extracted_ids = {row["record_id"] for row in extractions}
    n_extracted = len(extracted_ids)
    rows: list[dict[str, Any]] = [
        _metric("n_relevant", n_relevant, n_relevant or 1, "relevant", "observed_evidence"),
        _metric("n_extracted_records", n_extracted, n_relevant or 1, "relevant", "observed_evidence"),
        _metric("extraction_coverage", n_extracted, n_relevant or 1, "relevant", "observed_evidence"),
        _metric("n_themes", len(themes), n_relevant or 1, "relevant", "observed_evidence"),
        _metric("n_segments", len(segments), n_relevant or 1, "relevant", "observed_evidence"),
        _metric("scrape_has_purchase_outcomes", 0, 1, "not in scrape", "hypothesis"),
    ]

    extracted_by_source: Counter[str] = Counter()
    for record_id in extracted_ids:
        source = str(relevant_by_id.get(record_id, {}).get("source") or "unknown")
        extracted_by_source[source] += 1
    source_counts = Counter(str(row.get("source") or "unknown") for row in relevant_rows)
    for source, count in source_counts.most_common():
        rows.append(
            _metric("n_relevant_by_source", count, n_relevant or 1, "relevant", "observed_evidence", slice_source=source)
        )
        rows.append(
            _metric(
                "n_extracted_by_source",
                extracted_by_source.get(source, 0),
                count or 1,
                f"relevant in source {source}",
                "observed_evidence",
                slice_source=source,
            )
        )

    extracted_by_category: Counter[str] = Counter()
    for record_id in extracted_ids:
        category = str(relevant_by_id.get(record_id, {}).get("fashion_category") or "unlabeled")
        extracted_by_category[category] += 1
    for category, count in sorted(n_by_category.items(), key=lambda item: (-item[1], item[0])):
        if count <= 0 and category not in ARCHITECTURE_CATEGORIES:
            continue
        status = "observed_evidence" if count >= SMALL_N_CATEGORY else "hypothesis"
        rows.append(
            _metric(
                "n_relevant_by_category",
                count,
                n_relevant or 1,
                "relevant",
                status,
                slice_category=category,
            )
        )
        rows.append(
            _metric(
                "n_extracted_by_category",
                extracted_by_category.get(category, 0),
                count,
                f"relevant in category {category}",
                status,
                slice_category=category,
            )
        )

    stage_counts = Counter(str(row.get("journey_stage") or "unlabeled") for row in relevant_rows)
    for stage, count in stage_counts.most_common():
        rows.append(
            _metric(
                f"n_relevant_by_journey_stage:{stage}",
                count,
                n_relevant or 1,
                "relevant",
                "observed_evidence",
            )
        )

    extractor_counts = Counter(row["extractor"] for row in extractions)
    for extractor, count in sorted(extractor_counts.items()):
        rows.append(
            _metric(f"n_extraction_rows:{extractor}", count, n_extracted or 1, "extracted records", "observed_evidence")
        )

    for theme in themes:
        rows.append(
            _metric(
                f"theme_unique_records:{theme['extractor']}:{theme['label']}",
                int(theme["unique_records"]),
                n_relevant or 1,
                "relevant",
                str(theme["status"]),
            )
        )
        if n_extracted:
            rows.append(
                _metric(
                    f"theme_share_of_extracted:{theme['extractor']}:{theme['label']}",
                    int(theme["unique_records"]),
                    n_extracted,
                    "extracted records",
                    str(theme["status"]),
                )
            )

    for segment in segments:
        rows.append(
            _metric(
                f"segment_unique_records:{segment['label']}",
                int(segment["unique_records"]),
                n_relevant or 1,
                "relevant",
                str(segment["status"]),
                slice_segment=str(segment["label"]),
            )
        )

    rows.extend(_cooccurrence(extractions, n_extracted or 1))

    dated = [row for row in relevant_rows if month_key(row.get("authored_at"))]
    rows.append(
        _metric(
            "relevant_with_authored_at",
            len(dated),
            n_relevant or 1,
            "relevant",
            "observed_evidence" if dated else "hypothesis",
        )
    )
    month_counts = Counter(month_key(row.get("authored_at")) for row in dated)
    date_coverage = len(dated) >= SMALL_N_CATEGORY and len(dated) * 2 >= n_relevant
    date_status = "observed_evidence" if date_coverage and len(month_counts) >= 2 else "hypothesis"
    for month, count in sorted(month_counts.items()):
        rows.append(
            _metric(
                f"relevant_by_month:{month}",
                count,
                len(dated) or 1,
                "relevant rows with authored_at",
                date_status,
            )
        )
    return rows
