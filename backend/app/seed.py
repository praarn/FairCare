"""Idempotent seed loader: ``app/data/seed/*.json`` -> Postgres.

    python -m app.seed            # upsert every fixture
    python -m app.seed --fresh    # delete + reload the reference tables first

Only the reference tables (treatments, cost_records, national_references,
hospitals, schemes) are touched. User / session / bill-analysis tables are
never modified here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.models import CostRecord, Hospital, NationalReference, Scheme, Treatment
from app.db.session import SessionLocal
from app.logging_config import configure_logging, get_logger

SEED_DIR = Path(__file__).resolve().parent / "data" / "seed"
log = get_logger("faircare.seed")


def _load(name: str):
    with open(SEED_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def _upsert(db: Session, model, rows: list[dict], pk: str = "id") -> int:
    for row in rows:
        obj = db.get(model, row[pk])
        if obj is None:
            db.add(model(**row))
        else:
            for k, v in row.items():
                setattr(obj, k, v)
    return len(rows)


def _national_reference_rows() -> list[dict]:
    raw = _load("national_reference.json")
    raw.pop("_read_me", None)
    out: list[dict] = []
    for treatment_id, by_type in raw.items():
        for hospital_type, entry in by_type.items():
            out.append(
                {
                    "id": f"natref_{treatment_id}_{hospital_type}",
                    "treatment_id": treatment_id,
                    "hospital_type": hospital_type,
                    "cost_min": entry["cost_min"],
                    "cost_avg": entry["cost_avg"],
                    "cost_max": entry["cost_max"],
                    "sample_size": entry["sample_size"],
                    "data_year": entry["data_year"],
                    "source": entry["source"],
                }
            )
    return out


def seed(fresh: bool = False) -> None:
    db = SessionLocal()
    try:
        if fresh:
            for model in (CostRecord, NationalReference, Hospital, Scheme, Treatment):
                db.execute(delete(model))
            db.flush()

        counts: dict[str, int] = {}
        # Parent rows first, flushed before the children that FK to them.
        counts["treatments"] = _upsert(db, Treatment, _load("treatments.json"))
        db.flush()
        counts["cost_records"] = _upsert(db, CostRecord, _load("cost_records.json"))
        counts["national_references"] = _upsert(
            db, NationalReference, _national_reference_rows()
        )
        counts["hospitals"] = _upsert(db, Hospital, _load("hospitals.json"))
        counts["schemes"] = _upsert(db, Scheme, _load("schemes.json"))
        db.commit()
        log.info("seed_complete", **counts)
        print("Seeded:", ", ".join(f"{v} {k}" for k, v in counts.items()))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    configure_logging()
    seed(fresh="--fresh" in sys.argv)
