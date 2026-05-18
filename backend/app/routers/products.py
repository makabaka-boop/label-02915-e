"""商品接口"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import R, PageResult
from app.schemas.product import ProductCreate, ProductUpdate, ProductVO
from app.services import product_service
from app.core.deps import get_current_user
from app.core.log_utils import record_log
from app.models.user import SysUser

router = APIRouter(prefix="/api/products", tags=["商品管理"])


@router.get("", response_model=R)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: SysUser = Depends(get_current_user),
):
    items, total = product_service.get_product_page(db, page, page_size, keyword, category_id, status)
    return R.ok(data=PageResult[ProductVO](items=items, total=total, page=page, page_size=page_size))


@router.get("/{product_id}", response_model=R)
def get_product(product_id: int, db: Session = Depends(get_db), _: SysUser = Depends(get_current_user)):
    vo = product_service.get_product_by_id(db, product_id)
    if not vo:
        raise HTTPException(status_code=404, detail="商品不存在")
    return R.ok(data=vo)


@router.post("", response_model=R)
def create_product(
    dto: ProductCreate, request: Request,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    try:
        product = product_service.create_product(db, dto)
        record_log(db, current_user.id, current_user.username, "商品", "新增",
                   method="POST /api/products", ip=request.client.host if request.client else "",
                   params=dto.model_dump())
        return R.ok(data={"id": product.id}, message="创建成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{product_id}", response_model=R)
def update_product(
    product_id: int, dto: ProductUpdate, request: Request,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    try:
        product_service.update_product(db, product_id, dto)
        record_log(db, current_user.id, current_user.username, "商品", "修改",
                   method=f"PUT /api/products/{product_id}", ip=request.client.host if request.client else "",
                   params=dto.model_dump(exclude_none=True))
        return R.ok(message="更新成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{product_id}", response_model=R)
def delete_product(
    product_id: int, request: Request,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    try:
        product_service.delete_product(db, product_id)
        record_log(db, current_user.id, current_user.username, "商品", "删除",
                   method=f"DELETE /api/products/{product_id}", ip=request.client.host if request.client else "")
        return R.ok(message="删除成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
