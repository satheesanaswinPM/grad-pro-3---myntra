from __future__ import annotations

from typing import Any

from src.ingest.adapters.base import CanonicalFeedback, build_record, cell, join_text, path_lcontains


class ProductQAAdapter:
    name = "product_qa"

    def matches(self, relative_path: str) -> bool:
        return path_lcontains(relative_path, "product_qa", "/qa/", "q&a", "qna")

    def convert(
        self,
        raw: dict[str, Any],
        *,
        relative_path: str,
        line_no: int,
        ingest_at: str,
    ) -> CanonicalFeedback | None:
        return build_record(
            source="product_qa",
            text=join_text(
                cell(raw, "question", "question_text"),
                cell(raw, "answer", "answer_text", "text", "body"),
            ),
            relative_path=relative_path,
            line_no=line_no,
            ingest_at=ingest_at,
            native_id=cell(raw, "id", "qa_id"),
            source_url=cell(raw, "url"),
            authored_at=cell(raw, "date", "created_at"),
            product_or_category=cell(raw, "product", "category", "product_name"),
            user_key=cell(raw, "user", "username", "author"),
            raw=raw,
            extra_meta={"adapter": self.name},
        )
