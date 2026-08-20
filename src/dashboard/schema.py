"""Phase 6 console and evidence-pack contracts. Quotes stay visible in the UI."""

from __future__ import annotations

QUOTE_LIMIT = 40

CONSOLE_MODULES = (
    "executive_summary",
    "wishlist_intent",
    "purchase_barriers",
    "user_segments",
    "uncertainty_map",
    "customer_journey",
    "comparison_behavior",
    "external_research",
    "category_analysis",
    "opportunity_matrix",
    "evidence_explorer",
    "research_hypotheses",
    "solution_concepts",
)

INSIGHT_FIELDS = (
    "insight_id",
    "problem_statement",
    "user_need",
    "barrier",
    "intent",
    "segment",
    "category",
    "source",
    "evidence_snippet",
    "record_id",
    "date",
    "frequency",
    "pct_relevant",
    "confidence",
    "ai_interpretation",
    "status",
    "extractor",
    "label",
    "text",
    "source_url",
    "journey_stage",
)

PACK_FIELDS = (
    "opportunity_id",
    "rank",
    "problem_statement",
    "user_need",
    "barrier",
    "status",
    "conversion_link_status",
    "unique_records",
    "pct_relevant",
    "denominator",
    "denominator_label",
    "total_score",
    "theme_ids",
    "segment_ids",
    "n_quotes",
    "n_evidence_records",
    "generated_at",
    "quotes",
    "note",
)
