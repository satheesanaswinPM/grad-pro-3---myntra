"""Non-monetary concepts and 30-day experiment briefs. Not a shipped product."""

from __future__ import annotations

from src.dashboard.components import banner, open_evidence, quote_cards
from src.dashboard.load import Store, split_ids
from src.qualify.config import ROOT
from src.synthesize.io import load_parquet

IDEATION = ROOT / "data" / "ideation"


def render(store: Store) -> None:
    import streamlit as st

    st.header("Solution concepts")
    banner()
    st.caption(
        "Phase 7 ideation. These are concepts and experiment designs, not a conversion product. "
        "Discounts are not the primary lever."
    )
    concepts_path = IDEATION / "concepts.parquet"
    if not concepts_path.exists():
        st.warning("No ideation tables yet. Run `python -m src.ideate` after Phases 5 and 6.")
        return

    concepts = load_parquet(concepts_path)
    validations = load_parquet(IDEATION / "validations.parquet") if (IDEATION / "validations.parquet").exists() else []
    experiments = load_parquet(IDEATION / "experiments.parquet") if (IDEATION / "experiments.parquet").exists() else []
    by_val = {row.get("concept_id"): row for row in validations}
    by_exp = {row.get("concept_id"): row for row in experiments}

    st.dataframe(
        [
            {
                "rank": row.get("rank"),
                "opportunity": row.get("opportunity_id"),
                "concept": row.get("title"),
                "readiness": by_val.get(row.get("concept_id"), {}).get("readiness"),
                "n": row.get("unique_records"),
                "% relevant": row.get("pct_relevant"),
                "conversion link": row.get("conversion_link_status"),
            }
            for row in concepts
        ],
        hide_index=True,
        width="stretch",
    )

    labels = [f"{row.get('rank')}. {row.get('title')}" for row in concepts]
    if not labels:
        return
    chosen = st.selectbox("Open concept", labels)
    concept = concepts[labels.index(chosen)]
    validation = by_val.get(concept.get("concept_id"), {})
    experiment = by_exp.get(concept.get("concept_id"), {})
    opp = store.opportunity(str(concept.get("opportunity_id")))

    st.markdown(f"**Need this must close:** {concept.get('addresses_need')}")
    st.markdown(f"**Mechanism:** {concept.get('mechanism')}")
    st.markdown(f"**Rejected lever:** {concept.get('rejected_lever')}")
    st.caption(concept.get("why_not_discount") or "")
    st.caption(
        f"Readiness `{validation.get('readiness')}`. {validation.get('notes') or ''} "
        f"n={concept.get('unique_records')} / {concept.get('denominator')} relevant "
        f"({concept.get('pct_relevant')}%). Conversion link: {concept.get('conversion_link_status')}."
    )
    if opp:
        open_evidence(
            split_ids(opp.get("evidence_record_ids")),
            str(opp.get("opportunity_id")),
            theme_ids=str(opp.get("theme_ids") or ""),
        )
        with st.expander("Supporting feedback"):
            quote_cards(store.insights_for_opportunity(opp, limit=6))
    if experiment:
        st.subheader("Experiment brief")
        st.markdown(f"**Hypothesis:** {experiment.get('hypothesis')}")
        st.markdown(f"**Treatment:** {experiment.get('treatment')}")
        st.markdown(f"**Control:** {experiment.get('control')}")
        st.markdown(f"**Primary metric:** {experiment.get('primary_metric')}")
        st.markdown(f"**Denominator:** {experiment.get('primary_denominator')}")
        st.caption(f"Do not optimize: {experiment.get('do_not_optimize')}")
