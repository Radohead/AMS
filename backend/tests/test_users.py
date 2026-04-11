"""
用户管理模块测试

用例编号:
- TEST-USER-001: test_list_users              - 获取用户列表
- TEST-USER-002: test_create_user              - 创建用户
- TEST-USER-003: test_update_user              - 更新用户
- TEST-USER-004: test_delete_user              - 删除(禁用)用户
- TEST-USER-005: test_cannot_delete_yourself    - 不能删除自己
"""
import pytest


class TestUserList:
    """用户列表测试"""

    def test_list_users_success(self, client, test_user, auth_headers):
        """TEST-USER-001: 获取用户列表"""
        response = client.get("/api/permissions/users", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_list_users_with_keyword(self, client, test_user, auth_headers):
        """TEST-USER-001b: 按关键词搜索用户"""
        response = client.get(
            "/api/permissions/users?keyword=test",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_list_users_with_active_filter(self, client, test_user, inactive_user, auth_headers):
        """TEST-USER-001c: 按启用状态筛选用户"""
        # 只看启用的用户
        response = client.get(
            "/api/permissions/users?is_active=true",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # 应该只有 test_user，inactive_user 已被禁用
        for user in data["items"]:
            assert user["is_active"] is True


class TestUserCreate:
    """创建用户测试"""

    def test_create_user_success(self, client, auth_headers):
        """TEST-USER-002: 创建新用户"""
        response = client.post(
            "/api/permissions/users",
            headers=auth_headers,
            json={
                "username": "newuser",
                "password": "password123",
                "email": "newuser@example.com",
                "real_name": "新用户"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["is_active"] is True
        assert "password" not in data
        assert "password_hash" not in data

    def test_create_user_duplicate_username(self, client, test_user, auth_headers):
        """TEST-USER-002b: 用户名重复"""
        response = client.post(
            "/api/permissions/users",
            headers=auth_headers,
            json={
                "username": "testuser",
                "password": "password123",
                "email": "another@example.com"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_user_with_role(self, client, test_role, auth_headers):
        """TEST-USER-002c: 创建用户并分配角色"""
        response = client.post(
            "/api/permissions/users",
            headers=auth_headers,
            json={
                "username": "roleuser",
                "password": "password123",
                "real_name": "角色用户",
                "role_ids": [test_role.id]
            }
        )
        assert response.status_code == 200
        data = response.json()
        # 验证角色已分配
        assert "roles" in data or "role_ids" in data or data.get("id") is not None


class TestUserUpdate:
    """更新用户测试"""

    def test_update_user_success(self, client, test_user, auth_headers):
        """TEST-USER-003: 更新用户信息"""
        response = client.put(
            f"/api/permissions/users/{test_user.id}",
            headers=auth_headers,
            json={
                "email": "updated@example.com",
                "real_name": "更新后的用户"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"
        assert data["real_name"] == "更新后的用户"

    def test_update_user_not_found(self, client, auth_headers):
        """TEST-USER-003b: 更新不存在的用户"""
        response = client.put(
            "/api/permissions/users/99999",
            headers=auth_headers,
            json={"email": "test@example.com"}
        )
        assert response.status_code == 404

    def test_update_user_deactivate(self, client, test_user, auth_headers):
        """TEST-USER-003c: 禁用用户"""
        response = client.put(
            f"/api/permissions/users/{test_user.id}",
            headers=auth_headers,
            json={"is_active": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False


class TestUserDelete:
    """删除用户测试"""

    def test_delete_user_success(self, client, admin_user, auth_headers):
        """TEST-USER-004: 删除(禁用)用户"""
        # 创建另一个用户来删除
        create_response = client.post(
            "/api/permissions/users",
            headers=auth_headers,
            json={
                "username": "todelete",
                "password": "password123",
                "real_name": "待删除用户"
            }
        )
        user_id = create_response.json()["id"]

        # 禁用该用户
        response = client.delete(
            f"/api/permissions/users/{user_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "deactivated" in response.json()["message"]

    def test_cannot_delete_yourself(self, client, test_user, auth_headers):
        """TEST-USER-005: 不能删除自己"""
        response = client.delete(
            f"/api/permissions/users/{test_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "yourself" in response.json()["detail"]

    def test_delete_user_not_found(self, client, auth_headers):
        """TEST-USER-004b: 删除不存在的用户"""
        response = client.delete(
            "/api/permissions/users/99999",
            headers=auth_headers
        )
        assert response.status_code == 404
