# Relevance and journey rules — Phase 2

Generated: 2026-08-19T19:15:38+00:00  
Input: `data/processed/canonical.parquet` (n = **24575**)  
Relevant corpus: `data/processed/relevant.parquet` (n = **17495**, 71.19% of canonical)  
Journey tags: `data/processed/journey_tags.parquet` (one row per canonical record)

These rules define the **denominator** for later percentages. They do not decide why wishlists fail to convert. Fit, quality, price, and similar phrases are inclusion *signals* to investigate, not assumed root causes.

## Denominators

| Population | n | Definition |
| --- | --- | --- |
| all | 24575 | Every CanonicalFeedback row from Phase 1 |
| relevant | 17495 | Canonical rows that match at least one inclusion rule and no exclusion rule |
| source slice | — | `source` on the canonical row |
| language slice | — | `language` from Phase 1; non-English rows are **not** dropped |

## Inclusion (OR)

A row is a candidate if **any** of these fire. Multiple rules may fire on one text.

| Rule id | Family | What it catches | Hits (all canonical) |
| --- | --- | --- | --- |
| in_wishlist | wishlist | Mentions wishlisting, shortlisting, bookmarking, or save-for-later. | 24 |
| in_cart_bag | cart | Mentions bag/cart/checkout as a shopping-intent action (not a product type). | 19 |
| in_hesitation | hesitation | Language of indecision or delayed purchase. Does not assume the reason. | 622 |
| in_comparison | comparison | Compares products, brands, or platforms. | 458 |
| in_abandonment | abandonment | Did not complete a purchase, cancelled, or switched away. | 438 |
| in_return_exchange | abandonment | Return or exchange after trying the product — post-purchase abandonment signal. | 2107 |
| in_fit_uncertainty | uncertainty | Fit or size language. Inclusion only — not a claim that sizing is the conversion problem. | 13702 |
| in_quality_uncertainty | uncertainty | Quality, fabric, or image-vs-reality language. Inclusion only. | 8774 |
| in_styling_occasion | uncertainty | Styling or occasion uncertainty after liking a product. | 724 |
| in_social_proof | uncertainty | Seeking or citing other shoppers' reviews before or after deciding. | 640 |

## Exclusion (applied after inclusion)

A candidate is dropped if any exclusion fires. Catalog copy is excluded even if the merchant text contains the word “fit”.

| Rule id | Family | What it drops | Hits (all canonical) |
| --- | --- | --- | --- |
| ex_catalog_copy | not_user_feedback | Drop `myntra_catalog` rows: merchant size/fit copy, not user feedback. | 961 |
| ex_too_short | weak_signal | Drop texts shorter than 20 characters after whitespace collapse. | 341 |
| ex_app_ops_only | off_journey | Pure app-operations complaints (login, crash, OTP) with no inclusion match. | 5 |

Minimum text length: **20** characters after whitespace collapse.

## Journey stages

Stages are tagged independently; the primary stage is the furthest match in this order:

Abandonment → Purchase → Evaluation → Wishlist → Consideration → Discovery → unlabeled

This is a **heuristic**. A clothing review that says “I bought it, it runs small, I returned it” is tagged abandonment (primary) plus purchase and evaluation flags.

| Primary stage | All canonical | Relevant only |
| --- | --- | --- |
| discovery | 88 | 34 |
| consideration | 181 | 68 |
| wishlist | 4 | 4 |
| evaluation | 8472 | 8207 |
| purchase | 8805 | 6467 |
| abandonment | 1373 | 1373 |
| unlabeled | 5652 | 1342 |

Journey rule patterns:

| Rule id | Stage | Description |
| --- | --- | --- |
| st_discovery | discovery | Discovery / finding the product or app. |
| st_consideration | consideration | Considering or browsing without a commit. |
| st_wishlist | wishlist | Explicit wishlist / save-for-later. |
| st_evaluation | evaluation | Evaluating attributes, proof, or logistics. |
| st_purchase | purchase | Purchase or receipt happened. |
| st_abandonment | abandonment | Did not keep or did not complete the buy. |

## External research flags

Not a journey stage. A record may list several destinations.

| Destination | Hits (all canonical) |
| --- | --- |
| Google search | 3 |
| Reddit | 1 |
| YouTube | 0 |
| Instagram | 21 |
| Friends or family | 892 |
| Influencer / blogger | 2 |
| Other shopping apps or brands | 107 |

## Fashion category

Tagged only when the product field or the text supports it.

- `product_field` — `product_or_category` is not an app id and maps to a fashion bucket, or looks like a department/class pair (`Tops / Blouses`).
- `text_keyword` — no usable product field; a category keyword appears in the text.
- `unlabeled` — left blank on purpose.

| Fashion category (relevant corpus) | Records |
| --- | --- |
| Clothing | 13227 |
| Western wear | 4107 |
| unlabeled | 143 |
| Beauty | 12 |
| Footwear | 4 |
| Ethnic wear | 2 |

## Language (measured before filtering)

Non-English rows stay in canonical and in relevant if they match inclusion rules.

| Language | All | % of all | Relevant |
| --- | --- | --- | --- |
| en | 23808 | 96.88 | 17343 |
| latin-other | 715 | 2.91 | 146 |
| hinglish | 23 | 0.09 | 5 |
| unknown | 21 | 0.09 | 0 |
| hi | 6 | 0.02 | 1 |
| kn | 1 | 0.0 | 0 |
| or+latin | 1 | 0.0 | 0 |

## Source coverage

| Source | All | Relevant | Relevant % of source |
| --- | --- | --- | --- |
| google_play | 856 | 151 | 17.64 |
| app_store | 47 | 19 | 40.43 |
| reddit | 77 | 39 | 50.65 |
| product_reviews | 22634 | 17286 | 76.37 |
| myntra_catalog | 961 | 0 | 0.0 |

## What Phase 2 did not do

- No LLM extraction, intent taxonomy, or barrier ranking (Phase 3).
- Did not treat every review as wishlist-relevant.
- Did not drop non-English rows in order to “clean” the corpus.
- Did not assume price, size, reviews, or discounts are the conversion problem.
- Did not write into `data/raw/`.

## Re-run

```bash
python -m src.process
```
