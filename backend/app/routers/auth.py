"""认证接口"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.common import R
from app.schemas.user import UserVO
from app.models.user import SysUser
from app.core.security import verify_password, create_token
from app.core.deps import get_current_user
from app.core.rate_limit import get_login_limiter
from app.core.log_utils import record_log

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=R)
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    # 登录接口独立限流：每 IP 每分钟最多 5 次
    get_login_limiter().check(request)

    user = db.query(SysUser).filter(SysUser.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = create_token(user.id, user.username)
    record_log(db, user.id, user.username, "认证", "登录",
               method="POST /api/auth/login", ip=request.client.host if request.client else "")
    return R.ok(data=LoginResponse(
        token=token, username=user.username,
        nickname=user.nickname, user_id=user.id,
    ))


@router.post("/logout", response_model=R)
def logout(request: Request, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    record_log(db, current_user.id, current_user.username, "认证", "登出",
               method="POST /api/auth/logout", ip=request.client.host if request.client else "")
    return R.ok(message="已登出")


@router.get("/profile", response_model=R)
def profile(current_user: SysUser = Depends(get_current_user)):
    return R.ok(data=UserVO.model_validate(current_user))
