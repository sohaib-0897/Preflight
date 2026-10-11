"""Immutable project evidence and reviewer assignments; additive migration."""

from alembic import op
import sqlalchemy as sa

revision = "b02c03d4e5f6"
down_revision = "a91b02c3d4e5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "evidence_sources",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("uri", sa.String(2048), nullable=False),
        sa.Column("facts", sa.JSON(), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.UniqueConstraint("project_id", "name", "version"),
    )
    op.create_index("ix_evidence_sources_project_id", "evidence_sources", ["project_id"])
    op.create_table(
        "review_assignments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "attempt_id", sa.String(36), sa.ForeignKey("scenario_attempts.id"), nullable=False
        ),
        sa.Column("reviewer_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assigned_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
    )
    for column in ["attempt_id", "reviewer_id"]:
        op.create_index("ix_review_assignments_" + column, "review_assignments", [column])


def downgrade():
    op.drop_table("review_assignments")
    op.drop_table("evidence_sources")
