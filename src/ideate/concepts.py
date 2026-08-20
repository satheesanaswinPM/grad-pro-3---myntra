"""Non-monetary solution concepts for ranked opportunities. Not a shipped product."""

from __future__ import annotations

from typing import Any

from src.ideate.schema import TOP_OPPORTUNITIES
from src.score.statements import copy_for

# Each entry is a concept that closes the named need. None of these are price cuts.
CATALOG: dict[str, tuple[dict[str, str], ...]] = {
    "returns_exchange": (
        {
            "title": "Recoverability preview before the first buy",
            "mechanism": (
                "On the wishlisted PDP and wishlist row, show the actual return and exchange path for this SKU: "
                "how size/color swaps work, how long reverse pickup takes, and what the shopper keeps "
                "if the first try-on fails. This is policy clarity, not a listed-price change."
            ),
            "rejected_lever": "Return window extensions bundled with a discount code",
            "why_not_discount": (
                "The need is confidence that a wrong-size or wrong-look outcome is recoverable. "
                "A markdown does not answer whether sending it back will be painful."
            ),
            "risks": (
                "Most return language in the scrape is post-purchase. Treating this as a proven "
                "pre-purchase conversion lever is a hypothesis until interviews split those stories."
            ),
        },
    ),
    "image_vs_reality": (
        {
            "title": "On-body proof pack",
            "mechanism": (
                "Surface buyer photos, short fabric-drape video, and color-in-daylight stills as visual proof "
                "next to the studio images, including on the wishlist card so the shopper can resolve "
                "'does this match the picture?' without leaving."
            ),
            "rejected_lever": "Price drop to compensate for photo mismatch",
            "why_not_discount": (
                "The need is trustworthy visual proof of drape, color, and on-body look. "
                "Paying people to ignore that gap leaves the uncertainty in place."
            ),
            "risks": "UGC can be unrepresentative. Label similar-body and similar-lighting shots.",
        },
    ),
    "price_watch": (
        {
            "title": "Worth-it proof at the current price",
            "mechanism": (
                "On wishlist and PDP, show construction, fabric weight, comparable quality cues, and "
                "what is included so the shopper can judge value at the listed price. "
                "Split waiters into 'would buy if quality/fit were clear' vs 'will only buy below a number'."
            ),
            "rejected_lever": "Coupons, cashback, markdowns, or wait-for-sale prompts as the primary treatment",
            "why_not_discount": (
                "Price-watch language can be a proxy for unresolved value. The open question is whether "
                "the item is worth the current price, not whether a markdown exists."
            ),
            "risks": "If interviews show a hard reservation price, do not relabel that as a quality gap.",
        },
    ),
    "comparison_loop": (
        {
            "title": "Decision attributes, not more options",
            "mechanism": (
                "Let a shopper pin 2–3 wishlisted alternatives and run a comparison on the attributes that "
                "actually show up in evidence: fit notes, fabric, on-body proof, exchange ease. Hide extra catalog "
                "noise. Do not compete on strikethrough price."
            ),
            "rejected_lever": "Sitewide sale to force a pick",
            "why_not_discount": (
                "The need is a way to compare the few attributes that change the decision. "
                "A coupon does not name a winner on fit or look."
            ),
            "risks": "A comparison UI can increase browsing time if it adds SKUs instead of closing attributes.",
        },
    ),
    "fit_uncertainty": (
        {
            "title": "Body-matched size evidence",
            "mechanism": (
                "On the wishlisted item, show fit measurements against a body-similar review set, "
                "garment-flat measurements, and how the piece sat on someone with the shopper's size "
                "inputs, rather than a generic chart."
            ),
            "rejected_lever": "Buy-two-sizes-and-return, subsidized by a coupon",
            "why_not_discount": (
                "The need is a reliable way to judge fit before buying. Ordering extra sizes is a "
                "workaround that still leaves fit unknown at wishlist time."
            ),
            "risks": "Fit evidence in this scrape is almost all product_reviews (single source). Corroborate in interviews.",
        },
    ),
    "intent:uncertain": (
        {
            "title": "Close the open question on the saved item",
            "mechanism": (
                "For uncertain-intent wishlists, prompt the missing fact (fit, look, occasion, quality) "
                "and jump to that proof on the same item. The job is to turn indecision into a yes or a no."
            ),
            "rejected_lever": "Limited-time coupon to manufacture urgency",
            "why_not_discount": (
                "The need is the missing fact that would decide the buy. Urgency pricing does not "
                "answer the open question."
            ),
            "risks": "If the true job of the save is bookmarking, a closer will look like nagging.",
        },
    ),
    "uncertain": (
        {
            "title": "Close the open question on the saved item",
            "mechanism": (
                "For uncertain-intent wishlists, prompt the missing fact (fit, look, occasion, quality) "
                "and jump to that proof on the same item."
            ),
            "rejected_lever": "Limited-time coupon to manufacture urgency",
            "why_not_discount": "Urgency pricing does not answer the open question after 'I like this.'",
            "risks": "Bookmark intent can be misread as hesitation.",
        },
    ),
    "styling_uncertainty": (
        {
            "title": "Wear-it-with context on the wishlist",
            "mechanism": (
                "Show 2–3 pairing examples and occasion tags on the wishlisted PDP so styling is visible "
                "in a wardrobe, not as an isolated studio shot."
            ),
            "rejected_lever": "Bundle discount on suggested pairs",
            "why_not_discount": (
                "The need is outfit context. A cheaper pair still leaves 'how do I wear this' unanswered "
                "if the pairing logic is missing."
            ),
            "risks": "Generic lookbooks that ignore the shopper's occasion will not close the gap.",
        },
    ),
    "barrier:availability": (
        {
            "title": "Size-intent restock, not a substitute SKU",
            "mechanism": (
                "When the wishlisted size is gone, keep the exact size/color intent and notify on restock "
                "with the same proof pack so availability of the chosen item is recovered. Do not push a "
                "different product as the default recovery."
            ),
            "rejected_lever": "Markdown on a nearby size or color to clear the save",
            "why_not_discount": "The barrier is availability of the chosen item, not willingness to pay.",
            "risks": "Restock promises that miss the window destroy trust.",
        },
    ),
    "barrier:delivery": (
        {
            "title": "Delivery date on the wishlisted SKU",
            "mechanism": (
                "Show a realistic delivery date for the saved size/pincode on the wishlist row so "
                "timing uncertainty is visible before checkout."
            ),
            "rejected_lever": "Free delivery coupon",
            "why_not_discount": (
                "This theme is mostly app-store ops language. If it is general UX, a coupon will not "
                "move 30-day wishlist conversion."
            ),
            "risks": "Scoring already treats delivery as possible general UX. Confirm it sits on wishlist → buy before a large test.",
        },
    ),
    "external_research": (
        {
            "title": "Bring off-platform proof onto the product",
            "mechanism": (
                "Put the proof questions people currently take to friends, Google, Reddit, or Instagram "
                "(real photos, fabric feel, 'is it worth it') into Q&A and UGC on the same PDP/wishlist item."
            ),
            "rejected_lever": "Cashback if they return from another app",
            "why_not_discount": (
                "The need is the proof they hunt for off-platform. Paying them to skip research leaves "
                "the unanswered question in place."
            ),
            "risks": "Some external research is social permission, which in-app UGC may not replace.",
        },
    ),
    "barrier:fabric": (
        {
            "title": "Material evidence in hand terms",
            "mechanism": (
                "Show fabric composition, weight/handfeel language from reviews, and close-up texture "
                "on the wishlisted item so 'what will this feel like' is answered before buy."
            ),
            "rejected_lever": "Lower price to offset fabric doubt",
            "why_not_discount": "The need is material information, not a cheaper unknown fabric.",
            "risks": "Single-source product_reviews. Corroborate with on-body video where possible.",
        },
    ),
    "quality_uncertainty": (
        {
            "title": "Construction proof after 'I like this'",
            "mechanism": (
                "Expose stitching, lining, durability mentions, and return-for-quality rates as product "
                "evidence, not as a star-average."
            ),
            "rejected_lever": "Markdown because quality is uncertain",
            "why_not_discount": "Cheaper does not prove make and durability.",
            "risks": "Smaller n than fit/returns. Do not over-claim category differences.",
        },
    ),
    "intent:bookmark": (
        {
            "title": "Separate parking-lot saves from buy-later saves",
            "mechanism": (
                "Let the shopper tag a save as remember / compare / buy. Only the buy-later set gets "
                "decision-closer proof. Do not nag inspiration saves."
            ),
            "rejected_lever": "Expiry discounts on old wishlist rows",
            "why_not_discount": "Bookmarking may never be a purchase job. A coupon cannot invent intent.",
            "risks": "n<30 in this scrape. Research-first; do not ship a large experiment yet.",
        },
    ),
    "occasion_uncertainty": (
        {
            "title": "Occasion fit check",
            "mechanism": (
                "Ask the occasion on the wishlist item and show dress-code, coverage, and similar-event "
                "photos instead of a generic trend rail."
            ),
            "rejected_lever": "Occasion sale campaign",
            "why_not_discount": "The need is whether the piece is appropriate for the event.",
            "risks": "Occasion language can be sparse. Keep n_small cuts labeled.",
        },
    ),
}


