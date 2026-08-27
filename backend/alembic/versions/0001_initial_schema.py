"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-27
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "treatments",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("name_hi", sa.String(length=200), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("category_hi", sa.String(length=120), nullable=True),
        sa.Column("aliases", sa.JSON(), nullable=False),
        sa.Column("symptoms", sa.JSON(), nullable=False),
        sa.Column("typical_duration", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
    )

    op.create_table(
        "cost_records",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "treatment_id",
            sa.String(length=64),
            sa.ForeignKey("treatments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=False),
        sa.Column("hospital_type", sa.String(length=32), nullable=False),
        sa.Column("cost_min", sa.Float(), nullable=False),
        sa.Column("cost_max", sa.Float(), nullable=False),
        sa.Column("cost_avg", sa.Float(), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("data_year", sa.Integer(), nullable=False),
    )
    op.create_index("ix_cost_records_treatment_id", "cost_records", ["treatment_id"])
    op.create_index("ix_cost_records_city", "cost_records", ["city"])
    op.create_index("ix_cost_records_state", "cost_records", ["state"])
    op.create_index("ix_cost_records_hospital_type", "cost_records", ["hospital_type"])

    op.create_table(
        "national_references",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column(
            "treatment_id",
            sa.String(length=64),
            sa.ForeignKey("treatments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("hospital_type", sa.String(length=32), nullable=False),
        sa.Column("cost_min", sa.Float(), nullable=False),
        sa.Column("cost_avg", sa.Float(), nullable=False),
        sa.Column("cost_max", sa.Float(), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("data_year", sa.Integer(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
    )
    op.create_index(
        "ix_national_references_treatment_id", "national_references", ["treatment_id"]
    )

    op.create_table(
        "hospitals",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("contact", sa.String(length=120), nullable=False),
        sa.Column("treatments_offered", sa.JSON(), nullable=False),
        sa.Column("empanelled_schemes", sa.JSON(), nullable=False),
        sa.Column("basic_rating", sa.Float(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
    )
    op.create_index("ix_hospitals_type", "hospitals", ["type"])
    op.create_index("ix_hospitals_city", "hospitals", ["city"])
    op.create_index("ix_hospitals_state", "hospitals", ["state"])

    op.create_table(
        "schemes",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("region_scope", sa.String(length=64), nullable=False),
        sa.Column("eligibility_rules", sa.JSON(), nullable=False),
        sa.Column("coverage_details", sa.Text(), nullable=False),
        sa.Column("application_steps", sa.JSON(), nullable=False),
        sa.Column("official_link", sa.String(length=300), nullable=False),
        sa.Column("last_verified_at", sa.String(length=32), nullable=True),
        sa.Column("note", sa.Text(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=128), nullable=False),
        sa.Column("password_salt", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "auth_sessions",
        sa.Column("token", sa.String(length=64), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_auth_sessions_email", "auth_sessions", ["email"])

    op.create_table(
        "password_reset_tokens",
        sa.Column("token", sa.String(length=64), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_password_reset_tokens_email", "password_reset_tokens", ["email"]
    )

    op.create_table(
        "bill_analyses",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.String(length=32), nullable=True),
        sa.Column("treatment_id", sa.String(length=64), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("extracted", sa.JSON(), nullable=False),
        sa.Column("verdict", sa.String(length=16), nullable=False),
        sa.Column("our_cost_avg", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("bill_analyses")
    op.drop_index("ix_password_reset_tokens_email", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_index("ix_auth_sessions_email", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("schemes")
    op.drop_index("ix_hospitals_state", table_name="hospitals")
    op.drop_index("ix_hospitals_city", table_name="hospitals")
    op.drop_index("ix_hospitals_type", table_name="hospitals")
    op.drop_table("hospitals")
    op.drop_index(
        "ix_national_references_treatment_id", table_name="national_references"
    )
    op.drop_table("national_references")
    op.drop_index("ix_cost_records_hospital_type", table_name="cost_records")
    op.drop_index("ix_cost_records_state", table_name="cost_records")
    op.drop_index("ix_cost_records_city", table_name="cost_records")
    op.drop_index("ix_cost_records_treatment_id", table_name="cost_records")
    op.drop_table("cost_records")
    op.drop_table("treatments")
