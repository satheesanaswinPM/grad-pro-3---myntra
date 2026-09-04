# Part 7 — Risks & Mitigation

Myntra Growth · Wishlist-to-Purchase Conversion · "Decide" MVP

This document is deliberately scoped to **this specific solution** — the validated
`comparison_loop` hypothesis from Part 4 (`reports/problem_definition.md`) and the "Decide" MVP built
for Part 5 (`src/mvp/`) — not generic product-launch risk. Every risk below traces to one of three
origins: (a) an evidentiary limit of the hypothesis itself, (b) a specific line of the MVP's actual
architecture, or (c) independent external market research surfacing a failure mode the original scoping
didn't anticipate (B5). Where a risk is already anticipated by a Part 6 guardrail
(`reports/define_success.md`), that link is called out explicitly — the guardrails were designed against
these exact failure modes, not written in the abstract.

Risks are grouped into four categories and ranked by priority within each.

---

## A. Hypothesis-validity risks

*Is `comparison_loop` actually the right problem, and is it actually causal?*

### A1. Correlation, not causation — **Critical**

**Why this could happen:** The entire root cause rests on two sources, neither of which contains real
purchase outcomes: the AI-mined review corpus (17,495 relevant records, no purchase/non-purchase
ground truth — every opportunity in `reports/opportunity_register.md` is explicitly labeled
`conversion link: hypothesis`) and a 36-respondent self-report survey. `comparison_loop` has the
highest *hesitation-link* score of all 20 scored opportunities (0.6338), but hesitation-link measures
*where in the journey* a theme sits, not whether fixing it moves actual 30-day purchases.

**Failure mode:** The MVP could successfully raise its own primary metric (30-Day Comparison
Resolution Rate) — more comparisons get an explicit Buy/Remove outcome — without that resolution rate
having any real relationship to the north-star business metric. We'd have optimized a proxy, not the
target.

**Mitigation:** Part 6 already frames the primary MVP metric as a *"hypothesis-linked proxy for the
business metric, not a replacement for it."* Before any scaling decision, the MVP's success must be
treated as a gate into a real randomized experiment against actual 30-day purchase behavior — not a
substitute for one. Track the Part 6 guardrails in parallel so a rise in Resolution Rate alone is never
sufficient grounds to declare the hypothesis proven.

### A2. Small, self-selected survey sample — **High**

**Why this could happen:** The primary research that corroborated `comparison_loop` (61% wishlist
motive, 42% top removal reason) is a 36-respondent Google Form, not the 5–6 qualitative interviews
originally scoped in Part 3. Those interviews were guided and 7 candidates opted in with contact
details, but — per the project's own status tracking — **were never actually conducted.** Form
respondents self-select toward people willing to fill out a survey, which likely skews toward more
analytical, engaged shoppers and under-represents the casual "just liked it" bookmarker segment
(which the survey itself still measured at 19–27% of responses).

**Failure mode:** "Active Comparers" may not generalize to the full wishlist user base; the MVP could
be solving a real problem for a segment that is smaller, or behaves differently in a live product
context, than the survey suggests.

**Mitigation:** Run the already-scoped interview guide (`doc/mvp_problem_statement.md` references the
same segment) against the 7 opted-in respondents before generalizing MVP results — treat current
findings as directional, not confirmatory, until that happens.

---

## B. Mechanism risks

*Does the MVP's specific design actually produce the intended behavior?*

### B1. Reason-capture friction shrinks the funnel it's meant to fix — **Critical**

**Why this could happen:** `src/mvp/app.py`'s `render_browse()` requires a mandatory reason chip
(`st.radio`, no skip option) before an item can be added to the wishlist. This is an extra step that
did not exist in the baseline wishlist flow.

**Failure mode:** If this friction meaningfully discourages wishlisting at all, the fix actively shrinks
the top of the funnel even while improving comparison resolution for the items that do get saved — a
net-negative outcome despite a positive primary metric.

**Mitigation:** This is precisely why Part 6 defined **Wishlist add rate** (must hold steady or grow)
and **Add-flow abandonment rate** as hard guardrails, not optional nice-to-haves. If either breaches,
the fallback is inferred tagging (e.g., flag "comparing" automatically when a user saves 2+ items in the
same category within a session) instead of a mandatory explicit prompt.

### B2. The AI agent can steer a user toward a bad decision — **Critical**

