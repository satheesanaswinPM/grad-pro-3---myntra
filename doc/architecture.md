# Wishlist-to-Purchase AI Discovery Engine — Architecture

**Project:** Myntra Growth · Part 1 is discovery only  
**North star:** Increase the share of users who purchase at least one wishlisted item within 30 days of adding it.  
**Primary constraint:** Monetary incentives (discounts, coupons, cashback, price-offs) are not the primary solution.

This document is the phasewise system architecture for Part 1. The conversion product is out of scope until problems are evidenced and ranked.

---

## 1. What this system is

Users add fashion products to a wishlist, signalling interest, then often do not buy within 30 days. The underlying reason is **unknown**. This engine discovers that reason from scraped public feedback — App Store, Google Play, Reddit, YouTube, social, product reviews, Q&A, and related discussions — and ranks which problems the Growth Team should investigate first.

The engine investigates the full journey:

**Discovery → Product consideration → Wishlist → Evaluation → Purchase / Abandonment**

It must answer:

> Who adds products to their wishlist, why they do it, what prevents purchase, what information is missing, which barriers matter most, and which opportunity the Myntra Growth Team should investigate first to improve 30-day wishlist-to-purchase conversion?

### Hard rules

- Do not assume price, sizing, reviews, or discounts are the problem.
- Do not overwrite raw scraped data.
- Do not present model guesses as facts.
- Do not build the final product solution in Part 1.
- Every insight must keep this chain:

**User evidence → behavior → problem → need → purchase barrier → potential business impact**

Keyword counting, sentiment analysis, and generic topic extraction are not sufficient.

---

## 2. Layered architecture

Raw data is its own layer so it can never be overwritten. Processing, AI analysis, scoring, and the dashboard stay strictly separated.

```
┌─────────────────────────────────────────────────────────────────┐
│ L4  Present     Product Discovery / Research Console            │
│                 12 decision modules. Insight → evidence.        │
├─────────────────────────────────────────────────────────────────┤
│ L3  Score       Opportunity ranking + research hypotheses       │
│                 Frequency, severity, hesitation link,           │
│                 segments affected, evidence confidence          │
├─────────────────────────────────────────────────────────────────┤
│ L2  Synthesize  Themes, segments, category cuts, metrics        │
│                 Segments only if patterns recur                 │
├─────────────────────────────────────────────────────────────────┤
│ L1  Extract     Intent | Barriers | Needs | Behavior            │
│                 Cache, failure logs, observed vs hypothesis     │
├─────────────────────────────────────────────────────────────────┤
│ L0  Process     Clean → dedupe → language → relevance → tags    │
│                 Source adapters are the only ingest path        │
├─────────────────────────────────────────────────────────────────┤
│ L-1 Data        Raw (immutable) · processed · LLM cache · logs  │
│                 Refresh = re-run, not rewrite                   │
└─────────────────────────────────────────────────────────────────┘
```

| Layer | Job |
|---|---|
| **L4 Present** | Product-discovery console. Not a generic BI dashboard. |
| **L3 Score** | Transparent opportunity ranking and testable hypotheses. |
| **L2 Synthesize** | Themes, segments, category cuts, quantification with explicit denominators. |
| **L1 Extract** | Structured AI extraction with evidence links. Modular so new extractors can be added. |
| **L0 Process** | Reproducible jobs. New scrapes enter only through adapters. |
| **L-1 Data** | Preserve the scrape. Processed datasets live beside it, never on top of it. |

---

## 3. Analysis pipeline

After relevance filtering, four extractors run in parallel, then join for synthesis.

```
Raw scrape
    ↓
Quality report
    ↓
Clean / dedupe / language
    ↓
Relevance + journey tags
    ↓
    ┌──────────┬──────────┬──────────┬──────────┐
    │  Intent  │ Barriers │  Needs   │ Behavior │
    └──────────┴──────────┴──────────┴──────────┘
                        ↓
              Segments + themes
                        ↓
              Opportunity score
                        ↓
              Research console
```

| Stage | Must produce | Is not enough |
|---|---|---|
| Intent | Why the item was wishlisted, from evidence | Positive/negative polarity |
| Barriers | What blocks purchase after liking the product | Star-rating averages |
| Needs | Unanswered questions post-wishlist | Keyword clouds |
| Behavior | Comparison, external research, journey stage | Generic topic labels |
| Impact | Which barrier is worth Growth investigation | Unranked theme dump |

