"""remove image from users

Revision ID: 8f2c1d4e6a7b
Revises: 5a97c92a63e1
Create Date: 2026-09-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f2c1d4e6a7b"
down_revision: Union[str, Sequence[str], None] = "5a97c92a63e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "image")


def downgrade() -> None:
    op.add_column("users", sa.Column("image", sa.Text(), nullable=True))
