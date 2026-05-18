"""认证模块测试"""
from tests.test_helpers import create_test_user, login, sha256


class TestAuth:
    def test_login_success(self, client):
        create_test_user(client)
        res = client.post("/api/auth/login", json={
            "username": "admin",
            "password": sha256("admin123"),
        })
        assert res.status_code == 200
        data = res.json()
        assert data["code"] == 200
        assert data["data"]["token"]
        assert data["data"]["username"] == "admin"

    def test_login_wrong_password(self, client):
        create_test_user(client)
        res = client.post("/api/auth/login", json={
            "username": "admin",
            "password": sha256("wrong"),
        })
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client):
        res = client.post("/api/auth/login", json={
            "username": "nobody",
            "password": sha256("test"),
        })
        assert res.status_code == 401

    def test_profile_with_token(self, client):
        token = login(client)
        res = client.get("/api/auth/profile", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["data"]["username"] == "admin"

    def test_profile_without_token(self, client):
        res = client.get("/api/auth/profile")
        assert res.status_code == 401
