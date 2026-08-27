"""Audio clip -> text, via Groq Whisper."""
from __future__ import annotations

from app.config import settings
from app.services.multimodal.groq_client import GroqUnavailable, transcribe

ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
}


class UploadRejected(ValueError):
    """The uploaded file failed a local guard (type / size) before any API call."""


def transcribe_audio(
    *, file_bytes: bytes, filename: str, content_type: str, language: str = "en"
) -> dict[str, str]:
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise UploadRejected(
            f"Unsupported audio type '{content_type}'. "
            f"Send one of: {', '.join(sorted(ALLOWED_AUDIO_TYPES))}."
        )
    max_bytes = settings.max_upload_mb_audio * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise UploadRejected(
            f"Audio is larger than the {settings.max_upload_mb_audio} MB limit."
        )
    if not file_bytes:
        raise UploadRejected("Empty audio upload.")

    result = transcribe(
        file_bytes=file_bytes,
        filename=filename or "audio.webm",
        content_type=content_type,
        language=language,
    )
    if not result["text"]:
        raise GroqUnavailable("Transcription came back empty.")
    return result