**Refresh path:** New scrapes enter only through adapters. Reprocess is ingest → process → extract (cache-aware) → synthesize → score → console reload. Identical feedback is never resent to the model.

---

## 4. Phasewise plan

Part 1 has seven build phases. Phase 7 (solution ideation) stays **gated** until ranked opportunities and the research console exist.

Relative effort is planning weight, not calendar time. Phase 3 (extraction) is the heaviest lift.

| Phase | Name | Part | Relative effort | Exit gate |
|---|---|---|---|---|
| 0 | Inspect & Qualify | Discovery | 8 | Quality report exists. Raw files untouched. Schema and denominators documented. |
| 1 | Data Foundation | Discovery | 12 | Every record has `id`, `source`, `raw_ref`, `text`, ingest timestamp. Pipeline is re-runnable. |
| 2 | Relevance & Journey | Discovery | 12 | Relevance definition is written down. All later % cite all / relevant / source / segment. |
| 3 | AI Extraction Engine | Discovery | 28 | No extraction without `record_id` + evidence snippet. Cache on. Hypothesis vs observed explicit. |
| 4 | Synthesize & Quantify | Discovery | 16 | Each segment cites recurring evidence. Every metric names its denominator. |
| 5 | Opportunity Scoring | Discovery | 10 | Ranked list with visible scores and evidence packs. Causal claims labeled when unproven. |
| 6 | Research Console | Discovery | 14 | A PM can answer the final research question from the console. |
| 7 | Solution Ideation | Ideation | — | Concepts validated against ranked barriers; 30-day experiments designed; no monetary primary lever. |

---

### Phase 0 — Inspect & Qualify

**Goal:** Know what the scraped corpus actually contains before any analysis or modelling.

**Why:** The problem is unknown. Analysis on uninspected data will invent a problem the reviews never stated.

**Inputs**

- All files and folders in the scraped dataset
- `problemstatement.md` as the research brief

**Work**

1. Inventory formats, schemas, and available fields (text, source, date, rating, category, user, URL, metadata).
2. Count records; measure duplicates, missingness, language mix, source mix.
3. Classify corpus: Myntra-specific vs broader fashion-shopping vs mixed.
4. Write a data-quality report. Do not overwrite raw data.

**Artifacts**

- `reports/data_quality.md`
- `reports/schema_catalog.json`
- `reports/source_coverage.csv`

**Do not**

- Start LLM extraction
- Assume price, size, or discounts are the problem
- Overwrite or “clean in place” the original scrape

---

### Phase 1 — Data Foundation

**Goal:** Stand up a reproducible, modular ingestion layer that never mutates raw data.

**Why:** New sources must be addable later. Every later insight needs a stable record ID and provenance.

**Inputs**

- Raw scrape (read-only)
- Schema catalog from Phase 0

**Work**

1. Source adapters: App Store, Play, Reddit, YouTube, social, product reviews, Q&A, other.
2. Normalize to `CanonicalFeedback` with stable IDs and raw-file pointers.
3. Deduplicate, detect language, keep processed output in a separate tree.
4. Secrets in env vars. Run logs for refresh/reprocess.

Re-run from the project root (reads `data/raw/` only):

```bash
python -m src.ingest.build
```

**Artifacts**

- `data/raw/` (immutable)
- `data/processed/canonical.parquet`
- `data/logs/ingest.log`
- `src/ingest/adapters/`

**Do not**

- Write into `data/raw/`
- Hard-code API keys
- Build one-off notebooks as the only pipeline

---

### Phase 2 — Relevance & Journey

**Goal:** Define the relevant corpus and tag where each item sits on the shopping journey.

**Why:** Percentages are meaningless without an explicit denominator. Most reviews will not be about wishlisting.

**Inputs**

- `CanonicalFeedback`

**Work**

1. Document inclusion/exclusion rules for wishlist, hesitation, comparison, abandonment, fit/quality uncertainty.
2. Tag journey stage: Discovery → Consideration → Wishlist → Evaluation → Purchase / Abandonment.
3. Flag external-research mentions (Google, Reddit, YouTube, Instagram, friends, other apps).
4. Tag fashion category only where the data supports it.

Re-run from the project root:

```bash
python -m src.process
```

**Artifacts**

- `data/processed/relevant.parquet`
- `reports/relevance_rules.md`
- `data/processed/journey_tags.parquet`

