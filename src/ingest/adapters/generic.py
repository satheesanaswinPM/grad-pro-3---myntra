from __future__ import annotations

from typing import Any

from src.ingest.adapters.base import CanonicalFeedback, build_record, cell, join_text
from src.qualify.schema import infer_role


class GenericAdapter:
    """Catch-all so new sources can be added without changing the builder."""

    name = "other"

    def matches(self, relative_path: str) -> bool:
        return True

    def convert(
        self,
        raw: dict[str, Any],
        *,
        relative_path: str,
        line_no: int,
        ingest_at: str,
    ) -> CanonicalFeedback | None:
        roles: dict[str, str] = {}
        for key in raw:
            role = infer_role(key)
            if role and role not in roles:
                roles[role] = key
        text_key = roles.get("text")
        text = cell(raw, text_key) if text_key else ""
        if not text:
            longest = ""
            for value in raw.values():
                if isinstance(value, str) and len(value.strip()) > len(longest):
                    longest = value.strip()
            text = longest
        return build_record(
            source="other",
            text=join_text(text),
            relative_path=relative_path,
            line_no=line_no,
            ingest_at=ingest_at,
            native_id=cell(raw, "id", "reviewId", "record_id"),
            source_url=cell(raw, roles["url"]) if "url" in roles else cell(raw, "url"),
            authored_at=cell(raw, roles["date"]) if "date" in roles else "",
            rating=raw.get(roles["rating"]) if "rating" in roles else None,
            product_or_category=cell(raw, roles["product_or_category"])
            if "product_or_category" in roles
            else "",
            user_key=cell(raw, roles["user_key"]) if "user_key" in roles else "",
            raw=raw,
            extra_meta={"adapter": self.name},
        )
