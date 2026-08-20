"""Problem statements and research asks. No monetary incentives. No causal claims."""

from __future__ import annotations

STATEMENTS: dict[str, dict[str, str]] = {
    "fit_uncertainty": {
        "problem": "Shoppers still cannot tell whether an item will fit before they commit.",
        "need": "A reliable way to judge fit and size for their body before buying.",
        "barrier": "fit",
        "statement": "If fit uncertainty is a purchase-delay mechanism, people who cannot map size information to their body will keep items wishlisted rather than buying within 30 days.",
        "ask": "Ask recent wishlisters whether they delayed because they could not tell if it would fit, and what evidence would have let them decide.",
        "signal": "Share of still-intending wishlisters who name fit or size as the reason they have not bought, with verbatim evidence.",
    },
    "image_vs_reality": {
        "problem": "Product images and on-body proof do not settle whether the item matches what the shopper expects.",
        "need": "Trustworthy visual proof of drape, color, and on-body look.",
        "barrier": "proof",
        "statement": "If missing visual proof blocks conversion, wishlisters who cannot tell whether the item matches the photos will delay or abandon the buy.",
        "ask": "Ask what photos, video, or reviews they still needed after liking the product, and whether that gap is why it stayed wishlisted.",
        "signal": "Share of wishlisters who say image-vs-reality uncertainty is why they have not purchased, independent of price.",
    },
    "quality_uncertainty": {
        "problem": "Shoppers cannot tell whether quality is good enough to justify the buy.",
        "need": "Concrete quality and construction evidence after they already like the item.",
        "barrier": "quality",
        "statement": "If quality uncertainty delays purchase, people who like an item but cannot judge make and durability will not convert within 30 days.",
        "ask": "Ask what quality evidence they looked for after wishlisting, and what was still missing on the product page or reviews.",
        "signal": "Share of wishlisters who name quality or construction doubt as the open question, with examples of missing proof.",
    },
    "returns_exchange": {
        "problem": "Return and exchange friction shows up after try-on, and may also shape hesitation before the first buy.",
        "need": "Confidence that a wrong-size or wrong-look outcome is recoverable without pain.",
        "barrier": "returns",
        "statement": "If return friction is part of pre-purchase hesitation, shoppers who expect sending items back to be hard will delay the first order from a wishlist.",
        "ask": "Separate post-purchase return stories from pre-purchase fear of returns. Ask wishlisters whether return policy or past return pain is why they have not bought yet.",
        "signal": "Among people with wishlisted items not bought in 30 days, share who cite returns/exchange risk as a reason they waited.",
    },
    "occasion_uncertainty": {
        "problem": "People like an item but are unsure it is right for the occasion they have in mind.",
        "need": "Clarity on whether the piece works for their event, dress code, or setting.",
        "barrier": "occasion",
        "statement": "If occasion fit is unresolved, liked items stay wishlisted until the shopper knows it is appropriate for the event.",
        "ask": "Ask which occasion they had in mind and what would confirm the item is right for it.",
        "signal": "Share of wishlisters with an occasion in mind who say they have not bought because appropriateness is still unclear.",
    },
    "styling_uncertainty": {
        "problem": "People like the item but do not know how to wear or pair it.",
        "need": "Outfit context: what to pair it with and how it sits in a wardrobe.",
        "barrier": "styling",
        "statement": "If styling uncertainty delays purchase, shoppers who cannot picture how to wear the item will not convert from wishlist within 30 days.",
        "ask": "Ask whether they delayed because they could not see how to style it, and what pairing examples would help.",
        "signal": "Share of wishlisters who name 'how to wear it' as an open question, not price.",
    },
    "comparison_loop": {
        "problem": "Shoppers keep comparing options instead of deciding on the wishlisted item.",
        "need": "A clear way to compare the few attributes that actually change the decision.",
        "barrier": "comparison",
        "statement": "If comparison loops delay conversion, people who are evaluating alternatives will leave the wishlisted item unbought until the comparison is resolved.",
        "ask": "Ask what they compared, on which attributes, and what was still missing to pick a winner.",
        "signal": "Share of unbought wishlisters who are actively comparing alternatives, and the attributes they say are unresolved.",
    },
    "external_research": {
        "problem": "People leave the app to get proof from friends, other sites, or social before they will buy.",
        "need": "The same proof they currently hunt for off-platform, in context on the product.",
        "barrier": "proof",
        "statement": "If off-platform research is a conversion gate, wishlisters who go to friends, Google, Reddit, or other apps will not buy until that research is done.",
        "ask": "Ask where they went after wishlisting, what they looked for, and whether the app already had that information.",
        "signal": "Share of wishlisters who did off-platform research before buying or abandoning, and the question they were trying to answer.",
    },
    "price_watch": {
        "problem": "Some shoppers are waiting on price or value, which can look like a discount brief but may be missing value proof.",
        "need": "Enough value and quality information to decide whether the current price is acceptable, without assuming a coupon is required.",
        "barrier": "value",
        "statement": "If price-watch language is a proxy for unresolved value, the open question is whether the item is worth it, not whether a markdown exists.",
        "ask": "Ask whether they are waiting for a sale or still cannot tell if the item is worth the current price. Do not treat a sale request as the research conclusion.",
        "signal": "Split of waiters into (a) would buy at current price if quality/fit were clear vs (b) will only buy below a number. Coupons are not the recommended lever.",
    },
    "uncertain": {
        "problem": "Shoppers like the item enough to save it but still cannot decide whether to buy.",
        "need": "The missing fact or proof that would turn indecision into a yes or a no.",
        "barrier": "uncertain",
        "statement": "If unresolved intent is a conversion delay, people who say they are unsure after wishlisting will not buy within 30 days until that uncertainty is closed.",
        "ask": "Ask what they are unsure about after liking the item, and whether that is why it is still unbought.",
        "signal": "Share of still-intending wishlisters who describe an open question rather than a firm later plan.",
    },
    "bookmark": {
        "problem": "The wishlist is being used as a bookmark, which may never become a purchase.",
        "need": "A reason and the missing information to convert a saved item into a buy, or a clear later plan.",
        "barrier": "bookmark",
        "statement": "If bookmarking is a parking lot rather than a purchase plan, save-for-later items will have a lower 30-day conversion rate than items saved with a stated buy intent.",
        "ask": "Ask whether they saved the item to buy it, to remember it, or to compare later, and what would make them buy.",
        "signal": "Share of wishlisters whose stated job for the wishlist is reminder or inspiration vs intended purchase, among items unbought at 30 days.",
    },
}


