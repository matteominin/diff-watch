import pytest
from unittest.mock import MagicMock

import respx
from httpx import Response 

from pathlib import Path

from uuid import uuid4
from datetime import datetime, timedelta
from pydantic import HttpUrl

from diffwatch.core.checker import CheckStatus, parse_and_hash
from diffwatch.models.monitor_model import Monitor
from diffwatch.services.monitor_service import MonitorService

FIXTURE_DIR = Path(__file__).parent.parent.parent / "fixtures" / "html_samples"
def _load_fixture(filename: str) -> str:
    return (FIXTURE_DIR / filename).read_text()

@pytest.fixture
def sample_monitor():
    return Monitor(
        id=uuid4(),
        user_id=uuid4(),
        name="test",
        url=HttpUrl("http://test.com"),
        check_freq=60,
        next_check_at=datetime.now(),
        created_at=datetime.now() - timedelta(minutes=60)
    )

@pytest.fixture
def notification_service():
    return MagicMock()

@pytest.fixture
def monitor_service(notification_service):
    return MonitorService(
        monitor_dao=MagicMock(),
        notification_service=notification_service,
        log_dao=MagicMock()
    )

def test_process_monitor_no_changes(monitor_service, sample_monitor, notification_service):
    html_content = _load_fixture("sample_page.html")
    sample_monitor.selector = "#product-price"
    sample_monitor.hash = parse_and_hash(html_content, sample_monitor.selector).hash

    with respx.mock:
        respx.get(str(sample_monitor.url)).mock(
            return_value=Response(status_code=200, text=html_content)
        )

        monitor_service.process_monitor(sample_monitor)

    notification_service.should_and_send_notification.assert_not_called()

    monitor_service.log_dao.create.assert_called_once()
    log = monitor_service.log_dao.create.call_args.args[0]
    assert log.user_id == sample_monitor.user_id
    assert log.monitor_id == sample_monitor.id
    assert log.status == CheckStatus.OK
    assert log.http_status == 200
    assert log.has_notified is False
    assert log.prev_hash == sample_monitor.hash
    assert log.next_hash == sample_monitor.hash


def test_process_monitor_detects_change(monitor_service, sample_monitor, notification_service):
    original_html = _load_fixture("sample_page.html")
    changed_html = original_html.replace("49.99", "59.99")
    sample_monitor.selector = "#product-price"
    sample_monitor.hash = parse_and_hash(original_html, sample_monitor.selector).hash
    notification_service.should_and_send_notification.return_value = True

    with respx.mock:
        respx.get(str(sample_monitor.url)).mock(
            return_value=Response(status_code=200, text=changed_html)
        )

        monitor_service.process_monitor(sample_monitor)

    notification_service.should_and_send_notification.assert_called_once_with(sample_monitor)

    monitor_service.log_dao.create.assert_called_once()
    log = monitor_service.log_dao.create.call_args.args[0]
    assert log.status == CheckStatus.OK
    assert log.has_notified is True
    assert log.prev_hash == sample_monitor.hash
    assert log.next_hash == parse_and_hash(changed_html, sample_monitor.selector).hash
    assert log.next_hash != log.prev_hash
