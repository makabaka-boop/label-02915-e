"""全局异常处理"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import json


class UTF8JSONResponse(JSONResponse):
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


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} | path={request.url.path}")
    return UTF8JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = "; ".join([f"{e.get('loc', '')}: {e.get('msg', '')}" for e in errors])
    logger.warning(f"参数校验失败: {msg} | path={request.url.path}")
    return UTF8JSONResponse(
        status_code=422,
        content={"code": 422, "message": f"参数校验失败: {msg}", "data": None},
    )


async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"未处理异常: {exc} | path={request.url.path}")
    return UTF8JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None},
    )
