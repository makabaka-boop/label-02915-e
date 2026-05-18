"""边界测试用例 — 覆盖参数校验、权限、异常路径等"""
import io
from tests.test_helpers import create_test_user, login, auth_header, sha256


class TestAuthEdgeCases:
    """认证边界测试"""

    def test_login_empty_username(self, client):
        """用户名为空"""
        res = client.post("/api/auth/login", json={"username": "", "password": "x"})
        assert res.status_code == 422

    def test_login_empty_password(self, client):
        """密码为空"""
        res = client.post("/api/auth/login", json={"username": "admin", "password": ""})
        assert res.status_code == 422

    def test_login_missing_fields(self, client):
        """缺少必填字段"""
        res = client.post("/api/auth/login", json={})
        assert res.status_code == 422

    def test_login_disabled_user(self, client):
        """禁用用户登录"""
        from tests.conftest import TestingSessionLocal
        from app.models.user import SysUser
        from app.core.security import hash_password

        db = TestingSessionLocal()
        user = SysUser(username="disabled", password_hash=hash_password(sha256("test123")),
                       nickname="禁用用户", status=0)
        db.add(user)
        db.commit()
        db.close()

        res = client.post("/api/auth/login", json={"username": "disabled", "password": sha256("test123")})
        assert res.status_code == 403

    def test_profile_invalid_token(self, client):
        """无效 Token"""
        res = client.get("/api/auth/profile", headers={"Authorization": "Bearer invalid.token.here"})
        assert res.status_code == 401

    def test_profile_malformed_auth_header(self, client):
        """格式错误的 Authorization 头"""
        res = client.get("/api/auth/profile", headers={"Authorization": "NotBearer xxx"})
        assert res.status_code == 401

    def test_logout_without_auth(self, client):
        """未登录时登出"""
        res = client.post("/api/auth/logout")
        assert res.status_code == 401

    def test_logout_success(self, client):
        """正常登出"""
        token = login(client)
        res = client.post("/api/auth/logout", headers=auth_header(token))
        assert res.status_code == 200


class TestCategoryEdgeCases:
    """分类边界测试"""

    def test_create_category_empty_name(self, client):
        """分类名为空"""
        token = login(client)
        res = client.post("/api/categories", json={"name": "", "sort_order": 1, "status": 1},
                          headers=auth_header(token))
        assert res.status_code == 422

    def test_create_category_without_auth(self, client):
        """未登录创建分类"""
        res = client.post("/api/categories", json={"name": "测试", "sort_order": 1, "status": 1})
        assert res.status_code == 401

    def test_update_nonexistent_category(self, client):
        """更新不存在的分类"""
        token = login(client)
        res = client.put("/api/categories/99999", json={"name": "不存在"},
                         headers=auth_header(token))
        assert res.status_code == 400

    def test_delete_nonexistent_category(self, client):
        """删除不存在的分类"""
        token = login(client)
        res = client.delete("/api/categories/99999", headers=auth_header(token))
        assert res.status_code == 400

    def test_list_categories_without_auth(self, client):
        """未登录查询分类"""
        res = client.get("/api/categories", params={"page": 1, "page_size": 10})
        assert res.status_code == 401

    def test_create_category_invalid_status(self, client):
        """无效状态值"""
        token = login(client)
        res = client.post("/api/categories", json={"name": "测试", "sort_order": 1, "status": 5},
                          headers=auth_header(token))
        assert res.status_code == 422

    def test_create_category_negative_sort(self, client):
        """负数排序"""
        token = login(client)
        res = client.post("/api/categories", json={"name": "测试", "sort_order": -1, "status": 1},
                          headers=auth_header(token))
        assert res.status_code == 422

    def test_pagination_page_zero(self, client):
        """分页参数 page=0"""
        token = login(client)
        res = client.get("/api/categories", params={"page": 0, "page_size": 10},
                         headers=auth_header(token))
        assert res.status_code == 422

    def test_pagination_oversized_page(self, client):
        """分页参数 page_size 超过上限"""
        token = login(client)
        res = client.get("/api/categories", params={"page": 1, "page_size": 999},
                         headers=auth_header(token))
        assert res.status_code == 422

    def test_empty_list(self, client):
        """空列表查询"""
        token = login(client)
        res = client.get("/api/categories", params={"page": 1, "page_size": 10},
                         headers=auth_header(token))
        assert res.status_code == 200
        assert res.json()["data"]["total"] == 0
        assert res.json()["data"]["items"] == []


