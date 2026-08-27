"""ORM models.

Column names deliberately mirror the original seed-JSON keys so the scoring
services and the Pydantic response schemas need almost no change — only the
data *source* moved from files to Postgres.

Portable types only (``JSON``, not ``ARRAY``/``JSONB``) so the same metadata
creates a SQLite schema for the unit tests and a Postgres schema in prod.
"""
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Treatment(Base):
    __tablename__ = "treatments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    name_hi: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category: Mapped[str] = mapped_column(String(120))
    category_hi: Mapped[str | None] = mapped_column(String(120), nullable=True)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    symptoms: Mapped[list] = mapped_column(JSON, default=list)
    typical_duration: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)

    cost_records: Mapped[list["CostRecord"]] = relationship(
        back_populates="treatment", cascade="all, delete-orphan"
    )


class CostRecord(Base):
    __tablename__ = "cost_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    treatment_id: Mapped[str] = mapped_column(
        ForeignKey("treatments.id", ondelete="CASCADE"), index=True
    )
    city: Mapped[str] = mapped_column(String(120), index=True)
    state: Mapped[str] = mapped_column(String(120), index=True)
    hospital_type: Mapped[str] = mapped_column(String(32), index=True)
    cost_min: Mapped[float] = mapped_column(Float)
    cost_max: Mapped[float] = mapped_column(Float)
    cost_avg: Mapped[float] = mapped_column(Float)
    sample_size: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(Text)
    data_year: Mapped[int] = mapped_column(Integer)

    treatment: Mapped["Treatment"] = relationship(back_populates="cost_records")


class NationalReference(Base):
    """One cited PM-JAY/CGHS package rate, per treatment x hospital type.

    Flattened from the original nested ``national_reference.json`` shape.
    """

    __tablename__ = "national_references"

    id: Mapped[str] = mapped_column(String(96), primary_key=True)
    treatment_id: Mapped[str] = mapped_column(
        ForeignKey("treatments.id", ondelete="CASCADE"), index=True
    )
    hospital_type: Mapped[str] = mapped_column(String(32), default="govt")
    cost_min: Mapped[float] = mapped_column(Float)
    cost_avg: Mapped[float] = mapped_column(Float)
    cost_max: Mapped[float] = mapped_column(Float)
    sample_size: Mapped[int] = mapped_column(Integer)
    data_year: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(Text)

    # Declared so the unit-of-work knows to INSERT treatments before national
    # references (a bare ForeignKey column alone does not drive that ordering).
    treatment: Mapped["Treatment"] = relationship()


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(32), index=True)
    city: Mapped[str] = mapped_column(String(120), index=True)
    state: Mapped[str] = mapped_column(String(120), index=True)
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    contact: Mapped[str] = mapped_column(String(120))
    treatments_offered: Mapped[list] = mapped_column(JSON, default=list)
    empanelled_schemes: Mapped[list] = mapped_column(JSON, default=list)
    basic_rating: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(Text)


class Scheme(Base):
    __tablename__ = "schemes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    region_scope: Mapped[str] = mapped_column(String(64), default="national")
    eligibility_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    coverage_details: Mapped[str] = mapped_column(Text)
    application_steps: Mapped[list] = mapped_column(JSON, default=list)
    official_link: Mapped[str] = mapped_column(String(300))
    last_verified_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    note: Mapped[str] = mapped_column(Text, default="")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    password_salt: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class BillAnalysis(Base):
    """Structured summary of a multimodal bill analysis. Never stores the image."""

    __tablename__ = "bill_analyses"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    user_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    treatment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    extracted: Mapped[dict] = mapped_column(JSON, default=dict)
    verdict: Mapped[str] = mapped_column(String(16), default="unknown")
    our_cost_avg: Mapped[float | None] = mapped_column(Float, nullable=True)


class CostContribution(Base):
    """A user-submitted bill amount, pending admin review.

    On approval an admin promotes it into a real ``cost_records`` row. Like
    ``BillAnalysis`` this deliberately keeps no ForeignKeys and plain string
    ids so the same metadata builds the SQLite test schema.
    """

    __tablename__ = "cost_contributions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    user_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    treatment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    hospital_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    hospital_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    amount: Mapped[float] = mapped_column(Float)
    line_items: Mapped[list] = mapped_column(JSON, default=list)
    source_note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(
        String(16), default="pending", server_default=text("'pending'"), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reviewed_by: Mapped[str | None] = mapped_column(String(32), nullable=True)
    promoted_cost_record_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class SavedEstimate(Base):
    """A logged-in user's saved cost estimate. The money columns are a
    snapshot taken (server-side) at save time; drift vs the live estimate is
    computed on read."""

    __tablename__ = "saved_estimates"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(32), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    treatment_id: Mapped[str] = mapped_column(String(64))
    treatment_name: Mapped[str] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    hospital_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    note: Mapped[str] = mapped_column(Text, default="")
    cost_min: Mapped[float] = mapped_column(Float)
    cost_avg: Mapped[float] = mapped_column(Float)
    cost_max: Mapped[float] = mapped_column(Float)
    confidence_label: Mapped[str] = mapped_column(String(16), default="low")
    lang: Mapped[str] = mapped_column(String(8), default="en")
