"""FastAPI 应用入口"""
import os
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
import json
import sys
import uuid

from app.config import settings
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)
from app.core.deps import get_current_user
from app.core.rate_limit import get_global_limiter
from app.schemas.common import R
from app.routers import auth, products, categories, users, logs

# 启动时校验配置
settings.validate()

# 日志配置
logger.remove()
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO")

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


class UTF8JSONResponse(JSONResponse):
    """确保中文不被转义为 \\uXXXX"""
    media_type = "application/json; charset=utf-8"

    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    default_response_class=UTF8JSONResponse,
)

# 静态文件 — 图片上传目录
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局限流中间件
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # 静态资源和健康检查不限流
    if not request.url.path.startswith("/api/"):
        return await call_next(request)
    get_global_limiter().check(request)
    response = await call_next(request)
    return response

# 全局异常处理
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 注册路由
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(users.router)
app.include_router(logs.router)


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


@app.post("/api/upload", response_model=R)
async def upload_image(file: UploadFile = File(...), _=Depends(get_current_user)):
    """上传图片，返回访问 URL"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式，仅允许: {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    url = f"/uploads/{filename}"
    logger.info(f"上传图片: {file.filename} -> {url}")
    return R.ok(data={"url": url}, message="上传成功")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