**Why this could happen:** `src/mvp/agent.py`'s comparison is a single LLM call with no human review.
It reasons from real attributes (`size_fit`, `product_details`, `ideal_for`, etc.) but LLM reasoning
over free-text product copy can misread nuance — e.g., recommending against an item whose `size_fit`
note actually supports the user's stated concern, or missing occasion mismatch buried in prose.

**Failure mode:** A confidently-worded but wrong recommendation could push a user to buy something
that doesn't fit their actual need, or to remove an item they would genuinely have wanted — actively
worse than no intervention.

**Mitigation:** This was anticipated at MVP-scoping time, not discovered after the fact — it's the
specific reason Part 6 defines **Regretted-removal rate** as a guardrail. Structurally,
`agent._validate()` already refuses to render a malformed or incomplete comparison (every input item id
must appear in the response) rather than silently guessing, but that only catches structural failure,
not reasoning quality. Add a lightweight "Was this helpful?" control on the result card as a fast
qualitative signal, ahead of the slower regretted-removal data.

### B3. Re-engagement is unvalidated on the real delivery channel — **High**

**Why this could happen:** The nudge mechanism is deliberately simulated in v1 — the "Fast-forward"
control stands in for real elapsed time *and* for push notifications, both explicitly out of scope per
`doc/mvp_problem_statement.md`. Every test so far (including the live walkthrough during the build) only
proves the in-app banner works once a user has *already opened the app*. It says nothing about whether a
real push notification would be delivered, allowed, or noticed.

**Failure mode:** Push notification opt-in and open rates are a well-known weak point for e-commerce
apps; if the real channel underperforms, Stage A (re-engagement) stays broken in production regardless
of how well the in-app mechanism tested.

**Mitigation:** Treat notification delivery as an explicit, unvalidated assumption. This is exactly why
Part 6 defines **Nudge-to-engagement rate** as a leading indicator rather than assuming it. Before wider
rollout, add an in-app-only fallback surface (e.g., a home-feed card) that doesn't depend on push
permission, and measure the two channels separately.

### B4. Live LLM dependency has no caching or fallback — **Medium**

**Why this could happen:** Every "Help me decide" invocation is a live call through `chat_json`
(`src/analyze/llm.py`) with no response caching — unlike the discovery pipeline, which caches by content
hash in `data/cache/llm.sqlite` specifically to control cost and rate-limit exposure. `agent.available()`
gates the button on a key being present, and `AgentError` fails visibly per spec rather than fabricating
a result, but a visible failure still means Stage C simply doesn't get fixed for that user at that
moment.

**Failure mode:** Cost scales linearly with invocation volume with no reuse; a provider outage or rate
limit degrades the feature for every concurrent user, not gracefully.

**Mitigation:** This was a deliberate v1 tradeoff (fail visibly, never fabricate). Before scaling
invocation volume, add response caching keyed on the comparison-set fingerprint (item ids + reasons),
mirroring the existing pipeline pattern, and lean on `chat_json`'s existing retry/backoff for transient
failures.

### B5. Success could increase returns, not just conversions — **High**

**Why this could happen:** Nudging a stale comparison back into an explicit decision doesn't guarantee a
well-considered one — pulling a user to decide *now* rather than on their own schedule could pull
forward marginal, lower-conviction purchases they would otherwise have let lapse entirely. This risk
surfaced from independent secondary research (a market case study external to this project's own data
collection), which cites Indian fashion e-commerce return rates of 25–40%, driven 53–70% by fit/size
issues — and Myntra's own public Trustpilot sentiment (1.1/5, with non-delivery and wrong/damaged items
as dominant complaints) independently corroborates that returns are already a live pain point,
regardless of anything this MVP does.

**Failure mode:** The MVP's primary metric (Comparison Resolution Rate) and even the raw count of "Buy"
decisions could rise while net realized revenue doesn't, if a meaningful share of newly-resolved "Buy"
decisions come back as returns — the same failure shape as A1 (a rising proxy metric that doesn't
reflect the real outcome), but here caused by the mechanism actively working rather than by it failing.

**Mitigation:** No existing Part 6 metric currently watches for this — it is a genuine gap, not yet
guarded. Before scaling, add a return-rate-of-MVP-driven-purchases metric alongside the existing
guardrails, and treat any increase relative to baseline as a signal to slow the nudge cadence or
strengthen the agent's fit/size confidence-checking, rather than counting Comparison Resolution Rate
alone as success.

---

## C. Compliance risk

*The one hard constraint the whole project is built around.*

