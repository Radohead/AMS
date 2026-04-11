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
from app.models.asset import Category, Department, Employee, AssetType, AssetStatus
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


@pytest.fixture(scope="function")
def test_category(db_session):
    """创建测试分类"""
    category = Category(
        name="电子设备",
        code="ELECTRONIC",
        asset_type=AssetType.FIXED,
        description="电子设备分类",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture(scope="function")
def test_department(db_session):
    """创建测试部门"""
    department = Department(
        name="技术部",
        code="TECH",
        description="技术部门",
        is_active=True,
    )
    db_session.add(department)
    db_session.commit()
    db_session.refresh(department)
    return department


@pytest.fixture(scope="function")
def test_employee(db_session, test_department):
    """创建测试员工"""
    employee = Employee(
        employee_no="EMP001",
        name="张三",
        email="zhangsan@example.com",
        phone="13800138000",
        department_id=test_department.id,
        position="工程师",
        status="active",
        is_active=True,
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee


@pytest.fixture(scope="function")
def test_role(db_session):
    """创建测试角色"""
    role = Role(
        name="资产管理员",
        code="asset_admin",
        description="负责资产管理",
        is_active=True,
        is_system=False,
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture(scope="function")
def test_permission(db_session):
    """创建测试权限"""
    permission = Permission(
        name="资产创建",
        code="asset:create",
        resource="asset",
        action="create",
        description="创建资产权限",
        is_active=True,
    )
    db_session.add(permission)
    db_session.commit()
    db_session.refresh(permission)
    return permission


@pytest.fixture(scope="function")
def user_with_asset_perms(db_session, test_role):
    """创建有资产权限的用户"""
    # 创建权限
    perms = []
    for resource, action in [("asset", "create"), ("asset", "update"), ("asset", "delete")]:
        # 检查是否已存在
        existing = db_session.query(Permission).filter(
            Permission.code == f"{resource}:{action}"
        ).first()
        if existing:
            perms.append(existing)
        else:
            perm = Permission(
                name=f"{resource}:{action}",
                code=f"{resource}:{action}",
                resource=resource,
                action=action,
                is_active=True,
            )
            db_session.add(perm)
            perms.append(perm)
    db_session.commit()
    for perm in perms:
        db_session.refresh(perm)

    # 创建角色
    role = Role(
        name="资产操作员",
        code="asset_operator",
        description="可操作资产",
        is_active=True,
        is_system=False,
    )
    role.permissions = perms
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)

    # 创建用户
    user = User(
        username="assetuser",
        password_hash=get_password_hash("assetpass123"),
        email="asset@example.com",
        real_name="资产用户",
        is_active=True,
        is_superuser=False,
    )
    user.roles = [role]
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def asset_user_headers(client, user_with_asset_perms):
    """获取有资产权限用户的认证 header"""
    response = client.post(
        "/api/auth/login",
        json={"username": "assetuser", "password": "assetpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
