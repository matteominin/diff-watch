from typing import Optional

from psycopg import Connection
from psycopg.rows import class_row, scalar_row

from diffwatch.core.exceptions import DiffWatchError
from diffwatch.models.plan_model import Plan


class PlanDAO:
    def __init__(self, conn: Connection):
        self.conn = conn

    def create(self, plan: Plan) -> int:
        query = """
            INSERT INTO plans (
                name,
                price_cents,
                max_active_monitors,
                min_check_freq_minutes,
                max_notifications_per_day,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        with self.conn.cursor(row_factory=scalar_row) as cur:
            cur.execute(
                query,
                (
                    plan.name,
                    plan.price_cents,
                    plan.max_active_monitors,
                    plan.min_check_freq_minutes,
                    plan.max_notifications_per_day,
                    plan.created_at,
                ),
            )

            plan_id = cur.fetchone()

            if plan_id is None:
                raise DiffWatchError("Insert statement executed but returned no ID.")

            return plan_id

    def get_by_id(self, plan_id: int) -> Optional[Plan]:
        query = "SELECT * FROM plans WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(Plan)) as cur:
            cur.execute(query, (plan_id,))
            return cur.fetchone()

    def get_all(self) -> list[Plan]:
        query = "SELECT * FROM plans ORDER BY price_cents, name"
        with self.conn.cursor(row_factory=class_row(Plan)) as cur:
            cur.execute(query)
            return cur.fetchall()