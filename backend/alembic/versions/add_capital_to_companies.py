"""add capital field to companies

Revision ID: add_capital_to_companies
Revises: add_user_settings_001
Create Date: 2026-02-06

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_capital_to_companies'
down_revision = 'add_user_settings_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar coluna capital à tabela companies
    op.add_column('companies', sa.Column('capital', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('companies', 'capital')
