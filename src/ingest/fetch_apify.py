"""Fetch review datasets from Apify actors into data/raw/apify/.

Requires APIFY_TOKEN or APIFY_API_TOKEN in the environment or a project .env file.
Does not write into existing Hugging Face files.
"""

from __future__ import annotations

from datetime import timedelta
import json
import os
from pathlib import Path
from typing import Any

from src.ingest.env import load_dotenv
from src.qualify.config import RAW_DIR, ROOT

APIFY_DIR = RAW_DIR / "apify"

# Myntra Android app + a few fashion-shopping peers named in the brief.
PLAY_URLS = [
    "https://play.google.com/store/apps/details?id=com.myntra.android&hl=en_IN",
    "https://play.google.com/store/apps/details?id=com.ril.ajio&hl=en_IN",
    "https://play.google.com/store/apps/details?id=com.meesho.supply&hl=en_IN",
]

# Public Myntra product pages used as a small seed for product-review actors.
MYNTRA_PRODUCT_URLS = [
    "https://www.myntra.com/jeans/levis/levis-men-blue-512-slim-tapered-fit-mid-rise-light-fade-stretchable-jeans/2485335/buy",
    "https://www.myntra.com/kurtas/anouk/anouk-women-pink-printed-straight-kurta/10941208/buy",
    "https://www.myntra.com/sports-shoes/nike/nike-men-black-revolution-6-running-shoes/16869844/buy",
]


def get_token() -> str | None:
    load_dotenv()
    return os.environ.get("APIFY_TOKEN") or os.environ.get("APIFY_API_TOKEN")


def _write_jsonl(path: Path, items: list[dict[str, Any]], extra: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            row = dict(item)
            row.update(extra)
            handle.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def run_actor(client: Any, actor_id: str, run_input: dict[str, Any], timeout_secs: int = 300) -> list[dict[str, Any]]:
    print(f"Starting Apify actor {actor_id}")
    wait = timedelta(seconds=timeout_secs)
    run = client.actor(actor_id).call(
        run_input=run_input,
        run_timeout=wait,
        wait_duration=wait,
    )
    if run is None:
        raise RuntimeError(f"{actor_id} returned no run object")
    dataset_id = getattr(run, "default_dataset_id", None)
    if not dataset_id:
        raise RuntimeError(f"{actor_id} finished without a default dataset")
    return list(client.dataset(dataset_id).iterate_items())


def fetch_play_reviews(client: Any) -> Path:
    items = run_actor(
        client,
        "webdatalabs/google-play-reviews-scraper",
        {
            "startUrls": [{"url": url} for url in PLAY_URLS],
            "maxReviews": 400,
            "sortBy": "NEWEST",
            "language": "en",
        },
        timeout_secs=360,
    )
    out = APIFY_DIR / "google_play_reviews.jsonl"
    _write_jsonl(
        out,
        items,
        {"_origin": "apify", "_apify_actor": "webdatalabs/google-play-reviews-scraper", "source": "google_play"},
    )
    print(f"wrote {out.relative_to(ROOT)} ({len(items)} items)")
    return out


def fetch_myntra_product_reviews(client: Any) -> Path:
    items = run_actor(
        client,
        "shahidirfan/myntra-reviews-scraper",
        {
            "productUrls": [{"url": url} for url in MYNTRA_PRODUCT_URLS],
            "reviewsLimit": 40,
        },
        timeout_secs=360,
    )
    out = APIFY_DIR / "myntra_product_reviews.jsonl"
    _write_jsonl(
        out,
        items,
        {"_origin": "apify", "_apify_actor": "shahidirfan/myntra-reviews-scraper", "source": "myntra_reviews"},
    )
    print(f"wrote {out.relative_to(ROOT)} ({len(items)} items)")
    return out


def fetch_reddit(client: Any) -> Path:
    items = run_actor(
        client,
        "trudax/reddit-scraper-lite",
        {
            "startUrls": [
                {"url": "https://www.reddit.com/search/?q=myntra%20wishlist"},
                {"url": "https://www.reddit.com/search/?q=myntra%20size%20fit"},
                {"url": "https://www.reddit.com/r/indianfashionaddicts/search/?q=myntra&restrict_sr=1"},
            ],
            "maxItems": 80,
            "skipComments": False,
        },
        timeout_secs=360,
    )
    out = APIFY_DIR / "reddit_myntra.jsonl"
    _write_jsonl(
        out,
        items,
        {"_origin": "apify", "_apify_actor": "trudax/reddit-scraper-lite", "source": "reddit"},
    )
    print(f"wrote {out.relative_to(ROOT)} ({len(items)} items)")
    return out


def run() -> list[Path]:
    token = get_token()
    if not token:
        raise RuntimeError(
            "APIFY_TOKEN is not set. Add it to a .env file at the project root "
            "(see .env.example) and re-run: python -m src.ingest.fetch_apify"
        )
    from apify_client import ApifyClient

    client = ApifyClient(token)
    APIFY_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    errors: list[str] = []
    for fn in (fetch_play_reviews, fetch_myntra_product_reviews, fetch_reddit):
        try:
            written.append(fn(client))
        except Exception as exc:  # noqa: BLE001 — one actor failing should not drop the others
            errors.append(f"{fn.__name__}: {exc}")
            print(f"Apify actor failed ({fn.__name__}): {exc}")
    (APIFY_DIR / "SOURCE.md").write_text(
        "\n".join(
            [
                "# Apify",
                "",
                "Actors attempted:",
                "- webdatalabs/google-play-reviews-scraper",
                "- shahidirfan/myntra-reviews-scraper",
                "- trudax/reddit-scraper-lite",
                "",
                "Errors:",
                *(errors or ["none"]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    if not written:
        raise RuntimeError("All Apify actors failed. See data/raw/apify/SOURCE.md")
    return written


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
