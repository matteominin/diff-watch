import pytest
from datetime import datetime
from uuid import uuid4

from diffwatch.models.user_model import User
from diffwatch.daos.user_dao import UserDAO

@pytest.fixture
def insert_users(db_conn):
    now = datetime.now()

    user1 = User(id=uuid4(), email=f"user1@example.com", name="user 1", created_at=now)
    user2 = User(id=uuid4(), email=f"user2@example.com", name="user 2", created_at=now)

    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO users (id, email, name, created_at) VALUES (%s, %s, %s, %s);", (user1.id, user1.email, user1.name, user1.created_at))
        cur.execute("INSERT INTO users (id, email, name, created_at) VALUES (%s, %s, %s, %s);", (user2.id, user2.email, user2.name, user2.created_at))

    return {"users": [user1, user2]}

def test_create_user(db_conn):
    dao = UserDAO(db_conn)

    user = User(id=uuid4(), email=f"user@example.com", name="user", created_at=datetime.now())
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
