
from sqlalchemy.orm import Session

from app.db import repositories

# Lower number = ranked first (cheapest / mission-aligned first)
TYPE_RANK = {"govt": 0, "private_low": 1, "private_mid": 2, "private_high": 3}


def find_hospitals(
    db: Session,
    treatment_id: str,
    city: str | None = None,
    hospital_type: str | None = None,
    budget_mode: bool = False,
) -> list[dict]:
    hospitals = repositories.all_hospitals(db)
    cost_records = repositories.all_cost_records(db)

    results = [h for h in hospitals if treatment_id in h.get("treatments_offered", [])]
    if city:
        results = [h for h in results if h["city"].lower() == city.lower()]
    if hospital_type:
        results = [h for h in results if h["type"] == hospital_type]

    enriched = []
    for h in results:
        match = next(
            (r for r in cost_records
             if r["treatment_id"] == treatment_id and r["city"].lower() == h["city"].lower()
             and r["hospital_type"] == h["type"]),
            None,
        )
        enriched.append({
            **h,
            "cost_avg": match["cost_avg"] if match else None,
            "cost_source": match["source"] if match else None,
        })

    if budget_mode:
        # Pure cost ascending, government-first as tiebreak
        enriched.sort(key=lambda h: (
            h["cost_avg"] if h["cost_avg"] is not None else float("inf"),
            TYPE_RANK.get(h["type"], 9),
        ))
    else:
        enriched.sort(key=lambda h: (TYPE_RANK.get(h["type"], 9), -h["basic_rating"]))

    return enriched


def get_hospital_by_id(db: Session, hospital_id: str) -> dict | None:
    return repositories.hospital_by_id(db, hospital_id)
