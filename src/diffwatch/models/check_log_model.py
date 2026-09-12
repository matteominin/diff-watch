from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_serializer

from diffwatch.core.checker import CheckStatus


class CheckLog(BaseModel):
    id: Optional[int] = None
    user_id: UUID
    monitor_id: UUID
    status: CheckStatus
    http_status: Optional[int]
    has_notified: bool = False
    prev_hash: Optional[str]
    next_hash: Optional[str]
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime

    @field_serializer("created_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat()