"""add role column to users

Revision ID: 83580ff73395
Revises: 334fd6837a6d
Create Date: 2026-03-09

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "83580ff73395"
down_revision: Union[str, None] = "334fd6837a6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role", sa.String(length=50), nullable=False, server_default="member"
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
