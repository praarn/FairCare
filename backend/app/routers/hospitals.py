
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import HospitalOut
from app.services.hospital_service import find_hospitals, get_hospital_by_id

router = APIRouter(prefix="/api/hospitals", tags=["hospitals"])


@router.get("", response_model=list[HospitalOut])
def list_hospitals(
    treatment_id: str,
    city: str | None = None,
    hospital_type: str | None = Query(default=None, alias="type"),
    budget_mode: bool = False,
    db: Session = Depends(get_db),
):
    return find_hospitals(db, treatment_id, city, hospital_type, budget_mode)


@router.get("/{hospital_id}", response_model=HospitalOut)
def get_hospital(hospital_id: str, db: Session = Depends(get_db)):
    hospital = get_hospital_by_id(db, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return HospitalOut(**hospital, cost_avg=None, cost_source=None)
