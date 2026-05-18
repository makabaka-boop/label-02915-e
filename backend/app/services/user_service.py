"""用户服务"""
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from loguru import logger

from app.models.user import SysUser
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


def get_user_page(
    db: Session, page: int, page_size: int, keyword: Optional[str] = None
) -> Tuple[List[SysUser], int]:
    query = db.query(SysUser)
    if keyword:
        query = query.filter(
            SysUser.username.like(f"%{keyword}%") | SysUser.nickname.like(f"%{keyword}%")
        )
    total = query.count()
    items = query.order_by(SysUser.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def create_user(db: Session, dto: UserCreate) -> SysUser:
    exists = db.query(SysUser).filter(SysUser.username == dto.username).first()
    if exists:
        raise ValueError(f"用户名 '{dto.username}' 已存在")
    user = SysUser(
        username=dto.username,
        password_hash=hash_password(dto.password),
        nickname=dto.nickname,
        status=dto.status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"创建用户: {user.username} (id={user.id})")
    return user


def update_user(db: Session, user_id: int, dto: UserUpdate) -> SysUser:
    user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not user:
        raise ValueError("用户不存在")
    if dto.nickname is not None:
        user.nickname = dto.nickname
    if dto.password is not None:
        user.password_hash = hash_password(dto.password)
    if dto.status is not None:
        user.status = dto.status
    db.commit()
    db.refresh(user)
    logger.info(f"更新用户: {user.username} (id={user.id})")
    return user


def delete_user(db: Session, user_id: int):
    user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not user:
        raise ValueError("用户不存在")
    if user.username == "admin":
        raise ValueError("不能删除超级管理员")
    db.delete(user)
    db.commit()
    logger.info(f"删除用户: {user.username} (id={user_id})")
