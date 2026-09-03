# Part 6 — Define Success

Myntra Growth · Success metrics for the "Decide" wishlist comparison agent MVP.
Slide source: `reports/define_success_part6.pptx`.

---

## The business metric (north star)

> % of users who purchase at least one wishlisted item within 30 days of adding it.

**Constraint:** no monetary incentives — discounts, coupons, cashback, and price-offs are excluded as
the primary lever.

**Why this metric alone can't run the MVP day to day:**
- 30-day window — far too slow a feedback loop for weekly iteration.
- Doesn't say where in the funnel to intervene.
- The AI-mined review corpus has no purchase outcomes — every downstream link is a hypothesis until
  tested (see `reports/opportunity_register.md`).

## Where the MVP sits in the funnel

Of the five funnel stages decomposed in Part 2 (Re-engagement → Uncertainty Resolution → Comparison
Resolution → Decision Trigger → Purchase Completion), the MVP's own instrumentation targets **A
(Re-engagement)** and **C (Comparison Resolution)** only. Stages D and E remain the business's
downstream responsibility, not this MVP's.

This is the highest hesitation-link opportunity of all 20 scored (`comparison_loop`, 0.6338) and the
only hypothesis dominant in two independent survey questions (see `reports/problem_definition.md`).

## Primary success metric for the MVP

**30-Day Comparison Resolution Rate**

```
resolved comparisons ÷ (resolved comparisons + still-cold comparisons)
```

**Definition:** Share of wishlisted items tagged "comparing" that reach an explicit outcome — bought
or removed — within 14 days of being added, instead of going cold with no activity.

**Why this metric:**
- It's the leading proxy for the highest-hesitation-link opportunity (`comparison_loop`, 0.6338) — not
  a downstream stand-in for revenue.
- It's measurable at 14 days, not 30 — fast enough to iterate on before a full conversion experiment.
- "Resolved" deliberately counts both Buy and Remove — the fix is deciding, not just buying.
- Already instrumented — this is the exact "Resolved / Still cold" tally the MVP shows in-app
  (`src/mvp/state.py::resolution_tally()`).

## Leading indicators

Fast-moving signals, visible in days — not the full 30-day window.

| Indicator | Definition | Rationale |
|---|---|---|
| Reason-capture rate | % of new wishlist adds where the user actually selects a reason tag. | The entry gate — nothing downstream works if items aren't tagged. |
| Nudge-to-engagement rate | % of stale "Comparing" nudges that get an active re-open within 48 hours of firing. | Proves Stage A (re-engagement) is actually being fixed, not just displayed. |
| "Help me decide" invocation rate | % of eligible comparison sets (2+ items) where the user actually calls the agent. | A comparison tool nobody opens can't resolve anything — this is adoption, not just existence. |
| Recommendation-acceptance rate | % of agent-assisted comparisons where the user acts on the recommended item. | Signals the agent's reasoning is trusted, not merely used. |

## Guardrail metrics

Every guardrail fails closed — a violation pauses the rollout, it doesn't get averaged away by a good
primary metric.

| Guardrail | Definition | Rationale |
|---|---|---|
| Wishlist add rate | Must hold steady or grow. | If reason-tagging friction discourages saving items at all, we shrink the funnel's top even as resolution improves. |
| Add-flow abandonment rate | % who open the reason step but abandon without completing. | The extra tap must not become a new drop-off point. |
| Regretted-removal rate | % of agent-driven "Remove" decisions followed by a re-search or re-add of a similar item. | The agent should help people decide well, not just decide fast. |
| Agent failure rate | % of "Help me decide" calls that surface a visible error instead of a comparison. | The spec requires failing visibly, not fabricating — but a high failure rate still kills trust in the mechanism. |
| Monetary-language leakage | % of agent outputs or nudges mentioning price drops, discounts, or urgency. Target: 0%. | A single violation invalidates the non-monetary premise the whole Problem Definition rests on. |

## How these metrics connect

```
Business metric        30-day wishlist-to-purchase conversion rate
        ↓
Primary MVP metric      30-day comparison resolution rate
        ↓
Leading indicators      Reason capture · Nudge engagement · Agent invocation · Rec. acceptance

Guardrails watch every level of this ladder at once — they aren't a rung, they're a
constraint on the whole stack. A guardrail breach pauses the rollout regardless of how
the primary metric is trending.
```

The primary metric is a hypothesis-linked proxy for the business metric, not a replacement for it.

## Project status

| # | Part | Status |
|---|---|---|
| 1 | AI Discovery Engine | Done |
| 2 | Metric Decomposition | Done |
| 3 | User Research | Survey done · interviews pending |
| 4 | Problem Definition | Done |
| 5 | MVP Build | Built · deploy pending |
| 6 | Define Success | Done — this document |
| 7 | Risks & Mitigation | Next |
