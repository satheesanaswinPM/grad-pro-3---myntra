"""Check each concept against the discovered need/barrier. Reject monetary primaries."""

from __future__ import annotations

import re
from typing import Any

from src.ideate.schema import (
    FORBIDDEN_LEVERS,
    MIN_HESITATION_FOR_TEST,
    READINESS_RESEARCH,
    READINESS_TEST,
    READINESS_WEAK,
    SMALL_N,
)
from src.score.schema import APP_UX_LABELS

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    stop = {
        "a",
        "an",
        "the",
        "to",
        "of",
        "and",
        "or",
        "for",
        "in",
        "on",
        "is",
        "it",
        "this",
        "that",
        "they",
        "their",
        "with",
        "before",
        "after",
        "from",
        "into",
        "still",
        "need",
        "user",
        "shopper",
        "shoppers",
    }
    return {tok for tok in _TOKEN.findall(text.casefold()) if tok not in stop and len(tok) > 2}


def contains_forbidden(text: str) -> bool:
    cleaned = re.sub(r"[^a-z0-9% ]+", " ", text.casefold())
    blob = f" {cleaned} "
    return any(f" {term} " in blob for term in FORBIDDEN_LEVERS)


def _overlap(left: str, right: str) -> bool:
    a, b = _tokens(left), _tokens(right)
    if not a or not b:
        return False
    return len(a & b) >= 1


def _mentions_barrier(mechanism: str, barrier: str) -> bool:
    blob = f" {re.sub(r'[^a-z0-9 ]+', ' ', mechanism.casefold())} "
    raw = re.sub(r"[^a-z0-9 ]+", " ", barrier.casefold()).strip()
    if raw and raw in blob:
        return True
    stem = raw.rstrip("s")
    if len(stem) >= 4 and stem in blob:
        return True
    return _overlap(mechanism, barrier)


def validate_concepts(
    concepts: list[dict[str, Any]],
    opportunities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_id = {str(row["opportunity_id"]): row for row in opportunities}
    rows: list[dict[str, Any]] = []
    for concept in concepts:
        opp = by_id.get(str(concept["opportunity_id"]), {})
        mechanism = str(concept.get("mechanism") or "")
        need = str(opp.get("user_need") or concept.get("addresses_need") or "")
        barrier = str(opp.get("barrier") or concept.get("addresses_barrier") or "")
        addresses_need = _overlap(mechanism, need) or _overlap(str(concept.get("addresses_need") or ""), need)
        addresses_barrier = _mentions_barrier(mechanism, barrier)
        # Treatment text must not use a forbidden lever; rejected_lever may name them to forbid them.
        non_monetary = not contains_forbidden(f"{concept.get('title')} {mechanism}")
        n = int(opp.get("unique_records") or concept.get("unique_records") or 0)
        n_small = n < SMALL_N or str(opp.get("status") or "") == "hypothesis"
        hesitation = float(opp.get("purchase_hesitation_link") or 0)
        evidence_status = str(opp.get("status") or "hypothesis")
        app_ux = barrier in APP_UX_LABELS
        notes: list[str] = []
        if not non_monetary:
            notes.append("Rejected: treatment text uses a monetary incentive as the primary lever.")
        if not addresses_need:
            notes.append("Weak fit: mechanism does not clearly address the Phase 5 user need.")
        if not addresses_barrier:
            notes.append("Weak fit: mechanism does not mention the ranked barrier.")
        if n_small:
            notes.append(f"n={n} is below {SMALL_N} or status is hypothesis; do not run a large conversion test yet.")
        if hesitation < MIN_HESITATION_FOR_TEST:
            notes.append(
                f"purchase_hesitation_link={hesitation:.4f} is below {MIN_HESITATION_FOR_TEST:.2f}. "
                "Do primary research on whether this sits on wishlist → buy before a conversion experiment."
            )
        if app_ux:
            notes.append(
                "Scoring treats this label as possible general app UX. Confirm it sits on wishlist → buy before a conversion experiment."
            )
        if str(opp.get("conversion_link_status") or "hypothesis") == "hypothesis":
            notes.append("Scrape has no purchase outcomes. Any conversion effect is a hypothesis until the experiment.")
        if str(concept.get("opportunity_id") or "").endswith("returns_exchange"):
            notes.append(
                "Return stories are often post-purchase. Interview to split pre-purchase fear vs reverse-logistics complaints."
            )

        if not non_monetary or not addresses_need:
            readiness = READINESS_WEAK
        elif n_small or hesitation < MIN_HESITATION_FOR_TEST or app_ux:
            readiness = READINESS_RESEARCH
        else:
            readiness = READINESS_TEST

        rows.append(
            {
                "validation_id": f"val:{concept['concept_id'].removeprefix('concept:')}",
                "concept_id": concept["concept_id"],
                "opportunity_id": concept["opportunity_id"],
                "rank": int(concept.get("rank") or 0),
                "addresses_stated_need": bool(addresses_need),
                "addresses_stated_barrier": bool(addresses_barrier),
                "non_monetary": bool(non_monetary),
                "evidence_status": evidence_status,
                "n_small": bool(n_small),
                "hesitation": round(hesitation, 4),
                "readiness": readiness,
                "notes": " ".join(notes),
                "status": "observed_evidence" if evidence_status == "observed_evidence" else "hypothesis",
            }
        )
    return rows
