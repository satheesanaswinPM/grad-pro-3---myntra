"""Phase 5: rank opportunities and write research hypotheses. Never writes to data/raw/."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from src.ingest.env import load_dotenv
from src.qualify.config import LOGS_DIR, REPORTS_DIR, ROOT
from src.score.formula import score_opportunities
from src.score.hypotheses import research_hypotheses
from src.score.report import render_hypotheses, render_register
from src.score.schema import (
    FORMULA_VERSION,
    HYPOTHESIS_COLUMNS,
    HYPOTHESIS_TYPES,
    SCORE_COLUMNS,
    SCORE_TYPES,
    TOP_HYPOTHESES,
)
from src.synthesize.io import load_parquet, load_relevant, relevant_index, write_rows

SYNTHESIS = ROOT / "data" / "synthesis"
SCORING = ROOT / "data" / "scoring"
REQUIRED = (
    SYNTHESIS / "themes.parquet",
    SYNTHESIS / "segments.parquet",
    SYNTHESIS / "metrics.parquet",
)
MANIFEST = SCORING / "manifest.json"


def _logger() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("phase5")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(LOGS_DIR / "score.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


def _purchase_outcomes(metrics: list[dict[str, Any]]) -> bool:
    for row in metrics:
        if row.get("name") == "scrape_has_purchase_outcomes":
            return float(row.get("numerator") or 0) > 0 and str(row.get("status") or "") == "observed_evidence"
    return False


def run() -> dict[str, Any]:
    load_dotenv()
    logger = _logger()
    missing = [path for path in REQUIRED if not path.exists()]
    if missing:
        names = ", ".join(str(path.relative_to(ROOT)).replace("\\", "/") for path in missing)
        raise FileNotFoundError(f"Missing Phase 4 inputs: {names}. Run python -m src.synthesize first.")

    themes = load_parquet(SYNTHESIS / "themes.parquet")
    segments = load_parquet(SYNTHESIS / "segments.parquet")
    metrics = load_parquet(SYNTHESIS / "metrics.parquet")
    relevant_rows = load_relevant()
    if not themes:
        raise RuntimeError("data/synthesis/themes.parquet is empty. Re-run python -m src.synthesize.")
    if not relevant_rows:
        raise RuntimeError("data/processed/relevant.parquet is empty. Re-run python -m src.process.")

    n_relevant = len(relevant_rows)
    n_sources = len({str(row.get("source") or "unknown") for row in relevant_rows})
    purchase = _purchase_outcomes(metrics)
    relevant_by_id = relevant_index(relevant_rows)

    logger.info(
        "Phase 5 starting. themes=%s segments=%s relevant=%s purchase_outcomes=%s formula=%s",
        len(themes),
        len(segments),
        n_relevant,
        purchase,
        FORMULA_VERSION,
    )

    opportunities = score_opportunities(
        themes,
        segments,
        relevant_by_id,
        n_relevant,
        n_sources,
        purchase,
    )
    if not opportunities:
        raise RuntimeError("No scoreable opportunities. Check Phase 4 barrier/need themes.")
    hypotheses = research_hypotheses(opportunities)

    write_rows(opportunities, SCORING / "opportunities.parquet", SCORE_COLUMNS, SCORE_TYPES)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    stats = {
        "generated_at": generated_at,
        "n_relevant": n_relevant,
        "purchase_outcomes": purchase,
    }
    (REPORTS_DIR / "opportunity_register.md").write_text(render_register(stats, opportunities), encoding="utf-8")
    (REPORTS_DIR / "research_hypotheses.md").write_text(
        render_hypotheses(stats, hypotheses, opportunities), encoding="utf-8"
    )

    manifest = {
        "generated_at": generated_at,
        "formula_version": FORMULA_VERSION,
        "n_relevant": n_relevant,
        "n_opportunities": len(opportunities),
        "n_observed_opportunities": sum(1 for row in opportunities if row["status"] == "observed_evidence"),
        "n_hypotheses": len(hypotheses),
        "top_hypotheses": TOP_HYPOTHESES,
        "purchase_outcomes": purchase,
        "conversion_link_status": "observed_evidence" if purchase else "hypothesis",
        "top5": [
            {
                "rank": row["rank"],
                "opportunity_id": row["opportunity_id"],
                "total_score": row["total_score"],
                "unique_records": row["unique_records"],
                "pct_relevant": row["pct_relevant"],
                "status": row["status"],
            }
            for row in opportunities[:5]
        ],
        "outputs": {
            "opportunities": "data/scoring/opportunities.parquet",
            "register": "reports/opportunity_register.md",
            "hypotheses": "reports/research_hypotheses.md",
        },
        "notes": [
            "Frequency uses the relevant corpus, not the full scrape.",
            "Total is an un-inflated sum of five 0-1 dimensions (max 5).",
            "Conversion link is hypothesis unless the scrape contains purchase outcomes.",
            "Do not treat this ranking as a coupon or markdown brief.",
        ],
    }
    SCORING.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info(
        "Phase 5 done. opportunities=%s hypotheses=%s top=%s score=%s",
        len(opportunities),
        len(hypotheses),
        opportunities[0]["opportunity_id"],
        opportunities[0]["total_score"],
    )
    return manifest


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
