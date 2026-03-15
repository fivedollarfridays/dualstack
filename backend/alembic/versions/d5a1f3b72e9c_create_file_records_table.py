"""Create file_records table.

Revision ID: d5a1f3b72e9c
Revises: c3f9a2e81b4c
Create Date: 2026-03-09
"""

from alembic import op
import sqlalchemy as sa


revision = "d5a1f3b72e9c"
down_revision = "c3f9a2e81b4c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "file_records",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column("storage_key", sa.String(), nullable=False, unique=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column("content_type", sa.String(127), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("file_records")
