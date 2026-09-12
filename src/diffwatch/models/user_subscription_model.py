from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_serializer


class UserSubscription(BaseModel):
    id: Optional[int] = None
    user_id: UUID
    plan_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool = True

    @field_serializer("started_at", "ended_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat()