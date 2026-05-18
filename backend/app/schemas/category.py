from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sort_order: int = Field(0, ge=0)
    status: int = Field(1, ge=0, le=1)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    sort_order: Optional[int] = Field(None, ge=0)
    status: Optional[int] = Field(None, ge=0, le=1)


class CategoryVO(BaseModel):
    id: int
    name: str
    sort_order: int
    status: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
