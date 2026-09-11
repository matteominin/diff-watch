"""create users table

Revision ID: 1798f9b38e38
Revises: 5a97c92a63e1
Create Date: 2026-09-11 17:05:14.344996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1798f9b38e38'
down_revision: Union[str, Sequence[str], None] = 'c73a95b272b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(255) NULL,
            image TEXT NULL,
            
            plan_id INTEGER NOT NULL DEFAULT 1 REFERENCES plans(id) ON DELETE RESTRICT,
            
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)


def downgrade() -> None:
    op.execute("""
        DROP TABLE IF EXISTS users;
    """)