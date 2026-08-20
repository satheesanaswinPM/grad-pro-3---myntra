# Experiment briefs — Phase 7

Generated: 2026-08-20T15:20:07+00:00  
North star: share of users who purchase at least one wishlisted item within **30 days** of adding it.

This scrape has **no purchase outcomes**, so every conversion experiment is a **hypothesis** until it runs.  
Do **not** use discounts, coupons, cashback, or price-offs as the primary treatment or KPI.

## Roster

| Rank | Experiment | Opportunity | Readiness | Conversion link |
| --- | --- | --- | --- | --- |
| 1 | exp:returns_exchange:1 | opp:returns_exchange | primary_research_first | hypothesis |
| 2 | exp:image_vs_reality:1 | opp:image_vs_reality | ready_to_test | hypothesis |
| 3 | exp:price_watch:1 | opp:price_watch | ready_to_test | hypothesis |
| 4 | exp:comparison_loop:1 | opp:comparison_loop | ready_to_test | hypothesis |
| 5 | exp:fit_uncertainty:1 | opp:fit_uncertainty | ready_to_test | hypothesis |
| 6 | exp:intent-uncertain:1 | opp:intent:uncertain | ready_to_test | hypothesis |
| 7 | exp:styling_uncertainty:1 | opp:styling_uncertainty | ready_to_test | hypothesis |
| 8 | exp:barrier-availability:1 | opp:barrier:availability | ready_to_test | hypothesis |
| 9 | exp:barrier-delivery:1 | opp:barrier:delivery | primary_research_first | hypothesis |
| 10 | exp:external_research:1 | opp:external_research | ready_to_test | hypothesis |

## Briefs

### 1. `exp:returns_exchange:1`

30-day test: Recoverability preview before the first buy

**Hypothesis:** If we close 'Confidence that a wrong-size or wrong-look outcome is recoverable without pain.' with 'Recoverability preview before the first buy', users who wishlisted a treated item will be more likely to purchase at least one wishlisted item within 30 days than users on the current experience. This conversion link is unproven in the scrape.

**Audience:** Shoppers who wishlisted an item in the last 7 days where the open barrier is `returns` (opportunity `opp:returns_exchange`, n=2095 / 17495 relevant in the scrape — scrape n is not the test sample).

**Treatment:** On the wishlisted PDP and wishlist row, show the actual return and exchange path for this SKU: how size/color swaps work, how long reverse pickup takes, and what the shopper keeps if the first try-on fails. This is policy clarity, not a listed-price change.

**Control:** Current PDP + wishlist. No added proof module. No price change in either arm.

**Primary metric:** Share of users who purchase at least one wishlisted item within 30 days of adding it.

**Denominator:** Users who added a treatment-eligible item to wishlist in the assignment window, still intending to buy it (exclude accidental saves if a save-job tag exists).

**Guardrails:** Return rate on treated items; customer-support contacts; un-wishlist rate; time-to-decision (buy or remove). Do not treat AOV lift from markdowns as success.

**Success rule:** Statistically and practically higher 30-day wishlist-item purchase rate vs control, with return rate not worse beyond the pre-registered bound. Readiness `primary_research_first`: do not launch a powered A/B yet; run the Phase 5 research ask first, then a small prototype.

**Do not optimize:** Coupon redemption, discount depth, cashback take-up, markdown attach rate, or any price-off as the primary KPI.

Status: `hypothesis` · conversion link `hypothesis` · readiness `primary_research_first`

### 2. `exp:image_vs_reality:1`

30-day test: On-body proof pack

**Hypothesis:** If we close 'Trustworthy visual proof of drape, color, and on-body look.' with 'On-body proof pack', users who wishlisted a treated item will be more likely to purchase at least one wishlisted item within 30 days than users on the current experience. This conversion link is unproven in the scrape.

**Audience:** Shoppers who wishlisted an item in the last 7 days where the open barrier is `proof` (opportunity `opp:image_vs_reality`, n=2023 / 17495 relevant in the scrape — scrape n is not the test sample).

**Treatment:** Surface buyer photos, short fabric-drape video, and color-in-daylight stills as visual proof next to the studio images, including on the wishlist card so the shopper can resolve 'does this match the picture?' without leaving.

**Control:** Current PDP + wishlist. No added proof module. No price change in either arm.

**Primary metric:** Share of users who purchase at least one wishlisted item within 30 days of adding it.

**Denominator:** Users who added a treatment-eligible item to wishlist in the assignment window, still intending to buy it (exclude accidental saves if a save-job tag exists).

**Guardrails:** Return rate on treated items; customer-support contacts; un-wishlist rate; time-to-decision (buy or remove). Do not treat AOV lift from markdowns as success.

