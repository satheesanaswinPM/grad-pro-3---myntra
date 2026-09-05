# Representative product photos

**Source:** ["Fashion Product Images (Small)"](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small)
by Param Aggarwal on Kaggle (MIT license), scraped from Myntra.com — 44,000 products with images.
Fetched via the Hugging Face mirror [`ashraq/fashion-product-images-small`](https://huggingface.co/datasets/ashraq/fashion-product-images-small).

**Why this exists:** the MVP's actual product catalog (`data/raw/huggingface/Gssmc__myntra_dataset/`)
has no image field at all — verified directly against its schema and the live Hugging Face dataset
page (Modalities: Tabular, Text only; no image column, no alternate config, no separate image
manifest in the repo). Rather than leave product cards with no photo, or fabricate one, each of our
451 catalog items is paired with a **real photo of a different, comparable Myntra product** —
matched by category (`articleType`) and color (`baseColour`), not the exact item that was originally
scraped for `data/raw/huggingface/Gssmc__myntra_dataset/`.

**This is a representative photo, not proof of what that specific scraped item actually looked like.**
The UI must always label it as such (see `src/mvp/app.py`) — this is the same honesty discipline the
project already applies to the color-swatch fallback and to every AI-extracted claim elsewhere in the
repo (`observed_evidence` vs `hypothesis`).

**Build/refresh:** matching is deterministic (hashed on our catalog item's id, so re-running produces
the same assignment). Of 451 items: 399 matched on category **and** color exactly; 52 matched on
category only (color fell back) because their `dominant_color` value (e.g. a rare shade) had no
counterpart in the source dataset's color vocabulary; 0 were left unmatched. See `manifest.json` for
the per-item mapping and match type. The one-off extraction script is not part of the committed
pipeline (it was run once, ad hoc, against a local copy of the two source parquet shards, which are
not committed here — only the ~3.4 MB of resulting images are).