**Do not**

- Treat every review as wishlist-relevant
- Skip documenting filter rules
- Drop non-English data before measuring language distribution

---

### Phase 3 — AI Extraction Engine

**Goal:** Extract intent, barriers, unanswered questions, and comparison/external-research behavior with evidence links.

**Why:** This is the core of the engine. Keyword counts and sentiment are not insights.

**Inputs**

- Relevant corpus
- Emergent taxonomies (not forced)

**Work**

1. **Intent** — strong purchase, future, bookmark, compare, price-watch, occasion, inspiration, uncertain, plus whatever the data adds.
2. **Barriers** — investigate fit, quality, fabric, styling, occasion, proof, returns, delivery, availability, value, comparison, fatigue, urgency, trust. Do not assume any of them.
3. **Post-wishlist uncertainty** — questions still unanswered after “I like this.”
4. **Comparison attributes** and external-research destinations, plus why.
5. Cache by content hash + prompt version. Log failures. Never resend identical text.
6. Label every extraction as **observed evidence** vs **AI hypothesis**.

Re-run from the project root (reads `data/processed/relevant.parquet` only):

```bash
python -m src.analyze
```

If `OPENAI_API_KEY` is set, unique texts are batched to the LLM and cached in `data/cache/llm.sqlite`. Otherwise a span-grounded local extractor runs. Either backend drops a row if it cannot quote a verbatim `evidence_span`.

**Artifacts**

- `data/extractions/intents.parquet`
- `data/extractions/barriers.parquet`
- `data/extractions/needs.parquet`
- `data/extractions/behaviors.parquet`
- `data/cache/llm.sqlite`
- `data/logs/ai_failures.log`

**Do not**

- Sentiment-only or topic-only summaries
- Force feedback into the suggested lists
- Present model guesses as facts
- Call the LLM on duplicate texts

---

### Phase 4 — Synthesize & Quantify

**Goal:** Turn extractions into data-supported segments, themes, and numbered patterns.

**Why:** Growth needs size and concentration, not a wall of quotes. Segments must earn their existence.

**Inputs**

- Linked extractions
- Category and source fields

**Work**

1. Cluster themes; keep evidence IDs on every cluster.
2. Form behavioral segments only from recurring patterns (high-intent, bookmarkers, comparers, fit-conscious, occasion, social-validation, quality, inspiration — **if the data shows them**).
3. Compare barriers across clothing, footwear, accessories, beauty, ethnic, western, sportswear when counts allow.
4. Quantify: mentions, % of relevant, unique records, source/category/segment mix, co-occurrence, time trend.

Re-run from the project root:

```bash
python -m src.synthesize
```

**Artifacts**

- `data/synthesis/themes.parquet`
- `data/synthesis/segments.parquet`
- `data/synthesis/category_diffs.parquet`
- `data/synthesis/metrics.parquet`

**Do not**

- Invent personas
- Treat mention frequency as proven purchase causality
- Hide small-n category cuts as if they were robust

---

### Phase 5 — Opportunity Scoring

**Goal:** Rank which user problems the Growth Team should investigate first — transparently.

**Why:** The north-star is 30-day wishlist-to-purchase conversion, without discounts as the lever.

**Inputs**

- Quantified themes
- Evidence packs
- Segment coverage

**Work**

1. Score on frequency, severity, link to purchase hesitation, segments affected, evidence confidence.
2. Publish the formula. Do not inflate scores.
3. If purchase behavior is not in the scrape, label the conversion link as hypothesis, not causality.
4. Turn top opportunities into testable primary-research hypotheses.

Re-run from the project root:

```bash
python -m src.score
```

**Artifacts**

- `data/scoring/opportunities.parquet`
- `reports/opportunity_register.md`
- `reports/research_hypotheses.md`

**Do not**

- Recommend coupons, cashback, or markdowns as the primary answer
- Jump to product features before the ranking exists
- Assign high scores without evidence

---

### Phase 6 — Research Console

**Goal:** Ship a product-discovery console a PM can use to answer the final research question.

**Why:** Insights without click-through evidence will not survive a Growth review.

**Inputs**

- All processed, extraction, synthesis, and scoring tables

**Work**

