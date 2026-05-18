from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)
    nickname: str = Field("", max_length=50)
    status: int = Field(1, ge=0, le=1)


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    password: Optional[str] = Field(None, min_length=4, max_length=100)
    status: Optional[int] = Field(None, ge=0, le=1)


class UserVO(BaseModel):
    id: int
    username: str
    nickname: str
    avatar: str
    status: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
