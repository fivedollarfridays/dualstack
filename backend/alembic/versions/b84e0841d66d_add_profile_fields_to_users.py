"""add profile fields to users

Revision ID: b84e0841d66d
Revises: 83580ff73395
Create Date: 2026-03-09

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b84e0841d66d"
down_revision: Union[str, None] = "83580ff73395"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("display_name", sa.String(length=255), nullable=True)
    )
    op.add_column("users", sa.Column("avatar_url", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "display_name")
