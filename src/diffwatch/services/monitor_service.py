from datetime import datetime, timezone, timedelta
from uuid import UUID

from diffwatch.models.monitor_model import Monitor
from diffwatch.models.check_log_model import CheckLog
from diffwatch.core.checker import check, CheckStatus
from diffwatch.core.logging import logger

from diffwatch.daos.monitor_dao import MonitorDAO
from diffwatch.daos.check_log_dao import CheckLogDAO
from diffwatch.daos.user_subscription_dao import UserSubscriptionDAO

from diffwatch.services.notification_service import NotificationService
from diffwatch.core.exceptions import UserNotFoundError, PlanNotFoundError, ValidationError, MonitorNotFoundError

class MonitorService:
    def __init__(
        self,
        monitor_dao: MonitorDAO,
        notification_service: NotificationService,
        log_dao: CheckLogDAO,
        user_subscription_dao: UserSubscriptionDAO
    ) -> None:
        self.monitor_dao = monitor_dao
        self.notification_service = notification_service
        self.log_dao = log_dao
        self.user_subscription_dao = user_subscription_dao

    def create_monitor(self, monitor: Monitor) -> UUID:
        plan = self.user_subscription_dao.get_active_plan_by_user_id(monitor.user_id)
        if plan is None:
            raise PlanNotFoundError(monitor.user_id)

        active_monitors = self.monitor_dao.count_active_by_user_id(monitor.user_id)
        if monitor.is_active and active_monitors >= plan.max_active_monitors:
            raise ValidationError(
                f"Active monitor limit reached for plan {plan.name}: "
                f"{plan.max_active_monitors}"
            )

        return self.monitor_dao.create(monitor)

    def _get_monitor_by_id(self, id: UUID) -> Monitor:
        monitor = self.monitor_dao.get_by_id(id)
        if monitor is None:
            raise MonitorNotFoundError(id)

        return monitor

    def process_monitor(self, id: UUID) -> None:
        now = datetime.now(timezone.utc)

        monitor = self._get_monitor_by_id(id)
        if monitor.id is None:
            raise ValidationError("Monitor should have a valid id")
        
        result = check(str(monitor.url), monitor.selector)

        if result.status != CheckStatus.OK:
            logger.warning(
                "Monitor %s check failed with status %s: %s",
                monitor.name,
                result.status.value,
                result.error or "no details",
            )

        has_changed = (result.status == CheckStatus.OK and result.hash != monitor.hash)

        has_notified = False
        try:
            if has_changed and monitor.hash is not None: 
                has_notified = self.notification_service.notify(monitor)
        except (UserNotFoundError, PlanNotFoundError) as ex:
            logger.warning("Skipping notification for monitor %s: %s", monitor.name, ex)

        next_check_at = now + timedelta(minutes=monitor.check_freq)
        new_hash = result.hash if result.hash is not None else monitor.hash
        self.monitor_dao.update(
            monitor_id=monitor.id,
            hash=new_hash,
            next_check_at=next_check_at,
            last_checked_at=now
        )

        log = CheckLog(
            user_id=monitor.user_id,
            monitor_id=monitor.id,
            status=result.status,
            http_status=result.http_status_code,
            has_notified=has_notified,
            prev_hash=monitor.hash,
            next_hash=result.hash,
            response_time=0.0, # TODO: calculate real response time
            error_message=result.error,
            created_at=now
        )

        self.log_dao.create(log)