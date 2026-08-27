from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import EpisodeRequest, EpisodeResponse
from app.services.episode_service import estimate_episode

router = APIRouter(prefix="/api/estimate-episode", tags=["episode"])


@router.post("", response_model=EpisodeResponse)
def estimate_episode_endpoint(payload: EpisodeRequest, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Add at least one treatment.")
    if not payload.city and not payload.state:
        raise HTTPException(
            status_code=400, detail="Provide at least a city or a state/UT."
        )

    lang = payload.lang if payload.lang in ("en", "hi") else "en"
    return estimate_episode(
        db,
        [item.model_dump() for item in payload.items],
        city=payload.city,
        state=payload.state,
        hospital_type=payload.hospital_type,
        lang=lang,
        annual_household_income=payload.annual_household_income,
        is_govt_employee_or_pensioner=payload.is_govt_employee_or_pensioner,
    )
