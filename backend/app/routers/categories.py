"""分类接口"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import R, PageResult
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryVO
from app.services import category_service
from app.core.deps import get_current_user
from app.core.log_utils import record_log
from app.models.user import SysUser

router = APIRouter(prefix="/api/categories", tags=["分类管理"])


@router.get("", response_model=R)
def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    items, total = category_service.get_category_page(db, page, page_size, keyword)
    return R.ok(data=PageResult[CategoryVO](items=items, total=total, page=page, page_size=page_size))


@router.get("/all", response_model=R)
def all_categories(db: Session = Depends(get_db), _: SysUser = Depends(get_current_user)):
    cats = category_service.get_all_categories(db)
    return R.ok(data=[CategoryVO.model_validate(c) for c in cats])


@router.post("", response_model=R)
def create_category(
    dto: CategoryCreate, request: Request,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    cat = category_service.create_category(db, dto)
    record_log(db, current_user.id, current_user.username, "分类", "新增",
               method="POST /api/categories", ip=request.client.host if request.client else "",
               params=dto.model_dump())
    return R.ok(data={"id": cat.id}, message="创建成功")


@router.put("/{cat_id}", response_model=R)
def update_category(
    cat_id: int, dto: CategoryUpdate, request: Request,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    try:
        category_service.update_category(db, cat_id, dto)
        record_log(db, current_user.id, current_user.username, "分类", "修改",
                   method=f"PUT /api/categories/{cat_id}", ip=request.client.host if request.client else "",
                   params=dto.model_dump(exclude_none=True))
        return R.ok(message="更新成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cat_id}", response_model=R)
def delete_category(
    cat_id: int, request: Request,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    try:
        category_service.delete_category(db, cat_id)
        record_log(db, current_user.id, current_user.username, "分类", "删除",
                   method=f"DELETE /api/categories/{cat_id}", ip=request.client.host if request.client else "")
        return R.ok(message="删除成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
