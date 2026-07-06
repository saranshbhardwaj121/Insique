"""add oauth_sessions table

Revision ID: ff79be707e1a
Revises: 7bdaebff161a
Create Date: 2026-07-07 00:10:37.577610

"""
from alembic import op
import sqlalchemy as sa


revision = 'ff79be707e1a'
down_revision = '7bdaebff161a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('oauth_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('code', sa.String(length=128), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_oauth_sessions_code'), 'oauth_sessions', ['code'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_oauth_sessions_code'), table_name='oauth_sessions')
    op.drop_table('oauth_sessions')
