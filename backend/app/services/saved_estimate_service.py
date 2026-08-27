"""Per-user saved estimates.

The stored money columns are a snapshot taken server-side at save time (the
client's numbers are never trusted — ``save_estimate`` recomputes via
``cost_service``). On read, each row is re-estimated with the same parameters
so the caller can show drift since it was saved.
"""
from __future__ import annotations

import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SavedEstimate
from app.services import cost_service, treatment_service


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _base_dict(s: SavedEstimate) -> dict:
    return {
        "id": s.id,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "treatment_id": s.treatment_id,
        "treatment_name": s.treatment_name,
        "city": s.city,
        "state": s.state,
        "hospital_type": s.hospital_type,
        "label": s.label,
        "note": s.note or "",
        "cost_min": s.cost_min,
        "cost_avg": s.cost_avg,
        "cost_max": s.cost_max,
        "confidence_label": s.confidence_label,
        "lang": s.lang,
    }


def _drift(saved_avg: float, current_avg: float) -> dict:
    if saved_avg <= 0:
        return {"current_avg": round(current_avg, 2), "delta_pct": 0.0, "direction": "flat"}
    delta_pct = round((current_avg - saved_avg) / saved_avg * 100, 1)
    direction = "flat"
    if delta_pct >= 0.5:
        direction = "up"
    elif delta_pct <= -0.5:
        direction = "down"
    return {
        "current_avg": round(current_avg, 2),
        "delta_pct": delta_pct,
        "direction": direction,
    }


def save_estimate(
    db: Session,
    user_id: str,
    *,
    treatment_id: str,
    city: str | None,
    state: str | None,
    hospital_type: str | None,
    label: str | None,
    note: str | None,
    lang: str,
) -> dict | None:
    treatment = treatment_service.get_treatment_by_id(db, treatment_id)
    if not treatment:
        return None

    result = cost_service.estimate_cost(
        db, treatment_id, city, state, hospital_type, lang=lang
    )
    est = result.get("estimate")
    if not est:
        return None

    row = SavedEstimate(
        id=secrets.token_hex(8),
        user_id=user_id,
        created_at=_utcnow(),
        treatment_id=treatment_id,
        treatment_name=treatment["name"],
        city=(city or None),
        state=(state or None),
        hospital_type=(hospital_type or None),
        label=(label.strip() if label and label.strip() else None),
        note=(note or "").strip(),
        cost_min=est["cost_min"],
        cost_avg=est["cost_avg"],
        cost_max=est["cost_max"],
        confidence_label=est["confidence_label"],
        lang=lang,
    )
    db.add(row)
    db.commit()
    out = _base_dict(row)
    out["drift"] = None
    return out


def list_estimates(db: Session, user_id: str) -> list[dict]:
    rows = db.execute(
        select(SavedEstimate)
        .where(SavedEstimate.user_id == user_id)
        .order_by(SavedEstimate.created_at.desc())
    ).scalars().all()

    out: list[dict] = []
    for s in rows:
        d = _base_dict(s)
        d["drift"] = None
        try:
            result = cost_service.estimate_cost(
                db, s.treatment_id, s.city, s.state, s.hospital_type, lang=s.lang
            )
            est = result.get("estimate")
            if est:
                d["drift"] = _drift(s.cost_avg, est["cost_avg"])
        except Exception:  # noqa: BLE001 - drift is best-effort, never fatal
            d["drift"] = None
        out.append(d)
    return out


def delete_estimate(db: Session, user_id: str, estimate_id: str) -> bool:
    row = db.get(SavedEstimate, estimate_id)
    if row is None or row.user_id != user_id:
        return False
    db.delete(row)
    db.commit()
    return True
