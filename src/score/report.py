"""Write the opportunity register and research-hypothesis reports. Formula is public."""

from __future__ import annotations

from typing import Any

from src.score.schema import DIMENSION_WEIGHTS, FORMULA_VERSION, FREQ_SATURATION, TOP_HYPOTHESES


def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join("" if cell is None else str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([line, sep, *body]) if rows else line + "\n" + sep + "\n| _(empty)_ |"


def render_register(stats: dict[str, Any], opportunities: list[dict[str, Any]]) -> str:
    n_rel = stats["n_relevant"]
    generated = stats["generated_at"]
    purchase = stats["purchase_outcomes"]
    table = _md_table(
        ["Rank", "Opportunity", "Total /5", "Freq", "Sev", "Hesitation", "Segments", "Evidence", "n", "% relevant", "Sources", "Status", "Conversion link"],
        [
            [
                row["rank"],
                row["opportunity_id"],
                row["total_score"],
                row["frequency"],
                row["severity"],
                row["purchase_hesitation_link"],
                row["segments_affected"],
                row["evidence_confidence"],
                row["unique_records"],
                row["pct_relevant"],
                row["n_sources"],
                row["status"],
                row["conversion_link_status"],
            ]
            for row in opportunities
        ],
    )
    details = []
    for row in opportunities[:12]:
        details.append(
            f"### {row['rank']}. `{row['opportunity_id']}` (total {row['total_score']})\n\n"
            f"**Problem:** {row['problem_statement']}\n\n"
            f"**User need:** {row['user_need']}\n\n"
            f"- Barrier label: `{row['barrier']}`\n"
            f"- Themes: `{row['theme_ids']}`\n"
            f"- Segments: `{row['segment_ids'] or '(none)'}`\n"
            f"- Unique records: **{row['unique_records']}** / {n_rel} relevant ({row['pct_relevant']}%)\n"
            f"- Sources: `{row['source_mix']}`\n"
            f"- Status: `{row['status']}` ; conversion link: `{row['conversion_link_status']}`\n"
        )
    conversion_note = (
        "The scrape **does not** contain purchase outcomes, so every purchase-hesitation score is a "
        "**hypothesis**, not causality."
        if not purchase
        else "Purchase outcomes were present in the scrape; treat conversion-link scores as observed only where labeled."
    )
    return f"""# Opportunity register — Phase 5

Generated: {generated}  
Formula: `{FORMULA_VERSION}`  
Denominator for frequency: **relevant** (n = **{n_rel}**), not the full scrape.

North star: share of users who purchase at least one wishlisted item within 30 days.  
Monetary incentives (discounts, coupons, cashback, markdowns) are **not** the primary recommendation.

## Formula

Each dimension is 0-1. Weights are equal. Total is the weighted sum (max 5). Scores are **not** min-max rescaled to the current top theme.

| Dimension | Weight | Definition | Failure mode avoided |
| --- | --- | --- | --- |
| frequency | {DIMENSION_WEIGHTS['frequency']} | unique records / relevant, then divided by saturation {FREQ_SATURATION:.0%} (capped at 1.0) | Counting the full scrape, including irrelevant reviews |
| severity | {DIMENSION_WEIGHTS['severity']} | Mean journey-stage weight of evidence records, times extractor factor (barrier 1.0, need 0.9, behavior 0.75, intent 0.8) | Treating loud one-off complaints as severe for everyone |
| purchase_hesitation_link | {DIMENSION_WEIGHTS['purchase_hesitation_link']} | Share of evidence on wishlist/evaluation/consideration plus wishlist/hesitation/comparison/did-not-buy inclusion rules. Return language is excluded here (it is post-purchase). App-UX labels (delivery, trust, support) that are mostly Play/App Store are halved. | Claiming the theme is on wishlist-to-buy when it is generic app UX or only post-purchase returns |
| segments_affected | {DIMENSION_WEIGHTS['segments_affected']} | Share of **emitted** Phase 4 segments with at least 3 overlapping unique records. Segments that did not earn existence are not invented. | Inventing personas to inflate breadth |
| evidence_confidence | {DIMENSION_WEIGHTS['evidence_confidence']} | 0.4 mean extraction confidence + 0.3 source diversity + 0.3 observed-record ratio. Single-source clusters x0.85. Clusters with n<30 or hypothesis status capped at 0.40. Source mix is counted on unique records (no double-count across grouped themes). | High score on a thin, single-source cluster |

{conversion_note}

Journey-stage severity weights: abandonment 1.00, wishlist 0.85, evaluation 0.70, consideration 0.50, purchase 0.40, unlabeled 0.30, discovery 0.25. This is a **proxy**, not a causal model.

## Ranked opportunities

{table}

## Top opportunities (readable)

{''.join(details)}

## Do not

- Recommend coupons, cashback, or markdowns as the primary answer
- Jump to product features before using this ranking
- Treat mention frequency as proven 30-day conversion causality
- Assign high scores to hypothesis or n<3 clusters (evidence_confidence is capped)

Related themes (fit + will_it_fit, proof + vs_images, and similar) are **unioned** into one opportunity so Growth does not double-count the same records.
"""


def render_hypotheses(stats: dict[str, Any], hypotheses: list[dict[str, Any]], opportunities: list[dict[str, Any]]) -> str:
    by_id = {row["opportunity_id"]: row for row in opportunities}
    generated = stats["generated_at"]
    blocks = []
    for row in hypotheses:
        opp = by_id.get(row["opportunity_id"], {})
        blocks.append(
            f"### H{row['rank']}. `{row['hypothesis_id']}`\n\n"
            f"Opportunity: `{row['opportunity_id']}` (rank {row['rank']}, total {opp.get('total_score', '')}, "
            f"n={opp.get('unique_records', '')} relevant)\n\n"
            f"**Hypothesis:** {row['statement']}\n\n"
            f"**Primary research ask:** {row['primary_research_ask']}\n\n"
            f"**Success signal:** {row['success_signal']}\n\n"
            f"**Status:** `{row['status']}` "
            f"(conversion link is not proven in this scrape)\n"
        )
    body = "\n".join(blocks) if blocks else "_No hypotheses. Re-run Phase 4–5 with extractions._"
    return f"""# Research hypotheses — Phase 5

Generated: {generated}  
These are **testable follow-ups for primary research**, not product specs and not a discount brief.

Top {TOP_HYPOTHESES} ranked opportunities with recurring observed evidence (or the next best rows if fewer).

Do **not** use discounts, coupons, cashback, or price-offs as the primary solution to test. If a theme mentions price-watch or value, the research question is whether missing quality/fit/proof is masquerading as a wait-for-sale, not whether to markdown.

{body}

## How to use

1. Pick the highest-ranked opportunity whose evidence you can actually interview against.
2. Recruit from the evidence `record_id`s on that opportunity (Phase 6 evidence explorer).
3. Keep the success signal's denominator explicit (wishlisters who still intend to buy, not the whole scrape).
"""
