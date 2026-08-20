"""Publish the scoring formula. Do not inflate scores. Do not recommend monetary incentives."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

from src.score.statements import copy_for
from src.score.schema import (
    APP_UX_LABELS,
    APP_UX_SOURCES,
    DIMENSION_WEIGHTS,
    EXTRACTOR_SEVERITY,
    FORMULA_VERSION,
    FREQ_SATURATION,
    HESITATION_INCLUSION,
    OPPORTUNITY_GROUPS,
    PATH_STAGES,
    SKIP_INTENT_LABELS,
    STAGE_SEVERITY,
    clamp01,
)
from src.synthesize.io import join_ids, mix_json
from src.synthesize.schema import MIN_RECURRING_RECORDS, SMALL_N_CATEGORY, pct


def _ids(raw: Any) -> list[str]:
    return [part for part in str(raw or "").split("|") if part]


def _mean(values: list[float], default: float = 0.0) -> float:
    if not values:
        return default
    return sum(values) / len(values)


def _grouped_members() -> dict[tuple[str, str], str]:
    mapping: dict[tuple[str, str], str] = {}
    for key, members in OPPORTUNITY_GROUPS:
        for member in members:
            mapping[member] = key
    return mapping


def build_candidates(themes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One candidate per problem group (union of theme evidence). Intent-only non-problems are skipped."""
    grouped = _grouped_members()
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for theme in themes:
        extractor = str(theme.get("extractor") or "")
        label = str(theme.get("label") or "")
        if extractor == "intent" and label in SKIP_INTENT_LABELS:
            continue
        if extractor == "intent" and label not in {"uncertain", "bookmark", "future_purchase", "price_watch", "comparison"}:
            continue
        key = grouped.get((extractor, label), f"{extractor}:{label}")
        buckets[key].append(theme)

    candidates: list[dict[str, Any]] = []
    for key, members in buckets.items():
        record_ids: set[str] = set()
        confidences: list[float] = []
        extractors: Counter[str] = Counter()
        labels: list[str] = []
        theme_ids: list[str] = []
        statuses: list[str] = []
        observed_num = 0
        observed_den = 0
        for theme in members:
            ids = _ids(theme.get("evidence_record_ids"))
            record_ids.update(ids)
            confidences.append(float(theme.get("mean_confidence") or 0))
            extractors[str(theme.get("extractor") or "")] += int(theme.get("unique_records") or 0)
            labels.append(str(theme.get("label") or ""))
            theme_ids.append(str(theme.get("theme_id") or ""))
            statuses.append(str(theme.get("status") or "hypothesis"))
            observed_num += int(theme.get("observed_records") or 0)
            observed_den += int(theme.get("unique_records") or 0)
        primary = extractors.most_common(1)[0][0] if extractors else "barrier"
        primary_label = labels[0] if labels else key
        n_unique = len(record_ids)
        observed_ratio = (observed_num / observed_den) if observed_den else 0.0
        n_observed = int(round(observed_ratio * n_unique))
        observed = n_unique >= MIN_RECURRING_RECORDS and "observed_evidence" in statuses
        candidates.append(
            {
                "key": key,
                "extractor": primary,
                "label": primary_label,
                "theme_ids": theme_ids,
                "record_ids": sorted(record_ids),
                "n_unique": n_unique,
                "n_observed": n_observed,
                "mean_confidence": _mean(confidences),
                "status": "observed_evidence" if observed else "hypothesis",
            }
        )
    return candidates


def _frequency(n_unique: int, n_relevant: int) -> float:
    if n_relevant <= 0:
        return 0.0
    share = n_unique / n_relevant
    return clamp01(share / FREQ_SATURATION)


def _severity(record_ids: list[str], extractor: str, relevant_by_id: dict[str, dict[str, Any]]) -> float:
    weights = [
        STAGE_SEVERITY.get(str(relevant_by_id.get(record_id, {}).get("journey_stage") or "unlabeled"), 0.30)
        for record_id in record_ids
    ]
    base = _mean(weights, 0.30)
    return clamp01(base * EXTRACTOR_SEVERITY.get(extractor, 0.80))


def _hesitation(
    record_ids: list[str],
    label: str,
    source_mix: dict[str, int],
    relevant_by_id: dict[str, dict[str, Any]],
) -> float:
    if not record_ids:
        return 0.0
    path_hits = 0
    inclusion_hits = 0
    for record_id in record_ids:
        row = relevant_by_id.get(record_id) or {}
        stage = str(row.get("journey_stage") or "")
        if stage in PATH_STAGES:
            path_hits += 1
        rules = {part for part in str(row.get("inclusion_rules") or "").split("|") if part}
        if rules & HESITATION_INCLUSION:
            inclusion_hits += 1
    score = 0.5 * (path_hits / len(record_ids)) + 0.5 * (inclusion_hits / len(record_ids))
    app_n = sum(int(source_mix.get(source, 0)) for source in APP_UX_SOURCES)
    total_src = sum(source_mix.values()) or 1
    if label in APP_UX_LABELS and app_n / total_src >= 0.5:
        score *= 0.5
    return clamp01(score)


