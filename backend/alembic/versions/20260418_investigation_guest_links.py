"""Links de convidado (data room leve) para investigações.

Revision ID: guest_links_20260418
Revises: 20260417_saas_org
Create Date: 2026-04-18
"""

import sqlalchemy as sa

from alembic import op

revision = "guest_links_20260418"
down_revision = "20260417_saas_org"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "investigation_guest_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("allow_downloads", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("access_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_access_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_investigation_guest_links_token_hash",
        "investigation_guest_links",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_investigation_guest_links_investigation_id",
        "investigation_guest_links",
        ["investigation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_investigation_guest_links_investigation_id", table_name="investigation_guest_links"
    )
    op.drop_index("ix_investigation_guest_links_token_hash", table_name="investigation_guest_links")
    op.drop_table("investigation_guest_links")
