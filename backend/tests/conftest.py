"""
pytest fixtures - 测试数据库配置
"""
import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 确保可以导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base
from app.models.user import User, Role, Permission, LoginLog
from app.core.security import get_password_hash


# 测试数据库 URL - 使用 SQLite 内存数据库
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """创建测试数据库引擎"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    yield engine
    # 关闭连接
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """创建测试数据库会话"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """创建 FastAPI 测试客户端"""
    from fastapi.testclient import TestClient
    from app.core.database import get_db
    from main import app

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username="testuser",
        password_hash=get_password_hash("testpass123"),
        email="test@example.com",
        real_name="测试用户",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_user(db_session):
    """创建管理员用户"""
    user = User(
        username="admin",
        password_hash=get_password_hash("admin123"),
        email="admin@example.com",
        real_name="管理员",
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def inactive_user(db_session):
    """创建已禁用的用户"""
    user = User(
        username="inactive",
        password_hash=get_password_hash("inactive123"),
        email="inactive@example.com",
        real_name="已禁用用户",
        is_active=False,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """获取认证后的请求头"""
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_headers(client, admin_user):
    """获取管理员认证后的请求头"""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