**Success rule:** Statistically and practically higher 30-day wishlist-item purchase rate vs control, with return rate not worse beyond the pre-registered bound. Readiness `ready_to_test`: run as an A/B on-product test after a short interview check.

**Do not optimize:** Coupon redemption, discount depth, cashback take-up, markdown attach rate, or any price-off as the primary KPI.

Status: `hypothesis` · conversion link `hypothesis` · readiness `ready_to_test`

### 3. `exp:price_watch:1`

30-day test: Worth-it proof at the current price

**Hypothesis:** If we close 'Enough value and quality information to decide whether the current price is acceptable, without assuming a coupon is required.' with 'Worth-it proof at the current price', users who wishlisted a treated item will be more likely to purchase at least one wishlisted item within 30 days than users on the current experience. This conversion link is unproven in the scrape.

**Audience:** Shoppers who wishlisted an item in the last 7 days where the open barrier is `value` (opportunity `opp:price_watch`, n=1143 / 17495 relevant in the scrape — scrape n is not the test sample).

**Treatment:** On wishlist and PDP, show construction, fabric weight, comparable quality cues, and what is included so the shopper can judge value at the listed price. Split waiters into 'would buy if quality/fit were clear' vs 'will only buy below a number'.

**Control:** Current PDP + wishlist. No added proof module. No price change in either arm.

**Primary metric:** Share of users who purchase at least one wishlisted item within 30 days of adding it.

**Denominator:** Users who added a treatment-eligible item to wishlist in the assignment window, still intending to buy it (exclude accidental saves if a save-job tag exists).

**Guardrails:** Return rate on treated items; customer-support contacts; un-wishlist rate; time-to-decision (buy or remove). Do not treat AOV lift from markdowns as success.

**Success rule:** Statistically and practically higher 30-day wishlist-item purchase rate vs control, with return rate not worse beyond the pre-registered bound. Readiness `ready_to_test`: run as an A/B on-product test after a short interview check.

**Do not optimize:** Coupon redemption, discount depth, cashback take-up, markdown attach rate, or any price-off as the primary KPI.

Status: `hypothesis` · conversion link `hypothesis` · readiness `ready_to_test`

### 4. `exp:comparison_loop:1`

30-day test: Decision attributes, not more options

**Hypothesis:** If we close 'A clear way to compare the few attributes that actually change the decision.' with 'Decision attributes, not more options', users who wishlisted a treated item will be more likely to purchase at least one wishlisted item within 30 days than users on the current experience. This conversion link is unproven in the scrape.

**Audience:** Shoppers who wishlisted an item in the last 7 days where the open barrier is `comparison` (opportunity `opp:comparison_loop`, n=523 / 17495 relevant in the scrape — scrape n is not the test sample).

**Treatment:** Let a shopper pin 2–3 wishlisted alternatives and run a comparison on the attributes that actually show up in evidence: fit notes, fabric, on-body proof, exchange ease. Hide extra catalog noise. Do not compete on strikethrough price.

**Control:** Current PDP + wishlist. No added proof module. No price change in either arm.

**Primary metric:** Share of users who purchase at least one wishlisted item within 30 days of adding it.

**Denominator:** Users who added a treatment-eligible item to wishlist in the assignment window, still intending to buy it (exclude accidental saves if a save-job tag exists).

**Guardrails:** Return rate on treated items; customer-support contacts; un-wishlist rate; time-to-decision (buy or remove). Do not treat AOV lift from markdowns as success.

**Success rule:** Statistically and practically higher 30-day wishlist-item purchase rate vs control, with return rate not worse beyond the pre-registered bound. Readiness `ready_to_test`: run as an A/B on-product test after a short interview check.

**Do not optimize:** Coupon redemption, discount depth, cashback take-up, markdown attach rate, or any price-off as the primary KPI.

Status: `hypothesis` · conversion link `hypothesis` · readiness `ready_to_test`

### 5. `exp:fit_uncertainty:1`

30-day test: Body-matched size evidence

**Hypothesis:** If we close 'A reliable way to judge fit and size for their body before buying.' with 'Body-matched size evidence', users who wishlisted a treated item will be more likely to purchase at least one wishlisted item within 30 days than users on the current experience. This conversion link is unproven in the scrape.

**Audience:** Shoppers who wishlisted an item in the last 7 days where the open barrier is `fit` (opportunity `opp:fit_uncertainty`, n=2143 / 17495 relevant in the scrape — scrape n is not the test sample).

**Treatment:** On the wishlisted item, show fit measurements against a body-similar review set, garment-flat measurements, and how the piece sat on someone with the shopper's size inputs, rather than a generic chart.

**Control:** Current PDP + wishlist. No added proof module. No price change in either arm.

