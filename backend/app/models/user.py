"""
用户和权限模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


# 用户角色关联表
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True)
)

# 角色权限关联表
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True)
)


class User(Base):
    """系统用户"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    email = Column(String(100), nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="电话")
    real_name = Column(String(100), nullable=True, comment="真实姓名")
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="关联员工ID")
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_superuser = Column(Boolean, default=False, comment="是否超级管理员")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    employee = relationship("Employee")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    login_logs = relationship("LoginLog", back_populates="user")
    operation_logs = relationship("OperationLog", back_populates="user")


class Role(Base):
    """角色"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    code = Column(String(50), unique=True, nullable=False, comment="角色编码")
    description = Column(Text, nullable=True, comment="角色描述")
    is_system = Column(Boolean, default=False, comment="是否系统内置")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    """权限"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="权限名称")
    code = Column(String(100), unique=True, nullable=False, comment="权限编码")
    resource = Column(String(50), nullable=False, comment="资源类型: asset/category/employee/department/repair/scrap/inventory/user/role")
    action = Column(String(50), nullable=False, comment="操作类型: create/read/update/delete/approve/export")
    description = Column(Text, nullable=True, comment="权限描述")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class LoginLog(Base):
    """登录日志"""
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(50), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    status = Column(String(20), default="success", comment="登录状态: success/failed")
    fail_reason = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    user = relationship("User", back_populates="login_logs")


class OperationLog(Base):
    """操作日志"""
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False, comment="操作类型")
    resource = Column(String(50), nullable=False, comment="资源类型")
    resource_id = Column(Integer, nullable=True, comment="资源ID")
    method = Column(String(10), nullable=True, comment="HTTP方法")
    path = Column(String(500), nullable=True, comment="请求路径")
    ip_address = Column(String(50), nullable=True)
    before_data = Column(Text, nullable=True, comment="操作前数据")
    after_data = Column(Text, nullable=True, comment="操作后数据")
    status = Column(String(20), default="success", comment="操作状态")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    user = relationship("User", back_populates="operation_logs")
