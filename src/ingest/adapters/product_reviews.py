from __future__ import annotations

from typing import Any

from src.ingest.adapters.base import CanonicalFeedback, build_record, cell, join_text, path_lcontains


class ClothingReviewsAdapter:
    name = "product_reviews"

    def matches(self, relative_path: str) -> bool:
        return path_lcontains(
            relative_path,
            "womens-clothing",
            "clothing-ecommerce",
            "clothing_ecommerce",
        )

    def convert(
        self,
        raw: dict[str, Any],
        *,
        relative_path: str,
        line_no: int,
        ingest_at: str,
    ) -> CanonicalFeedback | None:
        category = " / ".join(
            part
            for part in (
                cell(raw, "department_name", "Department Name"),
                cell(raw, "class_name", "Class Name"),
            )
            if part
        )
        return build_record(
            source="product_reviews",
            text=cell(raw, "review_text", "Review Text", "text"),
            relative_path=relative_path,
            line_no=line_no,
            ingest_at=ingest_at,
            source_url="",
            authored_at="",
            rating=raw.get("rating") if raw.get("rating") is not None else raw.get("Rating"),
            product_or_category=category,
            user_key="",
            raw=raw,
            extra_meta={
                "adapter": self.name,
                "hf_dataset": cell(raw, "_hf_dataset"),
                "hf_split": cell(raw, "_hf_split"),
            },
        )


class MyntraPdpReviewsAdapter:
    name = "myntra_reviews"

    def matches(self, relative_path: str) -> bool:
        return path_lcontains(relative_path, "myntra_product_reviews", "myntra-reviews")

    def convert(
        self,
        raw: dict[str, Any],
        *,
        relative_path: str,
        line_no: int,
        ingest_at: str,
    ) -> CanonicalFeedback | None:
        return build_record(
            source="myntra_reviews",
            text=join_text(cell(raw, "review", "text", "content"), cell(raw, "title")),
            relative_path=relative_path,
            line_no=line_no,
            ingest_at=ingest_at,
            native_id=cell(raw, "id", "reviewId"),
            source_url=cell(raw, "reviewUrl", "url"),
            authored_at=cell(raw, "updatedAt", "date", "createdAt"),
            rating=raw.get("userRating") if raw.get("userRating") is not None else raw.get("rating"),
            product_or_category=cell(raw, "productName", "style.id"),
            user_key=cell(raw, "userName", "author"),
            raw=raw,
            extra_meta={"adapter": self.name},
        )
