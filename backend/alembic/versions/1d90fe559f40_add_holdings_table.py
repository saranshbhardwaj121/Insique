"""add_holdings_table

Revision ID: 1d90fe559f40
Revises: 5352ff6c95f5
Create Date: 2026-06-21 23:41:23.588676

"""
from alembic import op
import sqlalchemy as sa


revision = '1d90fe559f40'
down_revision = '5352ff6c95f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('holdings',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('ticker', sa.String(length=20), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=18, scale=6), nullable=False),
    sa.Column('average_cost_basis', sa.Numeric(precision=12, scale=4), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'ticker', name='uq_holding_user_ticker')
    )
    op.create_index(op.f('ix_holdings_ticker'), 'holdings', ['ticker'], unique=False)
    op.create_index(op.f('ix_holdings_user_id'), 'holdings', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_holdings_user_id'), table_name='holdings')
    op.drop_index(op.f('ix_holdings_ticker'), table_name='holdings')
    op.drop_table('holdings')
