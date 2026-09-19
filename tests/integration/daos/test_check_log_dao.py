from datetime import datetime, timezone, timedelta
from uuid import uuid4

import pytest

from diffwatch.core.checker import CheckStatus
from diffwatch.daos.check_log_dao import CheckLogDAO
from diffwatch.models.check_log_model import CheckLog

FIXED_NOW = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def check_log_dependencies(db_conn):
    user_id = uuid4()
    monitor_id = uuid4()
    now = datetime.now(timezone.utc)

    with db_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (id, email, name, created_at) VALUES (%s, %s, %s, %s)",
            (user_id, f"user@example.com", "Test user", now),
        )
        cur.execute(
            """
            INSERT INTO monitors
                (id, user_id, name, url, selector, check_freq, next_check_at, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (monitor_id, user_id, "Test monitor", "https://example.com", "body", 60, now, now),
        )

    return user_id, monitor_id


def make_check_log(user_id, monitor_id):
    return CheckLog(
        user_id=user_id,
        monitor_id=monitor_id,
        status=CheckStatus.OK,
        http_status=200,
        prev_hash="old-hash",
        next_hash="new-hash",
        response_time=0.42,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def notification_count_dependencies(db_conn, check_log_dependencies):
    user_id, monitor_id = check_log_dependencies
    other_user_id = uuid4()
    other_monitor_id = uuid4()

    with db_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (id, email, name, created_at) VALUES (%s, %s, %s, %s)",
            (other_user_id, "other@example.com", "Other user", FIXED_NOW),
        )
        cur.execute(
            """
            INSERT INTO monitors
                (id, user_id, name, url, selector, check_freq, next_check_at, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                other_monitor_id,
                other_user_id,
                "Other monitor",
                "https://example.org",
                "body",
                60,
                FIXED_NOW,
                FIXED_NOW,
            ),
        )

    dao = CheckLogDAO(db_conn)
    logs = [
        CheckLog(
            user_id=user_id,
            monitor_id=monitor_id,
            status=CheckStatus.OK,
            http_status=200,
            has_notified=True,
            prev_hash="hash-1",
            next_hash="hash-2",
            created_at=FIXED_NOW - timedelta(days=10),
        ),
        CheckLog(
            user_id=user_id,
            monitor_id=monitor_id,
            status=CheckStatus.OK,
            http_status=200,
            has_notified=True,
            prev_hash="hash-2",
            next_hash="hash-3",
            created_at=FIXED_NOW - timedelta(days=11),
        ),
        CheckLog(
            user_id=user_id,
            monitor_id=monitor_id,
            status=CheckStatus.OK,
            http_status=200,
            has_notified=False,
            prev_hash="hash-3",
            next_hash="hash-4",
            created_at=FIXED_NOW - timedelta(days=5),
        ),
        CheckLog(
            user_id=other_user_id,
            monitor_id=other_monitor_id,
            status=CheckStatus.OK,
            http_status=200,
            has_notified=True,
            prev_hash="other-1",
            next_hash="other-2",
            created_at=FIXED_NOW - timedelta(days=5),
        ),
    ]

    for log in logs:
        dao.create(log)

    return user_id


def test_create(db_conn, check_log_dependencies):
    user_id, monitor_id = check_log_dependencies
    dao = CheckLogDAO(db_conn)

    check_log_id = dao.create(make_check_log(user_id, monitor_id))

    assert check_log_id is not None


def test_get_by_id(db_conn, check_log_dependencies):
    user_id, monitor_id = check_log_dependencies
    dao = CheckLogDAO(db_conn)
    check_log_id = dao.create(make_check_log(user_id, monitor_id))

    result = dao.get_by_id(check_log_id)

    assert result is not None
    assert result.id == check_log_id
    assert result.status is CheckStatus.OK
    assert result.http_status == 200
    assert result.has_notified is False


def test_get_by_id_returns_none_for_unknown_check_log(db_conn):
    dao = CheckLogDAO(db_conn)

    result = dao.get_by_id(999)

    assert result is None


def test_get_by_monitor_id(db_conn, check_log_dependencies):
    user_id, monitor_id = check_log_dependencies
    dao = CheckLogDAO(db_conn)
    dao.create(make_check_log(user_id, monitor_id))

    results = dao.get_by_monitor_id(monitor_id)

    assert len(results) == 1
    assert results[0].monitor_id == monitor_id

def test_count_notifications_since_counts_only_matching_notifications(
    db_conn, notification_count_dependencies
):
    dao = CheckLogDAO(db_conn)
    user_id = notification_count_dependencies
    start_date = FIXED_NOW - timedelta(days=10)

    result = dao.count_notifications_since(user_id, start_date)

    assert result == 1


def test_count_notifications_since_returns_zero_without_logs(
    db_conn, check_log_dependencies
):
    dao = CheckLogDAO(db_conn)
    user_id, _ = check_log_dependencies

    result = dao.count_notifications_since(user_id, FIXED_NOW)

    assert result == 0