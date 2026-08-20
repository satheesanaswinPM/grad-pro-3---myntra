"""Phase 3 sanity checks. No network unless --llm is passed."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

from src.analyze.cache import connect, get as cache_get, put as cache_put
from src.analyze.llm import parse_json_content
from src.analyze.local import extract_text
from src.analyze.run import alias_batch, flatten_rows, payloads_from_parsed, records_by_id
from src.analyze.validate import clamp_confidence, locate_span, sanitize_payload


def _assert(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def test_span_must_exist() -> None:
    text = "I added this to my wishlist but it runs small."
    dropped = sanitize_payload(
        text,
        {"intents": [{"label": "bookmark", "evidence_span": "not actually in the text", "confidence": 0.9}]},
        "t",
        "h",
    )
    _assert(dropped["intent"] == [], "invented span must be dropped")
    kept = sanitize_payload(
        text,
        {"intents": [{"label": "bookmark", "evidence_span": "wishlist", "status": "observed_evidence", "confidence": 1.4}]},
        "t",
        "h",
    )
    _assert(len(kept["intent"]) == 1, "verbatim span must be kept")
    _assert(kept["intent"][0]["evidence_span"].lower() in text.lower(), "kept span must occur in text")
    _assert(kept["intent"][0]["confidence"] <= 0.99, "confidence must be clamped")


def test_local_spans_are_verbatim() -> None:
    text = "I bought this dress and it was too small so I returned it. My sister compared it on Amazon."
    payload = extract_text(text, "hash1")
    n = 0
    for extractor, items in payload.items():
        for item in items:
            n += 1
            _assert(item["evidence_span"], f"{extractor} missing span")
            _assert(locate_span(text, item["evidence_span"]), f"{extractor} span not in text: {item['evidence_span']!r}")
            _assert(item["status"] in {"observed_evidence", "hypothesis"}, "bad status")
    _assert(n > 0, "local extractor returned nothing")
    _assert(payload["intent"] or payload["barrier"], "expected purchase/fit/return signals")


def test_cache_roundtrip() -> None:
    payload = extract_text("I wishlisted this for a wedding.", "h2")
    with tempfile.TemporaryDirectory() as tmp:
        conn = connect(Path(tmp) / "llm.sqlite")
        try:
            _assert(cache_get(conn, "h2", "extract_v1") is None, "empty cache should miss")
            cache_put(conn, "h2", "extract_v1", payload)
            again = cache_get(conn, "h2", "extract_v1")
            _assert(again == payload, "cache roundtrip mismatch")
            _assert(cache_get(conn, "h2", "span_extract_v2") is None, "other prompt version must miss")
        finally:
            conn.close()


def test_no_cross_record_bleed() -> None:
    parsed = {
        "records": [
            {"record_id": "a", "intents": [{"label": "bookmark", "evidence_span": "wishlist"}]},
            {"record_id": "b", "barriers": [{"label": "fit", "evidence_span": "too small"}]},
        ]
    }
    batch = [{"record_id": "a"}, {"record_id": "b"}, {"record_id": "c"}]
    by_id = records_by_id(parsed, batch)
    _assert(set(by_id) == {"a", "b"}, "missing ids must not inherit the whole payload")
    _assert("intents" in by_id["a"] and "barriers" not in by_id["a"], "record a mixed with b")
    # Whole-object fallback used to assign every row the batch JSON.
    _assert(records_by_id(parsed, [{"record_id": "z"}]).get("z") is None, "unmatched id must stay unmatched")


def test_json_fence_and_list() -> None:
    obj = parse_json_content("```json\n{\"records\": []}\n```")
    _assert(obj == {"records": []}, "fenced JSON failed")
    wrapped = parse_json_content('[{"record_id": "1"}]')
    _assert(wrapped == {"records": [{"record_id": "1"}]}, "top-level list should wrap")


def test_flatten_and_confidence() -> None:
    _assert(clamp_confidence("nope") == 0.5, "bad confidence should default")
    payload = sanitize_payload(
        "I compared this with another dress.",
        {"behaviors": [{"label": "comparison", "evidence_span": "compared this", "confidence": 0.8, "status": "observed_evidence"}]},
        "extract_v1",
        "h3",
    )
    rows = flatten_rows("rec1", "h3", payload)
    _assert(len(rows) == 1, "flatten should emit one behavior")
    _assert(rows[0]["extraction_id"].startswith("behavior:"), "id prefix")
    _assert(rows[0]["record_id"] == "rec1", "record_id lost")


def test_groq_key_uses_groq_endpoint() -> None:
    from src.analyze.llm import llm_config

    old = {k: os.environ.get(k) for k in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL")}
    try:
        os.environ["OPENAI_API_KEY"] = "gsk_dummy_not_a_real_key"
        os.environ["OPENAI_BASE_URL"] = ""
        os.environ["LLM_MODEL"] = "gpt-4o-mini"
        cfg = llm_config()
        _assert(cfg is not None, "dummy groq key should enable llm")
        _assert("api.groq.com" in cfg["base_url"], "gsk_ key must not hit api.openai.com")
        _assert(cfg["model"] == "openai/gpt-oss-20b", "gsk_ key should remap gpt-4o-mini to a Groq model")
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_wait_seconds_parses_groq_retry() -> None:
    from src.analyze.llm import wait_seconds

    delay = wait_seconds("Please try again in 11.3925s. Need more tokens?", 0)
    _assert(12.0 <= delay <= 13.0, f"expected ~12.4s, got {delay}")
    daily = wait_seconds("Please try again in 15m59.904s. Need more tokens?", 0)
    _assert(950 <= daily <= 970, f"expected ~960s for 15m59s, got {daily}")
    fallback = wait_seconds("", 0)
    _assert(fallback >= 20.0, f"unparsed 429 should wait at least 20s, got {fallback}")


def test_alias_ids_map_back() -> None:
    batch = [
        {"record_id": "google_play:aaa", "text": "I wishlisted this.", "content_hash": "hA"},
        {"record_id": "google_play:bbb", "text": "It runs small.", "content_hash": "hB"},
    ]
    items, lookup = alias_batch(batch)
    _assert([item["record_id"] for item in items] == ["r1", "r2"], "aliases should be r1/r2")
    parsed = {
        "records": [
            {"record_id": "r1", "intents": [{"label": "bookmark", "evidence_span": "wishlisted"}]},
            {"record_id": "r2", "barriers": [{"label": "fit", "evidence_span": "runs small"}]},
        ]
    }
    mapped = payloads_from_parsed(parsed, lookup, "extract_v1")
    _assert(set(mapped) == {"hA", "hB"}, "alias map lost a record")
    _assert(mapped["hA"]["intent"][0]["label"] == "bookmark", "r1 intents not applied")
    _assert(mapped["hB"]["barrier"][0]["label"] == "fit", "r2 barriers not applied")


def test_llm_smoke() -> None:
    from src.analyze.llm import chat_json, llm_config
    from src.analyze.prompts import request_body
    from src.ingest.env import load_dotenv

    load_dotenv()
    cfg = llm_config()
    _assert(cfg is not None, "OPENAI_API_KEY is not set")
    text = "I added this kurta to my wishlist. Reviews say it runs small and I am not sure it will fit."
    parsed = chat_json(request_body([{"record_id": "smoke1", "text": text}], cfg["model"]))
    by_id = records_by_id(parsed, [{"record_id": "smoke1"}])
    raw = by_id.get("smoke1") or (parsed if isinstance(parsed, dict) and parsed.get("intents") is not None else None)
    _assert(isinstance(raw, dict), f"smoke response had no smoke1 record; keys={list(parsed)[:8] if isinstance(parsed, dict) else type(parsed)}")
    clean = sanitize_payload(text, raw, "extract_v1", "smokehash")
    n = sum(len(v) for v in clean.values())
    for items in clean.values():
        for item in items:
            _assert(locate_span(text, item["evidence_span"]), "LLM span not in smoke text")
    print("llm_smoke_ok extractions", n, "labels", {k: [i["label"] for i in v] for k, v in clean.items() if v})


def main() -> int:
    tests = [
        test_span_must_exist,
        test_local_spans_are_verbatim,
        test_cache_roundtrip,
        test_no_cross_record_bleed,
        test_json_fence_and_list,
        test_flatten_and_confidence,
        test_groq_key_uses_groq_endpoint,
        test_alias_ids_map_back,
        test_wait_seconds_parses_groq_retry,
    ]
    if os.environ.get("PHASE3_LLM_SMOKE", "").strip() in {"1", "true", "yes"} or "--llm" in sys.argv:
        tests.append(test_llm_smoke)
    failed = 0
    for fn in tests:
        try:
            fn()
            print("ok", fn.__name__)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print("FAIL", fn.__name__, type(exc).__name__, str(exc)[:400])
    print("selfcheck_failed", failed)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
