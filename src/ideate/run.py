"""Phase 7: ideate, validate, and design experiments. Never writes to data/raw/."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from src.ideate.concepts import build_concepts
from src.ideate.experiments import build_experiments
from src.ideate.gates import is_unlocked, missing_gates
from src.ideate.report import render_concepts, render_experiments
from src.ideate.schema import (
    CONCEPT_COLUMNS,
    CONCEPT_TYPES,
    EXPERIMENT_COLUMNS,
    EXPERIMENT_TYPES,
    IDEATION_VERSION,
    VALIDATION_COLUMNS,
    VALIDATION_TYPES,
)
from src.ideate.validate import validate_concepts
from src.ingest.env import load_dotenv
from src.qualify.config import LOGS_DIR, REPORTS_DIR, ROOT
from src.synthesize.io import load_parquet, write_rows

SCORING = ROOT / "data" / "scoring"
IDEATION = ROOT / "data" / "ideation"
MANIFEST = IDEATION / "manifest.json"


def _logger() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("phase7")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(LOGS_DIR / "ideate.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


def _lock_message() -> str:
    lines = [
        "Phase 7 - Solution Ideation is locked.",
        "Unlock only after Phases 5 and 6: ranked opportunities with evidence,",
        "and a console that can answer the research question.",
        "Do not use discounts, coupons, cashback, or price-offs as the primary solution.",
        "Gate files still missing:",
    ]
    for label, path in missing_gates():
        lines.append(f"  - {label}: {path.relative_to(ROOT).as_posix()}")
    return "\n".join(lines)


def run() -> dict[str, Any]:
    load_dotenv()
    logger = _logger()
    opportunities = load_parquet(SCORING / "opportunities.parquet")
    if not opportunities:
        raise RuntimeError("data/scoring/opportunities.parquet is empty. Re-run python -m src.score.")

    logger.info("Phase 7 starting. opportunities=%s catalog=%s", len(opportunities), IDEATION_VERSION)
    concepts = build_concepts(opportunities)
    validations = validate_concepts(concepts, opportunities)
    experiments = build_experiments(concepts, validations, opportunities)
    if not concepts:
        raise RuntimeError("No concepts produced. Check Phase 5 opportunities.")

    write_rows(concepts, IDEATION / "concepts.parquet", CONCEPT_COLUMNS, CONCEPT_TYPES)
    write_rows(validations, IDEATION / "validations.parquet", VALIDATION_COLUMNS, VALIDATION_TYPES)
    write_rows(experiments, IDEATION / "experiments.parquet", EXPERIMENT_COLUMNS, EXPERIMENT_TYPES)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    stats = {"generated_at": generated_at}
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "solution_concepts.md").write_text(
        render_concepts(stats, concepts, validations), encoding="utf-8"
    )
    (REPORTS_DIR / "experiment_briefs.md").write_text(render_experiments(stats, experiments), encoding="utf-8")

    readiness_counts: dict[str, int] = {}
    for row in validations:
        key = str(row.get("readiness") or "")
        readiness_counts[key] = readiness_counts.get(key, 0) + 1

    manifest = {
        "generated_at": generated_at,
        "ideation_version": IDEATION_VERSION,
        "n_opportunities": len(opportunities),
        "n_concepts": len(concepts),
        "n_validations": len(validations),
        "n_experiments": len(experiments),
        "readiness": readiness_counts,
        "outputs": {
            "concepts": "data/ideation/concepts.parquet",
            "validations": "data/ideation/validations.parquet",
            "experiments": "data/ideation/experiments.parquet",
            "concept_report": "reports/solution_concepts.md",
            "experiment_report": "reports/experiment_briefs.md",
        },
        "notes": [
            "Concepts are not a shipped conversion product.",
            "Discounts, coupons, cashback, and markdowns are not the primary solution.",
            "Conversion experiments stay labeled hypothesis until they run.",
        ],
    }
    IDEATION.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info(
        "Phase 7 done. concepts=%s experiments=%s readiness=%s",
        len(concepts),
        len(experiments),
        readiness_counts,
    )
    return manifest


def main() -> int:
    if not is_unlocked():
        print(_lock_message())
        return 3
    run()
    print("Phase 7 wrote concepts, validations, and 30-day experiment briefs.")
    print("Discounts, coupons, cashback, and markdowns are not the primary solution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
