"""CanonicalFeedback mapping helpers shared by source adapters."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

from src.qualify.language import detect_language
from src.qualify.schema import is_missing

NATIVE_ID_RE = re.compile(r"[^a-zA-Z0-9._:-]+")
DROP_META = {
    "html",
    "userImage",
    "images",
    "criteriaRatings",
    "specifications",
    "inventory",
    "care_instructions",
}


@dataclass
class CanonicalFeedback:
    record_id: str
    source: str
    source_url: str
    authored_at: str
    language: str
    raw_ref: str
    text: str
    rating: float | None
    product_or_category: str
    user_key: str
    ingest_at: str
    content_hash: str
    metadata: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class Adapter(Protocol):
    name: str

    def matches(self, relative_path: str) -> bool: ...

    def convert(
        self,
        raw: dict[str, Any],
        *,
        relative_path: str,
        line_no: int,
        ingest_at: str,
    ) -> CanonicalFeedback | None: ...


def cell(raw: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = raw.get(key)
        if is_missing(value):
            continue
        text = str(value).strip()
        if text and text.lower() not in {"none", "null", "nan"}:
            return text
    return ""


def join_text(*parts: str) -> str:
    seen: set[str] = set()
    kept: list[str] = []
    for part in parts:
        text = (part or "").strip()
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        kept.append(text)
    return "\n\n".join(kept)


def parse_rating(value: Any) -> float | None:
    if is_missing(value):
        return None
    try:
        number = float(str(value).strip())
    except ValueError:
        return None
    if number != number:  # NaN
        return None
    return number


def content_hash(text: str) -> str:
    normalized = " ".join(text.casefold().split())
    return hashlib.sha256(normalized.encode("utf-8", errors="replace")).hexdigest()


def make_record_id(source: str, native_id: str, digest: str) -> str:
    if native_id:
        slug = NATIVE_ID_RE.sub("-", native_id).strip("-")[:80]
        if slug:
            return f"{source}:{slug}"
    return f"{source}:{digest[:16]}"


def raw_ref(relative_path: str, line_no: int) -> str:
    return f"data/raw/{relative_path}#{line_no}"


def compact_metadata(raw: dict[str, Any], extra: dict[str, Any] | None = None) -> str:
    meta: dict[str, Any] = {}
    for key, value in raw.items():
        if key.startswith("_") or key in DROP_META:
            continue
        if is_missing(value):
            continue
        if isinstance(value, str) and len(value) > 500:
            continue
        meta[key] = value
    if extra:
        meta.update(extra)
    return json.dumps(meta, ensure_ascii=False, default=str)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_record(
    *,
    source: str,
    text: str,
    relative_path: str,
    line_no: int,
    ingest_at: str,
    native_id: str = "",
    source_url: str = "",
    authored_at: str = "",
    rating: Any = None,
    product_or_category: str = "",
    user_key: str = "",
    raw: dict[str, Any] | None = None,
    extra_meta: dict[str, Any] | None = None,
) -> CanonicalFeedback | None:
    text = text.strip()
    if not text:
        return None
    digest = content_hash(text)
    return CanonicalFeedback(
        record_id=make_record_id(source, native_id, digest),
        source=source,
        source_url=source_url,
        authored_at=authored_at,
        language=detect_language(text),
        raw_ref=raw_ref(relative_path, line_no),
        text=text,
        rating=parse_rating(rating),
        product_or_category=product_or_category,
        user_key=user_key,
        ingest_at=ingest_at,
        content_hash=digest,
        metadata=compact_metadata(raw or {}, extra_meta),
    )


def path_lcontains(relative_path: str, *needles: str) -> bool:
    lowered = relative_path.replace("\\", "/").lower()
    return any(needle in lowered for needle in needles)
