from typing import Optional
from uuid import UUID
from datetime import datetime

from psycopg import Connection
from psycopg.rows import class_row, scalar_row

from diffwatch.core.exceptions import DiffWatchError
from diffwatch.models.monitor_model import Monitor

class MonitorDAO:
    def __init__(self, conn: Connection):
        self.conn = conn

    def create(self, monitor_in: Monitor) -> UUID:
        query = """INSERT INTO monitors (user_id, name, url, selector, check_freq, next_check_at, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        with self.conn.cursor(row_factory=scalar_row) as cur:
            cur.execute(
                query,
                (
                    monitor_in.user_id,
                    monitor_in.name,
                    str(monitor_in.url),
                    monitor_in.selector,
                    monitor_in.check_freq,
                    monitor_in.next_check_at,
                    monitor_in.is_active,
                    monitor_in.created_at
                )
            )

            uuid = cur.fetchone()

            if not uuid:
                raise DiffWatchError("Insert statement executed but returned no ID.")

            return uuid

    def get_by_id(self, monitor_id: UUID) -> Optional[Monitor]:
            query = "SELECT * FROM monitors WHERE id = %s"
            with self.conn.cursor(row_factory=class_row(Monitor)) as cur:
                cur.execute(query, (monitor_id,))
                return cur.fetchone()

    def get_by_user_id(self, user_id: UUID) -> list[Monitor]:
        query = "SELECT * FROM monitors WHERE user_id = %s"
        with self.conn.cursor(row_factory=class_row(Monitor)) as cur:
            cur.execute(query, (user_id,))
            return cur.fetchall()

    def get_waiting_monitors(self, limit: int = 100) -> list[Monitor]:
        query = """
            SELECT * FROM monitors
            WHERE is_active = TRUE AND next_check_at <= NOW()
            ORDER BY next_check_at ASC
            LIMIT %s
            FOR UPDATE SKIP LOCKED;
        """

        with self.conn.cursor(row_factory=class_row(Monitor)) as cur:
            cur.execute(query, (limit,))
            return cur.fetchall()

    def update(
        self, 
        monitor_id: UUID,
        name: Optional[str] = None,
        selector: Optional[str] = None,
        hash: Optional[str] = None,
        check_freq: Optional[int] = None,
        next_check_at: Optional[datetime] = None,
        is_active: Optional[bool] = None,
        last_checked_at: Optional[datetime] = None
    ) -> Optional[Monitor]:
        query = """
            UPDATE monitors
            SET name = COALESCE(%s, name),
                selector = COALESCE(%s, selector),
                hash = COALESCE(%s, hash),
                check_freq = COALESCE(%s, check_freq),
                next_check_at = COALESCE(%s, next_check_at),
                is_active = COALESCE(%s, is_active),
                last_checked_at = COALESCE(%s, last_checked_at)
            WHERE id = %s
            RETURNING id, user_id, name, url, selector, hash, check_freq, next_check_at, is_active, last_checked_at, created_at;
        """
        with self.conn.cursor(row_factory=class_row(Monitor)) as cur:
            cur.execute(
                query,
                (   
                    name,
                    selector,
                    hash,
                    check_freq,
                    next_check_at,
                    is_active,
                    last_checked_at,
                    monitor_id,
                ),
            )
            return cur.fetchone()