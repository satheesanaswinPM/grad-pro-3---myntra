"""Load Phase 2-5 tables for the research console. Never reads data/raw for rewriting."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.analyze.schema import EXTRACTORS
from src.qualify.config import ROOT
from src.synthesize.io import extraction_path, load_parquet

RELEVANT_PATH = ROOT / "data" / "processed" / "relevant.parquet"
SYNTHESIS = ROOT / "data" / "synthesis"
SCORING = ROOT / "data" / "scoring"
PHASE2_MANIFEST = ROOT / "data" / "processed" / "phase2_manifest.json"
PHASE3_MANIFEST = ROOT / "data" / "extractions" / "manifest.json"
PHASE4_MANIFEST = SYNTHESIS / "manifest.json"
PHASE5_MANIFEST = SCORING / "manifest.json"

RELEVANT_COLS = (
    "record_id",
    "source",
    "source_url",
    "authored_at",
    "language",
    "text",
    "rating",
    "product_or_category",
    "fashion_category",
    "journey_stage",
    "inclusion_rules",
    "external_destinations",
)

STAGE_ORDER = (
    "discovery",
    "consideration",
    "wishlist",
    "evaluation",
    "purchase",
    "abandonment",
    "unlabeled",
)

REQUIRED = (
    RELEVANT_PATH,
    SYNTHESIS / "themes.parquet",
    SYNTHESIS / "segments.parquet",
    SCORING / "opportunities.parquet",
)


def _json_load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _ids(raw: Any) -> list[str]:
    return [part for part in str(raw or "").split("|") if part]


def _mix(raw: Any) -> dict[str, int]:
    if isinstance(raw, dict):
        return {str(key): int(value) for key, value in raw.items() if key}
    text = str(raw or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return {str(key): int(value) for key, value in parsed.items() if key}


def _theme_pair(theme_id: str) -> tuple[str, str] | None:
    if not theme_id.startswith("theme:"):
        return None
    rest = theme_id[len("theme:") :]
    extractor, _, label = rest.partition(":")
    if not extractor or not label:
        return None
    return extractor, label


@dataclass
class Store:
    n_relevant: int
    n_canonical: int
    relevant: dict[str, dict[str, Any]]
    extractions: list[dict[str, Any]]
    by_record: dict[str, list[dict[str, Any]]]
    themes: list[dict[str, Any]]
    segments: list[dict[str, Any]]
    category_diffs: list[dict[str, Any]]
    metrics: list[dict[str, Any]]
    opportunities: list[dict[str, Any]]
    manifests: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def build(cls) -> "Store":
        missing = [path for path in REQUIRED if not path.exists()]
        if missing:
            names = ", ".join(str(path.relative_to(ROOT)).replace("\\", "/") for path in missing)
            raise FileNotFoundError(f"Missing inputs: {names}. Run phases 2-5 first.")

        import pyarrow.parquet as pq

        table = pq.read_table(RELEVANT_PATH)
        present = [name for name in RELEVANT_COLS if name in table.column_names]
        relevant_rows = table.select(present).to_pylist()
        relevant = {str(row["record_id"]): row for row in relevant_rows if row.get("record_id")}

        extractions: list[dict[str, Any]] = []
        by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for extractor in EXTRACTORS:
            path = extraction_path(extractor)
            if not path.exists():
                continue
            for row in load_parquet(path):
                record_id = str(row.get("record_id") or "")
                if record_id not in relevant:
                    continue
                item = {
                    "extraction_id": str(row.get("extraction_id") or ""),
                    "record_id": record_id,
                    "extractor": str(row.get("extractor") or extractor),
                    "label": str(row.get("label") or ""),
                    "evidence_span": str(row.get("evidence_span") or ""),
                    "confidence": float(row.get("confidence") or 0),
                    "status": str(row.get("status") or ""),
                    "ai_interpretation": str(row.get("ai_interpretation") or ""),
                }
                if not item["extraction_id"] or not item["evidence_span"]:
                    continue
                extractions.append(item)
                by_record[record_id].append(item)

        phase2 = _json_load(PHASE2_MANIFEST)
        return cls(
            n_relevant=len(relevant),
            n_canonical=int(phase2.get("n_canonical") or 0),
            relevant=relevant,
            extractions=extractions,
            by_record=dict(by_record),
            themes=load_parquet(SYNTHESIS / "themes.parquet"),
            segments=load_parquet(SYNTHESIS / "segments.parquet"),
            category_diffs=load_parquet(SYNTHESIS / "category_diffs.parquet")
            if (SYNTHESIS / "category_diffs.parquet").exists()
            else [],
            metrics=load_parquet(SYNTHESIS / "metrics.parquet") if (SYNTHESIS / "metrics.parquet").exists() else [],
            opportunities=sorted(
                load_parquet(SCORING / "opportunities.parquet"),
                key=lambda row: int(row.get("rank") or 0),
            ),
            manifests={
                "phase2": phase2,
                "phase3": _json_load(PHASE3_MANIFEST),
                "phase4": _json_load(PHASE4_MANIFEST),
                "phase5": _json_load(PHASE5_MANIFEST),
            },
        )

    def source_counts(self) -> list[tuple[str, int]]:
        counts: Counter[str] = Counter(str(row.get("source") or "unknown") for row in self.relevant.values())
        return counts.most_common()

    def stage_counts(self) -> list[tuple[str, int]]:
        counts: Counter[str] = Counter(str(row.get("journey_stage") or "unlabeled") for row in self.relevant.values())
        return [(name, counts.get(name, 0)) for name in STAGE_ORDER]

    def themes_for(self, extractor: str) -> list[dict[str, Any]]:
        rows = [row for row in self.themes if row.get("extractor") == extractor]
        rows.sort(key=lambda row: -int(row.get("unique_records") or 0))
        return rows

    def opportunity(self, opportunity_id: str) -> dict[str, Any] | None:
        for row in self.opportunities:
            if row.get("opportunity_id") == opportunity_id:
                return row
        return None

    def wanted_pairs(self, theme_ids: str) -> set[tuple[str, str]]:
        pairs: set[tuple[str, str]] = set()
        for theme_id in _ids(theme_ids):
            pair = _theme_pair(theme_id)
            if pair:
                pairs.add(pair)
        return pairs

    def insights_for(
        self,
        record_ids: list[str],
        *,
        theme_ids: str = "",
        extractor: str = "",
        limit: int = 40,
        prefer_observed: bool = True,
    ) -> list[dict[str, Any]]:
        wanted = self.wanted_pairs(theme_ids)
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        for record_id in record_ids:
            linked = self.relevant.get(record_id)
            if not linked:
                continue
            for item in self.by_record.get(record_id, []):
                if extractor and item["extractor"] != extractor:
                    continue
                if wanted and (item["extractor"], item["label"]) not in wanted:
                    continue
                if item["extraction_id"] in seen:
                    continue
                seen.add(item["extraction_id"])
                rows.append(self._insight(item, linked))
        if prefer_observed:
            rows.sort(
                key=lambda row: (
                    0 if row["status"] == "observed_evidence" else 1,
                    -float(row.get("confidence") or 0),
                )
            )
        return rows[:limit]

    def insights_for_opportunity(self, opportunity: dict[str, Any], limit: int = 40) -> list[dict[str, Any]]:
        return self.insights_for(
            _ids(opportunity.get("evidence_record_ids")),
            theme_ids=str(opportunity.get("theme_ids") or ""),
            limit=limit,
        )

    def search_insights(
        self,
        *,
        query: str = "",
        source: str = "",
        category: str = "",
        extractor: str = "",
        status: str = "",
        record_ids: list[str] | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        needle = query.strip().casefold()
        allowed = set(record_ids) if record_ids is not None else None
        rows: list[dict[str, Any]] = []
        for item in self.extractions:
            if allowed is not None and item["record_id"] not in allowed:
                continue
            if extractor and item["extractor"] != extractor:
                continue
            if status and item["status"] != status:
                continue
            linked = self.relevant.get(item["record_id"])
            if not linked:
                continue
            if source and str(linked.get("source") or "") != source:
                continue
            if category and str(linked.get("fashion_category") or "") != category:
                continue
            if needle:
                blob = f"{item['evidence_span']} {linked.get('text') or ''}".casefold()
                if needle not in blob:
                    continue
            rows.append(self._insight(item, linked))
            if len(rows) >= limit:
                break
        return rows

    def _insight(self, item: dict[str, Any], linked: dict[str, Any]) -> dict[str, Any]:
        return {
            "insight_id": item["extraction_id"],
            "problem_statement": f"{item['extractor']}: {item['label']}",
            "user_need": "",
            "barrier": item["label"] if item["extractor"] == "barrier" else "",
            "intent": item["label"] if item["extractor"] == "intent" else "",
            "segment": "",
            "category": str(linked.get("fashion_category") or "unlabeled"),
            "source": str(linked.get("source") or ""),
            "evidence_snippet": item["evidence_span"],
            "record_id": item["record_id"],
            "date": str(linked.get("authored_at") or ""),
            "frequency": 1,
            "pct_relevant": 0.0,
            "confidence": item["confidence"],
            "ai_interpretation": item["ai_interpretation"],
            "status": item["status"],
            "extractor": item["extractor"],
            "label": item["label"],
            "text": str(linked.get("text") or ""),
            "source_url": str(linked.get("source_url") or ""),
            "journey_stage": str(linked.get("journey_stage") or ""),
        }


def split_ids(raw: Any) -> list[str]:
    return _ids(raw)


def mix_dict(raw: Any) -> dict[str, int]:
    return _mix(raw)
