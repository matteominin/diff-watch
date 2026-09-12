from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_serializer

class Plan(BaseModel):
    id: Optional[int] = None
    name: str
    price_cents: int = 0
    max_active_monitors: int
    min_check_freq_minutes: int
    max_notifications_per_day: int = 50
    created_at: datetime

    @field_serializer("created_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat()