"""
资产管理模块测试

用例编号:
- TEST-ASSET-001: test_list_assets             - 获取资产列表
- TEST-ASSET-002: test_create_asset             - 创建资产
- TEST-ASSET-003: test_update_asset             - 更新资产
- TEST-ASSET-004: test_delete_asset             - 删除资产
- TEST-ASSET-005: test_assign_asset             - 分配资产
- TEST-ASSET-006: test_transfer_asset           - 调拨资产
- TEST-ASSET-007: test_return_asset             - 退库资产
- TEST-ASSET-008: test_get_asset_records        - 获取资产变动记录
"""
import pytest
import json


class TestAssetList:
    """资产列表测试"""

    def test_list_assets_success(self, client, auth_headers):
        """TEST-ASSET-001: 获取资产列表"""
        response = client.get("/api/assets/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_list_assets_with_keyword(self, client, auth_headers):
        """TEST-ASSET-001b: 按关键词搜索资产"""
        response = client.get(
            "/api/assets/?keyword=test",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_list_assets_by_category(self, client, test_category, auth_headers):
        """TEST-ASSET-001c: 按分类筛选"""
        response = client.get(
            f"/api/assets/?category_id={test_category.id}",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_list_assets_by_status(self, client, auth_headers):
        """TEST-ASSET-001d: 按状态筛选"""
        response = client.get(
            "/api/assets/?status=stock",
            headers=auth_headers
        )
        assert response.status_code == 200


class TestAssetCreate:
    """创建资产测试"""

    def test_create_asset_success(self, client, test_category, test_department, asset_user_headers):
        """TEST-ASSET-002: 创建新资产"""
        response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "测试笔记本",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "brand": "ThinkPad",
                "model": "X1 Carbon",
                "serial_no": "SN123456",
                "purchase_price": 8000.00,
                "department_id": test_department.id,
                "location": "办公室A座"
            }
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert data["name"] == "测试笔记本"
        assert data["brand"] == "ThinkPad"
        assert data["status"] == "stock"
        assert data["asset_no"] is not None
        assert data["qr_code"] is not None

    def test_create_consumable_asset(self, client, asset_user_headers, auth_headers):
        """TEST-ASSET-002b: 创建易耗品"""
        # 先创建一个易耗品分类
        cat_response = client.post(
            "/api/categories/",
            headers=auth_headers,
            json={
                "name": "文具",
                "code": "STATIONERY",
                "asset_type": "consumable"
            }
        )
        cat_id = cat_response.json()["id"]

        response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "中性笔",
                "category_id": cat_id,
                "asset_type": "consumable",
                "quantity": 100,
                "unit": "支",
                "min_stock": 10,
                "current_stock": 50
            }
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert data["quantity"] == 100
        assert data["current_stock"] == 50


class TestAssetGet:
    """获取资产详情测试"""

    def test_get_asset_success(self, client, test_category, test_department, asset_user_headers):
        """TEST-ASSET-002c: 获取资产详情"""
        # 先创建资产
        create_response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待查询资产",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "department_id": test_department.id
            }
        )
        asset_id = create_response.json()["id"]

        # 获取详情
        response = client.get(
            f"/api/assets/{asset_id}",
            headers=asset_user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == asset_id
        assert data["name"] == "待查询资产"

    def test_get_asset_by_no(self, client, test_category, asset_user_headers):
        """TEST-ASSET-002d: 通过编码获取资产"""
        # 创建资产
        create_response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "扫码资产",
                "category_id": test_category.id,
                "asset_type": "fixed"
            }
        )
        asset_no = create_response.json()["asset_no"]

        # 通过编码获取
        response = client.get(f"/api/assets/no/{asset_no}")
        assert response.status_code == 200
        data = response.json()
        assert data["asset_no"] == asset_no


class TestAssetUpdate:
    """更新资产测试"""

    def test_update_asset_success(self, client, test_category, asset_user_headers):
        """TEST-ASSET-003: 更新资产信息"""
        # 创建资产
        create_response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待更新资产",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "brand": "旧品牌"
            }
        )
        asset_id = create_response.json()["id"]

        # 更新
        response = client.put(
            f"/api/assets/{asset_id}",
            headers=asset_user_headers,
            json={
                "name": "已更新资产",
                "brand": "新品牌",
                "location": "新位置"
            }
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert data["name"] == "已更新资产"
        assert data["brand"] == "新品牌"
        assert data["location"] == "新位置"

    def test_update_asset_not_found(self, client, asset_user_headers):
        """TEST-ASSET-003b: 更新不存在的资产"""
        response = client.put(
            "/api/assets/99999",
            headers=asset_user_headers,
            json={"name": "新名称"}
        )
        assert response.status_code == 404


class TestAssetDelete:
    """删除资产测试"""

    def test_delete_asset_in_stock(self, client, test_category, asset_user_headers):
        """TEST-ASSET-004: 删除在库状态的资产"""
        # 创建资产
        create_response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待删除资产",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "status": "stock"
            }
        )
        asset_id = create_response.json()["id"]

        # 删除
        response = client.delete(
            f"/api/assets/{asset_id}",
            headers=asset_user_headers
        )
        assert response.status_code == 200
        assert "deleted" in response.json()["message"]

    def test_delete_asset_in_use(self, client, test_category, test_employee, asset_user_headers):
        """TEST-ASSET-004b: 不能删除使用中的资产"""
        # 创建资产
        create_response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "使用中资产",
                "category_id": test_category.id,
                "asset_type": "fixed"
            }
        )
        asset_id = create_response.json()["id"]

        # 分配资产（使其状态变为 in_use）
        client.post(
            f"/api/assets/{asset_id}/assign",
            headers=asset_user_headers,
            json={
                "user_id": test_employee.id,
                "department_id": test_employee.department_id
            }
        )

        # 验证状态已变为 in_use
        get_response = client.get(f"/api/assets/{asset_id}", headers=asset_user_headers)
        assert get_response.json()["status"] == "in_use"

        # 尝试删除 - 应该失败
        response = client.delete(
            f"/api/assets/{asset_id}",
            headers=asset_user_headers
        )
        assert response.status_code == 400


