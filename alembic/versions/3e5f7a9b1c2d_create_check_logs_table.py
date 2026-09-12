"""create check logs table

Revision ID: 3e5f7a9b1c2d
Revises: 2d4e6f8a9b0c
Create Date: 2026-09-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "3e5f7a9b1c2d"
down_revision: Union[str, Sequence[str], None] = "2d4e6f8a9b0c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE check_logs (
            id SERIAL PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            monitor_id UUID NOT NULL REFERENCES monitors(id) ON DELETE CASCADE,
            status VARCHAR(32) NOT NULL,
            http_status INTEGER NULL,
            has_notified BOOLEAN NOT NULL DEFAULT FALSE,
            prev_hash VARCHAR(64) NULL,
            next_hash VARCHAR(64) NULL,
            response_time DOUBLE PRECISION NULL,
            error_message TEXT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)


def downgrade() -> None:
    op.execute("""
        DROP TABLE IF EXISTS check_logs;
    """)