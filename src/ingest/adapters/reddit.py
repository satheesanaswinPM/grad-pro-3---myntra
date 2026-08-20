from __future__ import annotations

from typing import Any

from src.ingest.adapters.base import CanonicalFeedback, build_record, cell, join_text, path_lcontains


class RedditAdapter:
    name = "reddit"

    def matches(self, relative_path: str) -> bool:
        return path_lcontains(relative_path, "reddit")

    def convert(
        self,
        raw: dict[str, Any],
        *,
        relative_path: str,
        line_no: int,
        ingest_at: str,
    ) -> CanonicalFeedback | None:
        return build_record(
            source="reddit",
            text=join_text(cell(raw, "body", "selftext", "text", "content"), cell(raw, "title")),
            relative_path=relative_path,
            line_no=line_no,
            ingest_at=ingest_at,
            native_id=cell(raw, "id", "parsedId"),
            source_url=cell(raw, "url", "permalink"),
            authored_at=cell(raw, "createdAt", "created_utc", "date"),
            product_or_category=cell(raw, "communityName", "parsedCommunityName", "subreddit"),
            user_key=cell(raw, "username", "author", "user"),
            raw=raw,
            extra_meta={"adapter": self.name, "dataType": cell(raw, "dataType")},
        )
