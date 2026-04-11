"""
分类管理模块测试

用例编号:
- TEST-CAT-001: test_list_categories         - 获取分类列表
- TEST-CAT-002: test_create_category          - 创建分类
- TEST-CAT-003: test_update_category          - 更新分类
- TEST-CAT-004: test_delete_category          - 删除分类(含子分类/资产检查)
"""
import pytest


class TestCategoryList:
    """分类列表测试"""

    def test_list_categories_success(self, client, test_category, auth_headers):
        """TEST-CAT-001: 获取分类列表"""
        response = client.get("/api/categories/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_categories_by_parent(self, client, test_category, auth_headers):
        """TEST-CAT-001b: 按父分类筛选 - 获取顶级分类"""
        # 不传 parent_id 参数会返回顶级分类（parent_id is None）
        response = client.get("/api/categories/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # 返回顶级分类
        for cat in data:
            assert cat["parent_id"] is None

    def test_list_categories_by_type(self, client, test_category, auth_headers):
        """TEST-CAT-001c: 按资产类型筛选"""
        response = client.get(
            "/api/categories/?asset_type=fixed",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for cat in data:
            assert cat["asset_type"] == "fixed"

    def test_get_category_tree(self, client, test_category, auth_headers):
        """TEST-CAT-001d: 获取分类树形结构"""
        response = client.get("/api/categories/tree", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCategoryCreate:
    """创建分类测试"""

    def test_create_category_success(self, client, auth_headers):
        """TEST-CAT-002: 创建新分类"""
        response = client.post(
            "/api/categories/",
            headers=auth_headers,
            json={
                "name": "办公设备",
                "code": "OFFICE",
                "asset_type": "fixed",
                "description": "办公设备分类"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "办公设备"
        assert data["code"] == "OFFICE"
        assert data["asset_type"] == "fixed"
        assert data["is_active"] is True

    def test_create_sub_category(self, client, test_category, auth_headers):
        """TEST-CAT-002b: 创建子分类"""
        response = client.post(
            "/api/categories/",
            headers=auth_headers,
            json={
                "name": "电脑",
                "code": "COMPUTER",
                "parent_id": test_category.id,
                "asset_type": "fixed",
                "description": "电脑设备"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "电脑"
        assert data["parent_id"] == test_category.id

    def test_create_category_duplicate_code(self, client, test_category, auth_headers):
        """TEST-CAT-002c: 分类编码重复"""
        response = client.post(
            "/api/categories/",
            headers=auth_headers,
            json={
                "name": "另一个电子设备",
                "code": test_category.code,
                "asset_type": "fixed"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestCategoryUpdate:
    """更新分类测试"""

    def test_update_category_success(self, client, test_category, auth_headers):
        """TEST-CAT-003: 更新分类信息"""
        response = client.put(
            f"/api/categories/{test_category.id}",
            headers=auth_headers,
            json={
                "name": "更新后的分类",
                "description": "更新后的描述"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的分类"
        assert data["description"] == "更新后的描述"

    def test_update_category_not_found(self, client, auth_headers):
        """TEST-CAT-003b: 更新不存在的分类"""
        response = client.put(
            "/api/categories/99999",
            headers=auth_headers,
            json={"name": "新名称"}
        )
        assert response.status_code == 404

    def test_update_category_change_parent(self, client, test_category, auth_headers):
        """TEST-CAT-003c: 更换父分类"""
        # 先创建一个新的顶级分类
        new_parent = client.post(
            "/api/categories/",
            headers=auth_headers,
            json={
                "name": "新父分类",
                "code": "NEW_PARENT",
                "asset_type": "fixed"
            }
        )
        new_parent_id = new_parent.json()["id"]

        # 更换父分类
        response = client.put(
            f"/api/categories/{test_category.id}",
            headers=auth_headers,
            json={"parent_id": new_parent_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] == new_parent_id


class TestCategoryDelete:
    """删除分类测试"""

    def test_delete_category_success(self, client, auth_headers):
        """TEST-CAT-004: 删除空分类"""
        # 先创建一个空分类
        create_response = client.post(
            "/api/categories/",
            headers=auth_headers,
            json={
                "name": "待删除分类",
                "code": "TO_DELETE",
                "asset_type": "fixed"
            }
        )
        cat_id = create_response.json()["id"]

        # 删除该分类
        response = client.delete(
            f"/api/categories/{cat_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "deleted" in response.json()["message"]

    def test_delete_category_with_children(self, client, test_category, auth_headers):
        """TEST-CAT-004b: 不能删除有子分类的分类"""
        # 创建子分类
        child_response = client.post(
            "/api/categories/",
            headers=auth_headers,
            json={
                "name": "子分类",
                "code": "CHILD_CAT",
                "parent_id": test_category.id,
                "asset_type": "fixed"
            }
        )

        # 尝试删除父分类
        response = client.delete(
            f"/api/categories/{test_category.id}",
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "children" in response.json()["detail"]

    def test_delete_category_not_found(self, client, auth_headers):
        """TEST-CAT-004c: 删除不存在的分类"""
        response = client.delete(
            "/api/categories/99999",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestCategoryGet:
    """获取分类详情测试"""

    def test_get_category_success(self, client, test_category, auth_headers):
        """TEST-CAT-005: 获取分类详情"""
        response = client.get(
            f"/api/categories/{test_category.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_category.id
        assert data["name"] == "电子设备"

    def test_get_category_not_found(self, client, auth_headers):
        """TEST-CAT-005b: 获取不存在的分类"""
        response = client.get("/api/categories/99999", headers=auth_headers)
        assert response.status_code == 404
