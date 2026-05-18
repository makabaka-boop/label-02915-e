"""通用响应模型"""
from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel

T = TypeVar("T")


class R(BaseModel, Generic[T]):
    """统一响应体"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

    @staticmethod
    def ok(data=None, message="success"):
        return R(code=200, message=message, data=data)

    @staticmethod
    def fail(message="操作失败", code=400):
        return R(code=code, message=message, data=None)


class PageResult(BaseModel, Generic[T]):
    """分页结果"""
    items: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 10
