"""Cluster extraction labels into themes. Keep evidence IDs on every cluster."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from src.synthesize.io import join_ids, mix_json
from src.synthesize.schema import MIN_RECURRING_RECORDS, pct


def cluster_themes(
    extractions: list[dict[str, Any]],
    relevant_by_id: dict[str, dict[str, Any]],
    n_relevant: int,
) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in extractions:
        if row["record_id"] not in relevant_by_id:
            continue
        buckets[(row["extractor"], row["label"])].append(row)

    themes: list[dict[str, Any]] = []
    for (extractor, label), items in sorted(buckets.items()):
        record_ids = [item["record_id"] for item in items]
        unique_ids = sorted(set(record_ids))
        observed_ids = {item["record_id"] for item in items if item["status"] == "observed_evidence"}
        hypothesis_ids = {item["record_id"] for item in items if item["status"] == "hypothesis"}
        sources: Counter[str] = Counter()
        categories: Counter[str] = Counter()
        for record_id in unique_ids:
            linked = relevant_by_id[record_id]
            sources[str(linked.get("source") or "unknown")] += 1
            categories[str(linked.get("fashion_category") or "unlabeled")] += 1
        mean_confidence = round(sum(item["confidence"] for item in items) / len(items), 4)
        recurring = len(unique_ids) >= MIN_RECURRING_RECORDS and len(observed_ids) >= MIN_RECURRING_RECORDS
        themes.append(
            {
                "theme_id": f"theme:{extractor}:{label}",
                "label": label,
                "extractor": extractor,
                "mention_count": len(items),
                "unique_records": len(unique_ids),
                "observed_records": len(observed_ids),
                "hypothesis_records": len(hypothesis_ids),
                "pct_relevant": pct(len(unique_ids), n_relevant),
                "denominator": n_relevant,
                "denominator_label": "relevant",
                "mean_confidence": mean_confidence,
                "source_mix": mix_json(dict(sources)),
                "category_mix": mix_json(dict(categories)),
                "segment_mix": "{}",
                "evidence_record_ids": join_ids(unique_ids),
                "extraction_ids": join_ids([item["extraction_id"] for item in items]),
                "status": "observed_evidence" if recurring else "hypothesis",
                "_record_ids": unique_ids,
            }
        )
    themes.sort(key=lambda row: (-int(row["unique_records"]), row["extractor"], row["label"]))
    return themes


def apply_segment_mix(themes: list[dict[str, Any]], record_segments: dict[str, list[str]]) -> None:
    for theme in themes:
        mix: Counter[str] = Counter()
        record_ids = theme.get("_record_ids") or [
            part for part in str(theme.get("evidence_record_ids") or "").split("|") if part
        ]
        for record_id in record_ids:
            for segment in record_segments.get(str(record_id), []):
                mix[segment] += 1
        theme["segment_mix"] = mix_json(dict(mix))
