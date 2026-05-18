from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class LogVO(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: str
    module: str
    action: str
    method: str
    ip: str
    params: Optional[str] = None
    result: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
