from typing import Optional
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from pydantic import BaseModel, Field, field_validator


def _validate_price_decimals(v: Decimal) -> Decimal:
    """校验价格最多 2 位小数"""
    if v is None:
        return v
    try:
        rounded = v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        raise ValueError("价格数值无效")
    if v != rounded:
        raise ValueError("价格最多保留 2 位小数")
    return v


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category_id: int = Field(..., gt=0)
    price: Decimal = Field(..., ge=0)
    stock: int = Field(0, ge=0)
    image: str = Field("", max_length=500)
    description: Optional[str] = None
    status: int = Field(1, ge=0, le=1)

    @field_validator("price")
    @classmethod
    def check_price_decimals(cls, v: Decimal) -> Decimal:
        return _validate_price_decimals(v)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category_id: Optional[int] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    image: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    status: Optional[int] = Field(None, ge=0, le=1)

    @field_validator("price")
    @classmethod
    def check_price_decimals(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is None:
            return v
        return _validate_price_decimals(v)


class ProductVO(BaseModel):
    id: int
    name: str
    category_id: int
    category_name: Optional[str] = ""
    price: Decimal
    stock: int
    image: str
    description: Optional[str] = None
    status: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
