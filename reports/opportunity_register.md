# Opportunity register — Phase 5

Generated: 2026-08-20T14:11:33+00:00  
Formula: `score_v1`  
Denominator for frequency: **relevant** (n = **17495**), not the full scrape.

North star: share of users who purchase at least one wishlisted item within 30 days.  
Monetary incentives (discounts, coupons, cashback, markdowns) are **not** the primary recommendation.

## Formula

Each dimension is 0-1. Weights are equal. Total is the weighted sum (max 5). Scores are **not** min-max rescaled to the current top theme.

| Dimension | Weight | Definition | Failure mode avoided |
| --- | --- | --- | --- |
| frequency | 1.0 | unique records / relevant, then divided by saturation 20% (capped at 1.0) | Counting the full scrape, including irrelevant reviews |
| severity | 1.0 | Mean journey-stage weight of evidence records, times extractor factor (barrier 1.0, need 0.9, behavior 0.75, intent 0.8) | Treating loud one-off complaints as severe for everyone |
| purchase_hesitation_link | 1.0 | Share of evidence on wishlist/evaluation/consideration plus wishlist/hesitation/comparison/did-not-buy inclusion rules. Return language is excluded here (it is post-purchase). App-UX labels (delivery, trust, support) that are mostly Play/App Store are halved. | Claiming the theme is on wishlist-to-buy when it is generic app UX or only post-purchase returns |
| segments_affected | 1.0 | Share of **emitted** Phase 4 segments with at least 3 overlapping unique records. Segments that did not earn existence are not invented. | Inventing personas to inflate breadth |
| evidence_confidence | 1.0 | 0.4 mean extraction confidence + 0.3 source diversity + 0.3 observed-record ratio. Single-source clusters x0.85. Clusters with n<30 or hypothesis status capped at 0.40. Source mix is counted on unique records (no double-count across grouped themes). | High score on a thin, single-source cluster |

The scrape **does not** contain purchase outcomes, so every purchase-hesitation score is a **hypothesis**, not causality.

Journey-stage severity weights: abandonment 1.00, wishlist 0.85, evaluation 0.70, consideration 0.50, purchase 0.40, unlabeled 0.30, discovery 0.25. This is a **proxy**, not a causal model.

## Ranked opportunities

