# Part 4 — Define the Problem

Myntra Growth · Wishlist-to-Purchase Conversion
Source evidence: `reports/opportunity_register.md` (Phase 5, AI discovery, n=17,495 relevant records), `reports/research_hypotheses.md` (Phase 5), and the Wishlist Behavior Survey (n=36 respondents, primary research).

---

## 1. Target user segment

**Active Comparers whose comparisons go cold** — users who add an item to their wishlist *while actively comparing it against alternatives*, but who never return to close that comparison before attention decays.

Evidence for the segment's existence and size:
- `segment:comparers` appears as a contributing segment in 9 of the top 10 AI-discovered opportunities (`reports/opportunity_register.md`), meaning comparison behavior is not a one-off theme — it recurs across barrier types.
- In the survey, "Comparing with other options" is the single most common reason for wishlisting instead of buying immediately: **61% overall, 59% among the 22 respondents who had not purchased anything from their wishlist in 30 days.**
- The same segment shows a second, compounding failure mode: **"I forgot about it" is the single most common reason items stay unpurchased among true non-converters (32%)** — up from 19% in the full sample. Comparison and forgetting are not two separate segments; they are two stages of the same failure for the same users.

## 2. Product outcome we intend to influence

**Not** the final purchase-completion step. The outcome we target sits upstream: the **30-day comparison-resolution rate** — the share of wishlisted items (added under an explicit comparison motive) that receive an active re-engagement and an explicit compare/decide action within roughly 14 days of being added, before default attention-decay sets in.

This is a leading, upstream proxy for the north-star metric. It sits at **Stage A (Re-engagement) → Stage C (Comparison Resolution)** of the funnel decomposed in Part 2, not Stage E (Purchase Completion), where volume-based review mining pointed first.

## 3. Root cause

The wishlist functions as a **passive bookmark list, not an active decision-support workspace.** When a user saves an item mid-comparison, the product:

1. Captures no structured reason for the save (why this item, vs. what alternatives) — so neither the user nor the product can act on the comparison later.
2. Has no mechanism to pull the user back into the unresolved comparison before attention naturally decays.
3. Offers no in-app way to actually resolve a comparison (side-by-side view, decision nudge) — forcing the user to reopen competitor apps or rely on memory.

The result: the comparison either resolves silently **off-platform** (a competitor wins without Myntra ever getting a chance to close the loop — the #1 stated reason for removing an item without buying, at 42%), or it **never resolves at all** (the user simply forgets — functionally identical to losing the sale, and the #1 reason among actual non-converters).

## 4. Existing user workarounds

- Keeping multiple shopping apps installed to compare in parallel — 25% of survey respondents check other shopping apps (Ajio, Amazon, Nykaa) before buying a wishlisted item.
- "Keep checking back on it" — manually reopening the wishlist repeatedly, relying on self-directed memory rather than any product-driven prompt.
- Asking friends or family for a second opinion to break a comparison deadlock (11%).
- Passive reliance on notifications that respondents describe as easy to miss or ignore.

These are all manual, memory-dependent substitutes for something the product isn't doing: keeping the comparison alive and actionable.

## 5. Why solving this creates meaningful user value

Users who let a comparison go cold don't just fail to convert — they lose something they genuinely wanted. They either re-search from scratch later, or the comparison resolves by default (whatever they encounter next) rather than by an actual decision. Helping a user close a comparison they already started is a service to their *original* intent, not an engineered urgency trick — which keeps the solution consistent with the no-monetary-incentive constraint by construction: the fix is decision support and attention, not price.

## 6. Why solving this makes business sense

- `opp:comparison_loop` carries the **highest purchase-hesitation-link score (0.6338) of all 20 scored opportunities** — the AI discovery engine's own formula, independent of raw volume, flags it as the theme most tightly coupled to the actual wishlist-to-buy decision.
- It is corroborated by **independent primary research**: dominant in two separate survey questions, and it holds (in fact strengthens) when the sample is restricted to true non-converters.
- It avoids over-investing the non-monetary constraint in `opp:returns_exchange` — ranked #1 by raw volume (11.97% of relevant records) but carrying the **lowest hesitation-link score of the top 10 (0.1074)** and **zero corroboration anywhere in the survey.** That theme is real user pain, but it is post-purchase noise picked up by App Store/Play Store review bias (reviewers are disproportionately people who already bought and are now complaining), not a wishlist-conversion driver.
- Because both failure modes (forgetting, losing to an unresolved comparison) sit upstream of checkout, fixing them raises the ceiling on every downstream stage at once, instead of a point-fix on one barrier further down the funnel.

---

## 7. How the thinking evolved

| Stage | What we knew | What it pointed to |
|---|---|---|
| **Business Metric** | % of users who purchase ≥1 wishlisted item within 30 days of adding it. Monetary incentives excluded. | A single, time-boxed conversion number — undiagnostic on its own. |
| **Product Outcomes** | Decomposed the metric into 5 sequential gates: Re-engagement → Uncertainty Resolution → Comparison Resolution → Decision Trigger → Purchase Completion. | A funnel to place evidence against, instead of guessing which barrier "feels" biggest. |
| **AI Discovery** | Raw opportunity ranking (frequency × severity × evidence) put `returns_exchange` at #1 by volume. But the same engine's `purchase_hesitation_link` sub-score ranked `comparison_loop` **highest** (0.6338) and `returns_exchange` **lowest** (0.1074) of the top 10 — volume and relevance disagreed. | A live contradiction the raw ranking alone would have missed: the "biggest" theme by mentions was not the theme structurally tied to the wishlist decision. |
| **Primary Research** | Survey (n=36) found comparison the #1 reason to wishlist (61%) *and* the #1 reason to abandon without buying (42%) — the only hypothesis dominant in two independent questions. Forgetting was the #1 blocker among actual non-converters (32%). Returns/exchange had **zero** mentions anywhere in the survey. | Confirmed the AI engine's hesitation-link signal and resolved the contradiction: `returns_exchange` is post-purchase review-mining bias; `comparison_loop` (plus its re-engagement precursor) is the real wishlist-stage bottleneck. |
| **Problem Definition** | Combined all three sources onto one root cause. | The wishlist is a passive bookmark, not a decision workspace — Active Comparers lose the sale not by deciding "no," but by never getting to decide at all. |

## Problem statement (one paragraph)

> Active Comparers — the largest and most consistently evidenced behavioral segment across both the AI discovery pipeline and the primary-research survey — add items to their Myntra wishlist while genuinely undecided between alternatives, intending to resolve that comparison later. But the wishlist gives them no way to capture what they were comparing, no prompt to return before attention decays, and no way to resolve the comparison inside the app. The comparison is therefore resolved passively: either a competitor wins off-platform (42% of abandoned items), or the user simply forgets the item exists (32% of true non-converters, the single largest blocker). This is not a price problem, a fit problem, or a returns problem — it is a decision-support and re-engagement problem, and it is solvable without any monetary incentive.
