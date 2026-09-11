"""create monitors table

Revision ID: 5a97c92a63e1
Revises: 
Create Date: 2026-09-11 17:01:46.952824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a97c92a63e1'
down_revision: Union[str, Sequence[str], None] = '1798f9b38e38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE monitors (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT NULL,
            url TEXT NOT NULL,
            selector TEXT NOT NULL DEFAULT '',
            hash VARCHAR(64) NULL,
            check_freq INTEGER NOT NULL,
            next_check_at TIMESTAMPTZ NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            last_checked_at TIMESTAMPTZ NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_monitors_due ON monitors (next_check_at) WHERE is_active = true;
    """)

def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS idx_monitors_due;
        DROP TABLE IF EXISTS monitors;
    """)