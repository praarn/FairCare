"""Shared pytest fixtures.

Tests run against a throwaway SQLite database (portable JSON columns make this
work with the same models used in Postgres). ``SEED_MINIMAL`` keeps the fixture
DB small and predictable so tier / scoring assertions are stable.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("GROQ_API_KEY", "")

import pytest  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db import models  # noqa: E402,F401
from app.db.base import Base  # noqa: E402
from app.db.models import (  # noqa: E402
    CostRecord,
    Hospital,
    NationalReference,
    Scheme,
    Treatment,
)


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # SQLite ignores foreign keys unless asked; turn them on so ordering /
    # referential bugs surface here the same way they would on Postgres.
    @event.listens_for(eng, "connect")
    def _fk_on(dbapi_conn, _rec):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(eng)
    return eng


@pytest.fixture()
def db(engine):
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = TestSession()
    _seed_minimal(session)
    try:
        yield session
    finally:
        session.rollback()
        for model in (CostRecord, NationalReference, Hospital, Scheme, Treatment):
            session.query(model).delete()
        session.commit()
        session.close()


@pytest.fixture()
def client(engine, monkeypatch):
    """A TestClient whose ``get_db`` yields a fresh, minimally-seeded session."""
    from fastapi.testclient import TestClient

    from app.db.session import get_db
    from app.main import app

    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    session = TestSession()
    _seed_minimal(session)

    def _override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    session.rollback()
    for model in (CostRecord, NationalReference, Hospital, Scheme, Treatment):
        session.query(model).delete()
    session.commit()
    session.close()


def _seed_minimal(session):
    session.add_all(
        [
            Treatment(
                id="t_knee",
                name="Knee Replacement",
                name_hi="घुटना प्रत्यारोपण",
                category="Orthopedics",
                category_hi="हड्डी रोग",
                aliases=["knee arthroplasty", "TKR"],
                symptoms=["knee pain", "joint pain when walking", "knee swelling stiffness"],
                typical_duration="5-7 days admission",
                description="Replacement of the knee joint with an implant.",
            ),
            Treatment(
                id="t_cataract",
                name="Cataract Surgery",
                name_hi="मोतियाबिंद सर्जरी",
                category="Ophthalmology",
                category_hi="नेत्र रोग",
                aliases=["eye lens surgery"],
                symptoms=["blurry vision", "cloudy vision", "foggy eyesight"],
                typical_duration="Day care, 1 day",
                description="Removal of a clouded lens.",
            ),
            Treatment(
                id="t_rare",
                name="Rare Procedure",
                category="General Surgery",
                aliases=[],
                symptoms=["obscure unrelated symptom text"],
                typical_duration="1 day",
                description="Has no cost data and no national reference.",
            ),
        ]
    )
    session.add_all(
        [
            # Delhi knee: govt + private_mid  -> tier-1 (city) works
            CostRecord(
                id="cr_k1", treatment_id="t_knee", city="Delhi", state="Delhi",
                hospital_type="govt", cost_min=80000, cost_max=130000, cost_avg=100000,
                sample_size=120, source="SAMPLE DATA", data_year=2026,
            ),
            CostRecord(
                id="cr_k2", treatment_id="t_knee", city="Delhi", state="Delhi",
                hospital_type="private_mid", cost_min=280000, cost_max=420000, cost_avg=350000,
                sample_size=40, source="SAMPLE DATA", data_year=2025,
            ),
            # Pune knee (Maharashtra) -> lets a "Mumbai" query fall back to state pool
            CostRecord(
                id="cr_k3", treatment_id="t_knee", city="Pune", state="Maharashtra",
                hospital_type="govt", cost_min=85000, cost_max=140000, cost_avg=110000,
                sample_size=30, source="SAMPLE DATA", data_year=2024,
            ),
            # cataract only exists in Chennai -> national-reference tier for other cities
            CostRecord(
                id="cr_c1", treatment_id="t_cataract", city="Chennai", state="Tamil Nadu",
                hospital_type="govt", cost_min=5000, cost_max=9000, cost_avg=6500,
                sample_size=50, source="SAMPLE DATA", data_year=2025,
            ),
        ]
    )
    session.add(
        NationalReference(
            id="natref_t_cataract_govt", treatment_id="t_cataract", hospital_type="govt",
            cost_min=5500, cost_avg=6500, cost_max=7500, sample_size=40, data_year=2025,
            source="Approx. PM-JAY day-care rate. Verify at nha.gov.in.",
        )
    )
    session.add_all(
        [
            Hospital(
                id="h_g1", name="Delhi Govt Hospital", type="govt", city="Delhi",
                state="Delhi", lat=28.6, lng=77.2, contact="011-000",
                treatments_offered=["t_knee", "t_cataract"],
                empanelled_schemes=["PM-JAY"], basic_rating=3.9, source="SAMPLE DATA",
            ),
            Hospital(
                id="h_p1", name="Delhi Premium Hospital", type="private_high", city="Delhi",
                state="Delhi", lat=28.5, lng=77.2, contact="011-111",
                treatments_offered=["t_knee"],
                empanelled_schemes=[], basic_rating=4.6, source="SAMPLE DATA",
            ),
        ]
    )
    session.add_all(
        [
            Scheme(
                id="s_pmjay", name="Ayushman Bharat PM-JAY", region_scope="national",
                eligibility_rules={"max_annual_household_income": 250000},
                coverage_details="Up to Rs. 5 lakh/family/year.",
                application_steps=["Check eligibility", "Visit empanelled hospital"],
                official_link="https://pmjay.gov.in", last_verified_at="2026-06-01",
                note="SAMPLE DATA",
            ),
            Scheme(
                id="s_cghs", name="CGHS", region_scope="national",
                eligibility_rules={"requires_govt_employment_or_pension": True},
                coverage_details="Central government employees and pensioners.",
                application_steps=["Confirm status", "Apply for CGHS card"],
                official_link="https://cghs.gov.in", last_verified_at="2026-06-01",
                note="SAMPLE DATA",
            ),
            Scheme(
                id="s_ka", name="Arogya Karnataka", region_scope="state:Karnataka",
                eligibility_rules={
                    "max_annual_household_income": 500000,
                    "states_included": ["Karnataka"],
                },
                coverage_details="Karnataka residents.",
                application_steps=["Check residency", "Register at govt hospital"],
                official_link="https://arogya.karnataka.gov.in",
                last_verified_at="2026-06-01", note="SAMPLE DATA",
            ),
        ]
    )
    session.commit()
