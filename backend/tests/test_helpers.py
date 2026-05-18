"""测试辅助函数"""
import hashlib

from app.core.security import hash_password


def sha256(text: str) -> str:
    """模拟前端 SHA-256 哈希"""
    return hashlib.sha256(text.encode()).hexdigest()


def create_test_user(client, username="admin", password="admin123", nickname="管理员"):
    """通过数据库直接创建测试用户"""
    from tests.conftest import TestingSessionLocal
    from app.models.user import SysUser

    db = TestingSessionLocal()
    user = SysUser(
        username=username,
        password_hash=hash_password(sha256(password)),
        nickname=nickname,
        status=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def login(client, username="admin", password="admin123"):
    """登录并返回 token"""
    create_test_user(client, username, password)
    res = client.post("/api/auth/login", json={
        "username": username,
        "password": sha256(password),
    })
    return res.json()["data"]["token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}
