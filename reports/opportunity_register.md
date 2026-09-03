# Opportunity register — Phase 5

Generated: 2026-09-03T20:17:35+00:00  
Formula: `score_v1`  
Denominator for frequency: **relevant** (n = **17343**), not the full scrape.

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
| 1 | opp:returns_exchange | 3.3198 | 0.6008 | 0.8015 | 0.1075 | 1.0 | 0.81 | 2084 | 12.0164 | 4 | observed_evidence | hypothesis |
| 2 | opp:image_vs_reality | 2.9678 | 0.5818 | 0.514 | 0.2668 | 1.0 | 0.6052 | 2018 | 11.6358 | 3 | observed_evidence | hypothesis |
| 3 | opp:price_watch | 2.8338 | 0.3287 | 0.4465 | 0.2776 | 1.0 | 0.781 | 1140 | 6.5733 | 4 | observed_evidence | hypothesis |
| 4 | opp:comparison_loop | 2.8045 | 0.1505 | 0.4913 | 0.6341 | 0.75 | 0.7786 | 522 | 3.0099 | 4 | observed_evidence | hypothesis |
| 5 | opp:fit_uncertainty | 2.7351 | 0.6147 | 0.5637 | 0.238 | 0.875 | 0.4437 | 2132 | 12.2931 | 1 | observed_evidence | hypothesis |
| 6 | opp:intent:uncertain | 2.6148 | 0.2563 | 0.4737 | 0.5034 | 0.75 | 0.6314 | 889 | 5.126 | 2 | observed_evidence | hypothesis |
| 7 | opp:styling_uncertainty | 2.5704 | 0.2575 | 0.4754 | 0.2492 | 0.875 | 0.7133 | 893 | 5.1491 | 3 | observed_evidence | hypothesis |
| 8 | opp:barrier:availability | 2.4782 | 0.0928 | 0.6026 | 0.2795 | 0.75 | 0.7533 | 322 | 1.8567 | 3 | observed_evidence | hypothesis |
| 9 | opp:barrier:delivery | 2.3753 | 0.0412 | 0.5857 | 0.2273 | 0.75 | 0.7711 | 143 | 0.8245 | 4 | observed_evidence | hypothesis |
| 10 | opp:external_research | 2.3603 | 0.1153 | 0.4161 | 0.2538 | 0.75 | 0.8251 | 400 | 2.3064 | 4 | observed_evidence | hypothesis |
| 11 | opp:barrier:fabric | 2.2762 | 0.235 | 0.5527 | 0.2258 | 0.875 | 0.3877 | 815 | 4.6993 | 1 | observed_evidence | hypothesis |
| 12 | opp:barrier:other:comfort | 2.1049 | 0.1142 | 0.5879 | 0.2563 | 0.75 | 0.3965 | 396 | 2.2833 | 1 | observed_evidence | hypothesis |
| 13 | opp:intent:bookmark | 2.0702 | 0.0069 | 0.58 | 0.8333 | 0.25 | 0.4 | 24 | 0.1384 | 3 | observed_evidence | hypothesis |
| 14 | opp:quality_uncertainty | 2.0408 | 0.0732 | 0.5705 | 0.2579 | 0.625 | 0.5142 | 254 | 1.4646 | 2 | observed_evidence | hypothesis |
| 15 | opp:intent:future_purchase | 1.9436 | 0.0383 | 0.4722 | 0.2669 | 0.5 | 0.6662 | 133 | 0.7669 | 2 | observed_evidence | hypothesis |
| 16 | opp:occasion_uncertainty | 1.9 | 0.1401 | 0.4676 | 0.1986 | 0.5 | 0.5937 | 486 | 2.8023 | 2 | observed_evidence | hypothesis |
| 17 | opp:barrier:other:shrinkage | 1.8315 | 0.0603 | 0.5641 | 0.2392 | 0.5 | 0.4679 | 209 | 1.2051 | 1 | observed_evidence | hypothesis |
| 18 | opp:barrier:other:support | 1.6575 | 0.0098 | 0.75 | 0.2206 | 0.125 | 0.5521 | 34 | 0.196 | 2 | observed_evidence | hypothesis |
| 19 | opp:barrier:trust | 1.5893 | 0.0043 | 0.6933 | 0.3667 | 0.125 | 0.4 | 15 | 0.0865 | 2 | observed_evidence | hypothesis |
| 20 | opp:barrier:other:color | 1.1892 | 0.0009 | 0.5 | 0.3333 | 0.0 | 0.355 | 3 | 0.0173 | 1 | hypothesis | hypothesis |

## Top opportunities (readable)

### 1. `opp:returns_exchange` (total 3.3198)

**Problem:** Return and exchange friction shows up after try-on, and may also shape hesitation before the first buy.

**User need:** Confidence that a wrong-size or wrong-look outcome is recoverable without pain.

- Barrier label: `returns`
- Themes: `theme:barrier:returns`
- Segments: `segment:bookmarkers|segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **2084** / 17343 relevant (12.0164%)
- Sources: `{"app_store": 4, "google_play": 46, "product_reviews": 2033, "reddit": 1}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 2. `opp:image_vs_reality` (total 2.9678)

**Problem:** Product images and on-body proof do not settle whether the item matches what the shopper expects.

**User need:** Trustworthy visual proof of drape, color, and on-body look.

