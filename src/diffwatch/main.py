from datetime import datetime, timedelta
from diffwatch.db.db import get_db_connection
from diffwatch.daos.monitor_dao import MonitorDAO
from diffwatch.core.checker import check, CheckStatus
from uuid import UUID

def main():
    conn = get_db_connection()
    monitor_dao = MonitorDAO(conn)

    monitors = monitor_dao.get_waiting_monitors()
    print(monitors)


if __name__ == "__main__":
    main();