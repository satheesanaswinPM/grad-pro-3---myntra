"""Groq (OpenAI-compatible chat completions API) client. Keys come from the environment only.

Groq only, by design -- no OpenAI endpoint, no provider auto-detection. Any OpenAI-compatible
Groq-hosted model works by setting LLM_MODEL; the client itself does not depend on which one.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any

RETRY_STATUSES = {429, 500, 502, 503}
FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I)
SECRETISH = re.compile(r"(?:gsk_|sk-|hf_|apify_api_)[A-Za-z0-9_-]+")
WAIT_IN = re.compile(
    r"try again in (?:(?P<hours>\d+)h)?(?:(?P<mins>\d+)m)?(?P<secs>[0-9.]+)\s*s",
    re.I,
)
GROQ_BASE = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-20b"
STALE_MODEL_PREFIXES = ("gpt-3", "gpt-4", "text-", "davinci")


def redact(text: str) -> str:
    return SECRETISH.sub("[redacted]", text or "")


def llm_config() -> dict[str, str] | None:
    key = (os.environ.get("GROQ_API_KEY") or os.environ.get("LLM_API_KEY") or "").strip()
    if not key:
        return None
    base_url = (os.environ.get("GROQ_BASE_URL") or "").strip().rstrip("/") or GROQ_BASE
    model = (os.environ.get("LLM_MODEL") or "").strip()
    if not model or model.startswith(STALE_MODEL_PREFIXES):
        model = GROQ_MODEL
    return {
        "api_key": key,
        "base_url": base_url,
        "model": model,
    }


def wait_seconds(detail: str, attempt: int) -> float:
    match = WAIT_IN.search(detail or "")
    if match:
        hours = float(match.group("hours") or 0)
        mins = float(match.group("mins") or 0)
        secs = float(match.group("secs") or 0)
        return min(3600.0, hours * 3600.0 + mins * 60.0 + secs + 1.0)
    return min(90.0, 20.0 + 5.0 * attempt)


def parse_json_content(content: Any) -> dict[str, Any]:
    if isinstance(content, dict):
        return content
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("empty LLM content")
    text = FENCE.sub("", content.strip()).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise RuntimeError("LLM content was not JSON") from None
        parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        if isinstance(parsed, list):
            return {"records": parsed}
        raise RuntimeError("LLM JSON was not an object")
    return parsed


def chat_json(messages_body: dict[str, Any], timeout: int = 90) -> dict[str, Any]:
    cfg = llm_config()
    if not cfg:
        raise RuntimeError("GROQ_API_KEY is not set")
    url = f"{cfg['base_url']}/chat/completions"
    data = json.dumps(messages_body).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(12):
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "WishlistDiscovery/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            choice = (raw.get("choices") or [{}])[0]
            message = choice.get("message") or {}
            content = message.get("content") or message.get("reasoning")
            if not content:
                reason = choice.get("finish_reason") or "unknown"
                raise RuntimeError(f"empty LLM content finish_reason={reason}")
            return parse_json_content(content)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:800]
            last_error = RuntimeError(f"LLM HTTP {exc.code}: {redact(body[:400])}")
            if exc.code in RETRY_STATUSES and attempt < 11:
                delay = wait_seconds(body, attempt)
                logging.getLogger("phase3").warning(
                    "LLM HTTP %s, retry %s in %.1f s (body_len=%s)",
                    exc.code,
                    attempt + 1,
                    delay,
                    len(body),
                )
                time.sleep(delay)
                continue
            raise last_error from exc
        except (TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
            last_error = RuntimeError(f"LLM request failed: {type(exc).__name__}")
            if attempt < 11:
                time.sleep(wait_seconds("", attempt))
                continue
            raise last_error from exc
    raise last_error or RuntimeError("LLM request failed")
