# Part 2 — Business Metric Decomposition

Myntra Growth · Wishlist-to-Purchase Conversion
Source evidence: `reports/opportunity_register.md` (Phase 5, AI discovery, n=17,343 relevant records after
language filtering — see `reports/relevance_rules.md`).

---

## The business metric

> % of users who purchase at least one wishlisted item within 30 days of adding it.

**Constraint:** no monetary incentives — discounts, coupons, cashback, and price-offs are excluded as
the primary lever.

This single number is a 30-day lagging outcome. It says nothing about *where* in the journey a
wishlisted item is lost, so it cannot by itself point Growth at an intervention.

## The funnel

A wishlisted item can only convert if it clears five sequential gates. The north-star is the **joint
probability of clearing all five within 30 days**, not any single one:

```
WPCR = P(Re-engage) × P(Resolve uncertainty | engaged) × P(Win comparison | resolved)
       × P(Decide now | won) × P(Complete purchase | decided)
```

| Stage | Product outcome (what should move) | User behavior (what the user actually does) | If this gate fails |
|---|---|---|---|
| **A. Re-engagement** | Wishlist revisit rate; reminder/notification open rate; sessions-that-touch-wishlist within 30 days | Opens the wishlist tab again, or a push/email pulls them back | Item goes cold — user never thinks about it again |
| **B. Uncertainty resolution** | % of revisits where the user views proof (reviews, size guide, on-body photos) and reaches a stated confidence level | Re-reads reviews, checks size guide, hunts for on-body photos, checks quality/fabric info | User stays stuck at "maybe," never reaches a yes/no |
| **C. Comparison resolution** | % of resolved sessions where *this* item, not an alternative, gets acted on | Opens competing apps/tabs, compares price/reviews, asks friends | User picks (or defaults to) a competitor's item instead |
| **D. Decision trigger** | % of comparison-winners that convert to "buy now" vs. staying in "wait" | Waits for an occasion, waits for a price drop, keeps saving it for later | Item is "won" but purchase is indefinitely deferred |
| **E. Purchase completion** | Cart-to-checkout completion rate for wishlist-originated adds | Adds to cart, then completes or abandons at checkout | Confidence collapses at the last step (returns, stock, delivery timing) |

## Mapping the AI discovery engine's opportunities onto the funnel

The Phase 5 scoring formula in `reports/opportunity_register.md` includes a `purchase_hesitation_link`
sub-score — how tightly a theme sits on the actual wishlist-to-buy moment vs. generic app noise or
post-purchase language. Read stage-by-stage, that sub-score tells a different story than the raw
total-score ranking:

| Stage | Opportunity | Rank (total score) | **Hesitation-link** | % relevant (n) |
|---|---|---|---|---|
| A. Re-engagement | `opp:intent:uncertain` (unresolved intent / forgetting) | 6 | **0.5034** (2nd highest in top 10) | 5.13% (889) |
| B. Uncertainty resolution | `opp:image_vs_reality` | 2 | 0.2668 | 11.64% (2018) |
| B. Uncertainty resolution | `opp:fit_uncertainty` | 5 | 0.2380 | 12.29% (2132) |
| B. Uncertainty resolution | `opp:styling_uncertainty` | 7 | 0.2492 | 5.15% (893) |
| B/C. Cross-cutting | `opp:external_research` (leaves app for proof/comparison) | 10 | 0.2538 | 2.31% (400) |
| **C. Comparison resolution** | `opp:comparison_loop` | 4 | **0.6341 (highest in top 10)** | 3.01% (522) |
| D. Decision trigger | `opp:price_watch` | 3 | 0.2776 | 6.57% (1140) |
| E. Purchase completion | `opp:barrier:availability` | 8 | 0.2795 | 1.86% (322) |
| E. Purchase completion | `opp:barrier:delivery` | 9 | 0.2273 | 0.82% (143) |
| E. Purchase completion | `opp:returns_exchange` | **1** | **0.1075 (lowest in top 10)** | 12.02% (2084) |

The volume-ranked #1 opportunity (`returns_exchange`) and the funnel-relevance-ranked #1 opportunity
(`comparison_loop`) are near opposites. `returns_exchange` scores highest on raw frequency and severity
because App Store/Play Store reviews are disproportionately written by people who already bought and are
now complaining about a return — that's a source bias in review-mining, not evidence about why a
*wishlisted, unbought* item stays unbought. The scoring engine itself flags this (hesitation-link
0.1075, the lowest in the top 10). `comparison_loop`, by contrast, has the strongest structural link to
the actual wishlist decision of anything in the ranked list, despite far lower raw volume.

## Where the primary research lands

The Wishlist Behavior Survey (36 respondents) triangulates onto the same two stages the hesitation-link
sub-score points to — see `reports/problem_definition.md` for the full analysis:

- **Stage A (Re-engagement)** — "I forgot about it" is the single most common reason items stay
  unpurchased, growing to 32% among people who genuinely didn't convert in 30 days (vs. 19% overall).
- **Stage C (Comparison resolution)** — "Comparing with other options" is the #1 reason to wishlist
  instead of buy (61%, 59% of non-converters), and "Found a better alternative" is the #1 reason people
  remove an item without ever buying it (42%). It is the only hypothesis dominant in two independent
  survey questions.
- **`returns_exchange`** has **zero** coverage anywhere in the survey — no option, no free-text mention
  as a reason for non-purchase, corroborating the pipeline's own low hesitation-link score.

## Where the highest-potential opportunity lies

Three independent signals converge on the same place — the AI discovery engine's own hesitation-link
sub-score, and the primary-research survey:

**Stages A + C — Re-engagement and Comparison Resolution — are the highest-potential lever**, not Stage
E (Purchase Completion / returns), which is where the raw opportunity ranking would have pointed first.

A user wishlists *because* they're comparing; if nothing pulls them back to resolve that comparison, the
item goes cold ("I forgot"); and even when they do come back, the resolution is more often "found it
cheaper/better elsewhere" than any fit/quality/return concern. Both failure modes sit upstream of
checkout, and neither can be fixed by anything at Stage E. This is the basis for the Part 4 problem
definition and the Part 5 MVP, which targets Stage A → Stage C specifically.
