from datetime import datetime, timedelta
from diffwatch.db.db import get_db_connection
from diffwatch.daos.monitor_dao import MonitorDAO
from diffwatch.core.checker import check, CheckStatus
from uuid import UUID

def main():
    conn = get_db_connection()
    monitor_dao = MonitorDAO(conn)

    monitor = monitor_dao.get_by_id(UUID("ec446717-02f1-40de-9cbe-8153645e0d7f"))
    if not monitor:
        raise Exception("Monitor not found")
    res = check(str(monitor.url), monitor.selector)

    if res.status == CheckStatus.OK:
        changed = monitor.hash is not None and monitor.hash != res.hash
        print("CHANGED" if changed else "UNCHANGED")

        if not monitor.id:
            print("Error: monitor has no id")
            return 

        monitor_dao.update(
            monitor_id=monitor.id, 
            hash=res.hash, 
            next_check_at=datetime.now() + timedelta(seconds=monitor.check_freq), 
            last_checked_at=datetime.now()
        )
    else:
        print(f"Check failed: {res.status} - {res.error}")


if __name__ == "__main__":
    main();