"""Read helpers that return plain dicts in the same shape the old
``data_loader.py`` produced, so the scoring/tier services downstream did not
have to change their internals — only where the data comes from.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CostRecord, Hospital, NationalReference, Scheme, Treatment


def _treatment_dict(t: Treatment) -> dict:
    return {
        "id": t.id,
        "name": t.name,
        "name_hi": t.name_hi,
        "category": t.category,
        "category_hi": t.category_hi,
        "aliases": list(t.aliases or []),
        "symptoms": list(t.symptoms or []),
        "typical_duration": t.typical_duration,
        "description": t.description,
    }


def _cost_dict(r: CostRecord) -> dict:
    return {
        "id": r.id,
        "treatment_id": r.treatment_id,
        "city": r.city,
        "state": r.state,
        "hospital_type": r.hospital_type,
        "cost_min": r.cost_min,
        "cost_max": r.cost_max,
        "cost_avg": r.cost_avg,
        "sample_size": r.sample_size,
        "source": r.source,
        "data_year": r.data_year,
    }


def _hospital_dict(h: Hospital) -> dict:
    return {
        "id": h.id,
        "name": h.name,
        "type": h.type,
        "city": h.city,
        "state": h.state,
        "lat": h.lat,
        "lng": h.lng,
        "contact": h.contact,
        "treatments_offered": list(h.treatments_offered or []),
        "empanelled_schemes": list(h.empanelled_schemes or []),
        "basic_rating": h.basic_rating,
        "source": h.source,
    }


def _scheme_dict(s: Scheme) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "region_scope": s.region_scope,
        "eligibility_rules": dict(s.eligibility_rules or {}),
        "coverage_details": s.coverage_details,
        "application_steps": list(s.application_steps or []),
        "official_link": s.official_link,
        "last_verified_at": s.last_verified_at,
        "note": s.note,
    }


# ---------- treatments ----------

def all_treatments(db: Session) -> list[dict]:
    rows = db.execute(select(Treatment).order_by(Treatment.name)).scalars().all()
    return [_treatment_dict(t) for t in rows]


def treatment_by_id(db: Session, treatment_id: str) -> dict | None:
    t = db.get(Treatment, treatment_id)
    return _treatment_dict(t) if t else None


# ---------- cost records ----------

def all_cost_records(db: Session) -> list[dict]:
    rows = db.execute(select(CostRecord)).scalars().all()
    return [_cost_dict(r) for r in rows]


def cost_records_for_treatment(db: Session, treatment_id: str) -> list[dict]:
    rows = db.execute(
        select(CostRecord).where(CostRecord.treatment_id == treatment_id)
    ).scalars().all()
    return [_cost_dict(r) for r in rows]


# ---------- national reference ----------

def national_reference_map(db: Session) -> dict[str, dict[str, dict]]:
    """Rebuild the original nested ``{treatment_id: {hospital_type: entry}}`` shape."""
    rows = db.execute(select(NationalReference)).scalars().all()
    out: dict[str, dict[str, dict]] = {}
    for r in rows:
        out.setdefault(r.treatment_id, {})[r.hospital_type] = {
            "cost_min": r.cost_min,
            "cost_avg": r.cost_avg,
            "cost_max": r.cost_max,
            "sample_size": r.sample_size,
            "data_year": r.data_year,
            "source": r.source,
        }
    return out


# ---------- hospitals ----------

def all_hospitals(db: Session) -> list[dict]:
    rows = db.execute(select(Hospital)).scalars().all()
    return [_hospital_dict(h) for h in rows]


def hospital_by_id(db: Session, hospital_id: str) -> dict | None:
    h = db.get(Hospital, hospital_id)
    return _hospital_dict(h) if h else None


# ---------- schemes ----------

def all_schemes(db: Session) -> list[dict]:
    rows = db.execute(select(Scheme).order_by(Scheme.name)).scalars().all()
    return [_scheme_dict(s) for s in rows]
