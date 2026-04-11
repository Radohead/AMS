"""
报修管理模块测试

用例编号:
- TEST-REPAIR-001: test_create_repair_order          - 创建报修工单
- TEST-REPAIR-002: test_assign_repair_order          - 指派维修人员
- TEST-REPAIR-003: test_complete_repair_order        - 完成维修工单
"""
import pytest


class TestRepairCreate:
    """报修工单创建测试"""

    def test_create_repair_order(
        self, client, test_category, test_employee, asset_user_headers
    ):
        """TEST-REPAIR-001: 创建报修工单"""
        # 先创建资产
        asset_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待报修设备",
                "category_id": test_category.id,
                "asset_type": "fixed",
            },
        )
        asset_id = asset_resp.json()["id"]

        # 创建报修工单
        response = client.post(
            "/api/repair/",
            headers=asset_user_headers,
            json={
                "asset_id": asset_id,
                "description": "屏幕出现亮点，需要更换",
                "priority": "normal",
            },
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert data["asset_id"] == asset_id
        assert data["status"] == "pending"
        assert data["order_no"] is not None

    def test_create_repair_high_priority(
        self, client, test_category, test_employee, asset_user_headers
    ):
        """TEST-REPAIR-001b: 创建高优先级报修"""
        asset_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "紧急设备",
                "category_id": test_category.id,
                "asset_type": "fixed",
            },
        )
        asset_id = asset_resp.json()["id"]

        response = client.post(
            "/api/repair/",
            headers=asset_user_headers,
            json={
                "asset_id": asset_id,
                "description": "服务器宕机",
                "priority": "urgent",
            },
        )
        assert response.status_code == 200
        assert response.json()["priority"] == "urgent"


class TestRepairAssign:
    """报修指派测试"""

    def test_assign_repair_order(
        self,
        client,
        test_category,
        test_employee,
        asset_user_headers,
    ):
        """TEST-REPAIR-002: 指派维修人员"""
        # 创建资产和报修工单
        asset_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待指派维修设备",
                "category_id": test_category.id,
                "asset_type": "fixed",
            },
        )
        asset_id = asset_resp.json()["id"]

        order_resp = client.post(
            "/api/repair/",
            headers=asset_user_headers,
            json={
                "asset_id": asset_id,
                "description": "设备故障",
            },
        )
        order_id = order_resp.json()["id"]

        # 指派维修人员 (handler_id 是 query 参数)
        response = client.post(
            f"/api/repair/{order_id}/assign?handler_id={test_employee.id}",
            headers=asset_user_headers,
        )
        assert response.status_code == 200, f"Failed: {response.json()}"


class TestRepairComplete:
    """报修完成测试"""

    def test_complete_repair_order(
        self,
        client,
        test_category,
        test_employee,
        asset_user_headers,
    ):
        """TEST-REPAIR-003: 完成维修工单"""
        # 创建资产和报修工单
        asset_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待完工设备",
                "category_id": test_category.id,
                "asset_type": "fixed",
            },
        )
        asset_id = asset_resp.json()["id"]

        order_resp = client.post(
            "/api/repair/",
            headers=asset_user_headers,
            json={
                "asset_id": asset_id,
                "description": "设备故障",
            },
        )
        order_id = order_resp.json()["id"]

        # 指派
        client.post(
            f"/api/repair/{order_id}/assign",
            headers=asset_user_headers,
            json={"handler_id": test_employee.id},
        )

        # 完成维修 (repair_result, repair_cost 是 query 参数)
        response = client.post(
            f"/api/repair/{order_id}/complete",
            headers=asset_user_headers,
            params={
                "repair_result": "已更换屏幕，正常使用",
                "repair_cost": 500.0,
            },
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
