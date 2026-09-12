from datetime import datetime, timezone
from uuid import uuid4
from pydantic import HttpUrl

from diffwatch.daos.monitor_dao import MonitorDAO
from diffwatch.models.monitor_model import Monitor

def test_get_waiting_monitors_calls_correct_sql(mock_db):
    conn, cursor = mock_db
    dao = MonitorDAO(conn)

    now = datetime.now(timezone.utc)
    fake_monitor = Monitor(
        id=uuid4(),
        name="test",
        user_id=uuid4(),
        url=HttpUrl("https://example.com"),
        selector="h1",
        hash="hash",
        check_freq=5,
        next_check_at=now,
        is_active=True,
        last_checked_at=now,
        created_at=now,
    )

    cursor.fetchall.return_value = [fake_monitor]

    
    results = dao.get_waiting_monitors(limit=5)

    assert len(results) == 1
    assert results[0].url == HttpUrl("https://example.com")

    cursor.execute.assert_called_once()