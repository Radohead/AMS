"""
盘点管理模块测试

用例编号:
- TEST-CHECK-001: test_create_inventory_check        - 创建盘点计划
- TEST-CHECK-002: test_start_inventory_check          - 开始盘点
- TEST-CHECK-003: test_update_check_item             - 更新盘点明细
- TEST-CHECK-004: test_complete_inventory_check      - 完成盘点
- TEST-CHECK-005: test_get_inventory_report          - 获取盘点报告
"""
import pytest
from datetime import datetime


class TestInventoryCheckCreate:
    """盘点计划创建测试"""

    def test_create_inventory_check(self, client, auth_headers):
        """TEST-CHECK-001: 创建盘点计划"""
        response = client.post(
            "/api/inventory-check/",
            headers=auth_headers,
            json={
                "name": "2024年Q1资产盘点",
                "start_date": datetime.now().isoformat(),
                "categories": None,
                "departments": None,
            },
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert data["name"] == "2024年Q1资产盘点"
        assert data["status"] == "planning"

    def test_create_check_with_filter(
        self, client, auth_headers, test_category, test_department
    ):
        """TEST-CHECK-001b: 创建带筛选条件的盘点计划"""
        response = client.post(
            "/api/inventory-check/",
            headers=auth_headers,
            json={
                "name": "部门专项盘点",
                "start_date": datetime.now().isoformat(),
                "categories": [test_category.id],
                "departments": [test_department.id],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "部门专项盘点"


class TestInventoryCheckStart:
    """盘点开始测试"""

    def test_start_inventory_check(
        self, client, auth_headers, asset_user_headers, test_category
    ):
        """TEST-CHECK-002: 开始盘点"""
        # 创建资产
        client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待盘点资产A",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "status": "stock",
            },
        )
        client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待盘点资产B",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "status": "in_use",
            },
        )

        # 创建盘点计划
        check_resp = client.post(
            "/api/inventory-check/",
            headers=auth_headers,
            json={
                "name": "快速盘点",
                "start_date": datetime.now().isoformat(),
            },
        )
        check_id = check_resp.json()["id"]

        # 开始盘点
        response = client.post(
            f"/api/inventory-check/{check_id}/start",
            headers=auth_headers,
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        resp_data = response.json()
        assert "message" in resp_data


class TestInventoryCheckItem:
    """盘点明细更新测试"""

    def test_update_check_item(
        self,
        client,
        auth_headers,
        asset_user_headers,
        test_category,
        test_employee,
    ):
        """TEST-CHECK-003: 更新盘点明细"""
        # 创建资产
        asset_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "盘点明细测试资产",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "status": "stock",
                "location": "原位置",
            },
        )
        asset_id = asset_resp.json()["id"]

        # 创建盘点计划并开始
        check_resp = client.post(
            "/api/inventory-check/",
            headers=auth_headers,
            json={
                "name": "明细测试盘点",
                "start_date": datetime.now().isoformat(),
            },
        )
        check_id = check_resp.json()["id"]
        client.post(
            f"/api/inventory-check/{check_id}/start",
            headers=auth_headers,
        )

        # 获取盘点明细
        items_resp = client.get(
            f"/api/inventory-check/{check_id}/items",
            headers=auth_headers,
        )
        assert items_resp.status_code == 200
        items = items_resp.json()["items"]
        assert len(items) >= 1

        # 找到当前资产对应的盘点项
        item = next((i for i in items if i["asset_id"] == asset_id), None)
        if item:
            item_id = item["id"]
            # 更新盘点明细
            response = client.put(
                f"/api/inventory-check/{check_id}/items/{item_id}",
                headers=auth_headers,
                json={
                    "actual_status": "normal",
                    "actual_location": "原位置",
                    "actual_user_id": test_employee.id,
                    "check_result": "normal",
                    "remarks": "盘点正常",
                },
            )
            assert response.status_code == 200, f"Failed: {response.json()}"


class TestInventoryCheckComplete:
    """盘点完成测试"""

    def test_complete_inventory_check(
        self, client, auth_headers, asset_user_headers, test_category
    ):
        """TEST-CHECK-004: 完成盘点"""
        # 创建资产
        client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "盘点完成测试资产",
                "category_id": test_category.id,
                "asset_type": "fixed",
            },
        )

        # 创建盘点计划并开始
        check_resp = client.post(
            "/api/inventory-check/",
            headers=auth_headers,
            json={
                "name": "完成测试盘点",
                "start_date": datetime.now().isoformat(),
            },
        )
        check_id = check_resp.json()["id"]
        client.post(
            f"/api/inventory-check/{check_id}/start",
            headers=auth_headers,
        )

        # 完成盘点
        response = client.post(
            f"/api/inventory-check/{check_id}/complete",
            headers=auth_headers,
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        resp_data = response.json()
        assert "message" in resp_data


class TestInventoryReport:
    """盘点报告测试"""

    def test_get_inventory_report(
        self, client, auth_headers, asset_user_headers, test_category
    ):
        """TEST-CHECK-005: 获取盘点报告"""
        # 创建资产
        client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "报告测试资产",
                "category_id": test_category.id,
                "asset_type": "fixed",
            },
        )

        # 创建并完成盘点
        check_resp = client.post(
            "/api/inventory-check/",
            headers=auth_headers,
            json={
                "name": "报告测试盘点",
                "start_date": datetime.now().isoformat(),
            },
        )
        check_id = check_resp.json()["id"]
        client.post(
            f"/api/inventory-check/{check_id}/start",
            headers=auth_headers,
        )
        client.post(
            f"/api/inventory-check/{check_id}/complete",
            headers=auth_headers,
        )

        # 获取报告
        response = client.get(
            f"/api/inventory-check/{check_id}/report",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "items" in data