| Rank | Opportunity | Total /5 | Freq | Sev | Hesitation | Segments | Evidence | n | % relevant | Sources | Status | Conversion link |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | opp:returns_exchange | 3.3151 | 0.5987 | 0.8006 | 0.1074 | 1.0 | 0.8084 | 2095 | 11.9748 | 4 | observed_evidence | hypothesis |
| 2 | opp:image_vs_reality | 2.9641 | 0.5782 | 0.5141 | 0.2672 | 1.0 | 0.6046 | 2023 | 11.5633 | 3 | observed_evidence | hypothesis |
| 3 | opp:price_watch | 2.8314 | 0.3267 | 0.4463 | 0.2778 | 1.0 | 0.7806 | 1143 | 6.5333 | 4 | observed_evidence | hypothesis |
| 4 | opp:comparison_loop | 2.8031 | 0.1495 | 0.491 | 0.6338 | 0.75 | 0.7788 | 523 | 2.9894 | 4 | observed_evidence | hypothesis |
| 5 | opp:fit_uncertainty | 2.7321 | 0.6125 | 0.5635 | 0.2382 | 0.875 | 0.4429 | 2143 | 12.2492 | 1 | observed_evidence | hypothesis |
| 6 | opp:intent:uncertain | 2.6126 | 0.2541 | 0.4737 | 0.5034 | 0.75 | 0.6314 | 889 | 5.0815 | 2 | observed_evidence | hypothesis |
| 7 | opp:styling_uncertainty | 2.5681 | 0.2555 | 0.4753 | 0.2489 | 0.875 | 0.7134 | 894 | 5.11 | 3 | observed_evidence | hypothesis |
| 8 | opp:barrier:availability | 2.4774 | 0.092 | 0.6026 | 0.2795 | 0.75 | 0.7533 | 322 | 1.8405 | 3 | observed_evidence | hypothesis |
| 9 | opp:barrier:delivery | 2.3956 | 0.0426 | 0.5963 | 0.2383 | 0.75 | 0.7684 | 149 | 0.8517 | 4 | observed_evidence | hypothesis |
| 10 | opp:external_research | 2.3578 | 0.1163 | 0.417 | 0.2543 | 0.75 | 0.8202 | 407 | 2.3264 | 4 | observed_evidence | hypothesis |
| 11 | opp:barrier:fabric | 2.2727 | 0.2338 | 0.5518 | 0.2249 | 0.875 | 0.3872 | 818 | 4.6756 | 1 | observed_evidence | hypothesis |
| 12 | opp:barrier:other:comfort | 2.1009 | 0.1137 | 0.5864 | 0.255 | 0.75 | 0.3958 | 398 | 2.2749 | 1 | observed_evidence | hypothesis |
| 13 | opp:intent:bookmark | 2.0702 | 0.0069 | 0.58 | 0.8333 | 0.25 | 0.4 | 24 | 0.1372 | 3 | observed_evidence | hypothesis |
| 14 | opp:quality_uncertainty | 2.0395 | 0.0734 | 0.5698 | 0.2588 | 0.625 | 0.5125 | 257 | 1.469 | 2 | observed_evidence | hypothesis |
| 15 | opp:intent:future_purchase | 1.9433 | 0.038 | 0.4722 | 0.2669 | 0.5 | 0.6662 | 133 | 0.7602 | 2 | observed_evidence | hypothesis |
| 16 | opp:occasion_uncertainty | 1.8966 | 0.1406 | 0.4652 | 0.1961 | 0.5 | 0.5947 | 492 | 2.8122 | 2 | observed_evidence | hypothesis |
| 17 | opp:barrier:other:shrinkage | 1.8309 | 0.0597 | 0.5641 | 0.2392 | 0.5 | 0.4679 | 209 | 1.1946 | 1 | observed_evidence | hypothesis |
| 18 | opp:barrier:trust | 1.5893 | 0.0043 | 0.6933 | 0.3667 | 0.125 | 0.4 | 15 | 0.0857 | 2 | observed_evidence | hypothesis |
| 19 | opp:barrier:other:support | 1.5455 | 0.0103 | 0.7639 | 0.1042 | 0.125 | 0.5421 | 36 | 0.2058 | 2 | observed_evidence | hypothesis |
| 20 | opp:barrier:other:color | 1.1892 | 0.0009 | 0.5 | 0.3333 | 0.0 | 0.355 | 3 | 0.0171 | 1 | hypothesis | hypothesis |

## Top opportunities (readable)

### 1. `opp:returns_exchange` (total 3.3151)

**Problem:** Return and exchange friction shows up after try-on, and may also shape hesitation before the first buy.

**User need:** Confidence that a wrong-size or wrong-look outcome is recoverable without pain.

- Barrier label: `returns`
- Themes: `theme:barrier:returns`
- Segments: `segment:bookmarkers|segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **2095** / 17495 relevant (11.9748%)
- Sources: `{"app_store": 5, "google_play": 55, "product_reviews": 2034, "reddit": 1}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 2. `opp:image_vs_reality` (total 2.9641)

**Problem:** Product images and on-body proof do not settle whether the item matches what the shopper expects.

**User need:** Trustworthy visual proof of drape, color, and on-body look.

- Barrier label: `proof`
- Themes: `theme:barrier:proof|theme:need:vs_images`
- Segments: `segment:bookmarkers|segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **2023** / 17495 relevant (11.5633%)
- Sources: `{"google_play": 5, "product_reviews": 2014, "reddit": 4}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 3. `opp:price_watch` (total 2.8314)

**Problem:** Some shoppers are waiting on price or value, which can look like a discount brief but may be missing value proof.

**User need:** Enough value and quality information to decide whether the current price is acceptable, without assuming a coupon is required.

- Barrier label: `value`
- Themes: `theme:barrier:value|theme:intent:price_watch`
- Segments: `segment:bookmarkers|segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **1143** / 17495 relevant (6.5333%)
- Sources: `{"app_store": 1, "google_play": 4, "product_reviews": 1127, "reddit": 11}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 4. `opp:comparison_loop` (total 2.8031)

**Problem:** Shoppers keep comparing options instead of deciding on the wishlisted item.

**User need:** A clear way to compare the few attributes that actually change the decision.

