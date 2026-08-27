"""Crowd-sourced bill amounts: submission, admin review, and promotion into
a real ``cost_records`` row.

Honesty rules carried over from the rest of the app: an approved contribution
becomes ONE sourced sample row (``sample_size = 1``), clearly labelled in its
``source`` string as a single user-contributed, reviewed data point. Nothing
here is generated or judged by an LLM.
"""
from __future__ import annotations

import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CostContribution, CostRecord, Treatment

_VALID_STATUSES = {"pending", "approved", "rejected"}


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _to_dict(c: CostContribution) -> dict:
    return {
        "id": c.id,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "user_id": c.user_id,
        "treatment_id": c.treatment_id,
        "city": c.city,
        "state": c.state,
        "hospital_type": c.hospital_type,
        "hospital_name": c.hospital_name,
        "amount": c.amount,
        "line_items": list(c.line_items or []),
        "source_note": c.source_note or "",
        "status": c.status,
        "reviewed_at": c.reviewed_at.isoformat() if c.reviewed_at else None,
        "reviewed_by": c.reviewed_by,
        "promoted_cost_record_id": c.promoted_cost_record_id,
    }


def create_contribution(
    db: Session,
    *,
    user_id: str | None,
    treatment_id: str | None,
    city: str | None,
    state: str | None,
    hospital_type: str | None,
    hospital_name: str | None,
    amount: float,
    line_items: list | None,
    source_note: str | None,
) -> dict:
    if amount is None or amount <= 0:
        raise ValueError("A positive bill amount is required.")

    row = CostContribution(
        id=secrets.token_hex(8),
        created_at=_utcnow(),
        user_id=user_id,
        treatment_id=(treatment_id or None),
        city=(city or None),
        state=(state or None),
        hospital_type=(hospital_type or None),
        hospital_name=(hospital_name or None),
        amount=float(amount),
        line_items=list(line_items or []),
        source_note=(source_note or "").strip(),
        status="pending",
    )
    db.add(row)
    db.commit()
    return _to_dict(row)


def list_contributions(db: Session, status: str = "pending") -> list[dict]:
    stmt = select(CostContribution).order_by(CostContribution.created_at.desc())
    if status and status != "all":
        stmt = stmt.where(CostContribution.status == status)
    return [_to_dict(c) for c in db.execute(stmt).scalars().all()]


def approve_contribution(
    db: Session,
    contribution_id: str,
    reviewer_id: str,
    *,
    treatment_id: str | None = None,
    city: str | None = None,
    state: str | None = None,
    hospital_type: str | None = None,
    cost_min: float | None = None,
    cost_max: float | None = None,
) -> dict:
    """Promote a pending contribution into a ``cost_records`` row.

    The reviewer may pass overrides for the fields a raw upload often can't
    resolve (treatment, city, state, hospital type). ``city`` and ``state``
    are required at this point because ``cost_records`` needs them NOT NULL.
    """
    c = db.get(CostContribution, contribution_id)
    if c is None:
        raise LookupError("Contribution not found.")
    if c.status != "pending":
        raise ValueError(f"Contribution is already {c.status}.")

    resolved_treatment = (treatment_id or c.treatment_id or "").strip()
    resolved_city = (city or c.city or "").strip()
    resolved_state = (state or c.state or "").strip()
    resolved_type = (hospital_type or c.hospital_type or "").strip()

    if not resolved_treatment:
        raise ValueError("A treatment must be assigned before approving.")
    if db.get(Treatment, resolved_treatment) is None:
        raise ValueError(f"Unknown treatment id '{resolved_treatment}'.")
    if not resolved_city or not resolved_state:
        raise ValueError("Both a city and a state are required to approve.")
    if not resolved_type:
        raise ValueError("A hospital type is required to approve.")

    lo = float(cost_min) if cost_min is not None else float(c.amount)
    hi = float(cost_max) if cost_max is not None else float(c.amount)
    if hi < lo:
        lo, hi = hi, lo
    avg = round((lo + hi) / 2, 2)

    record_id = f"user_{c.id}"
    today = _utcnow().date().isoformat()
    db.add(
        CostRecord(
            id=record_id,
            treatment_id=resolved_treatment,
            city=resolved_city,
            state=resolved_state,
            hospital_type=resolved_type,
            cost_min=round(lo, 2),
            cost_max=round(hi, 2),
            cost_avg=avg,
            sample_size=1,
            source=(
                f"User-contributed bill, reviewed and approved {today}. "
                "Single self-reported data point."
            ),
            data_year=_utcnow().year,
        )
    )

    c.status = "approved"
    c.reviewed_at = _utcnow()
    c.reviewed_by = reviewer_id
    c.promoted_cost_record_id = record_id
    db.commit()
    return {"contribution": _to_dict(c), "cost_record_id": record_id}


def reject_contribution(
    db: Session, contribution_id: str, reviewer_id: str
) -> dict:
    c = db.get(CostContribution, contribution_id)
    if c is None:
        raise LookupError("Contribution not found.")
    if c.status != "pending":
        raise ValueError(f"Contribution is already {c.status}.")
    c.status = "rejected"
    c.reviewed_at = _utcnow()
    c.reviewed_by = reviewer_id
    db.commit()
    return _to_dict(c)
