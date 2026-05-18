from sqlalchemy import Column, BigInteger, String, SmallInteger, Integer, DateTime, DECIMAL, Text
from sqlalchemy.sql import func

from app.database import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category_id = Column(BigInteger, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    stock = Column(Integer, nullable=False, default=0)
    image = Column(String(500), nullable=False, default="")
    description = Column(Text)
    status = Column(SmallInteger, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
