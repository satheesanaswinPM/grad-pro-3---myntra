"""Turn top opportunities into testable primary-research hypotheses."""

from __future__ import annotations

from typing import Any

from src.score.statements import copy_for
from src.score.schema import TOP_HYPOTHESES


def research_hypotheses(opportunities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen = [row for row in opportunities if row.get("status") == "observed_evidence"][:TOP_HYPOTHESES]
    if len(chosen) < TOP_HYPOTHESES:
        extras = [
            row
            for row in opportunities
            if row["opportunity_id"] not in {item["opportunity_id"] for item in chosen}
        ][: TOP_HYPOTHESES - len(chosen)]
        chosen.extend(extras)
    rows: list[dict[str, Any]] = []
    for row in chosen:
        text = copy_for(str(row.get("label") or ""), str(row.get("extractor") or ""), str(row.get("label") or ""))
        opp_id = str(row["opportunity_id"])
        rows.append(
            {
                "hypothesis_id": f"hyp:{opp_id.removeprefix('opp:')}",
                "opportunity_id": opp_id,
                "rank": int(row.get("rank") or 0),
                "statement": text["statement"],
                "primary_research_ask": text["ask"],
                "success_signal": text["signal"],
                "status": "hypothesis",
            }
        )
    return rows
