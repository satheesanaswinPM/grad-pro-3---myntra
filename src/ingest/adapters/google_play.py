from __future__ import annotations

from typing import Any

from src.ingest.adapters.base import CanonicalFeedback, build_record, cell, path_lcontains


class GooglePlayAdapter:
    name = "google_play"

    def matches(self, relative_path: str) -> bool:
        return path_lcontains(relative_path, "google_play", "play_store", "playstore")

    def convert(
        self,
        raw: dict[str, Any],
        *,
        relative_path: str,
        line_no: int,
        ingest_at: str,
    ) -> CanonicalFeedback | None:
        app_id = cell(raw, "appId", "app_id")
        return build_record(
            source="google_play",
            text=cell(raw, "text", "content", "review"),
            relative_path=relative_path,
            line_no=line_no,
            ingest_at=ingest_at,
            native_id=cell(raw, "reviewId", "review_id", "id"),
            source_url=cell(raw, "url")
            or (f"https://play.google.com/store/apps/details?id={app_id}" if app_id else ""),
            authored_at=cell(raw, "reviewDate", "at", "date", "authored_at"),
            rating=raw.get("rating") if raw.get("rating") is not None else raw.get("score"),
            product_or_category=app_id,
            user_key=cell(raw, "userName", "user", "author"),
            raw=raw,
            extra_meta={"adapter": self.name, "app_id": app_id},
        )