1. Twelve modules listed in [Section 7](#7-research-console-modules).
2. One click from insight → supporting feedback.
3. Decision-oriented layout. No vanity charts.

Re-run from the project root:

```bash
python -m src.dashboard
```

Streamlit Community Cloud uses `streamlit_app.py` at the repo root (Python 3.12). The console snapshot in `data/processed`, `data/extractions`, `data/synthesis`, and `data/scoring` is what the hosted app reads. Do not point Cloud at `python -m src.dashboard` (that path writes evidence packs).

**Artifacts**

- `src/dashboard/` (research console)
- `exports/evidence_packs/`

**Do not**

- Build a generic analytics dashboard
- Hide evidence behind exports-only
- Design the conversion product in this phase

---

### Phase 7 — Solution Ideation

**Goal:** Ideate, validate, and experiment on the strongest opportunity areas. Do not ship the conversion product here.

**Why:** The brief forbids building the product solution until the underlying problems are evidenced and ranked. Phases 5 and 6 are that gate.

**Inputs**

- Ranked opportunities
- Evidence packs / console click-through
- Research hypotheses

**Work**

1. Solution concepts that are not monetary incentives.
2. Validation against the discovered barriers and missing information.
3. Experiment design aimed at 30-day wishlist-to-purchase conversion.

Re-run from the project root (locked until Phase 5 scoring and Phase 6 console files exist):

```bash
python -m src.ideate
```

**Artifacts**

- `data/ideation/concepts.parquet`
- `data/ideation/validations.parquet`
- `data/ideation/experiments.parquet`
- `reports/solution_concepts.md`
- `reports/experiment_briefs.md`

**Do not**

- Use discounts, coupons, cashback, or price-offs as the primary solution
- Treat a high rank as causality (the scrape still has no purchase outcomes)
- Ship the final conversion product in this phase

---

## 5. Data contracts

Extra source-specific metadata stays in a metadata blob. These fields are the minimum so the console can show evidence and scoring stays auditable.

### CanonicalFeedback (L0)

| Field | Role |
|---|---|
| `record_id` | Stable ID |
| `source` | App Store / Play / Reddit / … |
| `source_url` | Original URL when available |
| `authored_at` | Feedback date if present |
| `language` | Detected language |
| `raw_ref` | Pointer into the immutable scrape |
| `text` | Review / comment body |
| `rating` | Star rating if present |
| `product_or_category` | Product or fashion category when known |
| `user_key` | Username / user ID if available |
| `ingest_at` | Ingest timestamp |
| `content_hash` | Hash used for dedupe and LLM cache |

### Extraction row (L1)

| Field | Role |
|---|---|
| `extraction_id` | Stable ID |
| `record_id` | Pointer into canonical / raw |
| `extractor` | `intent` \| `barrier` \| `need` \| `behavior` |
| `label` | Emergent label |
| `evidence_span` | Verbatim supporting span |
| `confidence` | Extraction confidence |
| `prompt_version` | Prompt / schema version for cache key |
| `status` | `observed_evidence` \| `hypothesis` |

### Insight object (console)

| Field | Role |
|---|---|
| `insight_id` | Stable ID for the generated insight |
| `problem_statement` | User problem in one sentence |
| `user_need` | What the user still needs in order to buy |
| `barrier` | Purchase barrier label (emergent) |
| `intent` | Wishlist intent label (emergent) |
| `segment` | Behavioral segment, if supported |
| `category` | Fashion category when known |
| `source` | App Store / Play / Reddit / … |
| `evidence_snippet` | Verbatim supporting text |
| `record_id` | Pointer into canonical / raw |
| `date` | Feedback date if present |
| `frequency` | Mention or record count |
| `pct_relevant` | % of the relevant corpus |
| `confidence` | Model + corroboration confidence |
| `ai_interpretation` | Separated from the quote |
| `status` | `observed_evidence` \| `hypothesis` |

---

## 6. Opportunity scoring

| Dimension | What it measures | Failure mode to avoid |
|---|---|---|
| **Frequency** | How often the barrier/need appears in relevant feedback | Counting the full scrape, including irrelevant reviews |
| **Severity** | How strongly it blocks or delays purchase in the text | Treating loud one-off complaints as severe for everyone |
| **Purchase-hesitation link** | Whether the theme sits on wishlist → buy, not general app UX | Claiming causality when the scrape has no purchase outcomes |
| **Segments affected** | Breadth across evidenced behavioral groups | Inventing segments to inflate this score |
| **Evidence confidence** | Corroboration, source mix, extraction confidence | High score on a thin, single-source cluster |

Publish the formula. Do not inflate scores. If the scrape has no purchase outcomes, the conversion link is a **hypothesis**, not causality.

---

## 7. Research console modules

The dashboard should feel like a product-discovery / research intelligence tool.

| # | Module | Job |
|---|---|---|
| 1 | Executive summary | Dataset size, sources, key findings, top opportunities |
| 2 | Wishlist intent | Why users wishlist; mix by source and category |
| 3 | Purchase barriers | Ranked barriers with frequency, severity, evidence |
| 4 | User segments | Definitions, size, behaviors, dominant barriers, needs |
| 5 | Uncertainty map | Questions still open after wishlisting |
| 6 | Customer journey | Discovery → Consideration → Wishlist → Evaluation → Purchase / Abandonment |
| 7 | Comparison behavior | Attributes compared, alternatives, decision criteria |
| 8 | External research | Where users go off-platform and why |
| 9 | Category analysis | Barrier and behavior differences by fashion category |
| 10 | Opportunity matrix | Frequency × severity/impact × evidence confidence |
| 11 | Evidence explorer | Click an insight, read the actual feedback |
| 12 | Research hypotheses | Testable follow-ups for primary research |
| 13 | Solution concepts | Non-monetary concepts and 30-day experiment briefs (Phase 7) |

---

## 8. Repository layout

| Path | Layer | Responsibility |
|---|---|---|
| `data/raw/` | L-1 | Original scrape. Read-only. |
| `data/processed/` | L-1 | Canonical, relevant, tagged tables |
| `data/extractions/` | L1 | Intent / barrier / need / behavior outputs |
| `data/synthesis/` | L2 | Themes, segments, metrics |
| `data/scoring/` | L3 | Opportunity scores and hypotheses |
| `data/cache/` and `data/logs/` | L-1 | LLM cache + ingest/AI failure logs |
| `src/qualify/` | Phase 0 | Inspect raw scrape; write quality reports only |
| `src/ingest/` | L0 | Per-source adapters |
| `src/process/` | L0 | Clean, dedupe, language, relevance |
| `src/analyze/` | L1 | Prompted extractors, schema validation |
| `src/synthesize/` | L2 | Themes, segments, quantification |
| `src/score/` | L3 | Scoring framework |
| `src/dashboard/` | L4 | Research console (12 discovery modules + Phase 7 concepts) |
| `src/ideate/` | Phase 7 | Solution ideation. Gated until 5 and 6 complete. |
| `reports/` | Cross-cutting | Quality report, opportunity register, experiment briefs |
| `exports/evidence_packs/` | L4 | Click-through evidence packs for the console |
| `data/ideation/` | Phase 7 | Concepts, validations, experiment briefs |
| `doc/architecture.md` | — | This document |

New phases keep this shape: `src/<package>/` with `__main__.py` + `run.py`, a `schema.py` contract, and outputs in the matching `data/` (or `reports/` / `exports/`) tree. Do not write into `data/raw/`.

---

## 9. Technical requirements

- Use the existing scraped data. Preserve the raw dataset.
- Create processed/analysis datasets separately.
- Make the pipeline reproducible and modular so new data sources can be added.
- Keep API keys and secrets in environment variables.
- Handle large datasets efficiently.
- Cache expensive AI operations. Hash text + prompt version; skip cache hits.
- Log AI processing failures.
- Allow the dataset to be refreshed/reprocessed later.

**Implementation note:** A practical split is a Python batch pipeline (Polars or DuckDB for large tables) plus a research console (Streamlit or a small FastAPI UI). The architecture does not depend on a specific LLM vendor.

---

## 10. Build sequence

1. Drop the scrape into `data/raw/` and run `python -m src.qualify` (Phase 0 quality report).
2. Build adapters and the canonical record: `python -m src.ingest.build` (Phase 1).
3. Define relevance and journey tags: `python -m src.process` (Phase 2).
4. Run extraction with cache and evidence links: `python -m src.analyze` (Phase 3).
5. Cluster, segment, and quantify: `python -m src.synthesize` (Phase 4).
6. Score opportunities and write hypotheses: `python -m src.score` (Phase 5).
7. Ship the research console: `python -m src.dashboard` (Phase 6).
8. Ideate and design 30-day experiments: `python -m src.ideate` (Phase 7). Do not ship the conversion product; do not use discounts as the primary lever.
