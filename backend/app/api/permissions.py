"""
权限管理API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.models.user import User, Role, Permission, OperationLog, LoginLog
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    PermissionCreate,
    PermissionResponse,
    LoginLogResponse,
    OperationLogResponse
)
from app.schemas.asset import PageResponse

router = APIRouter()


# ========== 用户管理 ==========

@router.get("/users", response_model=PageResponse)
async def list_users(
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户列表"""
    query = db.query(User)

    if keyword:
        query = query.filter(
            User.username.contains(keyword) |
            User.real_name.contains(keyword) |
            User.email.contains(keyword)
        )

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    items = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    item_responses = [UserResponse.model_validate(item) for item in items]
    return PageResponse(total=total, page=page, page_size=page_size, items=item_responses)


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建用户"""
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email,
        phone=user_data.phone,
        real_name=user_data.real_name,
        employee_id=user_data.employee_id,
    )

    if user_data.role_ids:
        roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
        user.roles = roles

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)

    if "role_ids" in update_data:
        role_ids = update_data.pop("role_ids")
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        user.roles = roles

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除用户"""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return {"message": "User deactivated successfully"}


# ========== 角色管理 ==========

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取角色列表"""
    query = db.query(Role)
    if is_active is not None:
        query = query.filter(Role.is_active == is_active)
    return query.order_by(Role.id).all()


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建角色"""
    if db.query(Role).filter(Role.code == role_data.code).first():
        raise HTTPException(status_code=400, detail="Role code already exists")

    role = Role(
        name=role_data.name,
        code=role_data.code,
        description=role_data.description
    )

    if role_data.permission_ids:
        permissions = db.query(Permission).filter(Permission.id.in_(role_data.permission_ids)).all()
        role.permissions = permissions

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot modify system role")

    update_data = role_data.model_dump(exclude_unset=True)

    if "permission_ids" in update_data:
        permission_ids = update_data.pop("permission_ids")
        permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        role.permissions = permissions

    for key, value in update_data.items():
        setattr(role, key, value)

    db.commit()
    db.refresh(role)

    return role


# ========== 权限管理 ==========

@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    resource: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取权限列表"""
    query = db.query(Permission).filter(Permission.is_active == True)
    if resource:
        query = query.filter(Permission.resource == resource)
    return query.order_by(Permission.resource, Permission.action).all()


@router.get("/permissions/grouped")
async def get_permissions_grouped(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取按资源分组的权限列表"""
    permissions = db.query(Permission).filter(Permission.is_active == True).all()

    grouped = {}
    for perm in permissions:
        if perm.resource not in grouped:
            grouped[perm.resource] = []
        grouped[perm.resource].append({
            "id": perm.id,
            "name": perm.name,
            "code": perm.code,
            "action": perm.action,
            "description": perm.description
        })

    return grouped


# ========== 日志管理 ==========

@router.get("/logs/login", response_model=PageResponse)
async def list_login_logs(
    username: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取登录日志"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Permission denied")

    query = db.query(LoginLog)

    if username:
        query = query.filter(LoginLog.username.contains(username))
    if status:
        query = query.filter(LoginLog.status == status)

    total = query.count()
    items = query.order_by(LoginLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    item_responses = [LoginLogResponse.model_validate(item) for item in items]
    return PageResponse(total=total, page=page, page_size=page_size, items=item_responses)


@router.get("/logs/operation", response_model=PageResponse)
async def list_operation_logs(
    username: Optional[str] = None,
    resource: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取操作日志"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Permission denied")

    query = db.query(OperationLog)

    if username:
        query = query.filter(OperationLog.username.contains(username))
    if resource:
        query = query.filter(OperationLog.resource == resource)

    total = query.count()
    items = query.order_by(OperationLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    item_responses = [OperationLogResponse.model_validate(item) for item in items]
    return PageResponse(total=total, page=page, page_size=page_size, items=item_responses)
