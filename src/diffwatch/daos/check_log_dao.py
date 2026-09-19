from typing import Optional
from uuid import UUID

from psycopg import Connection
from psycopg.rows import class_row, scalar_row
from datetime import datetime

from diffwatch.models.check_log_model import CheckLog
from diffwatch.core.exceptions import DiffWatchError

class CheckLogDAO:
    def __init__(self, conn: Connection):
        self.conn = conn

    def create(self, check_log: CheckLog) -> int:
        query = """
            INSERT INTO check_logs (
                user_id,
                monitor_id,
                status,
                http_status,
                has_notified,
                prev_hash,
                next_hash,
                response_time,
                error_message,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        with self.conn.cursor(row_factory=scalar_row) as cur:
            cur.execute(
                query,
                (
                    check_log.user_id,
                    check_log.monitor_id,
                    check_log.status.value,
                    check_log.http_status,
                    check_log.has_notified,
                    check_log.prev_hash,
                    check_log.next_hash,
                    check_log.response_time,
                    check_log.error_message,
                    check_log.created_at,
                ),
            )

            check_log_id = cur.fetchone()

            if check_log_id is None:
                raise DiffWatchError("Insert statement executed but returned no ID.")

            return check_log_id

    def get_by_id(self, check_log_id: int) -> Optional[CheckLog]:
        query = "SELECT * FROM check_logs WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(CheckLog)) as cur:
            cur.execute(query, (check_log_id,))
            return cur.fetchone()

    def get_by_monitor_id(self, monitor_id: UUID) -> list[CheckLog]:
        query = """
            SELECT * FROM check_logs
            WHERE monitor_id = %s
            ORDER BY created_at DESC
        """
        with self.conn.cursor(row_factory=class_row(CheckLog)) as cur:
            cur.execute(query, (monitor_id,))
            return cur.fetchall()

    def count_notifications_since(self, user_id: UUID, start_date: datetime) -> int:
        query = """
            SELECT COUNT(*) FROM check_logs
            WHERE user_id = %s AND created_at >= %s
            AND has_notified = True
        """

        with self.conn.cursor(row_factory=scalar_row) as cur:
            cur.execute(query, (user_id, start_date))
            return cur.fetchone() or 0