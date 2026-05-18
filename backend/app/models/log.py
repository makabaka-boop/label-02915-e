from sqlalchemy import Column, BigInteger, String, DateTime, Text
from sqlalchemy.sql import func

from app.database import Base


class OperationLog(Base):
    __tablename__ = "operation_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True)
    username = Column(String(50), nullable=False, default="")
    module = Column(String(50), nullable=False, default="")
    action = Column(String(50), nullable=False, default="")
    method = Column(String(200), nullable=False, default="")
    ip = Column(String(50), nullable=False, default="")
    params = Column(Text)
    result = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
