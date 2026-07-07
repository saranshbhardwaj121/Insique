"""add email verification fields

Revision ID: 9a9e3f2c1b5d
Revises: ff79be707e1a
Create Date: 2026-07-07 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '9a9e3f2c1b5d'
down_revision = 'ff79be707e1a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('verification_token_hash', sa.String(64), nullable=True))
    op.add_column('users', sa.Column('verification_token_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('verification_sent_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_users_verification_token_hash'), 'users', ['verification_token_hash'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_verification_token_hash'), table_name='users')
    op.drop_column('users', 'verification_sent_at')
    op.drop_column('users', 'verification_token_expires_at')
    op.drop_column('users', 'verification_token_hash')
