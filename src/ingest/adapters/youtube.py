from __future__ import annotations

from typing import Any

from src.ingest.adapters.base import CanonicalFeedback, build_record, cell, join_text, path_lcontains


class YouTubeAdapter:
    name = "youtube"

    def matches(self, relative_path: str) -> bool:
        return path_lcontains(relative_path, "youtube", "yt_")

    def convert(
        self,
        raw: dict[str, Any],
        *,
        relative_path: str,
        line_no: int,
        ingest_at: str,
    ) -> CanonicalFeedback | None:
        return build_record(
            source="youtube",
            text=join_text(cell(raw, "text", "comment", "content", "body"), cell(raw, "title")),
            relative_path=relative_path,
            line_no=line_no,
            ingest_at=ingest_at,
            native_id=cell(raw, "id", "commentId", "videoId"),
            source_url=cell(raw, "url", "link"),
            authored_at=cell(raw, "publishedAt", "date", "authored_at"),
            user_key=cell(raw, "author", "userName", "username"),
            raw=raw,
            extra_meta={"adapter": self.name},
        )
