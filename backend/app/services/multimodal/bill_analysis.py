"""Hospital-bill / prescription photo -> structured line items -> our verdict.

Pipeline:
  1. Local guards (MIME + size) before any network call.
  2. Groq vision: strict "transcribe only, invent nothing" OCR into JSON.
  3. Validate that JSON against ``ExtractedBill`` (Pydantic) — drift is rejected.
  4. Our code, not the model: fuzzy-match the treatment against our catalogue,
     run ``cost_service.estimate_cost``, and decide within/above/below by
     comparing the bill total to OUR sourced range.

The model never sees our cost data and never produces a verdict or a
reference number.
"""
from __future__ import annotations

import base64

from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy.orm import Session

from app.config import settings
from app.services import cost_service, treatment_service
from app.services.multimodal.groq_client import (
    GroqUnavailable,
    chat_vision,
    parse_json_block,
)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

_VISION_PROMPT = (
    "You are an OCR and document-structuring tool for Indian hospital bills, "
    "estimates, and prescriptions. Read ONLY what is printed in the image. "
    "Do NOT estimate, guess, infer, or add any amount that is not written. "
    "If a field is not present, use null (or an empty list). "
    "Return a single JSON object with exactly these keys:\n"
    '  "hospital_name": string or null,\n'
    '  "document_type": one of "bill", "estimate", "prescription", "other",\n'
    '  "detected_treatment": string or null  (the main procedure/treatment named),\n'
    '  "line_items": array of { "description": string, "amount": number }  (amounts in INR, numbers only),\n'
    '  "total_amount": number or null  (the printed grand total, INR, number only),\n'
    '  "currency": string  (usually "INR"),\n'
    '  "notes": string or null  (anything ambiguous or unreadable).\n'
    "Output the JSON object and nothing else."
)


class ExtractedLineItem(BaseModel):
    description: str = ""
    amount: float | None = None

    @field_validator("amount", mode="before")
    @classmethod
    def _coerce_amount(cls, v):
        if v in (None, "", "null"):
            return None
        if isinstance(v, str):
            v = v.replace(",", "").replace("Rs.", "").replace("₹", "").strip()
        try:
            return float(v)
        except (TypeError, ValueError):
            return None


class ExtractedBill(BaseModel):
    hospital_name: str | None = None
    document_type: str = "other"
    detected_treatment: str | None = None
    line_items: list[ExtractedLineItem] = Field(default_factory=list)
    total_amount: float | None = None
    currency: str = "INR"
    notes: str | None = None

    @field_validator("total_amount", mode="before")
    @classmethod
    def _coerce_total(cls, v):
        if v in (None, "", "null"):
            return None
        if isinstance(v, str):
            v = v.replace(",", "").replace("Rs.", "").replace("₹", "").strip()
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def effective_total(self) -> float | None:
        if self.total_amount is not None:
            return self.total_amount
        amounts = [li.amount for li in self.line_items if li.amount is not None]
        return round(sum(amounts), 2) if amounts else None


class UploadRejected(ValueError):
    """Local guard failure (type / size) before any API call."""


def _guard(file_bytes: bytes, content_type: str) -> None:
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise UploadRejected(
            f"Unsupported image type '{content_type}'. Send a JPEG, PNG, or WebP photo."
        )
    max_bytes = settings.max_upload_mb_image * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise UploadRejected(
            f"Image is larger than the {settings.max_upload_mb_image} MB limit."
        )
    if not file_bytes:
        raise UploadRejected("Empty image upload.")


def _verdict(total: float | None, cost_min: float, cost_max: float) -> str:
    if total is None:
        return "unknown"
    if total < cost_min:
        return "below"
    if total > cost_max:
        return "above"
    return "within"


DISCLAIMER = (
    "Line items and totals are read directly from your uploaded image by an "
    "OCR model — check them against the paper. The fair-range comparison uses "
    "our own sample cost data, not the model."
)


def analyze_bill(
    db: Session,
    *,
    file_bytes: bytes,
    content_type: str,
    city: str | None = None,
    treatment_id: str | None = None,
    lang: str = "en",
) -> dict:
    _guard(file_bytes, content_type)

    b64 = base64.b64encode(file_bytes).decode("ascii")
    data_uri = f"data:{content_type};base64,{b64}"

    raw = chat_vision(prompt=_VISION_PROMPT, image_data_uri=data_uri)
    try:
        extracted = ExtractedBill.model_validate(parse_json_block(raw))
    except (ValidationError, GroqUnavailable) as exc:
        raise GroqUnavailable(
            "Could not read a structured bill out of that image. "
            "Try a clearer, straight-on photo."
        ) from exc

    # ----- our code from here down: match + estimate + verdict -----
    matched_treatment: dict | None = None
    if treatment_id:
        matched_treatment = treatment_service.get_treatment_by_id(db, treatment_id)
    if matched_treatment is None and extracted.detected_treatment:
        candidates = treatment_service.search_treatments(
            db, extracted.detected_treatment, strict=False
        )
        matched_treatment = candidates[0] if candidates else None

    our_estimate = None
    verdict = "unknown"
    total = extracted.effective_total()
    if matched_treatment and (city or treatment_id):
        result = cost_service.estimate_cost(
            db,
            matched_treatment["id"],
            city=city,
            hospital_type=None,
            lang=lang,
        )
        if result.get("estimate"):
            our_estimate = result["estimate"]
            verdict = _verdict(
                total, our_estimate["cost_min"], our_estimate["cost_max"]
            )

    return {
        "extracted": extracted.model_dump(),
        "effective_total": total,
        "matched_treatment": matched_treatment,
        "our_estimate": our_estimate,
        "verdict": verdict,
        "disclaimer": DISCLAIMER,
    }
