"""上传模块测试"""
import io
from tests.test_helpers import login, auth_header


class TestUpload:
    def test_upload_image(self, client):
        token = login(client)
        h = auth_header(token)

        # 创建一个假的 PNG 文件 (最小有效 PNG)
        fake_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        res = client.post("/api/upload", headers=h, files={
            "file": ("test.png", io.BytesIO(fake_png), "image/png"),
        })
        assert res.status_code == 200
        assert res.json()["data"]["url"].startswith("/uploads/")
        assert res.json()["data"]["url"].endswith(".png")

    def test_upload_invalid_extension(self, client):
        token = login(client)
        h = auth_header(token)

        res = client.post("/api/upload", headers=h, files={
            "file": ("test.exe", io.BytesIO(b"fake"), "application/octet-stream"),
        })
        assert res.status_code == 400

    def test_upload_without_auth(self, client):
        res = client.post("/api/upload", files={
            "file": ("test.png", io.BytesIO(b"fake"), "image/png"),
        })
        assert res.status_code == 401
