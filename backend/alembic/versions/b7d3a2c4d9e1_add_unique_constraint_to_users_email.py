"""add unique constraint to users.email

Revision ID: b7d3a2c4d9e1
Revises: a0790c76a129
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "b7d3a2c4d9e1"
down_revision: Union[str, None] = "a0790c76a129"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_users_email", "users", ["email"])


def downgrade() -> None:
    op.drop_constraint("uq_users_email", "users", type_="unique")