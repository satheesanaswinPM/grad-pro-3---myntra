"""Write Phase 7 concept and experiment reports. Monetary incentives stay rejected."""

from __future__ import annotations

from typing import Any

from src.ideate.schema import IDEATION_VERSION, MIN_HESITATION_FOR_TEST, SMALL_N, TOP_OPPORTUNITIES


def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join("" if cell is None else str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([line, sep, *body]) if rows else line + "\n" + sep + "\n| _(empty)_ |"


def render_concepts(
    stats: dict[str, Any],
    concepts: list[dict[str, Any]],
    validations: list[dict[str, Any]],
) -> str:
    by_val = {row["concept_id"]: row for row in validations}
    table = _md_table(
        ["Rank", "Opportunity", "Concept", "Readiness", "n", "% relevant", "Conversion link"],
        [
            [
                row["rank"],
                row["opportunity_id"],
                row["title"],
                by_val.get(row["concept_id"], {}).get("readiness", ""),
                row["unique_records"],
                row["pct_relevant"],
                row["conversion_link_status"],
            ]
            for row in concepts
        ],
    )
    blocks = []
    for row in concepts:
        validation = by_val.get(row["concept_id"], {})
        blocks.append(
            f"### {row['rank']}. `{row['concept_id']}` — {row['title']}\n\n"
            f"Opportunity: `{row['opportunity_id']}` · readiness `{validation.get('readiness')}`\n\n"
            f"**Need this must close:** {row['addresses_need']}\n\n"
            f"**Barrier:** `{row['addresses_barrier']}`\n\n"
            f"**Mechanism:** {row['mechanism']}\n\n"
            f"**Rejected lever:** {row['rejected_lever']}\n\n"
            f"**Why not a discount:** {row['why_not_discount']}\n\n"
            f"**Risks:** {row['risks']}\n\n"
            f"- n = **{row['unique_records']}** / {row['denominator']} {row['denominator_label']} "
            f"({row['pct_relevant']}%)\n"
            f"- Conversion link: `{row['conversion_link_status']}`\n"
            f"- Validation: {validation.get('notes')}\n"
        )
    return f"""# Solution concepts — Phase 7

Generated: {stats['generated_at']}  
Catalog: `{IDEATION_VERSION}`  
Source ranking: top {TOP_OPPORTUNITIES} Phase 5 opportunities.

These are **concepts and experiment designs**, not a shipped conversion product.  
Monetary incentives (discounts, coupons, cashback, markdowns) are **not** the primary solution.

Readiness:

- `ready_to_test` — observed evidence, n ≥ {SMALL_N}, purchase-hesitation_link ≥ {MIN_HESITATION_FOR_TEST:.2f}, mechanism matches the need, non-monetary.
- `primary_research_first` — the concept is valid but hesitation is weak, n is small, or the scrape story may be post-purchase.
- `weak_fit` — dropped from experiment briefs.

Every percentage below uses the **relevant** corpus unless a row names another denominator. Conversion effects remain **hypotheses**.

## Concepts

{table}

## Concept briefs

{''.join(blocks)}

## Do not

- Use discounts, coupons, cashback, or price-offs as the primary solution
- Treat Phase 5 rank as a license to skip validation (returns rank high but hesitation is weak)
- Ship a full product in this phase
"""


def render_experiments(stats: dict[str, Any], experiments: list[dict[str, Any]]) -> str:
    table = _md_table(
        ["Rank", "Experiment", "Opportunity", "Readiness", "Conversion link"],
        [
            [
                row["rank"],
                row["experiment_id"],
                row["opportunity_id"],
                row["readiness"],
                row["conversion_link_status"],
            ]
            for row in experiments
        ],
    )
    blocks = []
    for row in experiments:
        blocks.append(
            f"### {row['rank']}. `{row['experiment_id']}`\n\n"
            f"{row['title']}\n\n"
            f"**Hypothesis:** {row['hypothesis']}\n\n"
            f"**Audience:** {row['audience']}\n\n"
            f"**Treatment:** {row['treatment']}\n\n"
            f"**Control:** {row['control']}\n\n"
            f"**Primary metric:** {row['primary_metric']}\n\n"
            f"**Denominator:** {row['primary_denominator']}\n\n"
            f"**Guardrails:** {row['guardrail_metrics']}\n\n"
            f"**Success rule:** {row['success_rule']}\n\n"
            f"**Do not optimize:** {row['do_not_optimize']}\n\n"
            f"Status: `{row['status']}` · conversion link `{row['conversion_link_status']}` · "
            f"readiness `{row['readiness']}`\n"
        )
    body = "\n".join(blocks) if blocks else "_No experiments passed validation._"
    return f"""# Experiment briefs — Phase 7

Generated: {stats['generated_at']}  
North star: share of users who purchase at least one wishlisted item within **30 days** of adding it.

This scrape has **no purchase outcomes**, so every conversion experiment is a **hypothesis** until it runs.  
Do **not** use discounts, coupons, cashback, or price-offs as the primary treatment or KPI.

## Roster

{table}

## Briefs

{body}

## How to use

1. Prefer `ready_to_test` briefs. Run `primary_research_first` as interviews against Phase 6 evidence IDs.
2. Keep both arms at the same listed price.
3. Pre-register the 30-day window from wishlist add, not from first session.
"""
