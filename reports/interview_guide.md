# Part 3 — User Research Interview Guide

Myntra Growth · Validating the "Active Comparers" opportunity (`opp:comparison_loop`)

**Purpose:** These interviews are the primary-research validation step for the hypothesis that already
has the strongest combined AI-discovery and survey evidence — see `reports/problem_definition.md` and
`reports/opportunity_register.md`. The goal is not to introduce a new theory; it is to stress-test
`comparison_loop` against real, live conversation before it goes into the final deck's Primary Research
slide.

**Target segment:** Active Comparers — users who wishlist an item while still comparing it against
alternatives. From the 36-respondent survey, this is the largest and most consistent segment (61% cite
"comparing with other options" as a wishlist motive; 59% among non-converters).

---

## Who to call

7 survey respondents opted into a follow-up and left a WhatsApp number in the original response sheet.
Contact details are not reproduced here — look them up directly in the source Google Sheet (the
"Provide WhatsApp number" and "Appropriate time to reach out" columns) to avoid duplicating personal
data in this document. Below is the recommended shortlist of 5–6, chosen to mix converters and
non-converters so you can compare what broke the tie.

| Respondent (by survey timestamp) | Wishlist size | Purchased in last 30d? | Why prioritize |
|---|---|---|---|
| 8/26 0:38:42 | 50+ | No | Large wishlist, "forgot about it" — pure re-engagement-lapse case |
| 8/25 23:32:04 | 0–5 | No | Comparison + occasion-timing, non-converter |
| 8/26 9:26:31 | 0–5 | No | "Want to think it over" + waiting-for-discount non-converter |
| 8/26 8:08:40 | 50+ | Yes | Converter who still cites "lost interest" for other items — good contrast case |
| 8/26 9:29:47 | 6–15 | Yes | Pure comparison motive, converted — what made this item win? |
| 8/26 10:10:52 | 16–50 | Yes | Converter, "want to think it over" motive — contrast to non-converters |

Aim for 5–6 completed calls. If someone doesn't respond or declines, the next-best backup is any other
respondent from the sheet who marked "Yes" to the follow-up question, prioritizing a mix of converters
and non-converters over any single trait.

## Format

Phone or video call (not a form) — 20–25 minutes, WhatsApp voice/video works since you already have
numbers. Ask consent to take notes / record before starting. Ask them to have the Myntra app open and
share their screen or read directly from their actual wishlist during the item deep-dive section —
evidence over recollection, the same principle the AI discovery engine follows.

---

## The 13 questions

### Item deep-dive — have them pull up one unbought wishlisted item

1. Walk me through the last time you added something to your wishlist — what were you doing right
   before that?
2. Why did you save *this* item instead of buying it on the spot?
3. Do you still intend to buy it? What's the one thing stopping you today?
4. Since you saved it, have you gone back and looked at it again? What brought you back — or what would
   it take?
5. Is there anything you still don't know about it that you'd want to know before buying?
6. Are you considering any alternatives to it — on this app or elsewhere? How do they compare?
7. Honestly — is this item still winning, or has something else already won and you just haven't
   removed it from the wishlist yet?

### Outside-the-app behavior

8. Before you'd actually buy it, do you check anywhere outside the app — Google, Instagram, other
   shopping apps, friends? What are you hoping to find there that you can't find in-app?

### Past conversion / abandonment — real decisions, not hypotheticals

9. Think of something you *did* buy from your wishlist — what tipped it from "maybe" to "yes"?
10. Think of something you removed from your wishlist *without* buying it — what made you finally give
    up on it?

### Uncertainty & re-engagement mechanics

11. When you're unsure whether something will fit, look right, or be worth it — what do you actually do
    to find out? Does that usually work?
12. Do you get wishlist notifications or reminders? Do they ever bring you back — and if they stopped
    entirely, would you remember the item on your own?

### Closing

13. If Myntra could fix exactly one thing to help you buy things from your wishlist — not a discount —
    what would it be?

---

## Interviewer notes

- Don't lead with "was it the return policy?" or "was it fit?" — let them name the blocker themselves
  (Q3) before you probe specifics, the same way the survey avoided pre-suggesting answers.
- Log verbatim quotes for Q2–Q7 and Q9–Q10 specifically — those map directly to opportunity evidence in
  `reports/opportunity_register.md` and should go into the same evidence-linked format as the
  AI-extracted insights.
- Keep the quote and your interpretation of it **separate**, the same discipline the discovery console
  uses everywhere (`observed_evidence` vs. `ai_interpretation`) — write down what they said, then
  separately what you think it means.

## What to send back

For each call, capture and send back:

1. Respondent identifier (survey timestamp is enough — no need to include their name or number).
2. Whether they converted in the last 30 days (from the sheet) — for the converter/non-converter
   contrast.
3. Answers to all 13 questions, with **verbatim quotes** for Q2–Q7 and Q9–Q10 kept separate from your
   own interpretation.
4. Anything that surprised you or contradicted the survey/AI-discovery findings — those are often the
   most useful signal.

Once all calls are in, send them back and they'll be folded into `reports/problem_definition.md` and the
final deck's Primary Research slide alongside the existing survey evidence.
