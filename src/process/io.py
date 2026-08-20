from __future__ import annotations

from pathlib import Path
from typing import Any


def write_parquet(rows: list[dict[str, Any]], path: Path) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Phase 2 needs pyarrow. pip install pyarrow") from exc
    if not rows:
        raise RuntimeError(f"Refusing to write empty parquet: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path, compression="zstd")
