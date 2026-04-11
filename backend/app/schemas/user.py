"""
Pydantic schemas - 用户和权限相关
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 用户 Schema ==========
class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    real_name: Optional[str] = Field(None, max_length=100)
    employee_id: Optional[int] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role_ids: Optional[List[int]] = None


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    real_name: Optional[str] = Field(None, max_length=100)
    employee_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 角色 Schema ==========
class RoleBase(BaseModel):
    name: str = Field(..., max_length=50)
    code: str = Field(..., max_length=50)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    id: int
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 权限 Schema ==========
class PermissionBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=100)
    resource: str
    action: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 认证 Schema ==========
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None


# ========== 日志 Schema ==========
class LoginLogResponse(BaseModel):
    id: int
    user_id: int
    username: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    fail_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OperationLogResponse(BaseModel):
    id: int
    user_id: int
    username: str
    action: str
    resource: str
    resource_id: Optional[int] = None
    method: Optional[str] = None
    path: Optional[str] = None
    ip_address: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
