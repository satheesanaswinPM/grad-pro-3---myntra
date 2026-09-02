"""Loads and filters the real Myntra product catalog for the MVP demo.

Reads data/raw/huggingface/Gssmc__myntra_dataset/train.jsonl directly (read-only) -- the raw scrape,
not the discovery pipeline's processed tables. Do not hand-write mock products; do not surface
variant_compare_at_price anywhere (discount framing is out of scope for the no-monetary-incentive MVP).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "data" / "raw" / "huggingface" / "Gssmc__myntra_dataset" / "train.jsonl"

# A coherent, comparable demo subset (see doc/mvp_problem_statement.md, Section 3). Of the 15,000
# rows only ~1,000 carry full product metadata; the rest are incomplete scrape rows and are dropped.
DEMO_CATEGORIES = ("Kurtas", "Kurta Sets", "Dresses", "Tops")


def _category(row: dict[str, Any]) -> str:
    parts = (row.get("type") or "").split("/")
    return parts[2] if len(parts) > 2 else (row.get("type") or "Other")


def _clean(row: dict[str, Any]) -> dict[str, Any] | None:
    title = row.get("title")
    brand = row.get("brand")
    price = row.get("variant_price")
    if not title or not brand or price is None:
        return None
    if row.get("is_in_stock") != "In Stock":
        return None
    category = _category(row)
    if category not in DEMO_CATEGORIES:
        return None
    return {
        "id": str(row.get("uniq_id") or row.get("variant_sku") or title),
        "title": str(title),
        "brand": str(brand),
        "category": category,
        "price": float(price),
        "material": str(row.get("dominant_material") or ""),
        "color": str(row.get("dominant_color") or ""),
        "size_fit": str(row.get("size_fit") or ""),
        "details": str(row.get("product_details") or ""),
        "pairing": str(row.get("complete_the_look") or ""),
        "occasion": str(row.get("ideal_for") or ""),
    }


def load_catalog() -> list[dict[str, Any]]:
    """Read the raw catalog file and return the cleaned, filtered demo subset. No caching here --
    callers (the Streamlit app) are responsible for caching across reruns."""
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            f"Catalog not found at {CATALOG_PATH}. This MVP reads the raw scrape directly; "
            "it does not run the discovery pipeline."
        )
    seen: set[str] = set()
    items: list[dict[str, Any]] = []
    with CATALOG_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            cleaned = _clean(row)
            if cleaned is None or cleaned["id"] in seen:
                continue
            seen.add(cleaned["id"])
            items.append(cleaned)
    items.sort(key=lambda r: (r["category"], r["brand"], r["title"]))
    return items


def categories(items: list[dict[str, Any]]) -> list[str]:
    return sorted({item["category"] for item in items})
