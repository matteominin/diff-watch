from datetime import datetime
from typing import Optional
from uuid import UUID

from psycopg import Connection
from psycopg.rows import class_row, scalar_row

from diffwatch.models.plan_model import Plan
from diffwatch.models.user_subscription_model import UserSubscription


class UserSubscriptionDAO:
    def __init__(self, conn: Connection):
        self.conn = conn

    def create(self, subscription: UserSubscription) -> int:
        query = """
            INSERT INTO user_subscription (
                user_id,
                plan_id,
                started_at,
                ended_at,
                is_active
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        with self.conn.cursor(row_factory=scalar_row) as cur:
            cur.execute(
                query,
                (
                    subscription.user_id,
                    subscription.plan_id,
                    subscription.started_at,
                    subscription.ended_at,
                    subscription.is_active,
                ),
            )

            subscription_id = cur.fetchone()

            if subscription_id is None:
                raise Exception("Insert statement executed but returned no ID.")

            return subscription_id

    def get_by_id(self, subscription_id: int) -> Optional[UserSubscription]:
        query = "SELECT * FROM user_subscription WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(UserSubscription)) as cur:
            cur.execute(query, (subscription_id,))
            return cur.fetchone()

    def get_active_plan_by_user_id(self, user_id: UUID) -> Optional[Plan]:
        query = """
            SELECT p.*
            FROM plans AS p
            JOIN user_subscription AS us ON us.plan_id = p.id
            WHERE us.user_id = %s AND us.is_active = TRUE
        """
        with self.conn.cursor(row_factory=class_row(Plan)) as cur:
            cur.execute(query, (user_id,))
            return cur.fetchone()

    def end(self, subscription_id: int, ended_at: datetime) -> bool:
        query = """
            UPDATE user_subscription
            SET ended_at = %s, is_active = FALSE
            WHERE id = %s;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (ended_at, subscription_id))
            return cur.rowcount > 0