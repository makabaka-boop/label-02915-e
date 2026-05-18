"""操作日志接口"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import R, PageResult
from app.schemas.log import LogVO
from app.models.log import OperationLog
from app.models.user import SysUser
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/logs", tags=["操作日志"])


@router.get("", response_model=R)
def list_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    module: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    allowed_modules = ["商品", "分类", "用户", "认证"]
    query = db.query(OperationLog).filter(OperationLog.module.in_(allowed_modules))
    if module:
        query = query.filter(OperationLog.module == module)
    total = query.count()
    items = query.order_by(OperationLog.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return R.ok(data=PageResult[LogVO](
        items=[LogVO.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size,
    ))
