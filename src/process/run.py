"""Phase 2: relevance filter and journey tags. Never writes to data/raw/."""

from __future__ import annotations

import json
import logging
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

from src.ingest.env import load_dotenv
from src.process.io import write_parquet
from src.process.report import render_report
from src.process.tag import decide_relevance
from src.qualify.config import LOGS_DIR, REPORTS_DIR, ROOT

PROCESSED_DIR = ROOT / "data" / "processed"
CANONICAL = PROCESSED_DIR / "canonical.parquet"
RELEVANT = PROCESSED_DIR / "relevant.parquet"
JOURNEY = PROCESSED_DIR / "journey_tags.parquet"
MANIFEST = PROCESSED_DIR / "phase2_manifest.json"
RULES_MD = REPORTS_DIR / "relevance_rules.md"

CANONICAL_KEEP = (
    "record_id",
    "source",
    "source_url",
    "authored_at",
    "language",
    "raw_ref",
    "text",
    "rating",
    "product_or_category",
    "user_key",
    "ingest_at",
    "content_hash",
    "metadata",
)


def _setup_log() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("phase2")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(LOGS_DIR / "process.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


def _join(values: list[str]) -> str:
    return "|".join(values)


def run() -> dict:
    load_dotenv()
    logger = _setup_log()
    if not CANONICAL.exists():
        raise FileNotFoundError("Missing data/processed/canonical.parquet. Run python -m src.ingest.build first.")

    import pyarrow.parquet as pq

    logger.info("Phase 2 starting. canonical=%s", CANONICAL)
    rows = pq.read_table(CANONICAL).to_pylist()
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    journey_rows: list[dict] = []
    relevant_rows: list[dict] = []
    inclusion_hits: Counter[str] = Counter()
    exclusion_hits: Counter[str] = Counter()
    stage_counts: Counter[str] = Counter()
    relevant_stage_counts: Counter[str] = Counter()
    language_all: Counter[str] = Counter()
    language_relevant: Counter[str] = Counter()
    by_source: dict[str, dict[str, int]] = defaultdict(lambda: {"all": 0, "relevant": 0})
    relevant_categories: list[str] = []
    external_hits: Counter[str] = Counter()

    for row in rows:
        tags = decide_relevance(row)
        language_all[str(row.get("language") or "unknown")] += 1
        source = str(row.get("source") or "unknown")
        by_source[source]["all"] += 1
        stage_counts[tags["journey_stage"]] += 1
        for rule_id in tags["inclusion_rules"]:
            inclusion_hits[rule_id] += 1
        for rule_id in tags["exclusion_rules"]:
            exclusion_hits[rule_id] += 1
        for dest in tags["external_destinations"]:
            external_hits[dest] += 1

        stages = set(tags["journey_stages"])
        journey_rows.append(
            {
                "record_id": row["record_id"],
                "source": source,
                "language": row.get("language") or "",
                "is_relevant": tags["is_relevant"],
                "inclusion_rules": _join(tags["inclusion_rules"]),
                "exclusion_rules": _join(tags["exclusion_rules"]),
                "journey_stage": tags["journey_stage"],
                "discovery": "discovery" in stages,
                "consideration": "consideration" in stages,
                "wishlist": "wishlist" in stages,
                "evaluation": "evaluation" in stages,
                "purchase": "purchase" in stages,
                "abandonment": "abandonment" in stages,
                "fashion_category": tags["fashion_category"],
                "category_source": tags["category_source"],
                "ext_google": "google" in tags["external_destinations"],
                "ext_reddit": "reddit" in tags["external_destinations"],
                "ext_youtube": "youtube" in tags["external_destinations"],
                "ext_instagram": "instagram" in tags["external_destinations"],
                "ext_friends_family": "friends_family" in tags["external_destinations"],
                "ext_influencer": "influencer" in tags["external_destinations"],
                "ext_other_apps": "other_apps" in tags["external_destinations"],
                "text_length": tags["text_length"],
            }
        )

        if tags["is_relevant"]:
            by_source[source]["relevant"] += 1
            language_relevant[str(row.get("language") or "unknown")] += 1
            relevant_stage_counts[tags["journey_stage"]] += 1
            relevant_categories.append(tags["fashion_category"])
            relevant_rows.append(
                {
                    **{key: row.get(key) for key in CANONICAL_KEEP},
                    "inclusion_rules": _join(tags["inclusion_rules"]),
                    "journey_stage": tags["journey_stage"],
                    "journey_stages": _join(tags["journey_stages"]),
                    "fashion_category": tags["fashion_category"],
                    "category_source": tags["category_source"],
                    "external_destinations": _join(tags["external_destinations"]),
                }
            )

    if not relevant_rows:
        raise RuntimeError("No relevant rows. Check inclusion rules before writing an empty corpus.")

    write_parquet(relevant_rows, RELEVANT)
    write_parquet(journey_rows, JOURNEY)

    stats = {
        "generated_at": generated_at,
        "n_canonical": len(rows),
        "n_relevant": len(relevant_rows),
        "inclusion_hits": dict(inclusion_hits),
        "exclusion_hits": dict(exclusion_hits),
        "stage_counts": dict(stage_counts),
        "relevant_stage_counts": dict(relevant_stage_counts),
        "language_all": dict(language_all),
        "language_relevant": dict(language_relevant),
        "by_source": dict(by_source),
        "relevant_categories": relevant_categories,
        "external_hits": dict(external_hits),
    }
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    RULES_MD.write_text(render_report(stats), encoding="utf-8")

    manifest = {
        "generated_at": generated_at,
        "n_canonical": len(rows),
        "n_relevant": len(relevant_rows),
        "pct_relevant": round(100.0 * len(relevant_rows) / len(rows), 2) if rows else 0,
        "relevant_path": "data/processed/relevant.parquet",
        "journey_path": "data/processed/journey_tags.parquet",
        "rules_path": "reports/relevance_rules.md",
        "by_source": dict(by_source),
        "stage_counts": dict(stage_counts),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info(
        "Phase 2 done. relevant=%s / canonical=%s (%.1f%%)",
        len(relevant_rows),
        len(rows),
        100.0 * len(relevant_rows) / len(rows) if rows else 0,
    )
    return manifest


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
