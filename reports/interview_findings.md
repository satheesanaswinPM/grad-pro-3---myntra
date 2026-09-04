# Part 3 — Primary Research Interview Findings

Myntra Growth · Active Comparers · n=2 qualitative interviews, conducted via the guide in
`reports/interview_guide.md`, following the 36-respondent Wishlist Behavior Survey.

**Sample:** 2 of the 5–6 originally scoped interviews were completed before primary research was
closed out. This is a smaller sample than planned — see the caveat at the end of this document and
`reports/risks_and_mitigation.md` (A2) for how that limitation is handled honestly rather than
glossed over.

| Respondent | Converted in last 30 days? | Wishlist scale |
|---|---|---|
| Anjali | Yes | Small, curated |
| Bhargavi Joshi | No | 1,220 items |

---

## What the interviews confirm

**`comparison_loop` is real, described unprompted, by both respondents.**

> Anjali: "I did not have a particular shoe in mind, so I wanted to compare, shortlist and compare."

> Bhargavi: "I want to compare it on other platforms. I want to see at what price Nykaa is selling it,
> at the same time at what price the brand is selling it on their website."

**Re-engagement without a prompt fails, and notifications don't fix it — for different reasons.**

> Anjali: "wishlist reminders don't really work because I am usually... in office or in a meeting...
> never sitting with my phone and relaxing." (Interpretation: attention-availability problem.)

> Bhargavi: "now there are more than 1,000 products, so I get bombarded with these alerts... I end up
> ignoring them." (Interpretation: signal-to-noise problem — notifications scoped to an entire
> 1,220-item wishlist are noise, not a useful nudge.)

This is a real design validation for the MVP: `src/mvp/app.py`'s nudge only fires for items explicitly
tagged "comparing," not the whole wishlist. Bhargavi's complaint is specifically about *unscoped*
reminders — which is the failure mode the MVP's reason-tagging was built to avoid.

**Fit uncertainty is not general — both respondents narrow it to *unfamiliar brands* specifically.**

> Anjali: "I'm not sure if that size will fit me because I've not tried that brand before."

> Bhargavi: "I am a very brand-conscious person... very used to with a brand's sizing... sizing is not
> an issue" — for her known brands (Mango, H&M, Zara). Fit only becomes a live concern outside them.

This sharpens H5 in `reports/problem_definition.md` from "fit uncertainty" to a more precise claim:
**fit uncertainty concentrates on unfamiliar brands**, not fit uncertainty in general. Both respondents
independently describe brand familiarity as their own de facto workaround.

---

## What the interviews add — findings the AI discovery pipeline underweighted

**1. Trust / counterfeit risk, unprompted, from a non-converter.**

> Bhargavi: "I am also very skeptical about receiving counterfeit products from Myntra because I've
> been through a lot of Reddit articles... if I have to buy a designer label, then probably I would
> not buy it from Myntra... I would rather reach out to Myntra for daily wear or not so costlier
> stuff." Backed by a real bad experience: ordered a size 6, received a mislabeled 6.5, could not
> return it.

`opp:barrier:trust` is **rank 18 of 20 in `reports/opportunity_register.md`** — the second-weakest
opportunity in the entire discovery-pipeline ranking (n=15, 0.09% of relevant records). A real,
unprompted interview account directly contradicts how thin that evidence looked from review-mining
alone. This doesn't mean the AI ranking is wrong — review-mining genuinely found very little trust
language — but it's a case where a single well-articulated primary-research account carries more
diagnostic weight than a low n suggests, and it should not be dismissed just because the automated
ranking under-counted it.

**2. Item-level intent, not user-level.** Bhargavi holds 1,220 wishlist items and describes most of
them candidly: "I don't really have that intention to buy... I am someone who just likes it and keeps
it." She is a pure bookmarker for nearly all of her wishlist — and an Active Comparer for exactly one
item (the ethnic wear she's buying for a wedding). This is a real refinement to the segment model:
**"Active Comparer" describes the state of one wishlisted item, not a fixed trait of the user who owns
it.** The same person can be both segments simultaneously, on different items.

**3. A third abandonment mechanism: need-obsolescence.** Bhargavi removed a set of midi dresses not
because a competitor won and not because she forgot, but because the underlying need disappeared —
she wore something she already owned to the event she'd been shopping for, and the wishlisted items
became moot. This is distinct from both patterns in the survey (competitor wins, 42%; forgot, 32%). One
account only — noted as directional, not a confirmed pattern, since it did not recur.

**4. Return-aversion as a pre-purchase deterrent, not only post-purchase pain.** Bhargavi: "I don't
want to order and then try and then return or exchange, so I think I would rather step into a mall."
`reports/opportunity_register.md` and `reports/metric_decomposition.md` both treat `returns_exchange`
as predominantly post-purchase noise (hesitation-link 0.1075, the lowest of the top 10) — correct on
balance, but this account shows fear of the *return process itself* can also function as a live
pre-purchase deterrent for some users, not only a post-purchase complaint. A minority pattern, not
grounds to revise the ranking, but worth naming rather than smoothing over.

---

## The pattern that matters most for the MVP: neither respondent's own "fix" matches our mechanism

Both respondents were asked, unprompted, what one non-monetary thing Myntra could fix. Neither answer
is "help me compare items with an AI recommendation" — the mechanism this MVP actually builds.

> Anjali wants a **Try & Buy bundle**: order 4–5 comparison candidates together, decide with them
> physically in hand, return the losers in one consolidated shipment — a logistics/fulfillment fix, not
> a decision-support one. (See the deeper breakdown already logged in this project's chat history:
> she needs physical trial for an unfamiliar brand, which no text-based AI reasoning can substitute for.)

> Bhargavi wants **AI-driven wishlist curation**: automatic occasion-aware collections ("push
> traditional outfits to the top before Diwali") built from her purchase history, so she doesn't have
> to manually organize or revisit a 1,220-item list to find what's actually relevant right now.

Both are real, coherent, non-monetary product ideas — and both are different in kind from "TieBreaker." The
underlying behavioral problem (`comparison_loop`, forgetting, fit uncertainty) is strongly validated by
both interviews. The specific solution shape this project chose to build is not what either respondent
reached for on their own. Two data points is not enough to say the MVP's mechanism is wrong — but it is
enough to say **the mechanism was never independently confirmed as the right one**, only the problem
was. This is now tracked explicitly as risk A3 in `reports/risks_and_mitigation.md`, rather than left
as an unstated gap.

---

## How to read this evidence honestly

- n=2 is well short of the 5–6 originally scoped. Both respondents happened to be women shopping
  fashion/footwear categories; neither is a councillor for how male shoppers, beauty-category shoppers,
  or first-time Myntra users experience this problem. Treat these findings as **directional
  corroboration of the survey**, not an independent confirmatory sample.
- Every quote above is verbatim from the interview transcripts; every interpretation is explicitly
  separated from the quote, the same discipline used throughout the AI-extracted evidence in
  `reports/opportunity_register.md`.
- Findings that recurred across both respondents (comparison behavior, notification fatigue,
  unfamiliar-brand fit uncertainty) are held with more confidence than single-respondent findings
  (need-obsolescence, return-aversion-as-pre-purchase-deterrent), which are logged as directional only.
