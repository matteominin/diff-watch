"""remove plan_id from users

Revision ID: 7d9e4f1a2b3c
Revises: 6b8c2d7e4f1a
Create Date: 2026-09-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7d9e4f1a2b3c"
down_revision: Union[str, Sequence[str], None] = "6b8c2d7e4f1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "plan_id")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "plan_id",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )
    op.create_foreign_key(
        "users_plan_id_fkey",
        "users",
        "plans",
        ["plan_id"],
        ["id"],
        ondelete="RESTRICT",
    )
