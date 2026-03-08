"""add tailor run trace metadata and ats keyword alignment

Revision ID: 20260309_0003
Revises: 20260309_0002
Create Date: 2026-03-09
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "20260309_0003"
down_revision = "20260309_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tailor_runs",
        sa.Column("run_attempt_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "tailor_runs",
        sa.Column("ats_keyword_alignment", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "tailor_runs",
        sa.Column("model_trace_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tailor_runs", "model_trace_metadata")
    op.drop_column("tailor_runs", "ats_keyword_alignment")
    op.drop_column("tailor_runs", "run_attempt_count")
