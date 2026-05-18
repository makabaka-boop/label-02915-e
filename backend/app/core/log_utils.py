"""操作日志工具"""
import json
from typing import Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.log import OperationLog


def record_log(
    db: Session,
    user_id: Optional[int],
    username: str,
    module: str,
    action: str,
    method: str = "",
    ip: str = "",
    params: Optional[dict] = None,
    result: Optional[str] = None,
):
    """记录操作日志"""
    try:
        log_entry = OperationLog(
            user_id=user_id,
            username=username,
            module=module,
            action=action,
            method=method,
            ip=ip,
            params=json.dumps(params, ensure_ascii=False, default=str) if params else None,
            result=result,
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"记录操作日志失败: {e}")
        db.rollback()
