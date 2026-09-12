"""create user subscription table

Revision ID: 2d4e6f8a9b0c
Revises: 8f2c1d4e6a7b
Create Date: 2026-09-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "2d4e6f8a9b0c"
down_revision: Union[str, Sequence[str], None] = "8f2c1d4e6a7b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE user_subscription (
            id SERIAL PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE RESTRICT,
            started_at TIMESTAMPTZ NOT NULL,
            ended_at TIMESTAMPTZ NULL DEFAULT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        );
    """)


def downgrade() -> None:
    op.execute("""
        DROP TABLE IF EXISTS user_subscription;
    """)