"""Pull Hugging Face datasets, then Apify (or Play Store fallback if no token)."""

from __future__ import annotations

from src.ingest.fetch_apify import get_token
from src.ingest.fetch_apify import run as run_apify
from src.ingest.fetch_huggingface import run as run_hf
from src.ingest.fetch_play_fallback import run as run_play_fallback


def main() -> int:
    print("=== Hugging Face ===")
    run_hf()
    print("=== Apify ===")
    if get_token():
        run_apify()
    else:
        print("APIFY_TOKEN missing — using public Google Play / App Store fallback (not Apify).")
        print("Set APIFY_TOKEN in .env to pull Myntra product reviews and Reddit via Apify.")
        run_play_fallback()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