class TestProductEdgeCases:
    """商品边界测试"""

    def test_create_product_empty_name(self, client):
        """商品名为空"""
        token = login(client)
        res = client.post("/api/products", json={
            "name": "", "category_id": 1, "price": 10, "stock": 1, "status": 1,
        }, headers=auth_header(token))
        assert res.status_code == 422

    def test_create_product_negative_price(self, client):
        """负数价格"""
        token = login(client)
        res = client.post("/api/products", json={
            "name": "测试", "category_id": 1, "price": -10, "stock": 1, "status": 1,
        }, headers=auth_header(token))
        assert res.status_code == 422

    def test_create_product_negative_stock(self, client):
        """负数库存"""
        token = login(client)
        res = client.post("/api/products", json={
            "name": "测试", "category_id": 1, "price": 10, "stock": -1, "status": 1,
        }, headers=auth_header(token))
        assert res.status_code == 422

    def test_create_product_zero_category_id(self, client):
        """category_id 为 0"""
        token = login(client)
        res = client.post("/api/products", json={
            "name": "测试", "category_id": 0, "price": 10, "stock": 1, "status": 1,
        }, headers=auth_header(token))
        assert res.status_code == 422

    def test_get_nonexistent_product(self, client):
        """查询不存在的商品"""
        token = login(client)
        res = client.get("/api/products/99999", headers=auth_header(token))
        assert res.status_code == 404

    def test_update_nonexistent_product(self, client):
        """更新不存在的商品"""
        token = login(client)
        res = client.put("/api/products/99999", json={"name": "不存在"},
                         headers=auth_header(token))
        assert res.status_code == 400

    def test_delete_nonexistent_product(self, client):
        """删除不存在的商品"""
        token = login(client)
        res = client.delete("/api/products/99999", headers=auth_header(token))
        assert res.status_code == 400

    def test_create_product_without_auth(self, client):
        """未登录创建商品"""
        res = client.post("/api/products", json={
            "name": "测试", "category_id": 1, "price": 10, "stock": 1, "status": 1,
        })
        assert res.status_code == 401

    def test_update_product_invalid_category(self, client):
        """更新商品到不存在的分类"""
        token = login(client)
        h = auth_header(token)
        # 先创建分类和商品
        cat_res = client.post("/api/categories", json={"name": "有效分类", "sort_order": 1, "status": 1}, headers=h)
        cat_id = cat_res.json()["data"]["id"]
        prod_res = client.post("/api/products", json={
            "name": "测试商品", "category_id": cat_id, "price": 10, "stock": 1, "status": 1,
        }, headers=h)
        pid = prod_res.json()["data"]["id"]

        # 更新到不存在的分类
        res = client.put(f"/api/products/{pid}", json={"category_id": 99999}, headers=h)
        assert res.status_code == 400

    def test_product_price_zero(self, client):
        """价格为 0 的商品"""
        token = login(client)
        h = auth_header(token)
        cat_res = client.post("/api/categories", json={"name": "免费分类", "sort_order": 1, "status": 1}, headers=h)
        cat_id = cat_res.json()["data"]["id"]

        res = client.post("/api/products", json={
            "name": "免费商品", "category_id": cat_id, "price": 0, "stock": 100, "status": 1,
        }, headers=h)
        assert res.status_code == 200

    def test_filter_by_category(self, client):
        """按分类筛选商品"""
        token = login(client)
        h = auth_header(token)
        cat1 = client.post("/api/categories", json={"name": "分类1", "sort_order": 1, "status": 1}, headers=h).json()["data"]["id"]
        cat2 = client.post("/api/categories", json={"name": "分类2", "sort_order": 2, "status": 1}, headers=h).json()["data"]["id"]

        client.post("/api/products", json={"name": "A", "category_id": cat1, "price": 10, "stock": 1, "status": 1}, headers=h)
        client.post("/api/products", json={"name": "B", "category_id": cat1, "price": 20, "stock": 1, "status": 1}, headers=h)
        client.post("/api/products", json={"name": "C", "category_id": cat2, "price": 30, "stock": 1, "status": 1}, headers=h)

        res = client.get("/api/products", params={"category_id": cat1}, headers=h)
        assert res.json()["data"]["total"] == 2


