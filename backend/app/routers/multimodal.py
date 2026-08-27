"""Multimodal endpoints — bill-photo analysis and voice transcription (Groq).

Every one of these degrades cleanly: with no ``GROQ_API_KEY`` set,
``/status`` reports the features off and the POST routes return 503.
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.rate_limit import limiter
from app.schemas import BillAnalysisResponse, MultimodalStatus, TranscriptionResponse
from app.services.multimodal.bill_analysis import UploadRejected, analyze_bill
from app.services.multimodal.groq_client import GroqUnavailable
from app.services.multimodal.transcription import (
    UploadRejected as AudioUploadRejected,
)
from app.services.multimodal.transcription import (
    transcribe_audio,
)

router = APIRouter(prefix="/api/multimodal", tags=["multimodal"])


@router.get("/status", response_model=MultimodalStatus)
def status():
    on = settings.groq_enabled
    return MultimodalStatus(
        vision=on,
        transcription=on,
        vision_model=settings.groq_vision_model if on else None,
        transcription_model=settings.groq_transcribe_model if on else None,
    )


@router.post("/analyze-bill", response_model=BillAnalysisResponse)
@limiter.limit(settings.rate_limit_multimodal)
async def analyze_bill_endpoint(
    request: Request,
    file: UploadFile = File(...),
    city: str | None = Form(default=None),
    treatment_id: str | None = Form(default=None),
    lang: str = Form(default="en"),
    db: Session = Depends(get_db),
):
    if not settings.groq_enabled:
        raise HTTPException(
            status_code=503,
            detail="Bill photo analysis is unavailable: no GROQ_API_KEY is configured.",
        )
    file_bytes = await file.read()
    try:
        result = analyze_bill(
            db,
            file_bytes=file_bytes,
            content_type=file.content_type or "",
            city=city or None,
            treatment_id=treatment_id or None,
            lang=lang if lang in ("en", "hi") else "en",
        )
    except UploadRejected as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except GroqUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return result


@router.post("/transcribe", response_model=TranscriptionResponse)
@limiter.limit(settings.rate_limit_multimodal)
async def transcribe_endpoint(
    request: Request,
    file: UploadFile = File(...),
    lang: str = Form(default="en"),
):
    if not settings.groq_enabled:
        raise HTTPException(
            status_code=503,
            detail="Voice transcription is unavailable: no GROQ_API_KEY is configured.",
        )
    file_bytes = await file.read()
    try:
        result = transcribe_audio(
            file_bytes=file_bytes,
            filename=file.filename or "audio.webm",
            content_type=file.content_type or "",
            language=lang if lang in ("en", "hi") else "en",
        )
    except AudioUploadRejected as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except GroqUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return result
