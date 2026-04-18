"""Governança de IA nos scores de risco (política por organização).

Revision ID: org_risk_ai_gov_20260418
Revises: guest_links_20260418
Create Date: 2026-04-18
"""

import sqlalchemy as sa

from alembic import op

revision = "org_risk_ai_gov_20260418"
down_revision = "guest_links_20260418"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column(
            "risk_ai_human_review_required", sa.Boolean(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "organizations",
        sa.Column("risk_ai_governance_reference_url", sa.Text(), nullable=True),
    )
    op.alter_column("organizations", "risk_ai_human_review_required", server_default=None)


def downgrade() -> None:
    op.drop_column("organizations", "risk_ai_governance_reference_url")
    op.drop_column("organizations", "risk_ai_human_review_required")
