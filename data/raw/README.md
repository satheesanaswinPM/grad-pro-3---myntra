# Raw scrape (immutable)

Drop original scraped feedback files here, or run:

```bash
python -m src.ingest.fetch_data
```

That command downloads Hugging Face datasets into `huggingface/` and, if `APIFY_TOKEN` is set, Apify actor output into `apify/`. Without an Apify token it falls back to public Google Play / App Store reviews.

Phase 0 and later pipelines **read** this folder only. They never overwrite, rename, or clean files in place.

Supported formats: `.json`, `.jsonl`, `.ndjson`, `.csv`, `.tsv`, `.txt`, `.parquet` (optional), `.xlsx` (optional).

After adding files, re-run Phase 0 from the project root:

```bash
python -m src.qualify
```
