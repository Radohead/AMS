"""
报废管理模块测试

用例编号:
- TEST-SCRAP-001: test_create_scrap_order           - 创建报废申请
- TEST-SCRAP-002: test_approve_scrap_order           - 审批报废申请
- TEST-SCRAP-003: test_dispose_scrap_order          - 处置报废资产
- TEST-SCRAP-004: test_reject_scrap_order            - 驳回报废申请
"""
import pytest


class TestScrapCreate:
    """报废申请创建测试"""

    def test_create_scrap_order(
        self, client, test_category, asset_user_headers
    ):
        """TEST-SCRAP-001: 创建报废申请"""
        # 创建资产
        asset_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待报废设备",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "status": "stock",
            },
        )
        asset_id = asset_resp.json()["id"]

        # 创建报废申请
        response = client.post(
            "/api/scrap/",
            headers=asset_user_headers,
            json={
                "asset_id": asset_id,
                "reason": "设备老旧，无法维修",
                "description": "使用年限超过10年",
            },
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert data["asset_id"] == asset_id
        assert data["status"] == "pending"
        assert data["order_no"] is not None


class TestScrapApprove:
    """报废审批测试"""

    def test_approve_scrap_order(
        self, client, test_category, asset_user_headers
    ):
        """TEST-SCRAP-002: 审批通过报废申请"""
        # 创建资产和报废申请
        asset_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待审批报废",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "status": "stock",
            },
        )
        asset_id = asset_resp.json()["id"]

        order_resp = client.post(
            "/api/scrap/",
            headers=asset_user_headers,
            json={
                "asset_id": asset_id,
                "reason": "设备损坏",
            },
        )
        order_id = order_resp.json()["id"]

        # 审批通过
        response = client.post(
            f"/api/scrap/{order_id}/approve",
            headers=asset_user_headers,
            json={
                "status": "approved",
                "review_comment": "同意报废",
                "disposal_method": "recycle",
                "residual_value": 100.0,
            },
        )
        assert response.status_code == 200, f"Failed: {response.json()}"


class TestScrapReject:
    """报废驳回测试"""

    def test_reject_scrap_order(
        self, client, test_category, asset_user_headers
    ):
        """TEST-SCRAP-004: 驳回报废申请"""
        asset_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待驳回报废",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "status": "stock",
            },
        )
        asset_id = asset_resp.json()["id"]

        order_resp = client.post(
            "/api/scrap/",
            headers=asset_user_headers,
            json={
                "asset_id": asset_id,
                "reason": "设备老旧",
            },
        )
        order_id = order_resp.json()["id"]

        # 驳回
        response = client.post(
            f"/api/scrap/{order_id}/approve",
            headers=asset_user_headers,
            json={
                "status": "rejected",
                "review_comment": "设备仍可使用，暂不报废",
            },
        )
        assert response.status_code == 200
        resp_data = response.json()
        assert "message" in resp_data


class TestScrapDispose:
    """报废处置测试"""

    def test_dispose_scrap_order(
        self, client, test_category, asset_user_headers
    ):
        """TEST-SCRAP-003: 处置报废资产"""
        asset_resp = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待处置报废",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "status": "stock",
            },
        )
        asset_id = asset_resp.json()["id"]

        order_resp = client.post(
            "/api/scrap/",
            headers=asset_user_headers,
            json={
                "asset_id": asset_id,
                "reason": "设备报废",
            },
        )
        order_id = order_resp.json()["id"]

        # 先审批
        client.post(
            f"/api/scrap/{order_id}/approve",
            headers=asset_user_headers,
            json={
                "status": "approved",
                "review_comment": "同意",
                "disposal_method": "discard",
            },
        )

        # 处置 (disposal_method 是 query 参数)
        response = client.post(
            f"/api/scrap/{order_id}/dispose",
            headers=asset_user_headers,
            params={
                "disposal_method": "discard",
            },
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
