"""Apply Phase 2 tags to one CanonicalFeedback row."""

from __future__ import annotations

from typing import Any

from src.process.rules import (
    APP_ID_LIKE,
    CATALOG_SOURCES,
    CATEGORY_KEYWORDS,
    COMPILED_APP_OPS,
    COMPILED_EXTERNAL,
    COMPILED_INCLUSION,
    COMPILED_JOURNEY,
    MIN_TEXT_CHARS,
    STAGE_ORDER,
)


def collapsed_text(text: str) -> str:
    return " ".join((text or "").split())


def is_emoji_only(text: str) -> bool:
    """True when the row has content but not a single letter or digit -- emoji/symbols/punctuation only."""
    return bool(text.strip()) and not any(ch.isalnum() for ch in text)


def is_mixed_dialect(language: str) -> bool:
    """True for code-switched text: Hinglish, or a non-Latin script mixed with Latin (Phase 1's `{script}+latin`)."""
    return language == "hinglish" or language.endswith("+latin")


def match_inclusion(text: str) -> list[str]:
    return [rule.id for rule, pattern in COMPILED_INCLUSION if pattern.search(text)]


def match_journey(text: str) -> list[str]:
    stages: list[str] = []
    seen: set[str] = set()
    for rule, pattern in COMPILED_JOURNEY:
        if rule.family not in seen and pattern.search(text):
            seen.add(rule.family)
            stages.append(rule.family)
    return stages


def primary_stage(stages: list[str]) -> str:
    rank = {name: i for i, name in enumerate(STAGE_ORDER)}
    if not stages:
        return "unlabeled"
    return sorted(stages, key=lambda name: rank.get(name, 99))[0]


def match_external(text: str) -> list[str]:
    return [name for name, pattern, _label in COMPILED_EXTERNAL if pattern.search(text)]


def fashion_category(product_or_category: str, text: str) -> tuple[str, str]:
    field = (product_or_category or "").strip()
    if field and not APP_ID_LIKE.search(field):
        mapped = _bucket(field.lower())
        if mapped:
            return mapped, "product_field"
        if "/" in field:
            return "Clothing", "product_field"
    mapped = _bucket((text or "").lower())
    if mapped:
        return mapped, "text_keyword"
    return "unlabeled", "unlabeled"


def _bucket(blob: str) -> str:
    for label, keywords in CATEGORY_KEYWORDS:
        if any(keyword in blob for keyword in keywords):
            return label
    return ""


def decide_relevance(row: dict[str, Any]) -> dict[str, Any]:
    text = collapsed_text(str(row.get("text") or ""))
    source = str(row.get("source") or "")
    language = str(row.get("language") or "unknown")
    inclusion = match_inclusion(text)
    exclusion: list[str] = []

    if source in CATALOG_SOURCES:
        exclusion.append("ex_catalog_copy")
    if len(text) < MIN_TEXT_CHARS:
        exclusion.append("ex_too_short")
    if COMPILED_APP_OPS.search(text) and not inclusion:
        exclusion.append("ex_app_ops_only")
    if is_emoji_only(text):
        exclusion.append("ex_emoji_only")
    elif is_mixed_dialect(language):
        exclusion.append("ex_mixed_dialect")
    elif language != "en":
        exclusion.append("ex_non_english")

    is_relevant = bool(inclusion) and not exclusion
    stages = match_journey(text)
    category, category_source = fashion_category(str(row.get("product_or_category") or ""), text)
    external = match_external(text)

    return {
        "is_relevant": is_relevant,
        "inclusion_rules": inclusion,
        "exclusion_rules": exclusion,
        "journey_stages": stages,
        "journey_stage": primary_stage(stages),
        "fashion_category": category,
        "category_source": category_source,
        "external_destinations": external,
        "text_length": len(text),
    }