- Barrier label: `proof`
- Themes: `theme:barrier:proof|theme:need:vs_images`
- Segments: `segment:bookmarkers|segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **2018** / 17343 relevant (11.6358%)
- Sources: `{"google_play": 4, "product_reviews": 2010, "reddit": 4}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 3. `opp:price_watch` (total 2.8338)

**Problem:** Some shoppers are waiting on price or value, which can look like a discount brief but may be missing value proof.

**User need:** Enough value and quality information to decide whether the current price is acceptable, without assuming a coupon is required.

- Barrier label: `value`
- Themes: `theme:barrier:value|theme:intent:price_watch`
- Segments: `segment:bookmarkers|segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **1140** / 17343 relevant (6.5733%)
- Sources: `{"app_store": 1, "google_play": 3, "product_reviews": 1126, "reddit": 10}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 4. `opp:comparison_loop` (total 2.8045)

**Problem:** Shoppers keep comparing options instead of deciding on the wishlisted item.

**User need:** A clear way to compare the few attributes that actually change the decision.

- Barrier label: `comparison`
- Themes: `theme:barrier:comparison|theme:behavior:comparison|theme:intent:comparison|theme:need:better_alternative`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **522** / 17343 relevant (3.0099%)
- Sources: `{"app_store": 1, "google_play": 11, "product_reviews": 499, "reddit": 11}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 5. `opp:fit_uncertainty` (total 2.7351)

**Problem:** Shoppers still cannot tell whether an item will fit before they commit.

**User need:** A reliable way to judge fit and size for their body before buying.

- Barrier label: `fit`
- Themes: `theme:barrier:fit|theme:need:will_it_fit`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **2132** / 17343 relevant (12.2931%)
- Sources: `{"product_reviews": 2132}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 6. `opp:intent:uncertain` (total 2.6148)

**Problem:** Shoppers like the item enough to save it but still cannot decide whether to buy.

**User need:** The missing fact or proof that would turn indecision into a yes or a no.

- Barrier label: `uncertain`
- Themes: `theme:intent:uncertain`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:social_validation`
- Unique records: **889** / 17343 relevant (5.126%)
- Sources: `{"product_reviews": 887, "reddit": 2}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 7. `opp:styling_uncertainty` (total 2.5704)

**Problem:** People like the item but do not know how to wear or pair it.

**User need:** Outfit context: what to pair it with and how it sits in a wardrobe.

- Barrier label: `styling`
- Themes: `theme:barrier:styling|theme:need:what_to_pair`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **893** / 17343 relevant (5.1491%)
- Sources: `{"google_play": 1, "product_reviews": 891, "reddit": 1}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 8. `opp:barrier:availability` (total 2.4782)

**Problem:** A recurring barrier labeled availability appears in relevant feedback.

**User need:** Resolution of the availability issue before purchase.

- Barrier label: `availability`
- Themes: `theme:barrier:availability`
- Segments: `segment:bookmarkers|segment:comparers|segment:fit_conscious|segment:high_intent|segment:occasion|segment:social_validation`
- Unique records: **322** / 17343 relevant (1.8567%)
- Sources: `{"google_play": 1, "product_reviews": 320, "reddit": 1}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 9. `opp:barrier:delivery` (total 2.3753)

**Problem:** A recurring barrier labeled delivery appears in relevant feedback.

**User need:** Resolution of the delivery issue before purchase.

- Barrier label: `delivery`
- Themes: `theme:barrier:delivery`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:social_validation`
- Unique records: **143** / 17343 relevant (0.8245%)
- Sources: `{"app_store": 2, "google_play": 27, "product_reviews": 112, "reddit": 2}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 10. `opp:external_research` (total 2.3603)

**Problem:** People leave the app to get proof from friends, other sites, or social before they will buy.

**User need:** The same proof they currently hunt for off-platform, in context on the product.

- Barrier label: `proof`
- Themes: `theme:behavior:external:friends_family|theme:behavior:external:google|theme:behavior:external:instagram|theme:behavior:external:other_apps|theme:behavior:external:reddit`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **400** / 17343 relevant (2.3064%)
- Sources: `{"app_store": 2, "google_play": 26, "product_reviews": 371, "reddit": 1}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 11. `opp:barrier:fabric` (total 2.2762)

**Problem:** A recurring barrier labeled fabric appears in relevant feedback.

**User need:** Resolution of the fabric issue before purchase.

- Barrier label: `fabric`
- Themes: `theme:barrier:fabric`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:inspiration|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **815** / 17343 relevant (4.6993%)
- Sources: `{"product_reviews": 815}`
- Status: `observed_evidence` ; conversion link: `hypothesis`
### 12. `opp:barrier:other:comfort` (total 2.1049)

**Problem:** A recurring barrier labeled comfort appears in relevant feedback.

**User need:** Resolution of the comfort issue before purchase.

- Barrier label: `other:comfort`
- Themes: `theme:barrier:other:comfort`
- Segments: `segment:comparers|segment:fit_conscious|segment:high_intent|segment:occasion|segment:quality|segment:social_validation`
- Unique records: **396** / 17343 relevant (2.2833%)
- Sources: `{"product_reviews": 396}`
- Status: `observed_evidence` ; conversion link: `hypothesis`


## Do not

- Recommend coupons, cashback, or markdowns as the primary answer
- Jump to product features before using this ranking
- Treat mention frequency as proven 30-day conversion causality
- Assign high scores to hypothesis or n<3 clusters (evidence_confidence is capped)

Related themes (fit + will_it_fit, proof + vs_images, and similar) are **unioned** into one opportunity so Growth does not double-count the same records.
