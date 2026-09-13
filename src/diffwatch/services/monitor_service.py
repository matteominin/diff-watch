from datetime import datetime, timezone, timedelta

from src.diffwatch.models.monitor_model import Monitor
from src.diffwatch.models.check_log_model import CheckLog
from src.diffwatch.core.checker import check, CheckStatus

from src.diffwatch.daos.monitor_dao import MonitorDAO
from src.diffwatch.daos.check_log_dao import CheckLogDAO

from src.diffwatch.services.notification_service import NotificationService

class MonitorService:
    def __init__(self, monitor_dao: MonitorDAO, notification_service: NotificationService,log_dao: CheckLogDAO) -> None:
        self.monitor_dao = monitor_dao
        self.notification_service = notification_service
        self.log_dao = log_dao

    def process_monitor(self, monitor: Monitor) -> None:
        if monitor.id is None:
            return # TODO: error handling

        now = datetime.now(timezone.utc)
        result = check(str(monitor.url), monitor.selector)

        has_changed = (result.status == CheckStatus.OK and result.hash != monitor.hash)

        has_notified = False
        if has_changed: 
            has_notified = self.notification_service.should_and_send_notification(monitor)

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
            error_message=result.error if hasattr(result, 'error') else None,
            created_at=now
        )

        self.log_dao.create(log)