### C1. Monetary-language leakage from the LLM itself — **Critical**

**Why this could happen:** The system prompt in `agent.py` explicitly forbids price-drop, discount,
cashback, and urgency language, and `catalog.py` deliberately never loads `variant_compare_at_price`.
But an LLM is not deterministic — and `price` *is* one of the attributes legitimately fed to the model
(needed to compare "similar price point" items), which is exactly the kind of input that could drift
toward "great value" or urgency-adjacent framing despite the instruction.

**Failure mode:** Even one instance of discount/urgency framing in production output would invalidate
the non-monetary premise the entire Part 4 problem definition rests on — this is why Part 6 sets
**Monetary-language leakage** at a hard target of 0%, not a soft goal.

**Mitigation:** Don't rely on the prompt alone. Add an automated post-response keyword/phrase scan
(discount, sale, price drop, deal, urgency terms) on every agent output before it renders, so the
guardrail is enforced in code, not only requested of the model.

---

## D. Scope & validation risk

*What the MVP has proven, and what it hasn't yet.*

### D1. Session-only state means the real metric can't be measured yet — **High**

**Why this could happen:** Per the explicit v1 scope boundary in `doc/mvp_problem_statement.md`, the
MVP has no accounts and no persistence across sessions or devices — `st.session_state` only. This was
the right call for a fast, deployable MVP, but it also means there is currently no way to measure a real
14- or 30-day Comparison Resolution Rate with real users; everything verified so far (real catalog data,
real LLM reasoning, the decide loop, the nudge firing) was confirmed within a single browser session
during testing.

**Failure mode:** The MVP proves the *mechanism* works, not that it *moves the metric* over a real
multi-day window — those are different claims, and it would be a mistake to present the former as
evidence for the latter.

**Mitigation:** The next build increment needs minimal persistence (even just a device-local identifier
plus a backend log of reason-tag, nudge, and decide events) specifically so the Part 6 metrics can be
measured for real before any impact claim is made.

### D2. Not yet deployed to production — **Medium**

**Why this could happen:** The MVP is code-complete and pushed to GitHub, but the Streamlit Community
Cloud deploy step requires the project owner's account and hasn't been completed — Part 5's own
definition of done isn't fully met yet.

**Failure mode:** All validation to date is from local/browser-preview testing, not from real external
users on a public URL — the interviews planned in A2 can't run against the live product until this is
done.

**Mitigation:** Complete the deployment (steps already provided after the MVP build), then run the
scoped Part 3 interviews against the live MVP rather than a description of it.

---

## Summary — how these risks map back to what's already built

| Risk | Category | Priority | Existing Part 6 metric watching for it |
|---|---|---|---|
| A1. Correlation, not causation | Hypothesis | Critical | — (handled by how the primary metric is framed: proxy, not replacement) |
| B1. Reason-capture friction shrinks the funnel | Mechanism | Critical | Guardrail: Wishlist add rate · Add-flow abandonment rate |
| B2. AI agent steers a bad decision | Mechanism | Critical | Guardrail: Regretted-removal rate |
| C1. Monetary-language leakage | Compliance | Critical | Guardrail: Monetary-language leakage (target 0%) |
| A2. Small, self-selected survey sample | Hypothesis | High | — (needs the scoped Part 3 interviews) |
| B3. Re-engagement channel unvalidated | Mechanism | High | Leading indicator: Nudge-to-engagement rate |
| B5. Success could increase returns, not just conversions | Mechanism | High | — (needs a new return-rate metric, not yet built) |
| D1. Session-only state, real metric unmeasured | Scope | High | — (needs minimal persistence) |
| B4. Live LLM dependency, no caching | Mechanism | Medium | Guardrail: Agent failure rate |
| D2. Not yet deployed to production | Scope | Medium | — (deploy steps already provided) |

Five of ten risks already have an existing Part 6 metric — a guardrail or a leading indicator —
watching for them directly. A1 is instead handled by how the primary metric itself is framed (proxy,
not replacement), rather than by a separate tracked number. The four genuine gaps (A2's missing
interviews, B5's missing return-rate metric, D1's missing persistence, D2's pending deploy) are each a
direct consequence either of an explicit, deliberate v1 scope cut, or — for B5 specifically — of a risk
identified after the fact from external market research rather than during the original MVP scoping.
Both are legitimate reasons a metric doesn't exist yet, but only one of them (B5) means the guardrail
set itself needs to grow before wider rollout.