def _source_mix(record_ids: list[str], relevant_by_id: dict[str, dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record_id in record_ids:
        counts[str(relevant_by_id.get(record_id, {}).get("source") or "unknown")] += 1
    return dict(counts)


def _segment_overlap(record_ids: list[str], segments: list[dict[str, Any]]) -> dict[str, int]:
    opp = set(record_ids)
    mix: dict[str, int] = {}
    for segment in segments:
        overlap = len(opp & set(_ids(segment.get("evidence_record_ids"))))
        if overlap >= MIN_RECURRING_RECORDS:
            mix[str(segment.get("label") or "")] = overlap
    return mix


def _evidence_confidence(
    mean_confidence: float,
    source_mix: dict[str, int],
    n_unique: int,
    n_observed: int,
    n_relevant_sources: int,
    status: str,
) -> float:
    n_sources = len(source_mix)
    source_div = n_sources / max(n_relevant_sources, 1)
    observed_ratio = (n_observed / n_unique) if n_unique else 0.0
    score = 0.4 * mean_confidence + 0.3 * source_div + 0.3 * observed_ratio
    if n_sources <= 1:
        score *= 0.85
    if n_unique < SMALL_N_CATEGORY or status != "observed_evidence":
        score = min(score, 0.40)
    return clamp01(score)


def score_opportunities(
    themes: list[dict[str, Any]],
    segments: list[dict[str, Any]],
    relevant_by_id: dict[str, dict[str, Any]],
    n_relevant: int,
    n_relevant_sources: int,
    purchase_outcomes: bool,
) -> list[dict[str, Any]]:
    n_segments = len(segments)
    conversion_status = "observed_evidence" if purchase_outcomes else "hypothesis"
    rows: list[dict[str, Any]] = []
    for candidate in build_candidates(themes):
        n_unique = int(candidate["n_unique"])
        if n_unique <= 0:
            continue
        source_mix = _source_mix(candidate["record_ids"], relevant_by_id)
        segment_mix = _segment_overlap(candidate["record_ids"], segments)
        frequency = _frequency(n_unique, n_relevant)
        severity = _severity(candidate["record_ids"], candidate["extractor"], relevant_by_id)
        hesitation = _hesitation(candidate["record_ids"], candidate["label"], source_mix, relevant_by_id)
        segments_score = clamp01(len(segment_mix) / n_segments) if n_segments else 0.0
        confidence = _evidence_confidence(
            float(candidate["mean_confidence"]),
            source_mix,
            n_unique,
            int(candidate["n_observed"]),
            n_relevant_sources,
            str(candidate["status"]),
        )
        components = {
            "frequency": frequency,
            "severity": severity,
            "purchase_hesitation_link": hesitation,
            "segments_affected": segments_score,
            "evidence_confidence": confidence,
            "weights": DIMENSION_WEIGHTS,
            "freq_saturation": FREQ_SATURATION,
        }
        total = round(
            sum(float(components[name]) * float(DIMENSION_WEIGHTS[name]) for name in DIMENSION_WEIGHTS),
            4,
        )
        text = copy_for(str(candidate["key"]), str(candidate["extractor"]), str(candidate["label"]))
        rows.append(
            {
                "opportunity_id": f"opp:{candidate['key']}",
                "rank": 0,
                "problem_statement": text["problem"],
                "user_need": text["need"],
                "barrier": text["barrier"],
                "extractor": candidate["extractor"],
                "label": candidate["key"] if ":" not in str(candidate["key"]) else candidate["label"],
                "frequency": frequency,
                "severity": severity,
                "purchase_hesitation_link": hesitation,
                "segments_affected": segments_score,
                "evidence_confidence": confidence,
                "total_score": total,
                "unique_records": n_unique,
                "observed_records": int(candidate["n_observed"]),
                "pct_relevant": pct(n_unique, n_relevant),
                "denominator": n_relevant,
                "denominator_label": "relevant",
                "n_sources": len(source_mix),
                "source_mix": mix_json(source_mix),
                "conversion_link_status": conversion_status,
                "evidence_record_ids": join_ids(candidate["record_ids"]),
                "theme_ids": join_ids(candidate["theme_ids"]),
                "segment_ids": join_ids([f"segment:{name}" for name in segment_mix]),
                "formula_version": FORMULA_VERSION,
                "score_components": json.dumps(components, sort_keys=True),
                "status": candidate["status"],
            }
        )
    rows.sort(
        key=lambda row: (
            0 if row["status"] == "observed_evidence" else 1,
            -float(row["total_score"]),
            -int(row["unique_records"]),
            str(row["opportunity_id"]),
        )
    )
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    return rows
