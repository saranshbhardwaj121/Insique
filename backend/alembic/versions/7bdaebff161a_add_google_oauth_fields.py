"""add google oauth fields to users table

Revision ID: 7bdaebff161a
Revises: 30c6fa5b4fd7
Create Date: 2026-07-06 23:45:53.127131

"""
from alembic import op
import sqlalchemy as sa


revision = "7bdaebff161a"
down_revision = "30c6fa5b4fd7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("google_id", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("auth_provider", sa.String(length=20), nullable=False, server_default="LOCAL"))
    op.add_column("users", sa.Column("avatar_url", sa.String(length=500), nullable=True))
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.create_index(op.f("ix_users_google_id"), "users", ["google_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_google_id"), table_name="users")
    op.drop_column("users", "email_verified")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "auth_provider")
    op.drop_column("users", "google_id")
