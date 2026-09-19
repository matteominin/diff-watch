from uuid import UUID
from datetime import datetime, timezone, timedelta

from diffwatch.models.monitor_model import Monitor

from diffwatch.daos.user_subscription_dao import UserSubscriptionDAO
from diffwatch.daos.check_log_dao import CheckLogDAO

class NotificationService:
    def __init__(self, subscription_dao: UserSubscriptionDAO, log_dao: CheckLogDAO) -> None:
        self.subscription_dao = subscription_dao
        self.log_dao = log_dao

    def should_and_send_notification(self, monitor: Monitor) -> bool:
        plan = self.subscription_dao.get_active_plan_by_user_id(monitor.user_id)
        if plan is None:
            raise Exception("Failed to fetch plan data")

        now = datetime.now(timezone.utc)
        one_day_ago = now - timedelta(days=1)
        start_date = min(one_day_ago, plan.created_at)

        notifications_sent_24h = self.log_dao.count_notifications_since(monitor.user_id, start_date)

        if notifications_sent_24h >= plan.max_notifications_per_day:
            return False

        # TODO: send notification
        return True
        
