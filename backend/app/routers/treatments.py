from fastapi import APIRouter, Query
from typing import List
from app.schemas import Treatment
from app.services.treatment_service import search_treatments

router = APIRouter(prefix="/api/treatments", tags=["treatments"])


@router.get("/search", response_model=List[Treatment])
def search(q: str = Query(default="", description="Search text, matched against name + aliases")):
    return search_treatments(q)
