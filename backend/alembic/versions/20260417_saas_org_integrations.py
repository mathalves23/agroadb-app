"""SaaS: organizações, subscrições, configs legais, API keys, MV dashboard (PG).

Revision ID: 20260417_saas_org
Revises: add_capital_to_companies
Create Date: 2026-04-17
"""
from alembic import op
import sqlalchemy as sa


revision = "20260417_saas_org"
down_revision = "add_capital_to_companies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)

    op.create_table(
        "organization_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_org_member_user"),
    )
    op.create_index("ix_org_members_org", "organization_members", ["organization_id"])
    op.create_index("ix_org_members_user", "organization_members", ["user_id"])

    op.create_table(
        "organization_subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("plan", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("billing_provider", sa.String(length=16), nullable=False),
        sa.Column("trial_ends_at", sa.DateTime(), nullable=True),
        sa.Column("current_period_end", sa.DateTime(), nullable=True),
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("pagarme_customer_id", sa.String(length=255), nullable=True),
        sa.Column("pagarme_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("limits", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id"),
    )

    op.create_table(
        "legal_integration_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("system_name", sa.String(length=120), nullable=False),
        sa.Column("api_endpoint", sa.Text(), nullable=False),
        sa.Column("api_key_encrypted", sa.Text(), nullable=True),
        sa.Column("credentials", sa.JSON(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "system_name", name="uq_legal_config_user_system"),
    )
    op.create_index("ix_legal_int_cfg_user", "legal_integration_configs", ["user_id"])

    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("rate_limit_rpm", sa.Integer(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )
    op.create_index("ix_api_keys_user", "api_keys", ["user_id"])

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            sa.text(
                """
                CREATE MATERIALIZED VIEW IF NOT EXISTS mv_dashboard_investigation_summary AS
                SELECT user_id, status::text AS status, COUNT(*)::bigint AS cnt
                FROM investigations
                GROUP BY user_id, status
                """
            )
        )
        op.execute(
            sa.text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS ix_mv_dashboard_inv_summary_uq
                ON mv_dashboard_investigation_summary (user_id, status)
                """
            )
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_investigation_summary CASCADE"))

    op.drop_index("ix_api_keys_user", table_name="api_keys")
    op.drop_table("api_keys")
    op.drop_index("ix_legal_int_cfg_user", table_name="legal_integration_configs")
    op.drop_table("legal_integration_configs")
    op.drop_table("organization_subscriptions")
    op.drop_index("ix_org_members_user", table_name="organization_members")
    op.drop_index("ix_org_members_org", table_name="organization_members")
    op.drop_table("organization_members")
    op.drop_index("ix_organizations_slug", table_name="organizations")
    op.drop_table("organizations")
