"""Download public Hugging Face datasets into data/raw/huggingface/ (append-only)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.qualify.config import RAW_DIR, ROOT

HF_DIR = RAW_DIR / "huggingface"

# Prefer user-feedback corpora, then Myntra catalog text (size/fit copy, details).
DATASETS: list[dict[str, Any]] = [
    {
        "id": "saattrupdan/womens-clothing-ecommerce-reviews",
        "why": "User review text about clothing fit, quality, and purchase/return decisions.",
        "max_rows": None,
    },
    {
        "id": "Gssmc/myntra_dataset",
        "why": "Myntra product catalog including size_fit and product_details copy.",
        "max_rows": None,
    },
]


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return str(value)


def export_dataset(dataset_id: str, max_rows: int | None = None) -> Path:
    from datasets import load_dataset

    slug = dataset_id.replace("/", "__")
    out_dir = HF_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    ds = load_dataset(dataset_id)
    written = 0
    for split, table in ds.items():
        out_path = out_dir / f"{split}.jsonl"
        with out_path.open("w", encoding="utf-8") as handle:
            for i, row in enumerate(table):
                if max_rows is not None and written >= max_rows:
                    break
                record = _jsonable(dict(row))
                record["_origin"] = "huggingface"
                record["_hf_dataset"] = dataset_id
                record["_hf_split"] = split
                record["source"] = record.get("source") or "huggingface"
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                written += 1
        print(f"wrote {out_path.relative_to(ROOT)}")
    (out_dir / "SOURCE.md").write_text(
        f"# {dataset_id}\n\nhttps://huggingface.co/datasets/{dataset_id}\n",
        encoding="utf-8",
    )
    return out_dir


def run() -> list[Path]:
    HF_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for spec in DATASETS:
        print(f"Downloading {spec['id']} — {spec['why']}")
        paths.append(export_dataset(spec["id"], spec.get("max_rows")))
    return paths


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
