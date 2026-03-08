"""add week2 resume versions jd and tailor run tables

Revision ID: 20260309_0002
Revises: 20260309_0001
Create Date: 2026-03-09
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "20260309_0002"
down_revision = "20260309_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_descriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_name", sa.Text(), nullable=True),
        sa.Column("position_title", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("extracted_requirements", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "resume_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "resume_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resume_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("based_on_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resume_versions.id"), nullable=True),
        sa.Column("job_description_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("job_descriptions.id"), nullable=True),
        sa.Column("latex_source", sa.Text(), nullable=False),
        sa.Column("pdf_file_url", sa.Text(), nullable=True),
        sa.Column("compile_status", sa.String(length=20), nullable=False),
        sa.Column("created_by", sa.String(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_resume_versions_resume_document_id", "resume_versions", ["resume_document_id"])
    op.create_unique_constraint("uq_resume_versions_doc_version_no", "resume_versions", ["resume_document_id", "version_no"])

    op.create_table(
        "tailor_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "resume_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resume_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_description_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("job_descriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("output_resume_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resume_versions.id"), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("idempotency_key", sa.Text(), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=True),
        sa.Column("prompt_version", sa.Text(), nullable=True),
        sa.Column("failure_stage", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_unique_constraint("uq_tailor_runs_user_idempotency", "tailor_runs", ["user_id", "idempotency_key"])


def downgrade() -> None:
    op.drop_constraint("uq_tailor_runs_user_idempotency", "tailor_runs", type_="unique")
    op.drop_table("tailor_runs")

    op.drop_constraint("uq_resume_versions_doc_version_no", "resume_versions", type_="unique")
    op.drop_index("idx_resume_versions_resume_document_id", table_name="resume_versions")
    op.drop_table("resume_versions")

    op.drop_table("job_descriptions")
