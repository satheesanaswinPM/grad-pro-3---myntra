"""Write reports/relevance_rules.md from the rule registry plus this-run counts."""

from __future__ import annotations

from collections import Counter
from typing import Any

from src.process.rules import (
    EXCLUSION_RULES,
    EXTERNAL_RULES,
    INCLUSION_RULES,
    JOURNEY_RULES,
    MIN_TEXT_CHARS,
)


def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join("" if c is None else str(c) for c in row) + " |" for row in rows]
    return "\n".join([line, sep, *body]) if rows else line + "\n" + sep + "\n| _(empty)_ |"


def render_report(stats: dict[str, Any]) -> str:
    n_all = stats["n_canonical"]
    n_rel = stats["n_relevant"]
    denom = n_all or 1

    inclusion_rows = [
        [r.id, r.family, r.description, stats["inclusion_hits"].get(r.id, 0)]
        for r in INCLUSION_RULES
    ]
    exclusion_rows = [
        [r.id, r.family, r.description, stats["exclusion_hits"].get(r.id, 0)]
        for r in EXCLUSION_RULES
    ]
    stage_rows = [
        [name, stats["stage_counts"].get(name, 0), stats["relevant_stage_counts"].get(name, 0)]
        for name in (
            "discovery",
            "consideration",
            "wishlist",
            "evaluation",
            "purchase",
            "abandonment",
            "unlabeled",
        )
    ]
    lang_all = stats["language_all"]
    lang_rel = stats["language_relevant"]
    lang_rows = [
        [lang, lang_all.get(lang, 0), round(100.0 * lang_all.get(lang, 0) / denom, 2), lang_rel.get(lang, 0)]
        for lang, _ in Counter(lang_all).most_common()
    ]
    source_rows = [
        [
            source,
            counts["all"],
            counts["relevant"],
            round(100.0 * counts["relevant"] / counts["all"], 2) if counts["all"] else 0,
        ]
        for source, counts in stats["by_source"].items()
    ]
    cat_rows = [
        [cat, n]
        for cat, n in Counter(stats["relevant_categories"]).most_common()
    ]
    ext_rows = [
        [label, stats["external_hits"].get(name, 0)]
        for name, _pat, label in EXTERNAL_RULES
    ]

    return f"""# Relevance and journey rules — Phase 2

Generated: {stats["generated_at"]}  
Input: `data/processed/canonical.parquet` (n = **{n_all}**)  
Relevant corpus: `data/processed/relevant.parquet` (n = **{n_rel}**, {round(100.0 * n_rel / denom, 2)}% of canonical)  
Journey tags: `data/processed/journey_tags.parquet` (one row per canonical record)

These rules define the **denominator** for later percentages. They do not decide why wishlists fail to convert. Fit, quality, price, and similar phrases are inclusion *signals* to investigate, not assumed root causes.

## Denominators

| Population | n | Definition |
| --- | --- | --- |
| all | {n_all} | Every CanonicalFeedback row from Phase 1 |
| relevant | {n_rel} | Canonical rows that match at least one inclusion rule and no exclusion rule |
| source slice | — | `source` on the canonical row |
| language slice | — | `language` from Phase 1; non-`en`, mixed-dialect, and emoji-only rows are excluded (see below) |

## Inclusion (OR)

A row is a candidate if **any** of these fire. Multiple rules may fire on one text.

{_md_table(["Rule id", "Family", "What it catches", "Hits (all canonical)"], inclusion_rows)}

## Exclusion (applied after inclusion)

A candidate is dropped if any exclusion fires. Catalog copy is excluded even if the merchant text contains the word “fit”.

{_md_table(["Rule id", "Family", "What it drops", "Hits (all canonical)"], exclusion_rows)}

Minimum text length: **{MIN_TEXT_CHARS}** characters after whitespace collapse.

## Journey stages

Stages are tagged independently; the primary stage is the furthest match in this order:

Abandonment → Purchase → Evaluation → Wishlist → Consideration → Discovery → unlabeled

This is a **heuristic**. A clothing review that says “I bought it, it runs small, I returned it” is tagged abandonment (primary) plus purchase and evaluation flags.

{_md_table(["Primary stage", "All canonical", "Relevant only"], stage_rows)}

Journey rule patterns:

{_md_table(["Rule id", "Stage", "Description"], [[r.id, r.family, r.description] for r in JOURNEY_RULES])}

## External research flags

Not a journey stage. A record may list several destinations.

{_md_table(["Destination", "Hits (all canonical)"], ext_rows)}

## Fashion category

Tagged only when the product field or the text supports it.

- `product_field` — `product_or_category` is not an app id and maps to a fashion bucket, or looks like a department/class pair (`Tops / Blouses`).
- `text_keyword` — no usable product field; a category keyword appears in the text.
- `unlabeled` — left blank on purpose.

{_md_table(["Fashion category (relevant corpus)", "Records"], cat_rows) if cat_rows else "_No relevant rows._"}

## Language (measured, then filtered)

Every row's language is tagged in Phase 1 regardless of this filter, so the "All" column below still
shows the full mix. Relevant is now restricted to rows tagged `en`: `ex_non_english`, `ex_mixed_dialect`
(Hinglish or a non-Latin script mixed with Latin), and `ex_emoji_only` (no letters or digits at all) are
applied as exclusion rules above, not silently — see the exclusion table for hit counts.

{_md_table(["Language", "All", "% of all", "Relevant"], lang_rows)}

## Source coverage

{_md_table(["Source", "All", "Relevant", "Relevant % of source"], source_rows)}

## What Phase 2 did not do

- No LLM extraction, intent taxonomy, or barrier ranking (Phase 3).
- Did not treat every review as wishlist-relevant.
- Did not drop non-English rows for any reason other than the three explicit, reported rules above (non-`en`, mixed-dialect, emoji-only) — this is a stated corpus-scope decision, not silent "cleaning".
- Did not assume price, size, reviews, or discounts are the conversion problem.
- Did not write into `data/raw/`.

## Re-run

```bash
python -m src.process
```
"""
