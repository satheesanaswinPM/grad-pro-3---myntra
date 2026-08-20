"""Span-grounded extractor used when no LLM key is set.

Produces quote-backed rows, not sentiment scores or term counts. Labels outside
the suggested lists are emitted as other:<slug>. Missing evidence => no row.
"""

from __future__ import annotations

import re
from typing import Any

from src.analyze.schema import PROMPT_VERSION_LOCAL
from src.analyze.validate import FIRST_PERSON, sanitize_payload

FLAGS = re.IGNORECASE | re.UNICODE
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

# Each tuple: extractor, label, pattern, interpretation
# Patterns require a real clause; we then store the whole sentence as the span.
DETECTORS: tuple[tuple[str, str, str, str], ...] = (
    ("intent", "bookmark", r"\bwish[\s-]?lists?\b|\bsave[ds]?\s+for\s+later\b|\bshortlists?\b|\bbookmarked\b", "User is saving the item rather than buying now."),
    ("intent", "comparison", r"\bcompar(?:e|ed|ing|ison)\b|\bversus\b|\bvs\.?\b|\balternatives?\b", "User is comparing options."),
    ("intent", "future_purchase", r"\blater\b|\bnext\s+(?:month|week|sale)\b|\bwaiting\s+(?:for|until)\b|\bsomeday\b|\bwhen\s+i\s+(?:get|have)\b", "Purchase is deferred."),
    ("intent", "price_watch", r"\bsale\b|\bdiscount\b|\bprice\s+drop\b|\bcheaper\b|\btoo\s+expensive\b|\bwait(?:ing)?\s+for\s+(?:a\s+)?sale\b", "User is watching price or promotion timing."),
    ("intent", "occasion", r"\bwedding\b|\binterview\b|\boffice\b|\bparty\b|\bfestival\b|\boccasion\b", "Purchase is tied to an occasion."),
    ("intent", "inspiration", r"\binspir(?:e|ed|ation)\b|\baesthetic\b|\blook\s+i\s+want\b|\bvibe\b", "Browsing for inspiration."),
    ("intent", "strong_purchase", r"\bbought\b|\bpurchased\b|\bordered\b|\bi\s+got\s+(?:this|it|them)\b|\bwearing\b", "User already bought or is wearing it."),
    ("intent", "uncertain", r"\bnot\s+sure\b|\bunsure\b|\bidk\b|\bmaybe\b|\bdon't\s+know\s+if\b", "Intent is unresolved."),
    ("barrier", "fit", r"\btoo\s+(?:small|big|tight|loose)\b|\bruns?\s+(?:small|large|big)\b|\bdoesn(?:'t|ot)\s+fit\b|\bsizing\s+(?:issue|problem|off)\b|\bsize\s+chart\b|\bwrong\s+size\b", "Fit or size is in question."),
    ("barrier", "quality", r"\bpoor(?:ly)?\s+(?:made|quality)\b|\bbad\s+quality\b|\blow\s+quality\b|\bcheap[- ]look|\bflimsy\b|\bquality\s+(?:issue|issues|problem)\b", "Quality is in question."),
    ("barrier", "fabric", r"\bsee[- ]through\b|\bitchy\b|\bscratchy\b|\bcheap\s+fabric\b|\bthin\s+material\b|\brough\s+(?:fabric|material)\b", "Fabric or material is in question."),
    ("barrier", "styling", r"\bhow\s+to\s+style\b|\bpair(?:ed|ing)?\s+(?:it|this)\b|\bdoesn't\s+go\s+with\b", "Styling is unresolved."),
    ("barrier", "occasion", r"\btoo\s+(?:formal|casual)\b|\bnot\s+(?:sure\s+)?(?:if\s+)?(?:appropriate|right)\s+for\b", "Occasion fit is unresolved."),
    ("barrier", "proof", r"\bas\s+(?:pictured|shown|advertised)\b|\blooks?\s+different\b|\bnot\s+as\s+(?:shown|pictured|expected)\b|\bmisleading\s+(?:photo|image|picture)s?\b", "Images/social proof do not settle the decision."),
    ("barrier", "returns", r"\breturn(?:ed|ing|s)?\b|\bexchang(?:e|ed|ing)\b|\bsent\s+(?:it|them)\s+back\b|\breturn\s+polic", "Returns or exchanges are part of the story."),
    ("barrier", "delivery", r"\bdeliver(?:y|ed)\b|\bshipping\b|\blate\b|\btook\s+forever\b|\bdispatch", "Delivery timing or experience is in question."),
    ("barrier", "availability", r"\bout\s+of\s+stock\b|\bsold\s+out\b|\bunavailable\b|\brestock\b", "Availability blocked the buy."),
    ("barrier", "value", r"\bnot\s+worth\b|\boverpriced\b|\btoo\s+expensive\b|\bvalue\s+for\s+money\b|\bwaste\s+of\s+money\b", "Value for money is in question."),
    ("barrier", "comparison", r"\bcompar(?:e|ed|ing)\b|\binstead\s+of\b|\bother\s+brand\b", "Another option is competing."),
    ("barrier", "trust", r"\bfake\b|\bscam\b|\bcounterfeit\b|\bdon't\s+trust\b|\bdo\s+not\s+trust\b", "Trust in seller or product is in question."),
    ("barrier", "other:shrinkage", r"\bshr[ua]nk\b|\bshrink(?:age|ing)?\b", "Garment changed size after wear or wash."),
    ("barrier", "other:color", r"\bcolor\s+(?:faded|ran|off)\b|\bcolour\s+(?:faded|ran|off)\b|\bnot\s+the\s+(?:same\s+)?colou?r\b", "Color did not match expectation."),
    ("barrier", "other:comfort", r"\bitchy\b|\bscratchy\b|\buncomfortable\b|\bhurts?\b", "Comfort is a problem."),
    ("barrier", "other:support", r"\bcustomer\s+(?:care|service)\b|\bno\s+response\b|\bwaste\s+(?:my\s+)?time\s+with\s+(?:support|chat)\b", "Support experience is a problem."),
    ("need", "will_it_fit", r"\btoo\s+(?:small|big|tight|loose)\b|\bnot\s+sure.{0,24}\bsize\b|\bruns?\s+(?:small|large|big)\b|\bdoesn(?:'t|ot)\s+fit\b|\bsize\s+chart\b", "Will this fit me?"),
    ("need", "is_quality_worth_it", r"\bnot\s+worth\b|\bpoor(?:ly)?\s+(?:made|quality)\b|\bbad\s+quality\b|\bflimsy\b|\bcheap[- ]look", "Is the quality worth it?"),
    ("need", "vs_images", r"\bas\s+(?:pictured|shown)\b|\blooks?\s+different\b|\bphotos?\b|\bpictures?\b", "How does the actual product compare with the images?"),
    ("need", "what_to_pair", r"\bpair(?:ed|ing)?\b|\bhow\s+to\s+style\b|\bwhat\s+to\s+wear\b", "What should I pair it with?"),
    ("need", "right_for_occasion", r"\boccasion\b|\bwedding\b|\boffice\s+wear\b|\bappropriate\b", "Is this appropriate for my occasion?"),
    ("need", "better_alternative", r"\bcompar(?:e|ed|ing)\b|\balternatives?\b|\bbetter\s+than\b|\binstead\s+of\b", "Is there a better alternative?"),
    ("behavior", "comparison", r"\bcompar(?:e|ed|ing|ison)\b|\bversus\b|\bvs\.?\b|\binstead\s+of\b", "Comparison behavior."),
    ("behavior", "external:google", r"\bgoogle[d]?\b|\bgoogling\b", "Sought information on Google."),
    ("behavior", "external:reddit", r"\breddit\b", "Sought information on Reddit."),
    ("behavior", "external:youtube", r"\byoutube\b", "Sought information on YouTube."),
    ("behavior", "external:instagram", r"\binstagram\b|\binsta\b", "Sought information on Instagram."),
    ("behavior", "external:friends_family", r"\bfriends?\b|\bfamily\b|\bsister\b|\bmom\b|\bmother\b|\bhusband\b", "Sought validation from people they know."),
    ("behavior", "external:other_apps", r"\bamazon\b|\bflipkart\b|\bajio\b|\bnykaa\b|\bmeesho\b|\bshein\b", "Looked at another shopping platform."),
)

