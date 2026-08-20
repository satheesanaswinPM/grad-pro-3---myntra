"""Evidence lookup and packs. Quotes stay in the console; packs are a copy, not a hiding place."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.dashboard.load import Store, split_ids
from src.dashboard.schema import QUOTE_LIMIT
from src.qualify.config import ROOT

PACKS_DIR = ROOT / "exports" / "evidence_packs"


def _safe_name(opportunity_id: str) -> str:
    return str(opportunity_id).replace(":", "-").replace("/", "-")


def write_evidence_pack(store: Store, opportunity: dict[str, Any], limit: int = QUOTE_LIMIT) -> dict[str, Any]:
    quotes = store.insights_for_opportunity(opportunity, limit=limit)
    payload = {
        "opportunity_id": opportunity.get("opportunity_id"),
        "rank": opportunity.get("rank"),
        "problem_statement": opportunity.get("problem_statement"),
        "user_need": opportunity.get("user_need"),
        "barrier": opportunity.get("barrier"),
        "status": opportunity.get("status"),
        "conversion_link_status": opportunity.get("conversion_link_status"),
        "unique_records": opportunity.get("unique_records"),
        "pct_relevant": opportunity.get("pct_relevant"),
        "denominator": opportunity.get("denominator"),
        "denominator_label": opportunity.get("denominator_label"),
        "total_score": opportunity.get("total_score"),
        "theme_ids": opportunity.get("theme_ids"),
        "segment_ids": opportunity.get("segment_ids"),
        "n_quotes": len(quotes),
        "n_evidence_records": len(split_ids(opportunity.get("evidence_record_ids"))),
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "quotes": quotes,
        "note": "Quotes are also shown in the research console. This file is a copy, not the only place to read evidence.",
    }
    PACKS_DIR.mkdir(parents=True, exist_ok=True)
    stem = _safe_name(str(opportunity.get("opportunity_id") or "unknown"))
    json_path = PACKS_DIR / f"{stem}.json"
    md_path = PACKS_DIR / f"{stem}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return payload


def write_all_packs(store: Store) -> int:
    count = 0
    for opportunity in store.opportunities:
        write_evidence_pack(store, opportunity)
        count += 1
    index = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "n_packs": count,
        "opportunities": [
            {
                "opportunity_id": row.get("opportunity_id"),
                "rank": row.get("rank"),
                "file": _safe_name(str(row.get("opportunity_id"))) + ".json",
            }
            for row in store.opportunities
        ],
        "note": "Open the research console to read quotes in context. Packs do not replace click-through evidence.",
    }
    PACKS_DIR.mkdir(parents=True, exist_ok=True)
    (PACKS_DIR / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return count


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# {payload.get('opportunity_id')}",
        "",
        f"**Problem:** {payload.get('problem_statement')}",
        "",
        f"**User need:** {payload.get('user_need')}",
        "",
        f"Rank {payload.get('rank')} · n={payload.get('unique_records')} / {payload.get('denominator')} "
        f"{payload.get('denominator_label')} ({payload.get('pct_relevant')}%) · "
        f"status `{payload.get('status')}` · conversion link `{payload.get('conversion_link_status')}`",
        "",
        "Conversion causality is not proven in this scrape. Monetary incentives are not the recommended lever.",
        "",
        f"Showing {payload.get('n_quotes')} quotes from {payload.get('n_evidence_records')} evidence records.",
        "",
    ]
    for quote in payload.get("quotes") or []:
        lines.extend(
            [
                f"## {quote.get('insight_id')}",
                "",
                f"- source: `{quote.get('source')}` · category: `{quote.get('category')}` · "
                f"stage: `{quote.get('journey_stage')}` · `{quote.get('extractor')}:{quote.get('label')}` · "
                f"`{quote.get('status')}`",
                f"- record: `{quote.get('record_id')}`",
                "",
                f"> {quote.get('evidence_snippet')}",
                "",
            ]
        )
        if quote.get("ai_interpretation"):
            lines.extend([f"*Interpretation (not the quote):* {quote['ai_interpretation']}", ""])
    return "\n".join(lines) + "\n"
