"""用户管理接口"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import R, PageResult
from app.schemas.user import UserCreate, UserUpdate, UserVO
from app.services import user_service
from app.core.deps import get_current_user
from app.core.log_utils import record_log
from app.models.user import SysUser

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("", response_model=R)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    items, total = user_service.get_user_page(db, page, page_size, keyword)
    return R.ok(data=PageResult[UserVO](
        items=[UserVO.model_validate(u) for u in items],
        total=total, page=page, page_size=page_size,
    ))


@router.post("", response_model=R)
def create_user(
    dto: UserCreate, request: Request,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    try:
        user = user_service.create_user(db, dto)
        record_log(db, current_user.id, current_user.username, "用户", "新增",
                   method="POST /api/users", ip=request.client.host if request.client else "",
                   params={"username": dto.username, "nickname": dto.nickname, "status": dto.status})
        return R.ok(data={"id": user.id}, message="创建成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=R)
def update_user(
    user_id: int, dto: UserUpdate, request: Request,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    try:
        user_service.update_user(db, user_id, dto)
        log_params = dto.model_dump(exclude_none=True)
        log_params.pop("password", None)
        record_log(db, current_user.id, current_user.username, "用户", "修改",
                   method=f"PUT /api/users/{user_id}", ip=request.client.host if request.client else "",
                   params=log_params)
        return R.ok(message="更新成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", response_model=R)
def delete_user(
    user_id: int, request: Request,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    try:
        user_service.delete_user(db, user_id)
        record_log(db, current_user.id, current_user.username, "用户", "删除",
                   method=f"DELETE /api/users/{user_id}", ip=request.client.host if request.client else "")
        return R.ok(message="删除成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