COMPILED = tuple(
    (extractor, label, re.compile(pattern, FLAGS), interpretation)
    for extractor, label, pattern, interpretation in DETECTORS
)


def sentences(text: str) -> list[str]:
    parts = [part.strip() for part in SENT_SPLIT.split(text or "") if part.strip()]
    return parts or ([text.strip()] if text and text.strip() else [])


def extract_text(text: str, content_hash: str) -> dict[str, list[dict[str, Any]]]:
    payload: dict[str, list[dict[str, Any]]] = {
        "intents": [],
        "barriers": [],
        "needs": [],
        "behaviors": [],
    }
    bucket = {
        "intent": "intents",
        "barrier": "barriers",
        "need": "needs",
        "behavior": "behaviors",
    }
    seen: set[tuple[str, str, str]] = set()
    for sentence in sentences(text):
        if len(sentence) < 8:
            continue
        person = bool(FIRST_PERSON.search(sentence))
        for extractor, label, pattern, interpretation in COMPILED:
            if not pattern.search(sentence):
                continue
            key = (extractor, label, sentence.casefold())
            if key in seen:
                continue
            seen.add(key)
            status = "observed_evidence" if person else "hypothesis"
            confidence = 0.72 if person else 0.55
            item = {
                "label": label,
                "evidence_span": sentence,
                "status": status,
                "confidence": confidence,
                "interpretation": interpretation,
            }
            payload[bucket[extractor]].append(item)
    return sanitize_payload(text, payload, PROMPT_VERSION_LOCAL, content_hash)