def _fallback(extractor: str, label: str) -> dict[str, str]:
    readable = label.replace("_", " ").replace("other:", "")
    if extractor == "need":
        problem = f"After liking the product, shoppers still have an unanswered question: {readable}."
        need = f"An answer to '{readable}' before they will commit."
        barrier = readable
    elif extractor == "behavior":
        problem = f"Shoppers show {readable} behavior while deciding, which may delay the buy."
        need = "The information that behavior is trying to obtain."
        barrier = readable
    elif extractor == "intent":
        problem = f"Wishlist intent labeled {readable} is unresolved, so the buy may be deferred."
        need = "Whatever is still missing for this intent to become a purchase."
        barrier = readable
    else:
        problem = f"A recurring barrier labeled {readable} appears in relevant feedback."
        need = f"Resolution of the {readable} issue before purchase."
        barrier = label
    return {
        "problem": problem,
        "need": need,
        "barrier": barrier,
        "statement": (
            f"If {readable} is a purchase-delay mechanism, people who mention it in relevant feedback "
            "will be less likely to buy a wishlisted item within 30 days. This conversion link is unproven."
        ),
        "ask": f"Ask wishlisters whether {readable} is why they have not bought yet, and what would close that gap. Do not offer discounts as the prompt.",
        "signal": f"Share of still-intending wishlisters who name {readable} as the reason the item is unbought, with verbatim evidence.",
    }


def copy_for(key: str, extractor: str = "", label: str = "") -> dict[str, str]:
    if key in STATEMENTS:
        return dict(STATEMENTS[key])
    slug = key.split(":")[-1] if ":" in key else key
    if slug in STATEMENTS:
        return dict(STATEMENTS[slug])
    return _fallback(extractor, label or slug)
