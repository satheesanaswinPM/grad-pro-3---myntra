"""Opportunity and hypothesis contracts. Causal claims stay labeled when unproven."""

from __future__ import annotations

from typing import Any

FORMULA_VERSION = "score_v1"
TOP_HYPOTHESES = 10

# Equal weights. Frequency is an absolute share of relevant, capped at FREQ_SATURATION.
DIMENSION_WEIGHTS = {
    "frequency": 1.0,
    "severity": 1.0,
    "purchase_hesitation_link": 1.0,
    "segments_affected": 1.0,
    "evidence_confidence": 1.0,
}
SCORE_DIMENSIONS = tuple(DIMENSION_WEIGHTS)

# 20% of the relevant corpus scores 1.0 on frequency. Not rescaled to the current top theme.
FREQ_SATURATION = 0.20

# Journey-stage proxy for blocking strength. Not a causal model of conversion.
STAGE_SEVERITY = {
    "abandonment": 1.00,
    "wishlist": 0.85,
    "evaluation": 0.70,
    "consideration": 0.50,
    "purchase": 0.40,
    "discovery": 0.25,
    "unlabeled": 0.30,
}

EXTRACTOR_SEVERITY = {
    "barrier": 1.00,
    "need": 0.90,
    "behavior": 0.75,
    "intent": 0.80,
}

# Inclusion rules that sit on wishlist -> buy. Return/exchange is post-purchase;
# it feeds severity via journey stage, not this dimension.
HESITATION_INCLUSION = frozenset(
    {"in_wishlist", "in_cart_bag", "in_hesitation", "in_comparison", "in_abandonment"}
)
PATH_STAGES = frozenset({"wishlist", "evaluation", "consideration"})

# App-store ops complaints may be general UX, not wishlist conversion.
APP_UX_LABELS = frozenset({"delivery", "trust", "other:support"})
APP_UX_SOURCES = frozenset({"google_play", "app_store"})

# Intent themes that are not user problems to rank.
SKIP_INTENT_LABELS = frozenset({"strong_purchase", "inspiration"})

# Related themes share one Growth investigation. Union of evidence IDs; no double-count.
OPPORTUNITY_GROUPS: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("fit_uncertainty", (("barrier", "fit"), ("need", "will_it_fit"))),
    ("image_vs_reality", (("barrier", "proof"), ("need", "vs_images"))),
    ("quality_uncertainty", (("barrier", "quality"), ("need", "is_quality_worth_it"))),
    ("occasion_uncertainty", (("barrier", "occasion"), ("need", "right_for_occasion"))),
    ("styling_uncertainty", (("barrier", "styling"), ("need", "what_to_pair"))),
    ("returns_exchange", (("barrier", "returns"),)),
    ("price_watch", (("intent", "price_watch"), ("barrier", "value"))),
    (
        "comparison_loop",
        (
            ("barrier", "comparison"),
            ("behavior", "comparison"),
            ("need", "better_alternative"),
            ("intent", "comparison"),
        ),
    ),
    (
        "external_research",
        (
            ("behavior", "external:friends_family"),
            ("behavior", "external:other_apps"),
            ("behavior", "external:instagram"),
            ("behavior", "external:google"),
            ("behavior", "external:reddit"),
            ("behavior", "external:youtube"),
        ),
    ),
)

SCORE_COLUMNS = (
    "opportunity_id",
    "rank",
    "problem_statement",
    "user_need",
    "barrier",
    "extractor",
    "label",
    "frequency",
    "severity",
    "purchase_hesitation_link",
    "segments_affected",
    "evidence_confidence",
    "total_score",
    "unique_records",
    "observed_records",
    "pct_relevant",
    "denominator",
    "denominator_label",
    "n_sources",
    "source_mix",
    "conversion_link_status",
    "evidence_record_ids",
    "theme_ids",
    "segment_ids",
    "formula_version",
    "score_components",
    "status",
)

SCORE_TYPES = {
    "opportunity_id": "string",
    "rank": "int",
    "problem_statement": "string",
    "user_need": "string",
    "barrier": "string",
    "extractor": "string",
    "label": "string",
    "frequency": "float",
    "severity": "float",
    "purchase_hesitation_link": "float",
    "segments_affected": "float",
    "evidence_confidence": "float",
    "total_score": "float",
    "unique_records": "int",
    "observed_records": "int",
    "pct_relevant": "float",
    "denominator": "int",
    "denominator_label": "string",
    "n_sources": "int",
    "source_mix": "string",
    "conversion_link_status": "string",
    "evidence_record_ids": "string",
    "theme_ids": "string",
    "segment_ids": "string",
    "formula_version": "string",
    "score_components": "string",
    "status": "string",
}

HYPOTHESIS_COLUMNS = (
    "hypothesis_id",
    "opportunity_id",
    "rank",
    "statement",
    "primary_research_ask",
    "success_signal",
    "status",
)

HYPOTHESIS_TYPES = {
    "hypothesis_id": "string",
    "opportunity_id": "string",
    "rank": "int",
    "statement": "string",
    "primary_research_ask": "string",
    "success_signal": "string",
    "status": "string",
}


def empty_row(columns: tuple[str, ...]) -> dict[str, Any]:
    return {name: None for name in columns}


def clamp01(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 4)