**Primary metric:** Share of users who purchase at least one wishlisted item within 30 days of adding it.

**Denominator:** Users who added a treatment-eligible item to wishlist in the assignment window, still intending to buy it (exclude accidental saves if a save-job tag exists).

**Guardrails:** Return rate on treated items; customer-support contacts; un-wishlist rate; time-to-decision (buy or remove). Do not treat AOV lift from markdowns as success.

**Success rule:** Statistically and practically higher 30-day wishlist-item purchase rate vs control, with return rate not worse beyond the pre-registered bound. Readiness `ready_to_test`: run as an A/B on-product test after a short interview check.

**Do not optimize:** Coupon redemption, discount depth, cashback take-up, markdown attach rate, or any price-off as the primary KPI.

Status: `hypothesis` · conversion link `hypothesis` · readiness `ready_to_test`

### 6. `exp:intent-uncertain:1`

30-day test: Close the open question on the saved item

**Hypothesis:** If we close 'The missing fact or proof that would turn indecision into a yes or a no.' with 'Close the open question on the saved item', users who wishlisted a treated item will be more likely to purchase at least one wishlisted item within 30 days than users on the current experience. This conversion link is unproven in the scrape.

**Audience:** Shoppers who wishlisted an item in the last 7 days where the open barrier is `uncertain` (opportunity `opp:intent:uncertain`, n=889 / 17495 relevant in the scrape — scrape n is not the test sample).

**Treatment:** For uncertain-intent wishlists, prompt the missing fact (fit, look, occasion, quality) and jump to that proof on the same item. The job is to turn indecision into a yes or a no.

**Control:** Current PDP + wishlist. No added proof module. No price change in either arm.

**Primary metric:** Share of users who purchase at least one wishlisted item within 30 days of adding it.

**Denominator:** Users who added a treatment-eligible item to wishlist in the assignment window, still intending to buy it (exclude accidental saves if a save-job tag exists).

**Guardrails:** Return rate on treated items; customer-support contacts; un-wishlist rate; time-to-decision (buy or remove). Do not treat AOV lift from markdowns as success.

**Success rule:** Statistically and practically higher 30-day wishlist-item purchase rate vs control, with return rate not worse beyond the pre-registered bound. Readiness `ready_to_test`: run as an A/B on-product test after a short interview check.

**Do not optimize:** Coupon redemption, discount depth, cashback take-up, markdown attach rate, or any price-off as the primary KPI.

Status: `hypothesis` · conversion link `hypothesis` · readiness `ready_to_test`

### 7. `exp:styling_uncertainty:1`

30-day test: Wear-it-with context on the wishlist

**Hypothesis:** If we close 'Outfit context: what to pair it with and how it sits in a wardrobe.' with 'Wear-it-with context on the wishlist', users who wishlisted a treated item will be more likely to purchase at least one wishlisted item within 30 days than users on the current experience. This conversion link is unproven in the scrape.

**Audience:** Shoppers who wishlisted an item in the last 7 days where the open barrier is `styling` (opportunity `opp:styling_uncertainty`, n=894 / 17495 relevant in the scrape — scrape n is not the test sample).

**Treatment:** Show 2–3 pairing examples and occasion tags on the wishlisted PDP so styling is visible in a wardrobe, not as an isolated studio shot.

**Control:** Current PDP + wishlist. No added proof module. No price change in either arm.

**Primary metric:** Share of users who purchase at least one wishlisted item within 30 days of adding it.

**Denominator:** Users who added a treatment-eligible item to wishlist in the assignment window, still intending to buy it (exclude accidental saves if a save-job tag exists).

**Guardrails:** Return rate on treated items; customer-support contacts; un-wishlist rate; time-to-decision (buy or remove). Do not treat AOV lift from markdowns as success.

**Success rule:** Statistically and practically higher 30-day wishlist-item purchase rate vs control, with return rate not worse beyond the pre-registered bound. Readiness `ready_to_test`: run as an A/B on-product test after a short interview check.

**Do not optimize:** Coupon redemption, discount depth, cashback take-up, markdown attach rate, or any price-off as the primary KPI.

Status: `hypothesis` · conversion link `hypothesis` · readiness `ready_to_test`

### 8. `exp:barrier-availability:1`

30-day test: Size-intent restock, not a substitute SKU

**Hypothesis:** If we close 'Resolution of the availability issue before purchase.' with 'Size-intent restock, not a substitute SKU', users who wishlisted a treated item will be more likely to purchase at least one wishlisted item within 30 days than users on the current experience. This conversion link is unproven in the scrape.

**Audience:** Shoppers who wishlisted an item in the last 7 days where the open barrier is `availability` (opportunity `opp:barrier:availability`, n=322 / 17495 relevant in the scrape — scrape n is not the test sample).

