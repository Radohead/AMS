"""
操作日志模块测试

用例编号:
- TEST-OPLOG-001: test_list_operation_logs           - 获取操作日志列表
- TEST-OPLOG-002: test_list_logs_filter_by_username - 按用户名筛选
- TEST-OPLOG-003: test_list_logs_filter_by_resource - 按资源类型筛选
- TEST-OPLOG-004: test_non_admin_cannot_access     - 非管理员禁止访问
- TEST-OPLOG-005: test_asset_crud_calls_logging    - 资产CRUD操作触发日志记录
- TEST-OPLOG-006: test_get_request_not_logged      - GET 请求不触发日志
"""
import pytest
from unittest.mock import patch, MagicMock
from app.middleware.operation_logging import OperationLoggingMiddleware


class TestOperationLogList:
    """操作日志列表测试"""

    def test_list_operation_logs_admin(
        self, client, admin_user, db_session
    ):
        """TEST-OPLOG-001: 管理员获取操作日志列表"""
        # 先登录管理员
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 获取操作日志
        response = client.get(
            "/api/permissions/logs/operation",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Failed: {response.json()}"
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_list_logs_filter_by_username(
        self, client, admin_user, test_user
    ):
        """TEST-OPLOG-002: 按用户名筛选操作日志"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 按用户名筛选
        response = client.get(
            "/api/permissions/logs/operation",
            headers={"Authorization": f"Bearer {token}"},
            params={"username": "admin"}
        )
        assert response.status_code == 200
        items = response.json()["items"]
        for item in items:
            assert "admin" in item.get("username", "")

    def test_list_logs_filter_by_resource(
        self, client, admin_user, test_category
    ):
        """TEST-OPLOG-003: 按资源类型筛选操作日志"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 按资源类型筛选（asset）
        response = client.get(
            "/api/permissions/logs/operation",
            headers={"Authorization": f"Bearer {token}"},
            params={"resource": "asset"}
        )
        assert response.status_code == 200


class TestOperationLogPermission:
    """操作日志权限测试"""

    def test_non_admin_cannot_access(
        self, client, test_user
    ):
        """TEST-OPLOG-004: 非管理员用户不能访问操作日志"""
        # 普通用户登录
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        token = login_resp.json()["access_token"]

        # 尝试访问操作日志
        response = client.get(
            "/api/permissions/logs/operation",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403, f"非管理员应该被拒绝，实际: {response.status_code}"


class TestOperationLogAutoRecord:
    """操作日志自动记录测试"""

    def test_asset_crud_calls_logging(
        self, client, asset_user_headers, admin_user, test_category
    ):
        """TEST-OPLOG-005: 资产CRUD操作触发中间件记录日志"""
        mock_write = MagicMock()

        # patch _write_log 使中间件调用 mock
        with patch.object(
            OperationLoggingMiddleware, "_write_log", mock_write
        ):
            # 创建资产
            resp = client.post(
                "/api/assets/",
                headers=asset_user_headers,
                json={
                    "name": "日志测试资产",
                    "category_id": test_category.id,
                    "asset_type": "fixed",
                },
            )
            assert resp.status_code == 200
            asset_id = resp.json()["id"]

            # 更新资产
            client.put(
                f"/api/assets/{asset_id}",
                headers=asset_user_headers,
                json={"name": "已更新日志资产"},
            )

            # 删除资产
            client.delete(
                f"/api/assets/{asset_id}",
                headers=asset_user_headers,
            )

        # 验证 _write_log 被调用了 3 次（create/update/delete）
        assert mock_write.call_count >= 3, \
            f"期望至少3次日志写入，实际: {mock_write.call_count}"

        # 验证调用参数包含正确的 HTTP 方法
        calls = mock_write.call_args_list
        methods = []
        for call in calls:
            # call[0] 是 positional args tuple
            args = call[0] if hasattr(call, '__getitem__') else call.args
            # args: (self, request, method, path, client_ip, status, error_message)
            # self is stripped by MagicMock, so method is at index 1
            methods.append(args[1])
        assert "POST" in methods, f"缺少 POST 操作，methods={methods}"
        assert "PUT" in methods, f"缺少 PUT 操作，methods={methods}"
        assert "DELETE" in methods, f"缺少 DELETE 操作，methods={methods}"

    def test_get_request_not_logged(self, client, test_category, asset_user_headers):
        """TEST-OPLOG-006: GET 请求不应记录操作日志"""
        mock_write = MagicMock()

        with patch.object(OperationLoggingMiddleware, "_write_log", mock_write):
            # 创建资产
            resp = client.post(
                "/api/assets/",
                headers=asset_user_headers,
                json={
                    "name": "GET测试资产",
                    "category_id": test_category.id,
                    "asset_type": "fixed",
                },
            )
            assert resp.status_code == 200

            # GET 请求查询列表
            client.get("/api/assets/", headers=asset_user_headers)

        # GET 请求不应触发日志记录，只有 POST create 那一次
        assert mock_write.call_count == 1, \
            f"GET 请求不应触发日志，实际调用: {mock_write.call_count}"
        first_call = mock_write.call_args_list[0]
        args = first_call[0] if hasattr(first_call, '__getitem__') else first_call.args
        assert args[1] == "POST", f"第一次调用应为 POST，实际: {args[1]}"
