"""Registo de revisão humana do score de risco (governança IA).

Revision ID: inv_risk_review_20260418
Revises: org_risk_ai_gov_20260418
Create Date: 2026-04-18
"""

from alembic import op
import sqlalchemy as sa


revision = "inv_risk_review_20260418"
down_revision = "org_risk_ai_gov_20260418"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "investigations",
        sa.Column("risk_score_reviewed_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "investigations",
        sa.Column("risk_score_reviewed_by_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_investigations_risk_score_reviewed_by",
        "investigations",
        "users",
        ["risk_score_reviewed_by_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_investigations_risk_score_reviewed_by", "investigations", type_="foreignkey"
    )
    op.drop_column("investigations", "risk_score_reviewed_by_id")
    op.drop_column("investigations", "risk_score_reviewed_at")
