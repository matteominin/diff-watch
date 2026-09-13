"""enforce one active subscription per user

Revision ID: 6b8c2d7e4f1a
Revises: 3e5f7a9b1c2d
Create Date: 2026-09-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "6b8c2d7e4f1a"
down_revision: Union[str, Sequence[str], None] = "3e5f7a9b1c2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE UNIQUE INDEX uq_user_subscription_active_user
        ON user_subscription (user_id)
        WHERE is_active = TRUE;
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS uq_user_subscription_active_user;
    """)