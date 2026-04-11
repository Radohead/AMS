"""
操作日志工具函数
提供独立的日志写入功能，供中间件和业务代码调用
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import OperationLog


def write_operation_log(
    db: Session,
    user_id: int,
    username: str,
    action: str,
    resource: str,
    resource_id: Optional[int] = None,
    method: Optional[str] = None,
    path: Optional[str] = None,
    ip_address: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None,
) -> OperationLog:
    """
    写入操作日志

    Args:
        db: 数据库会话（由调用方提供，确保在同一事务上下文中）
        user_id: 用户ID
        username: 用户名
        action: 操作类型 (create/update/delete)
        resource: 资源类型 (asset/category/employee等)
        resource_id: 资源ID
        method: HTTP方法
        path: 请求路径
        ip_address: 客户端IP
        status: 操作状态
        error_message: 错误信息

    Returns:
        创建的 OperationLog 记录
    """
    log = OperationLog(
        user_id=user_id,
        username=username,
        action=action,
        resource=resource,
        resource_id=resource_id,
        method=method,
        path=path,
        ip_address=ip_address,
        status=status,
        error_message=error_message,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def parse_resource_from_path(path: str) -> tuple:
    """
    从请求路径解析资源类型和资源ID

    Examples:
        /api/assets/123 -> ('assets', 123)
        /api/assets/123/assign -> ('assets', 123)
        /api/categories/ -> ('categories', None)
    """
    parts = path.strip("/").split("/")
    if len(parts) < 2:
        return "unknown", None

    resource = parts[1]
    resource_id = None
    if len(parts) >= 3 and parts[2].isdigit():
        resource_id = int(parts[2])

    return resource, resource_id


def map_http_method_to_action(method: str) -> str:
    """HTTP 方法映射到操作类型"""
    mapping = {
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }
    return mapping.get(method.upper(), method.lower())


# 需要记录日志的路径前缀
LOGGED_PATH_PREFIXES = (
    "/api/assets",
    "/api/categories",
    "/api/departments",
    "/api/employees",
    "/api/inventory",
    "/api/repair",
    "/api/scrap",
    "/api/inventory-check",
    "/api/permissions",
)

# 不需要记录的路径（排除项）
EXCLUDED_PATHS = frozenset({
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/permissions",
    "/api/permissions/logs/login",
    "/api/permissions/logs/operation",
})

# 不需要记录的 HTTP 方法
EXCLUDED_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def should_log_request(method: str, path: str) -> bool:
    """判断请求是否需要记录日志"""
    if method in EXCLUDED_METHODS:
        return False
    if path in EXCLUDED_PATHS:
        return False
    return any(path.startswith(prefix) for prefix in LOGGED_PATH_PREFIXES)
