from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_serializer

class User(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    email: EmailStr
    created_at: datetime

    @field_serializer("created_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat()