"""
认证相关API
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from app.core.config import settings
from app.models.user import User, LoginLog
from app.schemas.user import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPasswordUpdate
)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = db.query(User).filter(User.username == login_data.username).first()

    # 记录登录日志
    log = LoginLog(
        username=login_data.username,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    if not user or not verify_password(login_data.password, user.password_hash):
        log.status = "failed"
        log.fail_reason = "Invalid username or password"
        log.user_id = None
        db.add(log)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        log.status = "failed"
        log.fail_reason = "User is inactive"
        log.user_id = user.id
        db.add(log)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive"
        )

    # 更新登录信息
    user.last_login = datetime.utcnow()
    log.user_id = user.id
    log.status = "success"
    db.add(log)
    db.commit()

    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.id, "username": user.username})
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login/form", response_model=TokenResponse)
async def login_form(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2表单登录"""
    return await login(request, LoginRequest(username=form_data.username, password=form_data.password), db)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse.model_validate(current_user)


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册"""
    # 检查用户名是否存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # 创建用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email,
        phone=user_data.phone,
        real_name=user_data.real_name,
        employee_id=user_data.employee_id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)


@router.put("/me/password")
async def change_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )

    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


@router.get("/permissions")
async def get_user_permissions(current_user: User = Depends(get_current_user)):
    """获取用户权限列表"""
    permissions = []
    for role in current_user.roles:
        for perm in role.permissions:
            if perm.is_active:
                permissions.append({
                    "resource": perm.resource,
                    "action": perm.action,
                    "code": perm.code
                })
    return permissions
