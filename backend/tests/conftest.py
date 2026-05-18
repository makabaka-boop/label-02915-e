"""测试配置 — 使用 SQLite 内存数据库，无需 MySQL"""
import os
import pytest

# 设置测试环境变量（必须在导入 app 之前）
os.environ["DB_HOST"] = "localhost"
os.environ["DB_USER"] = "test"
os.environ["DB_PASSWORD"] = "test"
os.environ["DB_NAME"] = "test"
os.environ["JWT_SECRET"] = "test-secret-key"
os.environ["UPLOAD_DIR"] = "/tmp/test-uploads"

# ---- 让 BigInteger 在 SQLite 上映射为 INTEGER（支持 autoincrement）----
from sqlalchemy import BigInteger, Integer, event
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bi_to_int(element, compiler, **kw):
    return compiler.visit_INTEGER(element, **kw)

# ---- 创建 SQLite 内存引擎 ----
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---- 猴子补丁：替换 database 模块的引擎，避免 MySQL 连接 ----
import app.database as db_module
db_module.engine = engine
db_module.SessionLocal = TestingSessionLocal

# ---- 现在可以安全导入 app ----
from app.database import Base, get_db
from app.main import app as fastapi_app


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """每个测试前重建表并重置限流器"""
    os.makedirs("/tmp/test-uploads", exist_ok=True)
    Base.metadata.create_all(bind=engine)

    # 重置限流器，避免跨测试累积
    from app.core.rate_limit import get_global_limiter, get_login_limiter
    get_global_limiter().reset()
    get_login_limiter().reset()

    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(fastapi_app)
