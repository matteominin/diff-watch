from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from diffwatch.models.user_subscription_model import UserSubscription
from diffwatch.services.user_subscription_service import UserSubscriptionService


def test_subscribe_creates_active_user_subscription():
    user_subscription_dao = MagicMock()
    subscription_id = 1
    user_subscription_dao.create.return_value = subscription_id
    service = UserSubscriptionService(user_subscription_dao)
    user_id = uuid4()

    result = service.subscribe(user_id=user_id, plan_id=2)

    assert result == subscription_id
    created_subscription = user_subscription_dao.create.call_args.args[0]
    assert isinstance(created_subscription, UserSubscription)
    assert created_subscription.user_id == user_id
    assert created_subscription.plan_id == 2
    assert created_subscription.is_active is True
    assert created_subscription.started_at.tzinfo == timezone.utc