class TestUploadEdgeCases:
    """上传边界测试"""

    def test_upload_jpg(self, client):
        """上传 JPG"""
        token = login(client)
        fake_jpg = b'\xff\xd8\xff\xe0' + b'\x00' * 100
        res = client.post("/api/upload", headers=auth_header(token), files={
            "file": ("photo.jpg", io.BytesIO(fake_jpg), "image/jpeg"),
        })
        assert res.status_code == 200
        assert res.json()["data"]["url"].endswith(".jpg")

    def test_upload_gif(self, client):
        """上传 GIF"""
        token = login(client)
        fake_gif = b'GIF89a' + b'\x00' * 100
        res = client.post("/api/upload", headers=auth_header(token), files={
            "file": ("anim.gif", io.BytesIO(fake_gif), "image/gif"),
        })
        assert res.status_code == 200
        assert res.json()["data"]["url"].endswith(".gif")

    def test_upload_webp(self, client):
        """上传 WebP"""
        token = login(client)
        fake_webp = b'RIFF' + b'\x00' * 100
        res = client.post("/api/upload", headers=auth_header(token), files={
            "file": ("img.webp", io.BytesIO(fake_webp), "image/webp"),
        })
        assert res.status_code == 200
        assert res.json()["data"]["url"].endswith(".webp")

    def test_upload_pdf_rejected(self, client):
        """PDF 文件被拒绝"""
        token = login(client)
        res = client.post("/api/upload", headers=auth_header(token), files={
            "file": ("doc.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf"),
        })
        assert res.status_code == 400

    def test_upload_no_extension(self, client):
        """无扩展名文件被拒绝"""
        token = login(client)
        res = client.post("/api/upload", headers=auth_header(token), files={
            "file": ("noext", io.BytesIO(b"data"), "application/octet-stream"),
        })
        assert res.status_code == 400

    def test_upload_empty_file(self, client):
        """空文件上传"""
        token = login(client)
        res = client.post("/api/upload", headers=auth_header(token), files={
            "file": ("empty.png", io.BytesIO(b""), "image/png"),
        })
        # 空文件也能上传成功（大小为 0，未超限）
        assert res.status_code == 200


class TestLogsEdgeCases:
    """日志边界测试"""

    def test_logs_without_auth(self, client):
        """未登录查看日志"""
        res = client.get("/api/logs", params={"page": 1, "page_size": 10})
        assert res.status_code == 401

    def test_logs_only_login(self, client):
        """登录后仅有认证日志"""
        token = login(client)
        res = client.get("/api/logs", params={"page": 1, "page_size": 10},
                         headers=auth_header(token))
        assert res.status_code == 200
        # 登录本身会产生一条认证日志
        assert res.json()["data"]["total"] >= 1

    def test_logs_after_operations(self, client):
        """操作后日志自动记录"""
        token = login(client)
        h = auth_header(token)

        # 创建分类 → 应产生日志
        client.post("/api/categories", json={"name": "日志测试", "sort_order": 1, "status": 1}, headers=h)

        res = client.get("/api/logs", params={"page": 1, "page_size": 10}, headers=h)
        assert res.json()["data"]["total"] >= 1

    def test_logs_filter_by_module(self, client):
        """按模块筛选日志"""
        token = login(client)
        h = auth_header(token)

        # 创建分类和商品
        cat_res = client.post("/api/categories", json={"name": "筛选测试", "sort_order": 1, "status": 1}, headers=h)
        cat_id = cat_res.json()["data"]["id"]
        client.post("/api/products", json={
            "name": "日志商品", "category_id": cat_id, "price": 10, "stock": 1, "status": 1,
        }, headers=h)

        # 只查分类日志
        res = client.get("/api/logs", params={"module": "分类"}, headers=h)
        for item in res.json()["data"]["items"]:
            assert item["module"] == "分类"


class TestHealthCheck:
    """健康检查"""

    def test_health(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


class TestRateLimit:
    """限流测试"""

    def test_login_rate_limit(self, client):
        """登录接口限流：连续 6 次应触发 429"""
        create_test_user(client)
        for i in range(5):
            client.post("/api/auth/login", json={"username": "admin", "password": sha256("wrong")})
        # 第 6 次应被限流
        res = client.post("/api/auth/login", json={"username": "admin", "password": sha256("wrong")})
        assert res.status_code == 429
