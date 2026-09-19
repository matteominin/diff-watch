from uuid import UUID
from datetime import datetime, timezone, timedelta

from diffwatch.models.monitor_model import Monitor

from diffwatch.core.exceptions import UserNotFoundError, PlanNotFoundError, ValidationError

from diffwatch.daos.user_subscription_dao import UserSubscriptionDAO
from diffwatch.daos.check_log_dao import CheckLogDAO
from diffwatch.daos.user_dao import UserDAO

class NotificationService:
    def __init__(self, subscription_dao: UserSubscriptionDAO, log_dao: CheckLogDAO, user_dao: UserDAO) -> None:
        self.subscription_dao = subscription_dao
        self.log_dao = log_dao
        self.user_dao = user_dao

    def should_notify(self, monitor: Monitor) -> bool:
        if monitor.id is None:
            raise ValidationError("Monitor id can't be None")

        plan = self.subscription_dao.get_active_plan_by_user_id(monitor.user_id)
        if plan is None:
            raise PlanNotFoundError(monitor.user_id)

        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=1)

        notifications_sent_24h = self.log_dao.count_notifications_since(monitor.user_id, start_date)

        if notifications_sent_24h >= plan.max_notifications_per_day:
            return False

        return True

    def notify(self, monitor: Monitor) -> bool:
        if not self.should_notify(monitor):
            return False

        user = self.user_dao.get_by_id(monitor.user_id)
        if user is None: 
            raise UserNotFoundError(monitor.user_id)

        print(monitor.name + " has changed " + user.email + " notified") # TODO: replace with real notificaiton

        return True