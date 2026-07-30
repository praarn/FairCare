from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas import HospitalOut
from app.services.hospital_service import find_hospitals, get_hospital_by_id

router = APIRouter(prefix="/api/hospitals", tags=["hospitals"])


@router.get("", response_model=List[HospitalOut])
def list_hospitals(
    treatment_id: str,
    city: Optional[str] = None,
    hospital_type: Optional[str] = Query(default=None, alias="type"),
    budget_mode: bool = False,
):
    return find_hospitals(treatment_id, city, hospital_type, budget_mode)


@router.get("/{hospital_id}", response_model=HospitalOut)
def get_hospital(hospital_id: str):
    hospital = get_hospital_by_id(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return HospitalOut(**hospital, cost_avg=None, cost_source=None)
