"""Phase 2 relevance, journey, category, and external-research rules.

These are inclusion/exclusion detectors for building a denominator. They are not
findings about why wishlists fail to convert.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

FLAGS = re.IGNORECASE | re.UNICODE


@dataclass(frozen=True)
class Rule:
    id: str
    family: str
    pattern: str
    description: str


INCLUSION_RULES: tuple[Rule, ...] = (
    Rule(
        "in_wishlist",
        "wishlist",
        r"\bwish[\s-]?lists?\b|\bwishlisted\b|\bsave[ds]?\s+for\s+later\b|\bshortlists?\b|\bbookmarked\b|\badd(?:ed)?\s+to\s+(?:my\s+)?wish",
        "Mentions wishlisting, shortlisting, bookmarking, or save-for-later.",
    ),
    Rule(
        "in_cart_bag",
        "cart",
        r"\badd(?:ed)?\s+to\s+(?:the\s+)?(?:bag|cart)\b|\bin\s+(?:my\s+)?(?:bag|cart)\b|\bshopping\s+bag\b|\bcheckout\b",
        "Mentions bag/cart/checkout as a shopping-intent action (not a product type).",
    ),
    Rule(
        "in_hesitation",
        "hesitation",
        r"\bnot\s+sure\b|\bunsure\b|\bhesitat|\bon\s+the\s+fence\b|\bmaybe\s+later\b|\bstill\s+thinking\b|\bcan't\s+decide\b|\bcannot\s+decide\b|\bdeciding\s+(?:if|whether)\b|\bholding\s+off\b|\bwait(?:ing)?\s+to\s+(?:buy|order)\b",
        "Language of indecision or delayed purchase. Does not assume the reason.",
    ),
    Rule(
        "in_comparison",
        "comparison",
        r"\bcompar(?:e|ed|ing|ison)\b|\bversus\b|\bvs\.?\b|\balternatives?\b|\bother\s+(?:option|brand|app|site|platform)s?\b|\binstead\s+of\b",
        "Compares products, brands, or platforms.",
    ),
    Rule(
        "in_abandonment",
        "abandonment",
        r"\bdid(?:n't| not)\s+(?:buy|purchase|order|checkout)\b|\bnever\s+(?:bought|ordered|purchased)\b|\bcancell?ed\b|\bchanged\s+my\s+mind\b|\bwent\s+with\b|\bleft\s+(?:it|them)\s+in\s+(?:the\s+)?(?:bag|cart)\b|\babandoned\b",
        "Did not complete a purchase, cancelled, or switched away.",
    ),
    Rule(
        "in_return_exchange",
        "abandonment",
        r"\breturn(?:ed|ing|s)?\b|\bexchang(?:e|ed|ing)\b|\bsent\s+(?:it|them)\s+back\b|\btaking\s+it\s+back\b|\bgave\s+it\s+back\b",
        "Return or exchange after trying the product — post-purchase abandonment signal.",
    ),
    Rule(
        "in_fit_uncertainty",
        "uncertainty",
        r"\bfits?\b|\bfitting\b|\bsiz(?:e|es|ing)\b|\btoo\s+(?:small|big|tight|loose)\b|\bruns?\s+(?:small|large|big)\b|\btrue\s+to\s+size\b|\bsize\s+chart\b|\bmeasurements?\b",
        "Fit or size language. Inclusion only — not a claim that sizing is the conversion problem.",
    ),
    Rule(
        "in_quality_uncertainty",
        "uncertainty",
        r"\bqualit(?:y|ies)\b|\bfabric\b|\bmaterial\b|\bsee[- ]through\b|\bcheap[- ]look|\bas\s+(?:pictured|shown|advertised)\b|\blooks?\s+different\b|\bnot\s+as\s+(?:shown|pictured|expected)\b|\btrue\s+to\s+(?:the\s+)?(?:photo|image|picture)s?\b",
        "Quality, fabric, or image-vs-reality language. Inclusion only.",
    ),
    Rule(
        "in_styling_occasion",
        "uncertainty",
        r"\bpair(?:ed|ing)?\s+(?:it|this|them)\s+with\b|\bhow\s+to\s+style\b|\boccasions?\b|\bwedding\b|\boffice\s+wear\b|\bcasual\s+wear\b|\bwhat\s+to\s+wear\b",
        "Styling or occasion uncertainty after liking a product.",
    ),
    Rule(
        "in_social_proof",
        "uncertainty",
        r"\breviews?\s+say\b|\bother\s+reviewers?\b|\bread(?:ing)?\s+(?:the\s+)?reviews?\b|\blooking\s+at\s+reviews?\b|\bstars?\s+reviews?\b",
        "Seeking or citing other shoppers' reviews before or after deciding.",
    ),
)

EXCLUSION_RULES: tuple[Rule, ...] = (
    Rule(
        "ex_catalog_copy",
        "not_user_feedback",
        r"",
        "Drop `myntra_catalog` rows: merchant size/fit copy, not user feedback.",
    ),
    Rule(
        "ex_too_short",
        "weak_signal",
        r"",
        "Drop texts shorter than 20 characters after whitespace collapse.",
    ),
    Rule(
        "ex_app_ops_only",
        "off_journey",
        r"\blogin\b|\botp\b|\bcrash(?:ed|ing)?\b|\bforce\s+close\b|\bnotification\b|\bupdate\s+(?:the\s+)?app\b|\bwon't\s+open\b|\bcannot\s+open\b|\bplease\s+fix\s+(?:the\s+)?app\b",
        "Pure app-operations complaints (login, crash, OTP) with no inclusion match.",
    ),
)

JOURNEY_RULES: tuple[Rule, ...] = (
    Rule(
        "st_discovery",
        "discovery",
        r"\bdiscover(?:ed|y)?\b|\bfound\s+(?:this|it|them)\b|\bsearch(?:ed|ing)?\b|\badvert(?:s|isement)?\b|\bexplore\b",
        "Discovery / finding the product or app.",
    ),
    Rule(
        "st_consideration",
        "consideration",
        r"\bbrows(?:e|ed|ing)\b|\blooking\s+(?:at|for)\b|\bconsider(?:ing|ed)?\b|\bthinking\s+(?:about|of)\b|\bwindow\s+shop",
        "Considering or browsing without a commit.",
    ),
    Rule(
        "st_wishlist",
        "wishlist",
        r"\bwish[\s-]?lists?\b|\bwishlisted\b|\bsave[ds]?\s+for\s+later\b|\bshortlists?\b|\bbookmarked\b",
        "Explicit wishlist / save-for-later.",
    ),
    Rule(
        "st_evaluation",
        "evaluation",
        r"\bfits?\b|\bsiz(?:e|ing)\b|\bqualit(?:y|ies)\b|\bfabric\b|\breviews?\b|\bcompar(?:e|ed|ing)\b|\bnot\s+sure\b|\bas\s+pictured\b|\bdelivery\b",
        "Evaluating attributes, proof, or logistics.",
    ),
    Rule(
        "st_purchase",
        "purchase",
        r"\bbought\b|\bpurchased\b|\bordered\b|\breceived\b|\bwearing\b|\bdelivered\b|\border\s+(?:came|arrived)\b",
        "Purchase or receipt happened.",
    ),
    Rule(
        "st_abandonment",
        "abandonment",
        r"\bdid(?:n't| not)\s+(?:buy|purchase|order)\b|\breturn(?:ed|ing)\b|\bexchang(?:e|ed)\b|\bcancell?ed\b|\bchanged\s+my\s+mind\b|\bsent\s+(?:it|them)\s+back\b",
        "Did not keep or did not complete the buy.",
    ),
)

EXTERNAL_RULES: tuple[tuple[str, str, str], ...] = (
    ("google", r"\bgoogle[d]?\b|\bgoogling\b", "Google search"),
    ("reddit", r"\breddit\b", "Reddit"),
    ("youtube", r"\byoutube\b|\byoutu\.be\b", "YouTube"),
    ("instagram", r"\binstagram\b|\binsta\b", "Instagram"),
    ("friends_family", r"\bfriends?\b|\bfamily\b|\bsister\b|\bbrother\b|\bmom\b|\bmum\b|\bmother\b|\bhusband\b|\bwife\b|\bcousin\b", "Friends or family"),
    ("influencer", r"\binfluencers?\b|\bblogger\b|\byoutubers?\b", "Influencer / blogger"),
    ("other_apps", r"\bamazon\b|\bflipkart\b|\bajio\b|\bnykaa\b|\bmeesho\b|\bshein\b|\bzara\b|\bh&m\b|\basos\b", "Other shopping apps or brands"),
)

STAGE_ORDER = (
    "abandonment",
    "purchase",
    "evaluation",
    "wishlist",
    "consideration",
    "discovery",
)

MIN_TEXT_CHARS = 20
CATALOG_SOURCES = frozenset({"myntra_catalog"})
APP_ID_LIKE = re.compile(r"^(com\.|\d{6,}$)")

COMPILED_INCLUSION = tuple((r, re.compile(r.pattern, FLAGS)) for r in INCLUSION_RULES if r.pattern)
COMPILED_APP_OPS = re.compile(next(r.pattern for r in EXCLUSION_RULES if r.id == "ex_app_ops_only"), FLAGS)
COMPILED_JOURNEY = tuple((r, re.compile(r.pattern, FLAGS)) for r in JOURNEY_RULES)
COMPILED_EXTERNAL = tuple((name, re.compile(pat, FLAGS), label) for name, pat, label in EXTERNAL_RULES)

CATEGORY_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Ethnic wear", ("kurta", "kurti", "saree", "sari", "lehenga", "salwar", "anarkali", "ethnic")),
    ("Footwear", ("shoe", "sneaker", "heel", "sandal", "footwear", "boot", "flip flop", "slipper")),
    ("Beauty", ("lipstick", "makeup", "serum", "skincare", "beauty", "foundation", "kajal")),
    ("Sportswear", ("sportswear", "activewear", "running shoe", "gym wear", "yoga")),
    ("Accessories", ("jewellery", "jewelry", "watch", "sunglasses", "wallet", "belt", "earring", "necklace")),
    ("Western wear", ("jeans", "jeggings", "blouse", "sweater", "hoodie", "blazer", "trousers")),
    ("Clothing", ("dress", "top", "t-shirt", "tshirt", "shirt", "jacket", "coat", "skirt", "shorts", "intimate", "bra", "legging")),
)
