"""Phase 0 entry point: inspect data/raw/ and write reports/ only."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from src.qualify.config import LOGS_DIR, RAW_DIR, REPORTS_DIR, ROOT
from src.qualify.loaders import iter_loaded, iter_raw_files
from src.qualify.metrics import attach_file_meta, inspect_records
from src.qualify.report import write_quality_report, write_schema_catalog, write_source_coverage
from src.qualify.schema import field_stats


def _setup_log(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("phase0")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


def run(raw_dir: Path | None = None) -> dict:
    raw = raw_dir or RAW_DIR
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    logger = _setup_log(LOGS_DIR / "phase0_inspect.log")
    logger.info("Phase 0 inspect starting. raw=%s", raw)

    raw_files = iter_raw_files(raw)
    file_infos = []
    for path, fmt, records, error in iter_loaded(raw):
        relative = path.relative_to(raw).as_posix()
        fields = field_stats(records)
        info = attach_file_meta(
            relative=relative,
            fmt=fmt,
            size=path.stat().st_size,
            records=records,
            fields=fields,
            error=error,
        )
        file_infos.append(info)
        if error:
            logger.warning("Failed to parse %s: %s", relative, error)
        else:
            logger.info("Loaded %s records from %s (%s)", len(records), relative, fmt)

    summary = inspect_records(file_infos)
    write_schema_catalog(REPORTS_DIR / "schema_catalog.json", file_infos, summary)
    write_source_coverage(REPORTS_DIR / "source_coverage.csv", summary)
    write_quality_report(
        REPORTS_DIR / "data_quality.md",
        summary,
        file_infos,
        raw,
        raw_file_count=len(raw_files),
    )
    logger.info(
        "Phase 0 done. records=%s files=%s reports=%s",
        summary["record_count"],
        summary["file_count"],
        REPORTS_DIR,
    )
    for info in file_infos:
        info.pop("records", None)
    return {"summary": summary, "files": file_infos, "root": str(ROOT)}


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
