"""Extraction row contract for Phase 3."""

from __future__ import annotations

from typing import Any

EXTRACTORS = ("intent", "barrier", "need", "behavior")

SUGGESTED_INTENTS = (
    "strong_purchase",
    "future_purchase",
    "bookmark",
    "comparison",
    "price_watch",
    "occasion",
    "inspiration",
    "uncertain",
)

SUGGESTED_BARRIERS = (
    "fit",
    "quality",
    "fabric",
    "styling",
    "occasion",
    "proof",
    "returns",
    "delivery",
    "availability",
    "value",
    "comparison",
    "fatigue",
    "urgency",
    "trust",
)

PROMPT_VERSION_LLM = "extract_v1"
PROMPT_VERSION_LOCAL = "span_extract_v2"

EXTRACTION_COLUMNS = (
    "extraction_id",
    "record_id",
    "extractor",
    "label",
    "evidence_span",
    "confidence",
    "prompt_version",
    "status",
    "ai_interpretation",
    "content_hash",
)


def empty_extraction_row() -> dict[str, Any]:
    return {name: None for name in EXTRACTION_COLUMNS}
