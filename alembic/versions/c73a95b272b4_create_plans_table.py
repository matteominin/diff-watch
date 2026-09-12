"""create plans table

Revision ID: c73a95b272b4
Revises:
Create Date: 2026-09-11 17:13:10.700762

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c73a95b272b4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE plans (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            price_cents INTEGER NOT NULL DEFAULT 0,
            max_active_monitors INTEGER NOT NULL,
            min_check_freq_minutes INTEGER NOT NULL,
            max_notifications_per_day INTEGER NOT NULL DEFAULT 50,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        -- Popolamento dei piani base di DiffWatch
        INSERT INTO plans (id, name, price_cents, max_active_monitors, min_check_freq_minutes, max_notifications_per_day) 
        VALUES 
            (1, 'Free', 0, 1, 60, 2),
            (2, 'Pro', 990, 5, 5, 100)
        ON CONFLICT (id) DO NOTHING;

        SELECT setval(
            pg_get_serial_sequence('plans', 'id'),
            COALESCE((SELECT MAX(id) FROM plans), 1),
            TRUE
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP TABLE IF EXISTS plans;
    """)
