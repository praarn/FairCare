"""crowd-sourced contributions, saved estimates, admin flag

Revision ID: 0002_features
Revises: 0001_initial
Create Date: 2026-08-27
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_features"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_admin",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.create_table(
        "cost_contributions",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.String(length=32), nullable=True),
        sa.Column("treatment_id", sa.String(length=64), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state", sa.String(length=120), nullable=True),
        sa.Column("hospital_type", sa.String(length=32), nullable=True),
        sa.Column("hospital_name", sa.String(length=200), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("line_items", sa.JSON(), nullable=False),
        sa.Column("source_note", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.String(length=32), nullable=True),
        sa.Column("promoted_cost_record_id", sa.String(length=64), nullable=True),
    )

    op.create_table(
        "saved_estimates",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("user_id", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("treatment_id", sa.String(length=64), nullable=False),
        sa.Column("treatment_name", sa.String(length=200), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state", sa.String(length=120), nullable=True),
        sa.Column("hospital_type", sa.String(length=32), nullable=True),
        sa.Column("label", sa.String(length=200), nullable=True),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("cost_min", sa.Float(), nullable=False),
        sa.Column("cost_avg", sa.Float(), nullable=False),
        sa.Column("cost_max", sa.Float(), nullable=False),
        sa.Column("confidence_label", sa.String(length=16), nullable=False),
        sa.Column("lang", sa.String(length=8), nullable=False),
    )
    op.create_index(
        "ix_saved_estimates_user_id", "saved_estimates", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_saved_estimates_user_id", table_name="saved_estimates")
    op.drop_table("saved_estimates")
    op.drop_table("cost_contributions")
    op.drop_column("users", "is_admin")
