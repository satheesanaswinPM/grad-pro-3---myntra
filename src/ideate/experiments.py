"""Experiment briefs aimed at 30-day wishlist-to-purchase. Not a coupon test plan."""

from __future__ import annotations

from typing import Any

from src.ideate.schema import READINESS_WEAK

NORTH_STAR = (
    "Share of users who purchase at least one wishlisted item within 30 days of adding it."
)
PRIMARY_DENOMINATOR = (
    "Users who added a treatment-eligible item to wishlist in the assignment window, still "
    "intending to buy it (exclude accidental saves if a save-job tag exists)."
)
GUARDRAILS = (
    "Return rate on treated items; customer-support contacts; un-wishlist rate; "
    "time-to-decision (buy or remove). Do not treat AOV lift from markdowns as success."
)
DO_NOT_OPTIMIZE = (
    "Coupon redemption, discount depth, cashback take-up, markdown attach rate, "
    "or any price-off as the primary KPI."
)


def build_experiments(
    concepts: list[dict[str, Any]],
    validations: list[dict[str, Any]],
    opportunities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_val = {row["concept_id"]: row for row in validations}
    by_opp = {str(row["opportunity_id"]): row for row in opportunities}
    rows: list[dict[str, Any]] = []
    for concept in concepts:
        validation = by_val.get(str(concept["concept_id"]), {})
        if validation.get("readiness") == READINESS_WEAK:
            continue
        opp = by_opp.get(str(concept["opportunity_id"]), {})
        stem = str(concept["concept_id"]).removeprefix("concept:")
        readiness = str(validation.get("readiness") or "")
        rows.append(
            {
                "experiment_id": f"exp:{stem}",
                "concept_id": concept["concept_id"],
                "opportunity_id": concept["opportunity_id"],
                "rank": int(concept.get("rank") or 0),
                "title": f"30-day test: {concept.get('title')}",
                "hypothesis": (
                    f"If we close '{concept.get('addresses_need')}' with '{concept.get('title')}', "
                    "users who wishlisted a treated item will be more likely to purchase at least one "
                    "wishlisted item within 30 days than users on the current experience. "
                    "This conversion link is unproven in the scrape."
                ),
                "audience": (
                    f"Shoppers who wishlisted an item in the last 7 days where the open barrier is "
                    f"`{concept.get('addresses_barrier')}` "
                    f"(opportunity `{concept.get('opportunity_id')}`, n={concept.get('unique_records')} "
                    f"/ {concept.get('denominator')} relevant in the scrape — scrape n is not the test sample)."
                ),
                "treatment": concept.get("mechanism"),
                "control": "Current PDP + wishlist. No added proof module. No price change in either arm.",
                "primary_metric": NORTH_STAR,
                "primary_denominator": PRIMARY_DENOMINATOR,
                "guardrail_metrics": GUARDRAILS,
                "success_rule": (
                    "Statistically and practically higher 30-day wishlist-item purchase rate vs control, "
                    "with return rate not worse beyond the pre-registered bound. "
                    f"Readiness `{readiness}`: "
                    + (
                        "run as an A/B on-product test after a short interview check."
                        if readiness == "ready_to_test"
                        else "do not launch a powered A/B yet; run the Phase 5 research ask first, then a small prototype."
                    )
                ),
                "do_not_optimize": DO_NOT_OPTIMIZE,
                "readiness": readiness,
                "conversion_link_status": str(
                    opp.get("conversion_link_status") or concept.get("conversion_link_status") or "hypothesis"
                ),
                "status": "hypothesis",
            }
        )
    return rows
