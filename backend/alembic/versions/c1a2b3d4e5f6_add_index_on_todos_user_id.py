"""add index on todos.user_id

Revision ID: c1a2b3d4e5f6
Revises: b7d3a2c4d9e1
Create Date: 2026-06-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c1a2b3d4e5f6"
down_revision: Union[str, None] = "b7d3a2c4d9e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_todos_user_id", "todos", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_todos_user_id", table_name="todos")
