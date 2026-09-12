from datetime import datetime, timezone
from uuid import uuid4

import pytest

from diffwatch.daos.user_subscription_dao import UserSubscriptionDAO
from diffwatch.models.user_subscription_model import UserSubscription


@pytest.fixture
def subscription_dependencies(db_conn):
    with db_conn.cursor() as cur:
        user_id = uuid4()
        cur.execute(
            "INSERT INTO users (id, email, name, plan_id, created_at) VALUES (%s, %s, %s, %s, %s)",
            (user_id, "user@example.com", "Test user", 1, datetime.now(timezone.utc)),
        )

    return user_id, 1


def test_create(db_conn, subscription_dependencies):
    user_id, plan_id = subscription_dependencies
    subscription = UserSubscription(
        user_id=user_id,
        plan_id=plan_id,
        started_at=datetime.now(timezone.utc),
    )

    dao = UserSubscriptionDAO(db_conn)
    subscription_id = dao.create(subscription)

    assert subscription_id is not None


def test_get_by_id(db_conn, subscription_dependencies):
    user_id, plan_id = subscription_dependencies
    subscription = UserSubscription(
        user_id=user_id,
        plan_id=plan_id,
        started_at=datetime.now(timezone.utc),
    )
    dao = UserSubscriptionDAO(db_conn)
    subscription_id = dao.create(subscription)

    result = dao.get_by_id(subscription_id)

    assert result is not None
    assert result.id == subscription_id
    assert result.user_id == user_id
    assert result.plan_id == plan_id


def test_get_by_id_returns_none_for_unknown_subscription(db_conn):
    dao = UserSubscriptionDAO(db_conn)
    result = dao.get_by_id(999)

    assert result is None


def test_get_by_user_id(db_conn, subscription_dependencies):
    user_id, plan_id = subscription_dependencies
    dao = UserSubscriptionDAO(db_conn)
    subscription = UserSubscription(
        user_id=user_id,
        plan_id=plan_id,
        started_at=datetime.now(timezone.utc),
    )
    dao.create(subscription)

    results = dao.get_by_user_id(user_id)

    assert len(results) == 1
    assert results[0].user_id == user_id


def test_end_subscription(db_conn, subscription_dependencies):
    user_id, plan_id = subscription_dependencies
    dao = UserSubscriptionDAO(db_conn)
    subscription_id = dao.create(
        UserSubscription(
            user_id=user_id,
            plan_id=plan_id,
            started_at=datetime.now(timezone.utc),
        )
    )
    ended_at = datetime.now(timezone.utc)

    result = dao.end(subscription_id, ended_at)

    assert result is True
    subscription = dao.get_by_id(subscription_id)
    assert subscription is not None
    assert subscription.ended_at is not None
    assert subscription.is_active is False