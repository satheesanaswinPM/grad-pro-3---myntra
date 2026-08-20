from __future__ import annotations

from typing import Any

from src.ingest.adapters.base import CanonicalFeedback, build_record, cell, join_text, path_lcontains


class AppStoreAdapter:
    name = "app_store"

    def matches(self, relative_path: str) -> bool:
        return path_lcontains(relative_path, "app_store", "appstore", "itunes")

    def convert(
        self,
        raw: dict[str, Any],
        *,
        relative_path: str,
        line_no: int,
        ingest_at: str,
    ) -> CanonicalFeedback | None:
        app_id = cell(raw, "app_id", "appId")
        native_id = cell(raw, "id")
        url = cell(raw, "url", "source_url")
        if not url and app_id:
            url = f"https://apps.apple.com/app/id{app_id}"
        return build_record(
            source="app_store",
            text=join_text(cell(raw, "content", "text", "review"), cell(raw, "title")),
            relative_path=relative_path,
            line_no=line_no,
            ingest_at=ingest_at,
            native_id=native_id,
            source_url=url,
            authored_at=cell(raw, "updated", "authored_at", "date"),
            rating=raw.get("rating") or raw.get("im:rating"),
            product_or_category=cell(raw, "app_id", "appId"),
            user_key=cell(raw, "userName", "author", "user"),
            raw=raw,
            extra_meta={"adapter": self.name},
        )
