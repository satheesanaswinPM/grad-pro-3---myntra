"""Lightweight language tagging for quality reporting. Not an LLM step."""

from __future__ import annotations

from collections import Counter

SCRIPT_RANGES: tuple[tuple[str, int, int], ...] = (
    ("hi", 0x0900, 0x097F),
    ("bn", 0x0980, 0x09FF),
    ("pa", 0x0A00, 0x0A7F),
    ("gu", 0x0A80, 0x0AFF),
    ("or", 0x0B00, 0x0B7F),
    ("ta", 0x0B80, 0x0BFF),
    ("te", 0x0C00, 0x0C7F),
    ("kn", 0x0C80, 0x0CFF),
    ("ml", 0x0D00, 0x0D7F),
)

EN_MARKERS = {
    "the",
    "and",
    "to",
    "of",
    "a",
    "in",
    "is",
    "it",
    "for",
    "on",
    "this",
    "that",
    "with",
    "was",
    "are",
    "not",
    "but",
    "have",
    "app",
    "product",
}
HINGLISH_MARKERS = {
    "hai",
    "nahi",
    "nahin",
    "kya",
    "bahut",
    "acha",
    "accha",
    "achha",
    "bhai",
    "yaar",
    "mat",
    "karo",
    "kitna",
    "bohot",
    "theek",
    "thik",
    "wala",
    "wali",
}


def detect_language(text: str) -> str:
    if not text or not str(text).strip():
        return "empty"
    raw = str(text)
    script_counts: Counter[str] = Counter()
    latin = 0
    letters = 0
    for ch in raw:
        code = ord(ch)
        if ch.isalpha():
            letters += 1
        hit = False
        for label, start, end in SCRIPT_RANGES:
            if start <= code <= end:
                script_counts[label] += 1
                hit = True
                break
        if not hit and ("A" <= ch <= "Z" or "a" <= ch <= "z"):
            latin += 1
    if not letters:
        return "unknown"
    if script_counts:
        top, count = script_counts.most_common(1)[0]
        if count / letters >= 0.25:
            if latin / letters >= 0.25:
                return f"{top}+latin"
            return top
    tokens = {t.strip(".,!?;:\"'()[]").lower() for t in raw.split()}
    hi_hits = len(tokens & HINGLISH_MARKERS)
    en_hits = len(tokens & EN_MARKERS)
    if hi_hits >= 2 and hi_hits >= en_hits:
        return "hinglish"
    if en_hits >= 2:
        return "en"
    if latin / max(letters, 1) >= 0.6:
        return "latin-other"
    return "unknown"


def language_distribution(texts: list[str]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for text in texts:
        counts[detect_language(text)] += 1
    return dict(counts.most_common())
