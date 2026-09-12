from typing import Optional
from uuid import UUID
from src.diffwatch.models.user_model import User

from psycopg import Connection
from psycopg.rows import class_row, scalar_row

class UserDAO:
    def __init__(self, conn: Connection):
        self.conn = conn

    def create(self, user: User) -> UUID:
        query = """
            INSERT INTO users (email, name, plan_id, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        with self.conn.cursor(row_factory=scalar_row) as cur:
            cur.execute(
                query,
                (
                    user.name,
                    user.email,
                    user.plan_id,
                    user.created_at
                )
            )

            uuid = cur.fetchone()

            if not uuid:
                raise Exception("Insert statement executed but returned no ID.")

            return uuid


    def get_by_id(self, id: UUID) -> Optional[User]:
        query = "SELECT * FROM users WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(User)) as cur:
            cur.execute(query, (id, ))
            return cur.fetchone()

    def update_plan(self, user_id: UUID, plan_id: int) -> bool:
        query = """
            UPDATE users
            SET plan_id = %s
            WHERE id = %s;
        """

        with self.conn.cursor() as cur:
            cur.execute(
                query,
                (plan_id, user_id)
            )

            return cur.rowcount > 0