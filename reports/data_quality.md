# Data quality report — Phase 0

Generated: 2026-08-20T00:34:46  
Raw root: `C:/Users/sathe/grad project 3rs attempt/data/raw` (read-only)  
Records inspected: **39470** across **11** file(s)

This report inventories the scrape before any cleaning, LLM extraction, or modelling.
Original files were not modified.

## 1. Files and folders

| Relative path | Format | Bytes | Records | Source guess | Load error |
| --- | --- | --- | --- | --- | --- |
| apify/google_play_reviews.jsonl | jsonl | 409223 | 499 | google_play |  |
| apify/myntra_product_reviews.jsonl | jsonl | 0 | 0 | product_reviews |  |
| apify/reddit_myntra.jsonl | jsonl | 90442 | 80 | reddit |  |
| app_store/myntra.jsonl | jsonl | 16946 | 50 | app_store |  |
| google_play/ajio.jsonl | jsonl | 208505 | 400 | google_play |  |
| google_play/meesho.jsonl | jsonl | 272141 | 400 | google_play |  |
| google_play/myntra.jsonl | jsonl | 202994 | 400 | google_play |  |
| huggingface/Gssmc__myntra_dataset/train.jsonl | jsonl | 10845712 | 15000 | huggingface |  |
| huggingface/saattrupdan__womens-clothing-ecommerce-reviews/test.jsonl | jsonl | 620902 | 1000 | product_reviews |  |
| huggingface/saattrupdan__womens-clothing-ecommerce-reviews/train.jsonl | jsonl | 12954314 | 20641 | product_reviews |  |
| huggingface/saattrupdan__womens-clothing-ecommerce-reviews/val.jsonl | jsonl | 620361 | 1000 | product_reviews |  |

## 2. Formats and schemas

Per-file field names, inferred CanonicalFeedback roles, dtypes, and missingness are in [`schema_catalog.json`](schema_catalog.json).

Inferred roles are name-based heuristics (e.g. `review_text` → `text`). They are not ground truth.

## 3. Available fields (CanonicalFeedback mapping)

| Role | Non-empty records | Missing | Missing % |
| --- | --- | --- | --- |
| text | 39470 | 0 | 0.0 |
| source | 39470 | 0 | 0.0 |
| date | 1579 | 37891 | 96.0 |
| rating | 24390 | 15080 | 38.21 |
| product_or_category | 1072 | 38398 | 97.28 |
| user_key | 1829 | 37641 | 95.37 |
| url | 579 | 38891 | 98.53 |

Population for missing %: all inspected records (n = 39470).

## 4. Record count

- Files walked: 11
- Files parsed into the catalog: 11
- Total records: 39470

## 5. Duplicates

- Extra copies of the same **full row**: 14000
- Extra copies of the same **text** (case-insensitive SHA-256, empty text excluded): 14946
- Unique non-empty texts: 24524
- Empty text records: 0

Duplicates are counted, not removed. Deduplication is Phase 1.

## 6. Missing values

See the role table above and per-field `missing_pct` in the schema catalog.

## 7. Language distribution

Heuristic script + token tagging only (not an LLM). Labels include `en`, `hi`, `hinglish`, other Indic scripts, `latin-other`, `empty`, `unknown`.

| Language | Records | % of records |
| --- | --- | --- |
| en | 23002 | 58.28 |
| latin-other | 16389 | 41.52 |
| unknown | 42 | 0.11 |
| hinglish | 29 | 0.07 |
| hi | 6 | 0.02 |
| kn | 1 | 0.0 |
| or+latin | 1 | 0.0 |

Population: all inspected records (n = 39470). Non-English rows are **not** dropped in Phase 0.

## 8. Source distribution

Folder/file names supply `source_guess` when a `source` column is absent. Full breakdown: [`source_coverage.csv`](source_coverage.csv).

| Source | Records | % | Unique text | Missing text % |
| --- | --- | --- | --- | --- |
| huggingface | 37641 | 95.37 | 23574 | 0.0 |
| google_play | 1200 | 3.04 | 849 | 0.0 |
| apify | 579 | 1.47 | 429 | 0.0 |
| app_store | 50 | 0.13 | 46 | 0.0 |

Population: all inspected records (n = 39470).

## 9. Myntra vs broader fashion shopping

mixed — Myntra-specific and broader online-fashion shopping

- Myntra signal (mentions in path, source, or text): 39.49%
- Other-retailer signal: 2.07%
- Unlabeled: 58.45%
- Label counts: `{"unlabeled": 23071, "myntra": 15582, "broader_fashion": 814, "mixed": 3}`

This is corpus coverage, not a claim about why wishlists fail to convert.

## 10. Date span

- Min date string (raw, unparsed): 2019-06-01 05:10:12 +0000
- Max date string (raw, unparsed): 2026-08-18T19:01:33.771Z

## Load errors

None.

## What Phase 0 did not do

- No writes under `data/raw/`
- No LLM extraction, sentiment, or topic modelling
- No assumption that price, size, reviews, or discounts are the user problem
- No processed/canonical dataset (that is Phase 1)

## Exit gate

- Quality report: this file
- Schema catalog: `reports/schema_catalog.json`
- Source coverage: `reports/source_coverage.csv`
- Raw files untouched: yes

Re-run after adding or replacing files in `data/raw/`:

```bash
python -m src.qualify
```
