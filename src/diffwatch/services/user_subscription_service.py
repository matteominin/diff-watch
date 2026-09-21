from datetime import datetime, timezone
from uuid import UUID

from diffwatch.daos.user_subscription_dao import UserSubscriptionDAO
from diffwatch.models.user_subscription_model import UserSubscription


class UserSubscriptionService:
    def __init__(self, user_subscription_dao: UserSubscriptionDAO) -> None:
        self.user_subscription_dao = user_subscription_dao

    def subscribe(self, user_id: UUID, plan_id: int) -> int:
        subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan_id,
            started_at=datetime.now(timezone.utc),
        )
        return self.user_subscription_dao.create(subscription)