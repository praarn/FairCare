
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import SchemeEligibilityResult
from app.services.scheme_service import check_eligibility

router = APIRouter(prefix="/api/schemes", tags=["schemes"])


@router.get("/eligible", response_model=list[SchemeEligibilityResult])
def eligible_schemes(
    annual_household_income: float | None = None,
    state: str | None = None,
    is_govt_employee_or_pensioner: bool = False,
    db: Session = Depends(get_db),
):
    return check_eligibility(
        db, annual_household_income, state, is_govt_employee_or_pensioner
    )
