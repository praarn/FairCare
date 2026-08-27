
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import Treatment
from app.services.treatment_service import search_treatments

router = APIRouter(prefix="/api/treatments", tags=["treatments"])


@router.get("/search", response_model=list[Treatment])
def search(
    q: str = Query(default="", description="Search text, matched against name + aliases"),
    db: Session = Depends(get_db),
):
    return search_treatments(db, q)


@router.get("/search-symptoms", response_model=list[Treatment])
def search_symptoms(
    q: str = Query(
        default="",
        description="Symptom description, matched strictly against name + aliases + symptoms",
    ),
    db: Session = Depends(get_db),
):
    """
    Symptom checker endpoint. Delegates to search_treatments with strict=True,
    which uses the F1-based symptom scorer and returns an empty list (rather
    than a weak guess) when nothing clears the higher bar.
    """
    return search_treatments(db, q, strict=True)