def _slug(opportunity_id: str) -> str:
    return str(opportunity_id or "").removeprefix("opp:")


def _fallback(opportunity: dict[str, Any]) -> dict[str, str]:
    text = copy_for(
        str(opportunity.get("label") or ""),
        str(opportunity.get("extractor") or ""),
        str(opportunity.get("label") or ""),
    )
    need = text["need"]
    barrier = text["barrier"]
    return {
        "title": f"Answer '{need}' on the saved item",
        "mechanism": (
            f"Put the missing information for '{need}' on the wishlist row and PDP for this item. "
            f"Target barrier `{barrier}`. Do not change the listed price."
        ),
        "rejected_lever": "Discounts, coupons, cashback, or markdowns",
        "why_not_discount": (
            "The brief forbids monetary incentives as the primary solution. The job is to close "
            "the information gap named in the user need."
        ),
        "risks": "Generic closer if the catalog has no specific mechanism. Prefer a named proof type.",
    }


def _templates_for(opportunity_id: str) -> tuple[dict[str, str], ...]:
    slug = _slug(opportunity_id)
    if slug in CATALOG:
        return CATALOG[slug]
    short = slug.split(":")[-1]
    if short in CATALOG:
        return CATALOG[short]
    return (_fallback({"label": short, "extractor": ""}),)


