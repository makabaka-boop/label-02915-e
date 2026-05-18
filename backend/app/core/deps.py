"""依赖注入"""
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import decode_token
from app.models.user import SysUser


def get_current_user(request: Request, db: Session = Depends(get_db)) -> SysUser:
    """从请求头解析当前登录用户"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或Token无效")

    token = auth_header[7:]
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token已过期或无效")

    user_id = int(payload.get("sub", 0))
    user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if user is None or user.status != 1:
        raise HTTPException(status_code=401, detail="用户不存在或已被禁用")

    return user
