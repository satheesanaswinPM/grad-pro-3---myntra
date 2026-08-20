"""Phase 7 stays locked. Do not ideate product solutions or monetary incentives here."""

from __future__ import annotations

from src.qualify.config import ROOT

UNLOCK_GATES = (
    ROOT / "data" / "scoring" / "opportunities.parquet",
    ROOT / "reports" / "opportunity_register.md",
    ROOT / "reports" / "research_hypotheses.md",
)


def is_unlocked() -> bool:
    return all(path.exists() for path in UNLOCK_GATES)


def main() -> int:
    print("Phase 7 - Solution Ideation is locked.")
    print("Unlock only after Phases 5 and 6: ranked opportunities with evidence packs,")
    print("not model summaries, and a console that can answer the research question.")
    print("Do not use discounts, coupons, cashback, or price-offs as the primary solution.")
    if not is_unlocked():
        print("Gate files still missing:")
        for path in UNLOCK_GATES:
            if not path.exists():
                print(f"  - {path.relative_to(ROOT)}")
        return 3
    print("Gate files exist, but Phase 7 implementation is still out of scope for Part 1.")
    return 3
