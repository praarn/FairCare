"""Per-user saved estimates. Every route requires a valid session."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routers._deps import current_user
from app.schemas import SavedEstimateCreate, SavedEstimateOut
from app.services import saved_estimate_service

router = APIRouter(prefix="/api/saved-estimates", tags=["saved-estimates"])


@router.post("", response_model=SavedEstimateOut)
def create_saved_estimate(
    payload: SavedEstimateCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    if not payload.city and not payload.state:
        raise HTTPException(
            status_code=400, detail="Provide at least a city or a state/UT."
        )
    lang = payload.lang if payload.lang in ("en", "hi") else "en"
    result = saved_estimate_service.save_estimate(
        db,
        user["id"],
        treatment_id=payload.treatment_id,
        city=payload.city,
        state=payload.state,
        hospital_type=payload.hospital_type,
        label=payload.label,
        note=payload.note,
        lang=lang,
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No estimate is available for that treatment and location.",
        )
    return result


@router.get("", response_model=list[SavedEstimateOut])
def list_saved_estimates(
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    return saved_estimate_service.list_estimates(db, user["id"])


@router.delete("/{estimate_id}", status_code=204)
def delete_saved_estimate(
    estimate_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    if not saved_estimate_service.delete_estimate(db, user["id"], estimate_id):
        raise HTTPException(status_code=404, detail="Saved estimate not found.")
    return Response(status_code=204)
