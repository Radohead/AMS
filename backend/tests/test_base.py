"""
基础测试类
"""
import pytest


class BaseAPITest:
    """API 测试基类"""

    @pytest.fixture(autouse=True)
    def setup_method_fixture(self, client, db_session):
        """每个测试方法执行前的设置"""
        self.client = client
        self.db = db_session

    def assert_success(self, response):
        """断言响应成功"""
        assert response.status_code == 200 or response.status_code == 201, \
            f"Expected success, got {response.status_code}: {response.json()}"

    def assert_error(self, response, expected_code):
        """断言响应错误"""
        assert response.status_code == expected_code, \
            f"Expected {expected_code}, got {response.status_code}: {response.json()}"

    def assert_has_keys(self, data, keys):
        """断言数据包含指定键"""
        for key in keys:
            assert key in data, f"Missing key: {key}"


class AuthenticatedTest(BaseAPITest):
    """需要认证的测试基类"""

    @pytest.fixture(autouse=True)
    def setup_auth(self, client, db_session, test_user):
        """设置认证信息"""
        self.client = client
        self.db = db_session
        self.test_user = test_user

        # 获取认证 token
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}
