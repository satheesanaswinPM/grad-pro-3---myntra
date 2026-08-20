"""Unlock Phase 7 only when ranked opportunities and the research console exist."""

from __future__ import annotations

from pathlib import Path

from src.qualify.config import REPORTS_DIR, ROOT

UNLOCK_GATES: tuple[tuple[str, Path], ...] = (
    ("Phase 5 opportunities", ROOT / "data" / "scoring" / "opportunities.parquet"),
    ("Phase 5 opportunity register", REPORTS_DIR / "opportunity_register.md"),
    ("Phase 5 research hypotheses", REPORTS_DIR / "research_hypotheses.md"),
    ("Phase 6 console", ROOT / "src" / "dashboard" / "app.py"),
    ("Phase 6 relevant snapshot", ROOT / "data" / "processed" / "relevant.parquet"),
)


def missing_gates() -> list[tuple[str, Path]]:
    return [(label, path) for label, path in UNLOCK_GATES if not path.exists()]


def is_unlocked() -> bool:
    return not missing_gates()
