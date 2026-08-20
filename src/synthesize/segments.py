"""Behavioral segments only where the same pattern recurs in evidence. Do not invent personas."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from src.synthesize.io import join_ids
from src.synthesize.schema import MIN_RECURRING_RECORDS, pct

# Architecture candidates. A segment is emitted only if unique observed records meet MIN_RECURRING_RECORDS.
CANDIDATE_SEGMENTS: tuple[dict[str, Any], ...] = (
    {
        "label": "high_intent",
        "definition": "Records with extracted strong_purchase intent.",
        "intent": frozenset({"strong_purchase"}),
    },
    {
        "label": "bookmarkers",
        "definition": "Records with extracted bookmark / save-for-later intent.",
        "intent": frozenset({"bookmark"}),
    },
    {
        "label": "comparers",
        "definition": "Records with extracted comparison intent, barrier, or behavior.",
        "intent": frozenset({"comparison"}),
        "barrier": frozenset({"comparison"}),
        "behavior": frozenset({"comparison"}),
    },
    {
        "label": "fit_conscious",
        "definition": "Records with extracted fit barrier or will_it_fit need.",
        "barrier": frozenset({"fit"}),
        "need": frozenset({"will_it_fit"}),
    },
    {
        "label": "occasion",
        "definition": "Records with extracted occasion intent, barrier, or need.",
        "intent": frozenset({"occasion"}),
        "barrier": frozenset({"occasion"}),
        "need": frozenset({"right_for_occasion"}),
    },
    {
        "label": "social_validation",
        "definition": "Records with extracted friends/family or influencer research behavior.",
        "behavior": frozenset({"external:friends_family", "external:influencer"}),
    },
    {
        "label": "quality",
        "definition": "Records with extracted quality barrier or is_quality_worth_it need.",
        "barrier": frozenset({"quality"}),
        "need": frozenset({"is_quality_worth_it"}),
    },
    {
        "label": "inspiration",
        "definition": "Records with extracted inspiration intent.",
        "intent": frozenset({"inspiration"}),
    },
)


def _labels_by_extractor(items: list[dict[str, Any]]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    for item in items:
        grouped[item["extractor"]].add(item["label"])
    return grouped


def _matches(candidate: dict[str, Any], by_extractor: dict[str, set[str]]) -> bool:
    for extractor in ("intent", "barrier", "need", "behavior"):
        wanted = candidate.get(extractor)
        if wanted and (by_extractor.get(extractor, set()) & wanted):
            return True
    return False


def _dominant(items: list[dict[str, Any]], extractor: str, limit: int = 3) -> str:
    counts = Counter(item["label"] for item in items if item["extractor"] == extractor)
    return "|".join(f"{label}:{count}" for label, count in counts.most_common(limit))


def form_segments(
    extractions: list[dict[str, Any]],
    relevant_by_id: dict[str, dict[str, Any]],
    n_relevant: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in extractions:
        if row["record_id"] in relevant_by_id:
            by_record[row["record_id"]].append(row)

    segments: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for candidate in CANDIDATE_SEGMENTS:
        observed_ids: list[str] = []
        matched_items: list[dict[str, Any]] = []
        for record_id, items in by_record.items():
            observed_items = [item for item in items if item["status"] == "observed_evidence"]
            if not observed_items or not _matches(candidate, _labels_by_extractor(observed_items)):
                continue
            observed_ids.append(record_id)
            matched_items.extend(observed_items)
        observed_n = len(set(observed_ids))
        if observed_n < MIN_RECURRING_RECORDS:
            skipped.append(
                {
                    "label": candidate["label"],
                    "unique_records": observed_n,
                    "observed_records": observed_n,
                    "reason": f"needs {MIN_RECURRING_RECORDS}+ unique observed records to exist as a segment",
                }
            )
            continue
        segments.append(
            {
                "segment_id": f"segment:{candidate['label']}",
                "label": candidate["label"],
                "definition": candidate["definition"],
                "unique_records": observed_n,
                "observed_records": observed_n,
                "pct_relevant": pct(observed_n, n_relevant),
                "denominator": n_relevant,
                "denominator_label": "relevant",
                "dominant_barriers": _dominant(matched_items, "barrier"),
                "dominant_needs": _dominant(matched_items, "need"),
                "evidence_record_ids": join_ids(observed_ids),
                "status": "observed_evidence",
            }
        )
    segments.sort(key=lambda row: (-int(row["unique_records"]), row["label"]))
    return segments, skipped


def record_segment_map(segments: list[dict[str, Any]]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = defaultdict(list)
    for segment in segments:
        for record_id in str(segment.get("evidence_record_ids") or "").split("|"):
            if record_id:
                mapping[record_id].append(str(segment["label"]))
    return dict(mapping)
