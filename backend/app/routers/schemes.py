from fastapi import APIRouter
from typing import List, Optional
from app.schemas import SchemeEligibilityResult
from app.services.scheme_service import check_eligibility

router = APIRouter(prefix="/api/schemes", tags=["schemes"])


@router.get("/eligible", response_model=List[SchemeEligibilityResult])
def eligible_schemes(
    annual_household_income: Optional[float] = None,
    state: Optional[str] = None,
    is_govt_employee_or_pensioner: bool = False,
):
    return check_eligibility(annual_household_income, state, is_govt_employee_or_pensioner)
