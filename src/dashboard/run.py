"""Phase 6: write evidence packs, then launch the research console. Never writes to data/raw/."""

from __future__ import annotations

import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.dashboard.evidence import PACKS_DIR, write_all_packs
from src.dashboard.load import REQUIRED, Store
from src.ingest.env import load_dotenv
from src.qualify.config import LOGS_DIR, ROOT

APP = Path(__file__).with_name("app.py")


def _logger() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("phase6")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(LOGS_DIR / "dashboard.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


def export_packs(logger: logging.Logger | None = None) -> int:
    store = Store.build()
    n = write_all_packs(store)
    log = logger or logging.getLogger("phase6")
    log.info(
        "Phase 6 evidence packs=%s dir=%s generated_at=%s",
        n,
        PACKS_DIR.relative_to(ROOT).as_posix(),
        datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )
    return n


def main() -> int:
    load_dotenv()
    logger = _logger()
    missing = [path for path in REQUIRED if not path.exists()]
    if missing:
        names = ", ".join(str(path.relative_to(ROOT)).replace("\\", "/") for path in missing)
        print(f"Missing inputs: {names}. Run python -m src.process, python -m src.analyze, python -m src.synthesize, python -m src.score first.")
        return 1
    try:
        n = export_packs(logger)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to export evidence packs")
        print(f"Could not build the console tables: {exc}")
        return 1
    print(f"Wrote {n} evidence packs to {PACKS_DIR.relative_to(ROOT)}.")
    print("Quotes are in the console; packs are copies, not the only place to read evidence.")
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print("Streamlit is not installed. pip install streamlit")
        print("Evidence packs are ready. Install Streamlit, then re-run python -m src.dashboard")
        return 1
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP),
        "--browser.gatherUsageStats=false",
    ]
    logger.info("Launching console: %s", " ".join(cmd))
    return subprocess.call(cmd, cwd=str(ROOT))