def build_concepts(opportunities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen = [row for row in opportunities if row.get("status") == "observed_evidence"][:TOP_OPPORTUNITIES]
    if len(chosen) < TOP_OPPORTUNITIES:
        seen = {row["opportunity_id"] for row in chosen}
        chosen.extend([row for row in opportunities if row["opportunity_id"] not in seen][: TOP_OPPORTUNITIES - len(chosen)])
    rows: list[dict[str, Any]] = []
    for opportunity in chosen:
        opp_id = str(opportunity["opportunity_id"])
        text = copy_for(
            str(opportunity.get("label") or ""),
            str(opportunity.get("extractor") or ""),
            str(opportunity.get("label") or ""),
        )
        for index, template in enumerate(_templates_for(opp_id), start=1):
            stem = _slug(opp_id).replace(":", "-")
            rows.append(
                {
                    "concept_id": f"concept:{stem}:{index}",
                    "opportunity_id": opp_id,
                    "rank": int(opportunity.get("rank") or 0),
                    "title": template["title"],
                    "mechanism": template["mechanism"],
                    "addresses_need": text["need"],
                    "addresses_barrier": text["barrier"],
                    "rejected_lever": template["rejected_lever"],
                    "why_not_discount": template["why_not_discount"],
                    "risks": template["risks"],
                    "status": "concept",
                    "unique_records": int(opportunity.get("unique_records") or 0),
                    "pct_relevant": float(opportunity.get("pct_relevant") or 0),
                    "denominator": int(opportunity.get("denominator") or 0),
                    "denominator_label": str(opportunity.get("denominator_label") or "relevant"),
                    "conversion_link_status": str(opportunity.get("conversion_link_status") or "hypothesis"),
                }
            )
    return rows
