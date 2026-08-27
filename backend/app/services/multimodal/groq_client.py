"""Thin wrapper over Groq's OpenAI-compatible REST API.

Only two capabilities are used:
  * ``chat_vision``  — a multimodal chat completion (image + instructions in,
    JSON out) for reading an uploaded bill/prescription photo.
  * ``transcribe``   — Whisper speech-to-text for an uploaded audio clip.

Nothing here computes or reasons about money. The vision call is a strict
"transcribe what you see, invent nothing" OCR-structuring step; every
comparison number is produced later by our own rule-based ``cost_service``.
"""
from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import settings
from app.logging_config import get_logger

log = get_logger("sahaj.groq")


class GroqUnavailable(RuntimeError):
    """Raised when Groq is not configured or the upstream call failed."""


def _require_key() -> str:
    if not settings.groq_enabled:
        raise GroqUnavailable(
            "Multimodal features are turned off: no GROQ_API_KEY is configured."
        )
    return settings.groq_api_key


def _client() -> httpx.Client:
    return httpx.Client(
        base_url=settings.groq_base_url.rstrip("/"),
        timeout=settings.groq_timeout_seconds,
        headers={"Authorization": f"Bearer {_require_key()}"},
    )


def chat_vision(
    *,
    prompt: str,
    image_data_uri: str,
    model: str | None = None,
    force_json: bool = True,
) -> str:
    """Send one image + one text instruction, return the assistant's raw text."""
    model = model or settings.groq_vision_model
    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_data_uri}},
            ],
        }
    ]
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": 1500,
    }
    if force_json:
        payload["response_format"] = {"type": "json_object"}

    try:
        with _client() as client:
            resp = client.post("/chat/completions", json=payload)
        if resp.status_code >= 500:
            # one retry on a transient upstream error
            with _client() as client:
                resp = client.post("/chat/completions", json=payload)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("groq_vision_failed", error=str(exc), model=model)
        raise GroqUnavailable(f"Groq vision request failed: {exc}") from exc

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:  # pragma: no cover - upstream shape drift
        raise GroqUnavailable("Unexpected response shape from Groq vision.") from exc


def chat_text(
    *,
    prompt: str,
    model: str | None = None,
    force_json: bool = True,
) -> str:
    """Text-only chat completion (no image). Used by the estimate explainer.

    Same guarantees as ``chat_vision``: ``temperature=0``, one retry on a 5xx,
    optional strict JSON response format. Nothing here computes money — the
    caller passes in the already-computed figures for the model to describe.
    """
    model = model or settings.groq_text_model
    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 1200,
    }
    if force_json:
        payload["response_format"] = {"type": "json_object"}

    try:
        with _client() as client:
            resp = client.post("/chat/completions", json=payload)
        if resp.status_code >= 500:
            with _client() as client:
                resp = client.post("/chat/completions", json=payload)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("groq_text_failed", error=str(exc), model=model)
        raise GroqUnavailable(f"Groq text request failed: {exc}") from exc

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:  # pragma: no cover - upstream shape drift
        raise GroqUnavailable("Unexpected response shape from Groq text.") from exc


def transcribe(
    *,
    file_bytes: bytes,
    filename: str,
    content_type: str,
    language: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Whisper transcription. Returns ``{"text": ..., "language": ...}``."""
    model = model or settings.groq_transcribe_model
    files = {"file": (filename, file_bytes, content_type or "application/octet-stream")}
    form: dict[str, Any] = {"model": model, "response_format": "json"}
    if language and language in ("en", "hi"):
        form["language"] = language

    try:
        with _client() as client:
            resp = client.post("/audio/transcriptions", data=form, files=files)
        if resp.status_code >= 500:
            with _client() as client:
                resp = client.post("/audio/transcriptions", data=form, files=files)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("groq_transcribe_failed", error=str(exc), model=model)
        raise GroqUnavailable(f"Groq transcription request failed: {exc}") from exc

    data = resp.json()
    return {"text": (data.get("text") or "").strip(), "language": data.get("language")}


def parse_json_block(raw: str) -> dict[str, Any]:
    """Best-effort parse of a model reply that should be a JSON object."""
    raw = (raw or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if 0 <= start < end:
            try:
                return json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                pass
    raise GroqUnavailable("Model did not return valid JSON.")
