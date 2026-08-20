"""LLM prompt for evidence-linked extraction. Suggested labels are hints, not a closed set."""

from __future__ import annotations

from src.analyze.schema import PROMPT_VERSION_LLM, SUGGESTED_BARRIERS, SUGGESTED_INTENTS

SYSTEM = """You extract shopping-journey evidence from user feedback.

You are NOT doing sentiment analysis, star-rating summaries, or keyword counts.

Rules:
- Every item MUST include an evidence_span copied verbatim from the user text (a substring).
- Do not invent quotes. If you cannot quote support, omit the item.
- Suggested labels are optional. If the data shows a different behavior, use a short other:<slug> label.
- Do not force a label from the suggested lists.
- status is observed_evidence when the span itself states the claim; hypothesis when you inferred it.
- Separate interpretation from the quote. Never present interpretation as the user's words.
- Return JSON only.
"""


def user_prompt(items: list[dict[str, str]]) -> str:
    payload = []
    for item in items:
        payload.append(
            f"RECORD_ID: {item['record_id']}\nTEXT:\n{item['text']}\n"
        )
    joined = "\n---\n".join(payload)
    return f"""Suggested intent labels (do not force): {", ".join(SUGGESTED_INTENTS)}
Suggested barrier labels (do not force): {", ".join(SUGGESTED_BARRIERS)}
Need items should be unanswered questions after the user likes a product.
Behavior items capture comparison (what is compared, why) and external research (where, why).

For each record return an object in "records" with record_id copied EXACTLY (r1, r2, ...) and four arrays: intents, barriers, needs, behaviors.
Each array item: label, evidence_span, status, confidence (0-1), interpretation.
Respond with a single JSON object. No markdown.

{joined}
"""


def request_body(items: list[dict[str, str]], model: str, json_mode: bool = True) -> dict:
    body: dict = {
        "model": model,
        "temperature": 0,
        "max_completion_tokens": 2048,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_prompt(items)},
        ],
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    if "gpt-oss" in model:
        # Leave tokens for the JSON answer instead of spending the budget on reasoning.
        body["reasoning_effort"] = "low"
    return body


PROMPT_VERSION = PROMPT_VERSION_LLM
