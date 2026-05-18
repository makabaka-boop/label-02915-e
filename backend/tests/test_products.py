"""商品模块测试"""
from tests.test_helpers import login, auth_header


def _create_category(client, token, name="测试分类"):
    res = client.post("/api/categories", json={
        "name": name, "sort_order": 1, "status": 1,
    }, headers=auth_header(token))
    return res.json()["data"]["id"]


class TestProducts:
    def test_create_product(self, client):
        token = login(client)
        h = auth_header(token)
        cat_id = _create_category(client, token)

        res = client.post("/api/products", json={
            "name": "iPhone 16", "category_id": cat_id,
            "price": 9999.00, "stock": 50, "status": 1,
        }, headers=h)
        assert res.status_code == 200
        assert res.json()["data"]["id"]

    def test_list_products(self, client):
        token = login(client)
        h = auth_header(token)
        cat_id = _create_category(client, token)

        for i in range(3):
            client.post("/api/products", json={
                "name": f"商品{i}", "category_id": cat_id,
                "price": 100.00, "stock": 10, "status": 1,
            }, headers=h)

        res = client.get("/api/products", params={"page": 1, "page_size": 10}, headers=h)
        assert res.json()["data"]["total"] == 3

    def test_get_product_detail(self, client):
        token = login(client)
        h = auth_header(token)
        cat_id = _create_category(client, token)

        create_res = client.post("/api/products", json={
            "name": "详情测试", "category_id": cat_id,
            "price": 199.00, "stock": 20, "status": 1,
        }, headers=h)
        pid = create_res.json()["data"]["id"]

        res = client.get(f"/api/products/{pid}", headers=h)
        assert res.status_code == 200
        assert res.json()["data"]["name"] == "详情测试"

    def test_update_product(self, client):
        token = login(client)
        h = auth_header(token)
        cat_id = _create_category(client, token)

        create_res = client.post("/api/products", json={
            "name": "旧名称", "category_id": cat_id,
            "price": 100.00, "stock": 10, "status": 1,
        }, headers=h)
        pid = create_res.json()["data"]["id"]

        res = client.put(f"/api/products/{pid}", json={"name": "新名称", "price": 200.00}, headers=h)
        assert res.status_code == 200

    def test_delete_product(self, client):
        token = login(client)
        h = auth_header(token)
        cat_id = _create_category(client, token)

        create_res = client.post("/api/products", json={
            "name": "待删除", "category_id": cat_id,
            "price": 50.00, "stock": 5, "status": 1,
        }, headers=h)
        pid = create_res.json()["data"]["id"]

        res = client.delete(f"/api/products/{pid}", headers=h)
        assert res.status_code == 200

    def test_filter_by_status(self, client):
        token = login(client)
        h = auth_header(token)
        cat_id = _create_category(client, token)

        client.post("/api/products", json={
            "name": "上架", "category_id": cat_id, "price": 10, "stock": 1, "status": 1,
        }, headers=h)
        client.post("/api/products", json={
            "name": "下架", "category_id": cat_id, "price": 10, "stock": 1, "status": 0,
        }, headers=h)

        res = client.get("/api/products", params={"status": 1}, headers=h)
        assert res.json()["data"]["total"] == 1

    def test_search_products(self, client):
        token = login(client)
        h = auth_header(token)
        cat_id = _create_category(client, token)

        client.post("/api/products", json={
            "name": "苹果手机", "category_id": cat_id, "price": 9999, "stock": 10, "status": 1,
        }, headers=h)
        client.post("/api/products", json={
            "name": "华为手机", "category_id": cat_id, "price": 5999, "stock": 10, "status": 1,
        }, headers=h)

        res = client.get("/api/products", params={"keyword": "苹果"}, headers=h)
        assert res.json()["data"]["total"] == 1

    def test_create_product_invalid_category(self, client):
        token = login(client)
        h = auth_header(token)

        res = client.post("/api/products", json={
            "name": "无效分类", "category_id": 9999,
            "price": 10.00, "stock": 1, "status": 1,
        }, headers=h)
        assert res.status_code == 400
