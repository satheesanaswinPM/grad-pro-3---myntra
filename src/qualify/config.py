"""Shared paths and field-role aliases for Phase 0 inspection."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
REPORTS_DIR = ROOT / "reports"
LOGS_DIR = ROOT / "data" / "logs"

SKIP_NAMES = {".gitkeep", ".ds_store", "thumbs.db"}
SKIP_SUFFIXES = {".md"}

TEXT_ALIASES = (
    "text",
    "review",
    "review_text",
    "reviewtext",
    "comment",
    "comment_text",
    "content",
    "body",
    "snippet",
    "message",
    "description",
    "title",
)
SOURCE_ALIASES = (
    "source",
    "platform",
    "site",
    "store",
    "app",
    "channel",
    "origin",
)
DATE_ALIASES = (
    "date",
    "created_at",
    "createdat",
    "time",
    "timestamp",
    "review_date",
    "reviewdate",
    "authored_at",
    "published_at",
    "updated_at",
)
RATING_ALIASES = ("rating", "stars", "score", "star", "star_rating", "im:rating")
CATEGORY_ALIASES = (
    "category",
    "product",
    "product_name",
    "productname",
    "brand",
    "item",
    "department",
    "vertical",
)
USER_ALIASES = (
    "user",
    "username",
    "user_id",
    "userid",
    "author",
    "reviewer",
    "reviewer_name",
    "name",
)
URL_ALIASES = ("url", "link", "source_url", "permalink", "href", "review_url")

ROLE_ALIASES = {
    "text": TEXT_ALIASES,
    "source": SOURCE_ALIASES,
    "date": DATE_ALIASES,
    "rating": RATING_ALIASES,
    "product_or_category": CATEGORY_ALIASES,
    "user_key": USER_ALIASES,
    "url": URL_ALIASES,
}