- Barrier label: `comparison`
- Themes: `theme:barrier:comparison|theme:behavior:comparison|theme:intent:comparison|theme:need:better_alternative`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **523** / 17495 relevant (2.9894%)
- Sources: `{"app_store": 1, "google_play": 11, "product_reviews": 499, "reddit": 12}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 5. `opp:fit_uncertainty` (total 2.7321)

**Problem:** Shoppers still cannot tell whether an item will fit before they commit.

**User need:** A reliable way to judge fit and size for their body before buying.

- Barrier label: `fit`
- Themes: `theme:barrier:fit|theme:need:will_it_fit`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **2143** / 17495 relevant (12.2492%)
- Sources: `{"product_reviews": 2143}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 6. `opp:intent:uncertain` (total 2.6126)

**Problem:** Shoppers like the item enough to save it but still cannot decide whether to buy.

**User need:** The missing fact or proof that would turn indecision into a yes or a no.

- Barrier label: `uncertain`
- Themes: `theme:intent:uncertain`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:social_validation`
- Unique records: **889** / 17495 relevant (5.0815%)
- Sources: `{"product_reviews": 887, "reddit": 2}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 7. `opp:styling_uncertainty` (total 2.5681)

**Problem:** People like the item but do not know how to wear or pair it.

**User need:** Outfit context: what to pair it with and how it sits in a wardrobe.

- Barrier label: `styling`
- Themes: `theme:barrier:styling|theme:need:what_to_pair`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **894** / 17495 relevant (5.11%)
- Sources: `{"google_play": 1, "product_reviews": 892, "reddit": 1}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 8. `opp:barrier:availability` (total 2.4774)

**Problem:** A recurring barrier labeled availability appears in relevant feedback.

**User need:** Resolution of the availability issue before purchase.

- Barrier label: `availability`
- Themes: `theme:barrier:availability`
- Segments: `segment:bookmarkers|segment:comparers|segment:fit_conscious|segment:high_intent|segment:occasion|segment:social_validation`
- Unique records: **322** / 17495 relevant (1.8405%)
- Sources: `{"google_play": 1, "product_reviews": 320, "reddit": 1}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 9. `opp:barrier:delivery` (total 2.3956)

**Problem:** A recurring barrier labeled delivery appears in relevant feedback.

**User need:** Resolution of the delivery issue before purchase.

- Barrier label: `delivery`
- Themes: `theme:barrier:delivery`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:social_validation`
- Unique records: **149** / 17495 relevant (0.8517%)
- Sources: `{"app_store": 2, "google_play": 33, "product_reviews": 112, "reddit": 2}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 10. `opp:external_research` (total 2.3578)

**Problem:** People leave the app to get proof from friends, other sites, or social before they will buy.

**User need:** The same proof they currently hunt for off-platform, in context on the product.

- Barrier label: `proof`
- Themes: `theme:behavior:external:friends_family|theme:behavior:external:google|theme:behavior:external:instagram|theme:behavior:external:other_apps|theme:behavior:external:reddit`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **407** / 17495 relevant (2.3264%)
- Sources: `{"app_store": 2, "google_play": 32, "product_reviews": 371, "reddit": 2}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 11. `opp:barrier:fabric` (total 2.2727)

**Problem:** A recurring barrier labeled fabric appears in relevant feedback.

**User need:** Resolution of the fabric issue before purchase.

- Barrier label: `fabric`
- Themes: `theme:barrier:fabric`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **818** / 17495 relevant (4.6756%)
- Sources: `{"product_reviews": 818}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 12. `opp:barrier:other:comfort` (total 2.1009)

**Problem:** A recurring barrier labeled comfort appears in relevant feedback.

**User need:** Resolution of the comfort issue before purchase.

- Barrier label: `other:comfort`
- Themes: `theme:barrier:other:comfort`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **398** / 17495 relevant (2.2749%)
- Sources: `{"product_reviews": 398}`
- Status: `observed_evidence` ; conversion link: `hypothesis`


## Do not

- Recommend coupons, cashback, or markdowns as the primary answer
- Jump to product features before using this ranking
- Treat mention frequency as proven 30-day conversion causality
- Assign high scores to hypothesis or n<3 clusters (evidence_confidence is capped)

Related themes (fit + will_it_fit, proof + vs_images, and similar) are **unioned** into one opportunity so Growth does not double-count the same records.
