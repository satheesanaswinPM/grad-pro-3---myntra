from src.ingest.adapters.app_store import AppStoreAdapter
from src.ingest.adapters.generic import GenericAdapter
from src.ingest.adapters.google_play import GooglePlayAdapter
from src.ingest.adapters.myntra_catalog import MyntraCatalogAdapter
from src.ingest.adapters.product_qa import ProductQAAdapter
from src.ingest.adapters.product_reviews import ClothingReviewsAdapter, MyntraPdpReviewsAdapter
from src.ingest.adapters.reddit import RedditAdapter
from src.ingest.adapters.social import SocialAdapter
from src.ingest.adapters.youtube import YouTubeAdapter

# First match wins. Keep specific sources ahead of GenericAdapter.
ADAPTERS = [
    AppStoreAdapter(),
    GooglePlayAdapter(),
    RedditAdapter(),
    YouTubeAdapter(),
    SocialAdapter(),
    ProductQAAdapter(),
    ClothingReviewsAdapter(),
    MyntraPdpReviewsAdapter(),
    MyntraCatalogAdapter(),
    GenericAdapter(),
]
