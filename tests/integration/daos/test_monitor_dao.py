import pytest

from datetime import datetime, timezone, timedelta
from uuid import uuid4
from pydantic import HttpUrl

from diffwatch.models.user_model import User
from diffwatch.models.monitor_model import Monitor

from diffwatch.daos.monitor_dao import MonitorDAO

@pytest.fixture
def insert_test_data(db_conn):
    now = datetime.now(timezone.utc)

    # Create Users 
    user1 = User(id=uuid4(), email=f"user1-{uuid4()}@example.com", name="user 1", plan_id=1, created_at=now)
    user2 = User(id=uuid4(), email=f"user2-{uuid4()}@example.com", name="user 2", plan_id=1, created_at=now)

    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO users (id, email, name, plan_id, created_at) VALUES (%s, %s, %s, %s, %s);", (user1.id, user1.email, user1.name, user1.plan_id, user1.created_at))
        cur.execute("INSERT INTO users (id, email, name, plan_id, created_at) VALUES (%s, %s, %s, %s, %s);", (user2.id, user2.email, user2.name, user2.plan_id, user2.created_at))

    assert user1.id is not None
    assert user2.id is not None

    # Create Monitors
    monitors = [
        Monitor(id=uuid4(), user_id=user1.id, name="Expired", url=HttpUrl("https://example.com/1"), selector="h1", check_freq=60, next_check_at=now - timedelta(minutes=20), is_active=True, created_at=now),
        Monitor(id=uuid4(), user_id=user1.id, name="EDGE, Expired Now", url=HttpUrl("https://example.com/edge"), selector=".price", check_freq=30, next_check_at=now, is_active=True, created_at=now),
        Monitor(id=uuid4(), user_id=user1.id, name="Not Expired", url=HttpUrl("https://example.com/future"), selector="div", check_freq=60, next_check_at=now + timedelta(minutes=30), is_active=True, created_at=now),
        Monitor(id=uuid4(), user_id=user2.id, name="Deactivated", url=HttpUrl("https://example.com/off"), selector="#main", check_freq=60, next_check_at=now - timedelta(minutes=10), is_active=False, created_at=now),
        Monitor(id=uuid4(), user_id=user2.id, name="User2 Expired", url=HttpUrl("https://example.com/u2"), selector="span", check_freq=15, next_check_at=now - timedelta(minutes=5), is_active=True, created_at=now)
    ]
    
    with db_conn.cursor() as cur:
        for m in monitors:
            cur.execute(
                "INSERT INTO monitors (id, user_id, name, url, selector, check_freq, next_check_at, is_active, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                (m.id, m.user_id, m.name, str(m.url), m.selector, m.check_freq, m.next_check_at, m.is_active, m.created_at)
            )

    db_conn.commit()

    return {"users": [user1, user2], "monitors": monitors, "now": now}

def test_get_waiting_monitors(db_conn, insert_test_data):
    all_monitors = insert_test_data["monitors"]
    req_ids = {all_monitors[0].id, all_monitors[1].id, all_monitors[4].id}

    dao = MonitorDAO(db_conn)
    results = dao.get_waiting_monitors(limit=5)

    assert len(results) == 3

    returned_ids = {m.id for m in results}
    assert returned_ids == req_ids

def test_create(db_conn, insert_test_data):
    user = insert_test_data["users"][0]
    now = insert_test_data["now"]
    monitor = Monitor(
        user_id=user.id,
        name="New monitor",
        url=HttpUrl("https://example.com/new"),
        selector="main",
        check_freq=30,
        next_check_at=now,
        created_at=now,
    )

    dao = MonitorDAO(db_conn)
    monitor_id = dao.create(monitor)

    assert monitor_id is not None

def test_get_by_id(db_conn, insert_test_data):
    monitor = insert_test_data["monitors"][0]
    dao = MonitorDAO(db_conn)

    result = dao.get_by_id(monitor.id)

    assert result is not None
    assert result.id == monitor.id
    assert result.name == monitor.name

def test_get_by_id_returns_none_for_unknown_monitor(db_conn, insert_test_data):
    dao = MonitorDAO(db_conn)

    result = dao.get_by_id(uuid4())

    assert result is None

def test_get_by_user_id(db_conn, insert_test_data):
    user = insert_test_data["users"][0]
    dao = MonitorDAO(db_conn)

    results = dao.get_by_user_id(user.id)

    assert len(results) == 3
    assert all(monitor.user_id == user.id for monitor in results)

def test_update_monitor(db_conn, insert_test_data):
    monitor = insert_test_data["monitors"][0]
    dao = MonitorDAO(db_conn)

    result = dao.update(
        monitor.id,
        name="Updated monitor",
        selector="article",
        check_freq=15,
        is_active=False,
    )

    assert result is not None
    assert result.id == monitor.id
    assert result.name == "Updated monitor"
    assert result.selector == "article"
    assert result.check_freq == 15
    assert result.is_active is False

def test_update_unknown_monitor_returns_none(db_conn, insert_test_data):
    dao = MonitorDAO(db_conn)

    result = dao.update(uuid4(), name="Missing monitor")

    assert result is None