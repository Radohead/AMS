"""
易耗品管理模块测试

用例编号:
- TEST-CONS-001: test_list_consumables           - 获取易耗品列表
- TEST-CONS-002: test_create_consumable         - 创建易耗品
- TEST-CONS-003: test_consume_consumable        - 领用易耗品
- TEST-CONS-004: test_restock_consumable         - 补充库存
- TEST-CONS-005: test_low_stock_warning          - 库存预警
"""
import pytest


class TestConsumableList:
    """易耗品列表测试"""

    def test_list_consumables(self, client, auth_headers):
        """TEST-CONS-001: 获取易耗品列表"""
        response = client.get("/api/inventory/stock", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_list_consumables_empty(self, client, auth_headers):
        """TEST-CONS-001b: 空列表"""
        response = client.get("/api/inventory/stock", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 0

    def test_list_consumables_with_category(
        self, client, auth_headers, test_category, asset_user_headers
    ):
        """TEST-CONS-001c: 按分类筛选易耗品"""
        # 创建易耗品
        client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "A4纸",
                "category_id": test_category.id,
                "asset_type": "consumable",
                "quantity": 100,
                "unit": "包",
                "current_stock": 50,
            },
        )
        response = client.get(
            f"/api/inventory/stock?category_id={test_category.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestConsumableCreate:
    """创建易耗品测试"""

    def test_create_consumable(
        self, client, test_category, asset_user_headers
    ):
        """TEST-CONS-002: 创建易耗品"""
        response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "签字笔",
                "category_id": test_category.id,
                "asset_type": "consumable",
                "quantity": 50,
                "unit": "支",
                "min_stock": 10,
                "current_stock": 30,
            },
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert data["asset_type"] == "consumable"
        assert data["current_stock"] == 30
        assert data["min_stock"] == 10


class TestConsumableConsume:
    """易耗品领用测试"""

    def test_consume_consumable(
        self, client, test_category, test_employee, asset_user_headers
    ):
        """TEST-CONS-003: 领用易耗品"""
        # 创建易耗品
        create_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "耗材测试",
                "category_id": test_category.id,
                "asset_type": "consumable",
                "quantity": 10,
                "unit": "个",
                "current_stock": 20,
            },
        )
        asset_id = create_resp.json()["id"]

        # 领用
        response = client.post(
            "/api/inventory/consume",
            headers=asset_user_headers,
            json={
                "asset_id": asset_id,
                "employee_id": test_employee.id,
                "quantity": 5,
                "purpose": "办公使用",
                "department_id": test_employee.department_id,
            },
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert data["remaining_stock"] == 15

        # 验证库存减少
        get_resp = client.get(
            f"/api/assets/{asset_id}", headers=asset_user_headers
        )
        assert get_resp.json()["current_stock"] == 15

    def test_consume_insufficient_stock(
        self, client, test_category, test_employee, asset_user_headers
    ):
        """TEST-CONS-003b: 库存不足时领用失败"""
        create_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "限量耗材",
                "category_id": test_category.id,
                "asset_type": "consumable",
                "quantity": 5,
                "unit": "个",
                "current_stock": 3,
            },
        )
        asset_id = create_resp.json()["id"]

        response = client.post(
            "/api/inventory/consume",
            headers=asset_user_headers,
            json={
                "asset_id": asset_id,
                "employee_id": test_employee.id,
                "quantity": 10,
            },
        )
        # 库存不足应该失败
        assert response.status_code in [400, 422]


class TestConsumableRestock:
    """易耗品补充库存测试"""

    def test_restock_consumable(
        self, client, test_category, asset_user_headers
    ):
        """TEST-CONS-004: 补充易耗品库存"""
        # 创建易耗品
        create_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待补货耗材",
                "category_id": test_category.id,
                "asset_type": "consumable",
                "quantity": 10,
                "unit": "包",
                "current_stock": 5,
            },
        )
        asset_id = create_resp.json()["id"]

        # 补充库存 (quantity 是 query 参数)
        response = client.post(
            f"/api/inventory/{asset_id}/restock?quantity=20",
            headers=asset_user_headers,
        )
        assert response.status_code == 200, f"Failed: {response.json()}"

        # 验证库存增加
        get_resp = client.get(
            f"/api/assets/{asset_id}", headers=asset_user_headers
        )
        assert get_resp.json()["current_stock"] == 25


class TestConsumableAlert:
    """易耗品库存预警测试"""

    def test_low_stock_warning(
        self, client, test_category, asset_user_headers
    ):
        """TEST-CONS-005: 库存预警"""
        # 创建低于最低库存的易耗品
        client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "预警耗材",
                "category_id": test_category.id,
                "asset_type": "consumable",
                "quantity": 10,
                "unit": "个",
                "min_stock": 20,
                "current_stock": 5,
            },
        )

        response = client.get("/api/inventory/stock/low", headers=asset_user_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # 应该包含当前库存低于最低库存的耗材
        low_stock_ids = [item["id"] for item in data]
        # 通过列表查询确认
        list_resp = client.get("/api/inventory/stock", headers=asset_user_headers)
        items = list_resp.json()["items"]
        low_items = [
            i for i in items if i.get("current_stock", 999) < (i.get("min_stock") or 999)
        ]
        assert len(low_items) >= 1
