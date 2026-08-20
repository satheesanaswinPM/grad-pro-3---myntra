"""Classify whether the corpus is Myntra-specific, broader fashion, or mixed."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

MYNTRA_TERMS = ("myntra",)
OTHER_RETAIL = (
    "ajio",
    "nykaa",
    "meesho",
    "tatacliq",
    "tata cliq",
    "amazon fashion",
    "flipkart",
    "shein",
    "zara",
    "h&m",
    "hm ",
    "asos",
    "urbanic",
    "macy",
    "nordstrom",
    "zalando",
    "jabong",
    "koovs",
)


def _haystack(path: Path, source: str | None, text: str) -> str:
    parts = [path.as_posix().lower(), (source or "").lower(), (text or "").lower()]
    return " ".join(parts)


def classify_record(path: Path, source: str | None, text: str) -> str:
    blob = _haystack(path, source, text)
    myntra = any(term in blob for term in MYNTRA_TERMS)
    other = any(term in blob for term in OTHER_RETAIL)
    if myntra and other:
        return "mixed"
    if myntra:
        return "myntra"
    if other:
        return "broader_fashion"
    return "unlabeled"


def corpus_scope(labels: list[str]) -> dict[str, object]:
    counts = Counter(labels)
    total = sum(counts.values()) or 1
    myntra = counts.get("myntra", 0) + counts.get("mixed", 0)
    broader = counts.get("broader_fashion", 0) + counts.get("mixed", 0)
    unlabeled = counts.get("unlabeled", 0)
    if myntra and broader:
        overall = "mixed — Myntra-specific and broader online-fashion shopping"
    elif myntra:
        overall = "Myntra-specific (filename, source, or text mentions Myntra)"
    elif broader:
        overall = "broader online-fashion shopping (other retailers named; Myntra not found)"
    else:
        overall = (
            "unlabeled — no retailer names found in paths, source fields, or text; "
            "could still be Myntra app reviews that never mention the brand"
        )
    return {
        "overall": overall,
        "counts": dict(counts),
        "pct_myntra_signal": round(100.0 * myntra / total, 2),
        "pct_broader_signal": round(100.0 * broader / total, 2),
        "pct_unlabeled": round(100.0 * unlabeled / total, 2),
    }
