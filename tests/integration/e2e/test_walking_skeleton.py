from unittest.mock import patch

from psycopg import Connection
from datetime import datetime, timezone, timedelta
from pydantic import HttpUrl

from diffwatch.core.checker import CheckResult, CheckStatus

from diffwatch.models.plan_model import Plan
from diffwatch.models.user_model import User
from diffwatch.models.monitor_model import Monitor

from diffwatch.daos.plan_dao import PlanDAO
from diffwatch.daos.user_dao import UserDAO
from diffwatch.daos.monitor_dao import MonitorDAO
from diffwatch.daos.user_subscription_dao import UserSubscriptionDAO
from diffwatch.daos.check_log_dao import CheckLogDAO

from diffwatch.services.user_service import UserService
from diffwatch.services.monitor_service import MonitorService
from diffwatch.services.notification_service import NotificationService
from diffwatch.services.user_subscription_service import UserSubscriptionService

def test_walking_skeleton_e2e(db_conn: Connection):
    now = datetime.now(timezone.utc)

    plan_dao = PlanDAO(db_conn)
    user_dao = UserDAO(db_conn)
    user_service = UserService(user_dao)
    subscription_dao = UserSubscriptionDAO(db_conn)
    check_log_dao = CheckLogDAO(db_conn)
    monitor_dao = MonitorDAO(db_conn)

    subscription_service = UserSubscriptionService(subscription_dao)

    monitor_service = MonitorService(
        monitor_dao=monitor_dao,
        notification_service=NotificationService(
            subscription_dao,
            check_log_dao,
            user_dao,
        ),
        log_dao=check_log_dao,
        user_subscription_dao=subscription_dao,
    )

    # Database Seed
    plan = Plan(name="Test Plan", price_cents=10, max_active_monitors=1, max_notifications_per_day=1, min_check_freq_minutes=10, created_at=now);
    plan_id = plan_dao.create(plan)

    user = User(name="Test User", email="test@example.com", created_at=now)
    user_id = user_service.create_user(user)

    subscription_id = subscription_service.subscribe(user_id, plan_id)

    monitor_in = Monitor(user_id=user_id, name="Test Monitor", url=HttpUrl("http://test.com"), check_freq=10, next_check_at=now - timedelta(minutes=1), created_at=now)
    monitor_id = monitor_service.create_monitor(monitor_in)
    monitor = monitor_dao.get_by_id(monitor_id)

    assert plan_id is not None
    assert user_id is not None
    assert subscription_id is not None
    assert monitor is not None
    assert monitor.id is not None

    with patch("diffwatch.services.monitor_service.check") as mock_check:

        # First Check
        hash_v1 = "first hash"
        mock_check.return_value = CheckResult(CheckStatus.OK, hash_v1)
        monitor_service.process_monitor(monitor_id)

        mock_check.assert_called_once_with(str(monitor.url), monitor.selector)
        updated_monitor = monitor_dao.get_by_id(monitor_id)

        assert updated_monitor is not None
        assert updated_monitor.hash == hash_v1
        assert updated_monitor.next_check_at > now
        assert updated_monitor.last_checked_at is not None
        assert updated_monitor.last_checked_at >= now

        logs = check_log_dao.get_by_monitor_id(monitor_id)
        assert len(logs) == 1
        assert logs[0].status == CheckStatus.OK
        assert logs[0].has_notified is False
        assert logs[0].prev_hash is None
        assert logs[0].next_hash == hash_v1

        # Second Check (same hash)
        now = datetime.now(timezone.utc)
        monitor_service.process_monitor(monitor_id)
        updated_monitor = monitor_dao.get_by_id(monitor_id)

        assert updated_monitor is not None
        assert updated_monitor.hash == hash_v1
        assert updated_monitor.next_check_at > now
        assert updated_monitor.last_checked_at is not None
        assert updated_monitor.last_checked_at >= now

        logs = check_log_dao.get_by_monitor_id(monitor_id)
        assert len(logs) == 2
        assert logs[0].status == CheckStatus.OK
        assert logs[0].has_notified is False
        assert logs[0].prev_hash == hash_v1
        assert logs[0].next_hash == hash_v1

        # Third Check (different hash)
        hash_v2 = "second hash"
        mock_check.return_value = CheckResult(CheckStatus.OK, hash=hash_v2)

        now = datetime.now(timezone.utc)
        monitor_service.process_monitor(monitor_id)
        updated_monitor = monitor_dao.get_by_id(monitor_id)

        assert updated_monitor is not None
        assert updated_monitor.hash == hash_v2
        assert updated_monitor.next_check_at > now
        assert updated_monitor.last_checked_at is not None
        assert updated_monitor.last_checked_at >= now

        logs = check_log_dao.get_by_monitor_id(monitor_id)
        assert len(logs) == 3
        assert logs[0].status == CheckStatus.OK
        assert logs[0].has_notified is True
        assert logs[0].prev_hash == hash_v1
        assert logs[0].next_hash == hash_v2

        # Fourth Check (exceeded notification limit)
        hash_v3 = "third hash"
        mock_check.return_value = CheckResult(CheckStatus.OK, hash=hash_v3)
        monitor_service.process_monitor(monitor_id)

        updated_monitor = monitor_dao.get_by_id(monitor_id)

        assert updated_monitor is not None
        assert updated_monitor.hash == hash_v3
        assert updated_monitor.next_check_at > now
        assert updated_monitor.last_checked_at is not None
        assert updated_monitor.last_checked_at >= now

        logs = check_log_dao.get_by_monitor_id(monitor_id)
        assert len(logs) == 4
        assert logs[0].status == CheckStatus.OK
        assert logs[0].has_notified is False
        assert logs[0].prev_hash == hash_v2
        assert logs[0].next_hash == hash_v3