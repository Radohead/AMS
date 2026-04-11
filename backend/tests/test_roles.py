"""
角色权限模块测试

用例编号:
- TEST-ROLE-001: test_list_roles              - 获取角色列表
- TEST-ROLE-002: test_create_role             - 创建角色
- TEST-ROLE-003: test_update_role             - 更新角色
- TEST-ROLE-004: test_list_permissions        - 获取权限列表
"""
import pytest


class TestRoleList:
    """角色列表测试"""

    def test_list_roles_success(self, client, test_role, auth_headers):
        """TEST-ROLE-001: 获取角色列表"""
        response = client.get("/api/permissions/roles", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_roles_with_filter(self, client, test_role, auth_headers):
        """TEST-ROLE-001b: 按状态筛选角色"""
        response = client.get(
            "/api/permissions/roles?is_active=true",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for role in data:
            assert role["is_active"] is True


class TestRoleCreate:
    """创建角色测试"""

    def test_create_role_success(self, client, auth_headers):
        """TEST-ROLE-002: 创建新角色"""
        response = client.post(
            "/api/permissions/roles",
            headers=auth_headers,
            json={
                "name": "测试角色",
                "code": "test_role",
                "description": "测试用角色"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "测试角色"
        assert data["code"] == "test_role"
        assert data["is_active"] is True
        assert data["is_system"] is False

    def test_create_role_with_permissions(self, client, test_permission, auth_headers):
        """TEST-ROLE-002b: 创建角色并分配权限"""
        response = client.post(
            "/api/permissions/roles",
            headers=auth_headers,
            json={
                "name": "权限角色",
                "code": "perm_role",
                "description": "带权限的角色",
                "permission_ids": [test_permission.id]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "权限角色"

    def test_create_role_duplicate_code(self, client, test_role, auth_headers):
        """TEST-ROLE-002c: 角色编码重复"""
        response = client.post(
            "/api/permissions/roles",
            headers=auth_headers,
            json={
                "name": "另一个角色",
                "code": test_role.code,
                "description": "会失败"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestRoleUpdate:
    """更新角色测试"""

    def test_update_role_success(self, client, test_role, auth_headers):
        """TEST-ROLE-003: 更新角色"""
        response = client.put(
            f"/api/permissions/roles/{test_role.id}",
            headers=auth_headers,
            json={
                "name": "更新的角色名",
                "description": "更新后的描述"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新的角色名"
        assert data["description"] == "更新后的描述"

    def test_update_role_not_found(self, client, auth_headers):
        """TEST-ROLE-003b: 更新不存在的角色"""
        response = client.put(
            "/api/permissions/roles/99999",
            headers=auth_headers,
            json={"name": "新名称"}
        )
        assert response.status_code == 404

    def test_update_role_add_permissions(self, client, test_role, test_permission, auth_headers):
        """TEST-ROLE-003c: 为角色添加权限"""
        response = client.put(
            f"/api/permissions/roles/{test_role.id}",
            headers=auth_headers,
            json={"permission_ids": [test_permission.id]}
        )
        assert response.status_code == 200


class TestPermissionList:
    """权限列表测试"""

    def test_list_permissions_success(self, client, test_permission, auth_headers):
        """TEST-PERM-001: 获取权限列表"""
        response = client.get("/api/permissions/permissions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_permissions_by_resource(self, client, test_permission, auth_headers):
        """TEST-PERM-001b: 按资源筛选权限"""
        response = client.get(
            "/api/permissions/permissions?resource=asset",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for perm in data:
            assert perm["resource"] == "asset"

    def test_get_permissions_grouped(self, client, test_permission, auth_headers):
        """TEST-PERM-001c: 获取按资源分组的权限"""
        response = client.get(
            "/api/permissions/permissions/grouped",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
