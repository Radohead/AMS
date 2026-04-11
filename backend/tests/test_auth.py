"""
认证模块测试

用例编号说明:
- TEST-AUTH-001: test_login_success          - 正常登录
- TEST-AUTH-002: test_login_invalid_credentials - 错误凭证登录
- TEST-AUTH-003: test_get_current_user       - 获取当前用户信息
- TEST-AUTH-004: test_change_password         - 修改密码
- TEST-AUTH-005: test_unauthorized_access     - 未授权访问
"""
import pytest
from app.models.user import LoginLog


class TestLogin:
    """登录测试"""

    def test_login_success(self, client, test_user):
        """
        TEST-AUTH-001: 正常登录
        前置条件: 用户 testuser 已创建，密码为 testpass123
        测试步骤: 使用正确用户名和密码登录
        预期结果: 返回 access_token 和用户信息
        """
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        assert response.status_code == 200, f"登录失败: {response.json()}"
        data = response.json()

        # 验证返回数据结构
        assert "access_token" in data, "缺少 access_token"
        assert "token_type" in data, "缺少 token_type"
        assert data["token_type"] == "bearer", "token_type 应为 bearer"
        assert "user" in data, "缺少 user 信息"

        # 验证用户信息
        user = data["user"]
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"
        assert user["is_active"] is True
        assert "id" in user
        assert "password_hash" not in user, "密码哈希不应返回给客户端"

        # 验证登录日志已记录
        login_logs = test_user.login_logs
        assert len(login_logs) > 0
        latest_log = login_logs[-1]
        assert latest_log.status == "success"

    def test_login_invalid_credentials(self, client):
        """
        TEST-AUTH-002: 错误凭证登录
        前置条件: 用户 testuser 已创建，密码为 testpass123
        测试步骤:
            1. 使用错误密码登录
            2. 使用不存在的用户名登录
        预期结果: 返回 401 错误
        """
        # 错误密码 - 使用已创建的 testuser (由 test_login_success 测试前置创建)
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401, f"预期 401，实际 {response.status_code}"
        assert "Incorrect username or password" in response.json()["detail"]

        # 不存在的用户
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "anypassword"}
        )
        assert response.status_code == 401, f"预期 401，实际 {response.status_code}"

    def test_login_inactive_user(self, client, inactive_user):
        """
        TEST-AUTH-002b: 禁用用户登录
        前置条件: 用户 inactive 已创建但 is_active=False
        测试步骤: 使用禁用用户登录
        预期结果: 返回 401 错误，提示用户已禁用
        """
        response = client.post(
            "/api/auth/login",
            json={"username": "inactive", "password": "inactive123"}
        )
        assert response.status_code == 401, f"预期 401，实际 {response.status_code}"
        assert "inactive" in response.json()["detail"].lower()


class TestCurrentUser:
    """当前用户信息测试"""

    def test_get_current_user(self, client, test_user):
        """
        TEST-AUTH-003: 获取当前用户信息
        前置条件: 用户已登录并持有有效 token
        测试步骤: 调用 /api/auth/me 接口
        预期结果: 返回当前用户完整信息
        """
        # 先登录获取 token
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]

        # 获取当前用户信息
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"获取用户信息失败: {response.json()}"
        data = response.json()

        # 验证用户信息完整
        assert data["id"] == test_user.id
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["real_name"] == "测试用户"
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "created_at" in data
        assert "updated_at" in data
        assert "password_hash" not in data

    def test_get_current_user_no_token(self, client):
        """
        TEST-AUTH-005a: 无 token 访问受保护接口
        前置条件: 无
        测试步骤: 不带 Authorization header 调用 /api/auth/me
        预期结果: 返回 401 未授权
        """
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """
        TEST-AUTH-005b: 无效 token 访问受保护接口
        前置条件: 无
        测试步骤: 使用伪造的无效 token 调用 /api/auth/me
        预期结果: 返回 401 未授权
        """
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401


class TestChangePassword:
    """修改密码测试"""

    def test_change_password_success(self, client, test_user):
        """
        TEST-AUTH-004: 修改密码成功
        前置条件: 用户已登录
        测试步骤:
            1. 登录获取 token
            2. 调用修改密码接口
        预期结果: 密码修改成功，使用新密码可以登录
        """
        # 获取 token
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]

        # 修改密码
        response = client.put(
            "/api/auth/me/password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "old_password": "testpass123",
                "new_password": "newpass456"
            }
        )
        assert response.status_code == 200, f"修改密码失败: {response.json()}"
        assert response.json()["message"] == "Password updated successfully"

        # 使用新密码登录
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "newpass456"}
        )
        assert login_response.status_code == 200, "新密码应该可以登录"

    def test_change_password_wrong_old(self, client, test_user):
        """
        TEST-AUTH-004b: 旧密码错误
        前置条件: 用户已登录
        测试步骤: 使用错误的旧密码修改密码
        预期结果: 返回 400 错误
        """
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]

        response = client.put(
            "/api/auth/me/password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "old_password": "wrongoldpass",
                "new_password": "newpass456"
            }
        )
        assert response.status_code == 400, f"预期 400，实际 {response.status_code}"
        assert "incorrect" in response.json()["detail"].lower()


class TestRegister:
    """用户注册测试"""

    def test_register_success(self, client, db_session):
        """
        TEST-AUTH-006: 新用户注册
        前置条件: 无
        测试步骤: 使用新用户名注册
        预期结果: 注册成功，返回用户信息
        """
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "password": "newpass123",
                "email": "newuser@example.com",
                "real_name": "新用户"
            }
        )
        assert response.status_code == 200, f"注册失败: {response.json()}"
        data = response.json()

        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["is_active"] is True
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_username(self, client, test_user):
        """
        TEST-AUTH-006b: 用户名已存在
        前置条件: testuser 已存在
        测试步骤: 使用相同用户名注册
        预期结果: 返回 400 错误
        """
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "somepass123",
                "email": "another@example.com"
            }
        )
        assert response.status_code == 400, f"预期 400，实际 {response.status_code}"
        assert "already exists" in response.json()["detail"]


class TestPermissions:
    """权限测试"""

    def test_get_user_permissions(self, client, test_user):
        """
        TEST-AUTH-007: 获取用户权限列表
        前置条件: 用户已登录（无角色权限）
        测试步骤: 调用 /api/auth/permissions
        预期结果: 返回用户权限列表（空列表）
        """
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]

        response = client.get(
            "/api/auth/permissions",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        # test_user 没有分配角色，应该返回空列表
        assert isinstance(response.json(), list)
