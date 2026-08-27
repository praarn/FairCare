"""Crowd-sourced cost contributions.

``POST /`` is public (anyone can submit a bill amount; a signed-in submitter is
attributed). Everything else is admin-only and gated by ``is_admin`` on the
user's account.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.rate_limit import limiter
from app.routers._deps import current_admin, optional_user
from app.schemas import (
    ContributionApprove,
    ContributionApproveResponse,
    ContributionCreate,
    ContributionCreateResponse,
    ContributionOut,
)
from app.services import contribution_service

router = APIRouter(prefix="/api/contributions", tags=["contributions"])


@router.post("", response_model=ContributionCreateResponse)
@limiter.limit(settings.rate_limit_default)
def submit_contribution(
    request: Request,
    payload: ContributionCreate,
    db: Session = Depends(get_db),
    user: dict | None = Depends(optional_user),
):
    try:
        result = contribution_service.create_contribution(
            db,
            user_id=user["id"] if user else None,
            treatment_id=payload.treatment_id,
            city=payload.city,
            state=payload.state,
            hospital_type=payload.hospital_type,
            hospital_name=payload.hospital_name,
            amount=payload.amount,
            line_items=[li.model_dump() for li in payload.line_items],
            source_note=payload.source_note,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ContributionCreateResponse(status="received", id=result["id"])


@router.get("", response_model=list[ContributionOut])
def list_contributions(
    status: str = "pending",
    db: Session = Depends(get_db),
    _admin: dict = Depends(current_admin),
):
    return contribution_service.list_contributions(db, status=status)


@router.post("/{contribution_id}/approve", response_model=ContributionApproveResponse)
def approve_contribution(
    contribution_id: str,
    payload: ContributionApprove,
    db: Session = Depends(get_db),
    admin: dict = Depends(current_admin),
):
    try:
        result = contribution_service.approve_contribution(
            db,
            contribution_id,
            admin["id"],
            treatment_id=payload.treatment_id,
            city=payload.city,
            state=payload.state,
            hospital_type=payload.hospital_type,
            cost_min=payload.cost_min,
            cost_max=payload.cost_max,
        )
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return result


@router.post("/{contribution_id}/reject", response_model=ContributionOut)
def reject_contribution(
    contribution_id: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(current_admin),
):
    try:
        return contribution_service.reject_contribution(
            db, contribution_id, admin["id"]
        )
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
