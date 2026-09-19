from typing import Optional
from uuid import UUID
from diffwatch.models.user_model import User

from psycopg import Connection
from psycopg.rows import class_row, scalar_row

from diffwatch.core.exceptions import DiffWatchError

class UserDAO:
    def __init__(self, conn: Connection):
        self.conn = conn

    def create(self, user: User) -> UUID:
        query = """
            INSERT INTO users (name, email, created_at)
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        with self.conn.cursor(row_factory=scalar_row) as cur:
            cur.execute(
                query,
                (
                    user.name,
                    user.email,
                    user.created_at
                )
            )

            uuid = cur.fetchone()

            if not uuid:
                raise DiffWatchError("Insert statement executed but returned no ID.")

            return uuid


    def get_by_id(self, id: UUID) -> Optional[User]:
        query = "SELECT * FROM users WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(User)) as cur:
            cur.execute(query, (id, ))
            return cur.fetchone()
