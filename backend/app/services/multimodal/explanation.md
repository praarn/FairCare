# `backend/app/services/multimodal/` — Groq helpers

Optional AI features. All of them require `GROQ_API_KEY`; with it unset
`settings.groq_enabled` is false and the `/api/multimodal/*` POST routes return
`503` (the frontend hides the corresponding UI).

## Trust model

The LLM is never trusted with arithmetic or with our cost tables. Each helper:

1. builds a strict prompt (`"invent nothing"`, `"do not recompute"`),
2. constrains the reply to a Pydantic schema,
3. does **no** numeric post-scrub — the schema + prompt are the guardrail,
4. never sees the cost database; any figures in the prompt were computed by
   `cost_service` first.

## Files

| File | Role |
|---|---|
| `groq_client.py` | Thin `httpx` client for the Groq OpenAI-compatible API. `chat_text`, vision chat, Whisper transcription, `parse_json_block`, and the `GroqUnavailable` exception. Models come from `settings` (`GROQ_VISION_MODEL`, `GROQ_TRANSCRIBE_MODEL`, `GROQ_TEXT_MODEL`). |
| `bill_analysis.py` | `POST /api/multimodal/analyze-bill`. Vision model does **OCR / structuring only** — extracts line items. The within/above/below verdict and every comparison number are computed afterwards by our own `cost_service`. |
| `transcription.py` | `POST /api/multimodal/transcribe`. Groq Whisper fallback for voice input when the browser lacks the Web Speech API. |
| `explain.py` | `POST /api/multimodal/explain-estimate`. Recomputes the estimate server-side, then hands the model only those numbers and asks for a short plain-language explanation in EN/HI. Carries a disclaimer that the wording is AI-generated but the rupee amounts are not. |
