"""分类服务"""
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from loguru import logger

from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category_page(
    db: Session, page: int, page_size: int, keyword: Optional[str] = None
) -> Tuple[List[Category], int]:
    query = db.query(Category)
    if keyword:
        query = query.filter(Category.name.like(f"%{keyword}%"))
    total = query.count()
    items = query.order_by(Category.sort_order.asc(), Category.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_all_categories(db: Session) -> List[Category]:
    return db.query(Category).filter(Category.status == 1).order_by(Category.sort_order.asc()).all()


def create_category(db: Session, dto: CategoryCreate) -> Category:
    cat = Category(name=dto.name, sort_order=dto.sort_order, status=dto.status)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    logger.info(f"创建分类: {cat.name} (id={cat.id})")
    return cat


def update_category(db: Session, cat_id: int, dto: CategoryUpdate) -> Category:
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise ValueError("分类不存在")
    if dto.name is not None:
        cat.name = dto.name
    if dto.sort_order is not None:
        cat.sort_order = dto.sort_order
    if dto.status is not None:
        cat.status = dto.status
    db.commit()
    db.refresh(cat)
    logger.info(f"更新分类: {cat.name} (id={cat.id})")
    return cat


def delete_category(db: Session, cat_id: int):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise ValueError("分类不存在")
    product_count = db.query(Product).filter(Product.category_id == cat_id).count()
    if product_count > 0:
        raise ValueError(f"该分类下有 {product_count} 个商品，无法删除")
    db.delete(cat)
    db.commit()
    logger.info(f"删除分类: {cat.name} (id={cat_id})")