class TestAssetAssign:
    """资产分配测试"""

    def test_assign_asset_success(self, client, test_category, test_employee, asset_user_headers):
        """TEST-ASSET-005: 分配资产"""
        # 创建资产
        create_response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待分配资产",
                "category_id": test_category.id,
                "asset_type": "fixed"
            }
        )
        asset_id = create_response.json()["id"]

        # 分配
        response = client.post(
            f"/api/assets/{asset_id}/assign",
            headers=asset_user_headers,
            json={
                "user_id": test_employee.id,
                "department_id": test_employee.department_id,
                "location": "员工工位"
            }
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert data["status"] == "in_use"
        assert data["user_id"] == test_employee.id

    def test_assign_asset_not_found(self, client, asset_user_headers):
        """TEST-ASSET-005b: 分配不存在的资产"""
        response = client.post(
            "/api/assets/99999/assign",
            headers=asset_user_headers,
            json={"user_id": 1, "location": "test"}
        )
        assert response.status_code == 404


class TestAssetTransfer:
    """资产调拨测试"""

    def test_transfer_asset_success(self, client, test_category, asset_user_headers, auth_headers):
        """TEST-ASSET-006: 调拨资产"""
        # 创建资产
        create_response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待调拨资产",
                "category_id": test_category.id,
                "asset_type": "fixed"
            }
        )
        asset_id = create_response.json()["id"]

        # 创建另一个部门
        new_dept = client.post(
            "/api/departments/",
            headers=auth_headers,
            json={"name": "新部门", "code": "NEW_DEPT_FOR_TRANSFER"}
        )
        new_dept_id = new_dept.json()["id"]

        # 调拨
        response = client.post(
            f"/api/assets/{asset_id}/transfer",
            headers=asset_user_headers,
            json={
                "target_department_id": new_dept_id,
                "target_location": "新位置"
            }
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert data["department_id"] == new_dept_id
        assert data["location"] == "新位置"


class TestAssetReturn:
    """资产退库测试"""

    def test_return_asset_success(self, client, test_category, test_employee, asset_user_headers):
        """TEST-ASSET-007: 资产退库"""
        # 创建并分配资产
        create_response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "待退库资产",
                "category_id": test_category.id,
                "asset_type": "fixed"
            }
        )
        asset_id = create_response.json()["id"]

        # 先分配
        client.post(
            f"/api/assets/{asset_id}/assign",
            headers=asset_user_headers,
            json={
                "user_id": test_employee.id,
                "department_id": test_employee.department_id
            }
        )

        # 退库
        response = client.post(
            f"/api/assets/{asset_id}/return",
            headers=asset_user_headers,
            json={"remarks": "员工离职"}
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert data["status"] == "stock"
        assert data["user_id"] is None


class TestAssetRecords:
    """资产变动记录测试"""

    def test_get_asset_records(self, client, test_category, test_employee, asset_user_headers):
        """TEST-ASSET-008: 获取资产变动记录"""
        # 创建资产（会产生 create 记录）
        create_response = client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "有记录的资产",
                "category_id": test_category.id,
                "asset_type": "fixed"
            }
        )
        asset_id = create_response.json()["id"]

        # 分配（会产生 assign 记录）
        client.post(
            f"/api/assets/{asset_id}/assign",
            headers=asset_user_headers,
            json={
                "user_id": test_employee.id,
                "department_id": test_employee.department_id
            }
        )

        # 获取记录
        response = client.get(
            f"/api/assets/{asset_id}/records",
            headers=asset_user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # 至少有 create 和 assign 两条记录
        assert len(data) >= 2


class TestAssetStats:
    """资产统计测试"""

    def test_get_asset_stats(self, client, test_category, asset_user_headers):
        """TEST-ASSET-009: 获取资产统计"""
        # 创建一些资产
        client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "统计资产1",
                "category_id": test_category.id,
                "asset_type": "fixed",
                "purchase_price": 5000
            }
        )
        client.post(
            "/api/assets/",
            headers=asset_user_headers,
            json={
                "name": "统计资产2",
                "category_id": test_category.id,
                "asset_type": "consumable",
                "purchase_price": 100
            }
        )

        response = client.get("/api/assets/stats/overview", headers=asset_user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "in_stock" in data
        assert "fixed" in data
        assert "consumable" in data
        assert "total_value" in data
