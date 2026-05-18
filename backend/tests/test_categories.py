"""分类模块测试"""
from tests.test_helpers import login, auth_header


class TestCategories:
    def test_create_category(self, client):
        token = login(client)
        res = client.post("/api/categories", json={
            "name": "电子产品", "sort_order": 1, "status": 1,
        }, headers=auth_header(token))
        assert res.status_code == 200
        assert res.json()["data"]["id"]

    def test_list_categories(self, client):
        token = login(client)
        h = auth_header(token)
        client.post("/api/categories", json={"name": "分类A", "sort_order": 1, "status": 1}, headers=h)
        client.post("/api/categories", json={"name": "分类B", "sort_order": 2, "status": 1}, headers=h)

        res = client.get("/api/categories", params={"page": 1, "page_size": 10}, headers=h)
        assert res.status_code == 200
        assert res.json()["data"]["total"] == 2

    def test_update_category(self, client):
        token = login(client)
        h = auth_header(token)
        create_res = client.post("/api/categories", json={"name": "旧名称", "sort_order": 1, "status": 1}, headers=h)
        cat_id = create_res.json()["data"]["id"]

        res = client.put(f"/api/categories/{cat_id}", json={"name": "新名称"}, headers=h)
        assert res.status_code == 200

    def test_delete_category(self, client):
        token = login(client)
        h = auth_header(token)
        create_res = client.post("/api/categories", json={"name": "待删除", "sort_order": 1, "status": 1}, headers=h)
        cat_id = create_res.json()["data"]["id"]

        res = client.delete(f"/api/categories/{cat_id}", headers=h)
        assert res.status_code == 200

    def test_delete_category_with_products(self, client):
        token = login(client)
        h = auth_header(token)
        cat_res = client.post("/api/categories", json={"name": "有商品的分类", "sort_order": 1, "status": 1}, headers=h)
        cat_id = cat_res.json()["data"]["id"]

        client.post("/api/products", json={
            "name": "测试商品", "category_id": cat_id, "price": 10.00, "stock": 5, "status": 1,
        }, headers=h)

        res = client.delete(f"/api/categories/{cat_id}", headers=h)
        assert res.status_code == 400

    def test_get_all_categories(self, client):
        token = login(client)
        h = auth_header(token)
        client.post("/api/categories", json={"name": "启用", "sort_order": 1, "status": 1}, headers=h)
        client.post("/api/categories", json={"name": "禁用", "sort_order": 2, "status": 0}, headers=h)

        res = client.get("/api/categories/all", headers=h)
        assert res.status_code == 200
        # /all 只返回启用的
        assert len(res.json()["data"]) == 1

    def test_search_categories(self, client):
        token = login(client)
        h = auth_header(token)
        client.post("/api/categories", json={"name": "电子产品", "sort_order": 1, "status": 1}, headers=h)
        client.post("/api/categories", json={"name": "食品饮料", "sort_order": 2, "status": 1}, headers=h)

        res = client.get("/api/categories", params={"keyword": "电子"}, headers=h)
        assert res.json()["data"]["total"] == 1