**Treatment:** When the wishlisted size is gone, keep the exact size/color intent and notify on restock with the same proof pack so availability of the chosen item is recovered. Do not push a different product as the default recovery.

**Control:** Current PDP + wishlist. No added proof module. No price change in either arm.

**Primary metric:** Share of users who purchase at least one wishlisted item within 30 days of adding it.

**Denominator:** Users who added a treatment-eligible item to wishlist in the assignment window, still intending to buy it (exclude accidental saves if a save-job tag exists).

**Guardrails:** Return rate on treated items; customer-support contacts; un-wishlist rate; time-to-decision (buy or remove). Do not treat AOV lift from markdowns as success.

**Success rule:** Statistically and practically higher 30-day wishlist-item purchase rate vs control, with return rate not worse beyond the pre-registered bound. Readiness `ready_to_test`: run as an A/B on-product test after a short interview check.

**Do not optimize:** Coupon redemption, discount depth, cashback take-up, markdown attach rate, or any price-off as the primary KPI.

Status: `hypothesis` · conversion link `hypothesis` · readiness `ready_to_test`

### 9. `exp:barrier-delivery:1`

30-day test: Delivery date on the wishlisted SKU

**Hypothesis:** If we close 'Resolution of the delivery issue before purchase.' with 'Delivery date on the wishlisted SKU', users who wishlisted a treated item will be more likely to purchase at least one wishlisted item within 30 days than users on the current experience. This conversion link is unproven in the scrape.

**Audience:** Shoppers who wishlisted an item in the last 7 days where the open barrier is `delivery` (opportunity `opp:barrier:delivery`, n=149 / 17495 relevant in the scrape — scrape n is not the test sample).

**Treatment:** Show a realistic delivery date for the saved size/pincode on the wishlist row so timing uncertainty is visible before checkout.

**Control:** Current PDP + wishlist. No added proof module. No price change in either arm.

**Primary metric:** Share of users who purchase at least one wishlisted item within 30 days of adding it.

**Denominator:** Users who added a treatment-eligible item to wishlist in the assignment window, still intending to buy it (exclude accidental saves if a save-job tag exists).

**Guardrails:** Return rate on treated items; customer-support contacts; un-wishlist rate; time-to-decision (buy or remove). Do not treat AOV lift from markdowns as success.

**Success rule:** Statistically and practically higher 30-day wishlist-item purchase rate vs control, with return rate not worse beyond the pre-registered bound. Readiness `primary_research_first`: do not launch a powered A/B yet; run the Phase 5 research ask first, then a small prototype.

**Do not optimize:** Coupon redemption, discount depth, cashback take-up, markdown attach rate, or any price-off as the primary KPI.

Status: `hypothesis` · conversion link `hypothesis` · readiness `primary_research_first`

### 10. `exp:external_research:1`

30-day test: Bring off-platform proof onto the product

**Hypothesis:** If we close 'The same proof they currently hunt for off-platform, in context on the product.' with 'Bring off-platform proof onto the product', users who wishlisted a treated item will be more likely to purchase at least one wishlisted item within 30 days than users on the current experience. This conversion link is unproven in the scrape.

**Audience:** Shoppers who wishlisted an item in the last 7 days where the open barrier is `proof` (opportunity `opp:external_research`, n=407 / 17495 relevant in the scrape — scrape n is not the test sample).

**Treatment:** Put the proof questions people currently take to friends, Google, Reddit, or Instagram (real photos, fabric feel, 'is it worth it') into Q&A and UGC on the same PDP/wishlist item.

**Control:** Current PDP + wishlist. No added proof module. No price change in either arm.

**Primary metric:** Share of users who purchase at least one wishlisted item within 30 days of adding it.

**Denominator:** Users who added a treatment-eligible item to wishlist in the assignment window, still intending to buy it (exclude accidental saves if a save-job tag exists).

**Guardrails:** Return rate on treated items; customer-support contacts; un-wishlist rate; time-to-decision (buy or remove). Do not treat AOV lift from markdowns as success.

**Success rule:** Statistically and practically higher 30-day wishlist-item purchase rate vs control, with return rate not worse beyond the pre-registered bound. Readiness `ready_to_test`: run as an A/B on-product test after a short interview check.

**Do not optimize:** Coupon redemption, discount depth, cashback take-up, markdown attach rate, or any price-off as the primary KPI.

Status: `hypothesis` · conversion link `hypothesis` · readiness `ready_to_test`


## How to use

1. Prefer `ready_to_test` briefs. Run `primary_research_first` as interviews against Phase 6 evidence IDs.
2. Keep both arms at the same listed price.
3. Pre-register the 30-day window from wishlist add, not from first session.
