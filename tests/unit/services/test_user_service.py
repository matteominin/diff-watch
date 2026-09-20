from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from diffwatch.models.user_model import User
from diffwatch.services.user_service import UserService


def test_create_user_delegates_to_dao():
    user_dao = MagicMock()
    user = User(
        email="user@example.com",
        name="User",
        created_at=datetime(2026, 9, 21, tzinfo=timezone.utc),
    )
    user_id = uuid4()
    user_dao.create.return_value = user_id
    service = UserService(user_dao)

    assert service.create_user(user) == user_id
    user_dao.create.assert_called_once_with(user)