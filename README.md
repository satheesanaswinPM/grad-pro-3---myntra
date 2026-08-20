# Wishlist-to-purchase research console

Myntra Growth, Part 1: rank why wishlisted items are not bought, from public feedback. The Streamlit app is a product-discovery console. Conversion links are **hypotheses** (the scrape has no purchase outcomes). Discounts are not the recommended lever.

## Deploy on Streamlit Community Cloud

1. Open [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. **Create app** from [`satheesanaswinPM/grad-pro-3---myntra`](https://github.com/satheesanaswinPM/grad-pro-3---myntra).
3. Branch: `master`. **Main file path:** `streamlit_app.py`.
4. In **Advanced settings**, set **Python version to 3.12** (Cloud defaults can break pyarrow).
5. Deploy. No secrets are required for the console; tables are already in the repo.

Local run:

```bash
pip install -r requirements.txt
python -m src.dashboard
```

Or: `streamlit run streamlit_app.py`

Phase 7 (after 5 and 6): `python -m src.ideate` writes non-monetary concepts and 30-day experiment briefs.

Rebuild pipeline tables (optional): `pip install -r requirements-pipeline.txt`, then phases 0–5 in `doc/architecture.md`.
