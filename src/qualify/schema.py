"""Infer CanonicalFeedback-style field roles from raw column names."""

from __future__ import annotations

from collections import Counter
from typing import Any

from src.qualify.config import ROLE_ALIASES
from src.qualify.loaders import MAX_EXAMPLE_LEN


def normalize_name(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum() or ch in "._")


def infer_role(field_name: str) -> str | None:
    key = normalize_name(field_name)
    tail = key.split(".")[-1]
    compact = tail.replace("_", "")
    for role, aliases in ROLE_ALIASES.items():
        if tail in aliases or compact in {a.replace("_", "") for a in aliases}:
            return role
        if key in aliases:
            return role
    lowered = field_name.lower()
    if any(token in lowered for token in ("review", "comment", "feedback", "body")):
        if "url" not in lowered and "id" not in lowered:
            return "text"
    if "rating" in lowered or "stars" in lowered:
        return "rating"
    if any(token in lowered for token in ("created", "published", "timestamp", "datetime")):
        return "date"
    if any(token in lowered for token in ("username", "user_id", "author")):
        return "user_key"
    if "url" in lowered or "permalink" in lowered or lowered.endswith("href"):
        return "url"
    if any(token in lowered for token in ("category", "product", "brand")):
        return "product_or_category"
    return None


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def dtype_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    return "str"


def field_stats(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    names: list[str] = []
    seen: set[str] = set()
    for record in records:
        for key in record:
            if key not in seen:
                seen.add(key)
                names.append(key)

    n = len(records) or 1
    stats: list[dict[str, Any]] = []
    for name in names:
        values = [record.get(name) for record in records]
        present = [v for v in values if not is_missing(v)]
        types = Counter(dtype_name(v) for v in present)
        example = present[0] if present else None
        example_s = "" if example is None else str(example)
        if len(example_s) > MAX_EXAMPLE_LEN:
            example_s = example_s[: MAX_EXAMPLE_LEN - 1] + "…"
        stats.append(
            {
                "name": name,
                "inferred_role": infer_role(name),
                "dtype": types.most_common(1)[0][0] if types else "null",
                "non_null": len(present),
                "null": len(values) - len(present),
                "missing_pct": round(100.0 * (len(values) - len(present)) / n, 2),
                "example": example_s,
            }
        )
    return stats


def role_map(fields: list[dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for field in fields:
        role = field.get("inferred_role")
        if role and role not in mapping:
            mapping[role] = field["name"]
    return mapping
