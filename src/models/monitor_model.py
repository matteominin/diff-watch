from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl, field_serializer

class Monitor(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    url: HttpUrl
    selector: str = ""
    hash: Optional[str] = None
    check_freq: int

    next_check_at: datetime
    is_active: bool = True

    last_checked_at: Optional[datetime] = None
    created_at: datetime

    @field_serializer("next_check_at", "last_checked_at", "created_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat()