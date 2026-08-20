# Solution concepts — Phase 7

Generated: 2026-08-20T15:20:07+00:00  
Catalog: `ideate_v1`  
Source ranking: top 10 Phase 5 opportunities.

These are **concepts and experiment designs**, not a shipped conversion product.  
Monetary incentives (discounts, coupons, cashback, markdowns) are **not** the primary solution.

Readiness:

- `ready_to_test` — observed evidence, n ≥ 30, purchase-hesitation_link ≥ 0.20, mechanism matches the need, non-monetary.
- `primary_research_first` — the concept is valid but hesitation is weak, n is small, or the scrape story may be post-purchase.
- `weak_fit` — dropped from experiment briefs.

Every percentage below uses the **relevant** corpus unless a row names another denominator. Conversion effects remain **hypotheses**.

## Concepts

| Rank | Opportunity | Concept | Readiness | n | % relevant | Conversion link |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | opp:returns_exchange | Recoverability preview before the first buy | primary_research_first | 2095 | 11.9748 | hypothesis |
| 2 | opp:image_vs_reality | On-body proof pack | ready_to_test | 2023 | 11.5633 | hypothesis |
| 3 | opp:price_watch | Worth-it proof at the current price | ready_to_test | 1143 | 6.5333 | hypothesis |
| 4 | opp:comparison_loop | Decision attributes, not more options | ready_to_test | 523 | 2.9894 | hypothesis |
| 5 | opp:fit_uncertainty | Body-matched size evidence | ready_to_test | 2143 | 12.2492 | hypothesis |
| 6 | opp:intent:uncertain | Close the open question on the saved item | ready_to_test | 889 | 5.0815 | hypothesis |
| 7 | opp:styling_uncertainty | Wear-it-with context on the wishlist | ready_to_test | 894 | 5.11 | hypothesis |
| 8 | opp:barrier:availability | Size-intent restock, not a substitute SKU | ready_to_test | 322 | 1.8405 | hypothesis |
| 9 | opp:barrier:delivery | Delivery date on the wishlisted SKU | primary_research_first | 149 | 0.8517 | hypothesis |
| 10 | opp:external_research | Bring off-platform proof onto the product | ready_to_test | 407 | 2.3264 | hypothesis |

## Concept briefs

### 1. `concept:returns_exchange:1` — Recoverability preview before the first buy

Opportunity: `opp:returns_exchange` · readiness `primary_research_first`

**Need this must close:** Confidence that a wrong-size or wrong-look outcome is recoverable without pain.

**Barrier:** `returns`

**Mechanism:** On the wishlisted PDP and wishlist row, show the actual return and exchange path for this SKU: how size/color swaps work, how long reverse pickup takes, and what the shopper keeps if the first try-on fails. This is policy clarity, not a listed-price change.

**Rejected lever:** Return window extensions bundled with a discount code

**Why not a discount:** The need is confidence that a wrong-size or wrong-look outcome is recoverable. A markdown does not answer whether sending it back will be painful.

**Risks:** Most return language in the scrape is post-purchase. Treating this as a proven pre-purchase conversion lever is a hypothesis until interviews split those stories.

- n = **2095** / 17495 relevant (11.9748%)
- Conversion link: `hypothesis`
- Validation: purchase_hesitation_link=0.1074 is below 0.20. Do primary research on whether this sits on wishlist → buy before a conversion experiment. Scrape has no purchase outcomes. Any conversion effect is a hypothesis until the experiment. Return stories are often post-purchase. Interview to split pre-purchase fear vs reverse-logistics complaints.
### 2. `concept:image_vs_reality:1` — On-body proof pack

Opportunity: `opp:image_vs_reality` · readiness `ready_to_test`

**Need this must close:** Trustworthy visual proof of drape, color, and on-body look.

**Barrier:** `proof`

**Mechanism:** Surface buyer photos, short fabric-drape video, and color-in-daylight stills as visual proof next to the studio images, including on the wishlist card so the shopper can resolve 'does this match the picture?' without leaving.

**Rejected lever:** Price drop to compensate for photo mismatch

**Why not a discount:** The need is trustworthy visual proof of drape, color, and on-body look. Paying people to ignore that gap leaves the uncertainty in place.

**Risks:** UGC can be unrepresentative. Label similar-body and similar-lighting shots.

- n = **2023** / 17495 relevant (11.5633%)
- Conversion link: `hypothesis`
- Validation: Scrape has no purchase outcomes. Any conversion effect is a hypothesis until the experiment.
### 3. `concept:price_watch:1` — Worth-it proof at the current price

Opportunity: `opp:price_watch` · readiness `ready_to_test`

**Need this must close:** Enough value and quality information to decide whether the current price is acceptable, without assuming a coupon is required.

**Barrier:** `value`

**Mechanism:** On wishlist and PDP, show construction, fabric weight, comparable quality cues, and what is included so the shopper can judge value at the listed price. Split waiters into 'would buy if quality/fit were clear' vs 'will only buy below a number'.

**Rejected lever:** Coupons, cashback, markdowns, or wait-for-sale prompts as the primary treatment

**Why not a discount:** Price-watch language can be a proxy for unresolved value. The open question is whether the item is worth the current price, not whether a markdown exists.

**Risks:** If interviews show a hard reservation price, do not relabel that as a quality gap.

- n = **1143** / 17495 relevant (6.5333%)
- Conversion link: `hypothesis`
- Validation: Scrape has no purchase outcomes. Any conversion effect is a hypothesis until the experiment.
### 4. `concept:comparison_loop:1` — Decision attributes, not more options

Opportunity: `opp:comparison_loop` · readiness `ready_to_test`

**Need this must close:** A clear way to compare the few attributes that actually change the decision.

**Barrier:** `comparison`

**Mechanism:** Let a shopper pin 2–3 wishlisted alternatives and run a comparison on the attributes that actually show up in evidence: fit notes, fabric, on-body proof, exchange ease. Hide extra catalog noise. Do not compete on strikethrough price.

**Rejected lever:** Sitewide sale to force a pick

**Why not a discount:** The need is a way to compare the few attributes that change the decision. A coupon does not name a winner on fit or look.

**Risks:** A comparison UI can increase browsing time if it adds SKUs instead of closing attributes.

- n = **523** / 17495 relevant (2.9894%)
- Conversion link: `hypothesis`
- Validation: Scrape has no purchase outcomes. Any conversion effect is a hypothesis until the experiment.
### 5. `concept:fit_uncertainty:1` — Body-matched size evidence

Opportunity: `opp:fit_uncertainty` · readiness `ready_to_test`

**Need this must close:** A reliable way to judge fit and size for their body before buying.

**Barrier:** `fit`

**Mechanism:** On the wishlisted item, show fit measurements against a body-similar review set, garment-flat measurements, and how the piece sat on someone with the shopper's size inputs, rather than a generic chart.

**Rejected lever:** Buy-two-sizes-and-return, subsidized by a coupon

**Why not a discount:** The need is a reliable way to judge fit before buying. Ordering extra sizes is a workaround that still leaves fit unknown at wishlist time.

**Risks:** Fit evidence in this scrape is almost all product_reviews (single source). Corroborate in interviews.

- n = **2143** / 17495 relevant (12.2492%)
- Conversion link: `hypothesis`
- Validation: Scrape has no purchase outcomes. Any conversion effect is a hypothesis until the experiment.
### 6. `concept:intent-uncertain:1` — Close the open question on the saved item

Opportunity: `opp:intent:uncertain` · readiness `ready_to_test`

**Need this must close:** The missing fact or proof that would turn indecision into a yes or a no.

**Barrier:** `uncertain`

**Mechanism:** For uncertain-intent wishlists, prompt the missing fact (fit, look, occasion, quality) and jump to that proof on the same item. The job is to turn indecision into a yes or a no.

**Rejected lever:** Limited-time coupon to manufacture urgency

**Why not a discount:** The need is the missing fact that would decide the buy. Urgency pricing does not answer the open question.

**Risks:** If the true job of the save is bookmarking, a closer will look like nagging.

- n = **889** / 17495 relevant (5.0815%)
- Conversion link: `hypothesis`
- Validation: Scrape has no purchase outcomes. Any conversion effect is a hypothesis until the experiment.
### 7. `concept:styling_uncertainty:1` — Wear-it-with context on the wishlist

Opportunity: `opp:styling_uncertainty` · readiness `ready_to_test`

**Need this must close:** Outfit context: what to pair it with and how it sits in a wardrobe.

**Barrier:** `styling`

**Mechanism:** Show 2–3 pairing examples and occasion tags on the wishlisted PDP so styling is visible in a wardrobe, not as an isolated studio shot.

**Rejected lever:** Bundle discount on suggested pairs

**Why not a discount:** The need is outfit context. A cheaper pair still leaves 'how do I wear this' unanswered if the pairing logic is missing.

**Risks:** Generic lookbooks that ignore the shopper's occasion will not close the gap.

- n = **894** / 17495 relevant (5.11%)
- Conversion link: `hypothesis`
- Validation: Scrape has no purchase outcomes. Any conversion effect is a hypothesis until the experiment.
### 8. `concept:barrier-availability:1` — Size-intent restock, not a substitute SKU

Opportunity: `opp:barrier:availability` · readiness `ready_to_test`

**Need this must close:** Resolution of the availability issue before purchase.

**Barrier:** `availability`

**Mechanism:** When the wishlisted size is gone, keep the exact size/color intent and notify on restock with the same proof pack so availability of the chosen item is recovered. Do not push a different product as the default recovery.

**Rejected lever:** Markdown on a nearby size or color to clear the save

**Why not a discount:** The barrier is availability of the chosen item, not willingness to pay.

**Risks:** Restock promises that miss the window destroy trust.

- n = **322** / 17495 relevant (1.8405%)
- Conversion link: `hypothesis`
- Validation: Scrape has no purchase outcomes. Any conversion effect is a hypothesis until the experiment.
### 9. `concept:barrier-delivery:1` — Delivery date on the wishlisted SKU

Opportunity: `opp:barrier:delivery` · readiness `primary_research_first`

**Need this must close:** Resolution of the delivery issue before purchase.

**Barrier:** `delivery`

**Mechanism:** Show a realistic delivery date for the saved size/pincode on the wishlist row so timing uncertainty is visible before checkout.

**Rejected lever:** Free delivery coupon

**Why not a discount:** This theme is mostly app-store ops language. If it is general UX, a coupon will not move 30-day wishlist conversion.

**Risks:** Scoring already treats delivery as possible general UX. Confirm it sits on wishlist → buy before a large test.

- n = **149** / 17495 relevant (0.8517%)
- Conversion link: `hypothesis`
- Validation: Scoring treats this label as possible general app UX. Confirm it sits on wishlist → buy before a conversion experiment. Scrape has no purchase outcomes. Any conversion effect is a hypothesis until the experiment.
### 10. `concept:external_research:1` — Bring off-platform proof onto the product

Opportunity: `opp:external_research` · readiness `ready_to_test`

**Need this must close:** The same proof they currently hunt for off-platform, in context on the product.

**Barrier:** `proof`

**Mechanism:** Put the proof questions people currently take to friends, Google, Reddit, or Instagram (real photos, fabric feel, 'is it worth it') into Q&A and UGC on the same PDP/wishlist item.

**Rejected lever:** Cashback if they return from another app

**Why not a discount:** The need is the proof they hunt for off-platform. Paying them to skip research leaves the unanswered question in place.

**Risks:** Some external research is social permission, which in-app UGC may not replace.

- n = **407** / 17495 relevant (2.3264%)
- Conversion link: `hypothesis`
- Validation: Scrape has no purchase outcomes. Any conversion effect is a hypothesis until the experiment.


## Do not

- Use discounts, coupons, cashback, or price-offs as the primary solution
- Treat Phase 5 rank as a license to skip validation (returns rank high but hesitation is weak)
- Ship a full product in this phase
