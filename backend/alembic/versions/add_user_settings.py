"""add user_settings table

Revision ID: add_user_settings_001
Revises: 
Create Date: 2026-02-06

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_user_settings_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela user_settings
    op.create_table(
        'user_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Criar índices
    op.create_index('ix_user_settings_user_id', 'user_settings', ['user_id'])
    op.create_index('ix_user_settings_key', 'user_settings', ['key'])
    op.create_index('ix_user_settings_user_key', 'user_settings', ['user_id', 'key'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_user_settings_user_key', 'user_settings')
    op.drop_index('ix_user_settings_key', 'user_settings')
    op.drop_index('ix_user_settings_user_id', 'user_settings')
    op.drop_table('user_settings')
