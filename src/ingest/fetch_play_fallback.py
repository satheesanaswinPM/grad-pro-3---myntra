"""Public Play Store + App Store reviews when Apify cannot run (no token)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from src.qualify.config import RAW_DIR, ROOT

PLAY_DIR = RAW_DIR / "google_play"
APPSTORE_DIR = RAW_DIR / "app_store"

PLAY_APPS = [
    ("com.myntra.android", "myntra"),
    ("com.ril.ajio", "ajio"),
    ("com.meesho.supply", "meesho"),
]

# Myntra iOS app.
APPSTORE_ID = "907394059"


def fetch_play(app_id: str, brand: str, count: int = 400) -> Path:
    from google_play_scraper import Sort, reviews

    batch, _ = reviews(app_id, lang="en", country="in", sort=Sort.NEWEST, count=count)
    out = PLAY_DIR / f"{brand}.jsonl"
    PLAY_DIR.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for item in batch:
            row = {
                "reviewId": item.get("reviewId"),
                "userName": item.get("userName"),
                "content": item.get("content"),
                "score": item.get("score"),
                "thumbsUpCount": item.get("thumbsUpCount"),
                "reviewCreatedVersion": item.get("reviewCreatedVersion"),
                "at": item.get("at").isoformat() if item.get("at") else None,
                "replyContent": item.get("replyContent"),
                "app_id": app_id,
                "source": "google_play",
                "_origin": "google-play-scraper",
                "_note": "Public Play Store reviews. Used because APIFY_TOKEN was not set.",
            }
            handle.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    print(f"wrote {out.relative_to(ROOT)} ({len(batch)} items)")
    return out


def fetch_appstore() -> Path:
    url = (
        f"https://itunes.apple.com/in/rss/customerreviews/id={APPSTORE_ID}"
        "/sortBy=mostRecent/json"
    )
    req = Request(url, headers={"User-Agent": "wishlist-discovery-engine/0.1"})
    with urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    entries = payload.get("feed", {}).get("entry", [])
    reviews = entries[1:] if entries and "im:name" in entries[0] else entries
    out = APPSTORE_DIR / "myntra.jsonl"
    APPSTORE_DIR.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for entry in reviews:
            content = entry.get("content", {})
            rating = entry.get("im:rating", {})
            author = entry.get("author", {}).get("name", {})
            row = {
                "id": entry.get("id", {}).get("label"),
                "title": entry.get("title", {}).get("label"),
                "content": content.get("label") if isinstance(content, dict) else content,
                "rating": rating.get("label") if isinstance(rating, dict) else rating,
                "userName": author.get("label") if isinstance(author, dict) else author,
                "updated": entry.get("updated", {}).get("label"),
                "source": "app_store",
                "app_id": APPSTORE_ID,
                "_origin": "itunes_rss",
                "_fetched_at": datetime.now(timezone.utc).isoformat(),
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {out.relative_to(ROOT)} ({len(reviews)} items)")
    return out


def run() -> list[Path]:
    paths = [fetch_play(app_id, brand) for app_id, brand in PLAY_APPS]
    try:
        paths.append(fetch_appstore())
    except Exception as exc:  # noqa: BLE001
        print(f"App Store RSS failed: {exc}")
    (PLAY_DIR / "SOURCE.md").write_text(
        "Google Play reviews via google-play-scraper (public store pages).\n"
        "Replace/supplement with Apify by setting APIFY_TOKEN and running "
        "`python -m src.ingest.fetch_apify`.\n",
        encoding="utf-8",
    )
    return paths


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
