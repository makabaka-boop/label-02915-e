"""商品服务"""
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from loguru import logger

from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate, ProductVO


def get_product_page(
    db: Session,
    page: int,
    page_size: int,
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[int] = None,
) -> Tuple[List[ProductVO], int]:
    query = db.query(Product)
    if keyword:
        query = query.filter(Product.name.like(f"%{keyword}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if status is not None:
        query = query.filter(Product.status == status)
    total = query.count()
    items = query.order_by(Product.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 批量查分类名
    cat_ids = list({p.category_id for p in items})
    cat_map = {}
    if cat_ids:
        cats = db.query(Category).filter(Category.id.in_(cat_ids)).all()
        cat_map = {c.id: c.name for c in cats}

    vo_list = []
    for p in items:
        vo = ProductVO.model_validate(p)
        vo.category_name = cat_map.get(p.category_id, "")
        vo_list.append(vo)

    return vo_list, total


def get_product_by_id(db: Session, product_id: int) -> Optional[ProductVO]:
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        return None
    cat = db.query(Category).filter(Category.id == p.category_id).first()
    vo = ProductVO.model_validate(p)
    vo.category_name = cat.name if cat else ""
    return vo


def create_product(db: Session, dto: ProductCreate) -> Product:
    cat = db.query(Category).filter(Category.id == dto.category_id).first()
    if not cat:
        raise ValueError("分类不存在")
    product = Product(
        name=dto.name,
        category_id=dto.category_id,
        price=dto.price,
        stock=dto.stock,
        image=dto.image,
        description=dto.description,
        status=dto.status,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    logger.info(f"创建商品: {product.name} (id={product.id})")
    return product


def update_product(db: Session, product_id: int, dto: ProductUpdate) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError("商品不存在")
    if dto.category_id is not None:
        cat = db.query(Category).filter(Category.id == dto.category_id).first()
        if not cat:
            raise ValueError("分类不存在")
        product.category_id = dto.category_id
    for field in ["name", "price", "stock", "image", "description", "status"]:
        val = getattr(dto, field, None)
        if val is not None:
            setattr(product, field, val)
    db.commit()
    db.refresh(product)
    logger.info(f"更新商品: {product.name} (id={product.id})")
    return product


def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError("商品不存在")
    db.delete(product)
    db.commit()
    logger.info(f"删除商品: {product.name} (id={product_id})")
