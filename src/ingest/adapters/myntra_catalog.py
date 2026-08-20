from __future__ import annotations

from typing import Any

from src.ingest.adapters.base import CanonicalFeedback, build_record, cell, join_text, path_lcontains


class MyntraCatalogAdapter:
    name = "myntra_catalog"

    def matches(self, relative_path: str) -> bool:
        if path_lcontains(relative_path, "review"):
            return False
        return path_lcontains(relative_path, "myntra_dataset", "myntra-products", "myntra_fashion")

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
            for part in (cell(raw, "brand"), cell(raw, "product_type", "type"), cell(raw, "ideal_for"))
            if part
        )
        return build_record(
            source="myntra_catalog",
            text=join_text(
                cell(raw, "size_fit"),
                cell(raw, "product_details"),
                cell(raw, "body"),
                cell(raw, "complete_the_look"),
                cell(raw, "title", "name"),
            ),
            relative_path=relative_path,
            line_no=line_no,
            ingest_at=ingest_at,
            native_id=cell(raw, "uniq_id", "product_id", "sku"),
            source_url="",
            authored_at=cell(raw, "crawl_timestamp"),
            product_or_category=category,
            user_key="",
            raw=raw,
            extra_meta={"adapter": self.name, "hf_dataset": cell(raw, "_hf_dataset")},
        )
