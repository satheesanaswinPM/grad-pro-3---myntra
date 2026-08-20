"""Keep only extractions whose evidence_span is actually in the source text."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from src.analyze.schema import EXTRACTORS

SPAN_MAX = 400
FIRST_PERSON = re.compile(r"\b(i|i'm|i’ve|i've|me|my|we|our)\b", re.I)


def locate_span(text: str, span: str) -> str:
    if not text or not span:
        return ""
    needle = " ".join(span.split())
    hay = " ".join(text.split())
    if not needle:
        return ""
    idx = hay.lower().find(needle.lower())
    if idx >= 0:
        found = hay[idx : idx + len(needle)]
        return found[:SPAN_MAX]
    # Allow a shorter quoted fragment.
    if len(needle) > 24:
        piece = needle[:24]
        idx = hay.lower().find(piece.lower())
        if idx >= 0:
            return hay[idx : min(len(hay), idx + min(len(needle), SPAN_MAX))]
    return ""


def normalize_status(status: str, span: str) -> str:
    if status in {"observed_evidence", "hypothesis"}:
        return status
    return "observed_evidence" if FIRST_PERSON.search(span or "") else "hypothesis"


def make_extraction_id(record_id: str, extractor: str, label: str, span: str) -> str:
    digest = hashlib.sha256(f"{record_id}|{extractor}|{label}|{span}".encode("utf-8")).hexdigest()[:12]
    return f"{extractor}:{digest}"


def clamp_confidence(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.5
    return max(0.05, min(0.99, number))


def sanitize_payload(text: str, payload: dict[str, Any], prompt_version: str, content_hash: str) -> dict[str, list[dict[str, Any]]]:
    clean: dict[str, list[dict[str, Any]]] = {name: [] for name in EXTRACTORS}
    mapping = {
        "intent": payload.get("intents") or payload.get("intent") or [],
        "barrier": payload.get("barriers") or payload.get("barrier") or [],
        "need": payload.get("needs") or payload.get("need") or [],
        "behavior": payload.get("behaviors") or payload.get("behavior") or [],
    }
    for extractor, items in mapping.items():
        if not isinstance(items, list):
            continue
        seen: set[tuple[str, str]] = set()
        for item in items:
            if not isinstance(item, dict):
                continue
            label = str(item.get("label") or "").strip().lower().replace(" ", "_")
            if not label:
                continue
            span = locate_span(text, str(item.get("evidence_span") or item.get("span") or ""))
            if not span:
                continue
            key = (label, span.casefold())
            if key in seen:
                continue
            seen.add(key)
            clean[extractor].append(
                {
                    "extractor": extractor,
                    "label": label[:80],
                    "evidence_span": span,
                    "confidence": clamp_confidence(item.get("confidence")),
                    "prompt_version": prompt_version,
                    "status": normalize_status(str(item.get("status") or ""), span),
                    "ai_interpretation": str(item.get("interpretation") or item.get("ai_interpretation") or "").strip()[:400],
                    "content_hash": content_hash,
                }
            )
    return clean
