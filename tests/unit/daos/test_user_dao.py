import pytest
from datetime import datetime
from uuid import uuid4

from src.diffwatch.models.plan_model import Plan
from src.diffwatch.models.user_model import User
from src.diffwatch.daos.user_dao import UserDAO

@pytest.fixture
def insert_users(db_conn):
    now = datetime.now()

    user1 = User(id=uuid4(), email=f"user1@example.com", name="user 1", plan_id=1, created_at=now)
    user2 = User(id=uuid4(), email=f"user2@example.com", name="user 2", plan_id=1, created_at=now)

    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO users (id, email, name, plan_id, created_at) VALUES (%s, %s, %s, %s, %s);", (user1.id, user1.email, user1.name, user1.plan_id, user1.created_at))
        cur.execute("INSERT INTO users (id, email, name, plan_id, created_at) VALUES (%s, %s, %s, %s, %s);", (user2.id, user2.email, user2.name, user2.plan_id, user2.created_at))


    plan1 = Plan(id=100, name="new plan", price_cents=1000, max_active_monitors=5, min_check_freq_minutes=20, created_at=now)

    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO plans (id, name, price_cents, max_active_monitors, min_check_freq_minutes, created_at) VALUES (%s, %s, %s, %s, %s, %s)", (plan1.id, plan1.name, plan1.price_cents, plan1.max_active_monitors, plan1.min_check_freq_minutes, plan1.created_at))

    return {"plans": [plan1], "users": [user1, user2]}

def test_create_user(db_conn):
    dao = UserDAO(db_conn)

    user = User(id=uuid4(), email=f"user@example.com", name="user", plan_id=1, created_at=datetime.now())
    id = dao.create(user)

    assert id is not None

def test_get_by_id(db_conn, insert_users):
    dao = UserDAO(db_conn)
    expected_user = insert_users["users"][0]

    user = dao.get_by_id(expected_user.id)

    assert user is not None
    assert user.id == expected_user.id
    assert user.name == expected_user.name

def test_get_by_id_returns_none_for_unknown_user(db_conn, insert_users):
    dao = UserDAO(db_conn)
    result = dao.get_by_id(uuid4())
    assert result is None

def test_update_plan_successfully(db_conn, insert_users):
    dao = UserDAO(db_conn)
    user = insert_users["users"][0]
    new_plan = insert_users["plans"][0]
    result = dao.update_plan(user.id, new_plan.id)

    assert result

    fetched_user = dao.get_by_id(user.id)
    assert fetched_user is not None
    assert fetched_user.plan_id == new_plan.id