"""Phase 7 contracts. Concepts are not a conversion product and not a discount brief."""

from __future__ import annotations

from typing import Any

IDEATION_VERSION = "ideate_v1"
TOP_OPPORTUNITIES = 10
SMALL_N = 30
# Pre-purchase hesitation below this is too weak to treat as a conversion experiment first.
MIN_HESITATION_FOR_TEST = 0.20

# Primary solutions that the brief forbids.
FORBIDDEN_LEVERS = (
    "discount",
    "discounts",
    "coupon",
    "coupons",
    "cashback",
    "markdown",
    "markdowns",
    "price-off",
    "price off",
    "price-offs",
    "promo code",
    "promotional offer",
    "sale price",
    "% off",
    "percent off",
)

CONCEPT_COLUMNS = (
    "concept_id",
    "opportunity_id",
    "rank",
    "title",
    "mechanism",
    "addresses_need",
    "addresses_barrier",
    "rejected_lever",
    "why_not_discount",
    "risks",
    "status",
    "unique_records",
    "pct_relevant",
    "denominator",
    "denominator_label",
    "conversion_link_status",
)

CONCEPT_TYPES = {
    "concept_id": "string",
    "opportunity_id": "string",
    "rank": "int",
    "title": "string",
    "mechanism": "string",
    "addresses_need": "string",
    "addresses_barrier": "string",
    "rejected_lever": "string",
    "why_not_discount": "string",
    "risks": "string",
    "status": "string",
    "unique_records": "int",
    "pct_relevant": "float",
    "denominator": "int",
    "denominator_label": "string",
    "conversion_link_status": "string",
}

VALIDATION_COLUMNS = (
    "validation_id",
    "concept_id",
    "opportunity_id",
    "rank",
    "addresses_stated_need",
    "addresses_stated_barrier",
    "non_monetary",
    "evidence_status",
    "n_small",
    "hesitation",
    "readiness",
    "notes",
    "status",
)

VALIDATION_TYPES = {
    "validation_id": "string",
    "concept_id": "string",
    "opportunity_id": "string",
    "rank": "int",
    "addresses_stated_need": "bool",
    "addresses_stated_barrier": "bool",
    "non_monetary": "bool",
    "evidence_status": "string",
    "n_small": "bool",
    "hesitation": "float",
    "readiness": "string",
    "notes": "string",
    "status": "string",
}

EXPERIMENT_COLUMNS = (
    "experiment_id",
    "concept_id",
    "opportunity_id",
    "rank",
    "title",
    "hypothesis",
    "audience",
    "treatment",
    "control",
    "primary_metric",
    "primary_denominator",
    "guardrail_metrics",
    "success_rule",
    "do_not_optimize",
    "readiness",
    "conversion_link_status",
    "status",
)

EXPERIMENT_TYPES = {
    "experiment_id": "string",
    "concept_id": "string",
    "opportunity_id": "string",
    "rank": "int",
    "title": "string",
    "hypothesis": "string",
    "audience": "string",
    "treatment": "string",
    "control": "string",
    "primary_metric": "string",
    "primary_denominator": "string",
    "guardrail_metrics": "string",
    "success_rule": "string",
    "do_not_optimize": "string",
    "readiness": "string",
    "conversion_link_status": "string",
    "status": "string",
}

READINESS_TEST = "ready_to_test"
READINESS_RESEARCH = "primary_research_first"
READINESS_WEAK = "weak_fit"


def empty_row(columns: tuple[str, ...]) -> dict[str, Any]:
    return {name: None for name in columns}
