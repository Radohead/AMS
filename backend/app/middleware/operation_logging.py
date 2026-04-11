"""
操作日志中间件
自动拦截并记录所有写操作的 CRUD 日志
"""
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.utils.operation_log import (
    write_operation_log,
    parse_resource_from_path,
    map_http_method_to_action,
    should_log_request,
)


def get_user_info_from_request(request: Request) -> tuple:
    """
    从请求中提取用户信息

    优先级：
    1. request.state（由 get_current_user dependency 设置）
    2. Authorization header（Bearer token）
    """
    user_id = getattr(request.state, "user_id", None)
    username = getattr(request.state, "username", None)

    if user_id is not None:
        return user_id, username or "system"

    # 尝试从 Authorization header 解析
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return 0, "authenticated_user"

    return 0, "anonymous"


class OperationLoggingMiddleware(BaseHTTPMiddleware):
    """操作日志记录中间件"""

    def _write_log(self, request: Request, method: str, path: str,
                    client_ip: Optional[str], status: str, error_message: Optional[str]):
        """写入日志（抽取为方法便于测试 mock）"""
        try:
            user_id, username = get_user_info_from_request(request)
            resource, resource_id = parse_resource_from_path(path)
            action = map_http_method_to_action(method)

            # 从 request.state 获取 db（由 get_db dependency 设置）
            db = getattr(request.state, "db", None)

            if db is not None:
                write_operation_log(
                    db=db,
                    user_id=user_id,
                    username=username,
                    action=action,
                    resource=resource,
                    resource_id=resource_id,
                    method=method,
                    path=path,
                    ip_address=client_ip,
                    status=status,
                    error_message=error_message,
                )
        except Exception as e:
            # 日志记录失败不影响主业务
            print(f"[OperationLog] Failed to write log: {e}")

    async def dispatch(self, request: Request, call_next) -> Response:
        """拦截请求，记录操作日志"""
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else None

        # 判断是否需要记录
        should_log_this = should_log_request(method, path)

        response = None
        status = "success"
        error_message = None

        try:
            response = await call_next(request)

            if response.status_code >= 400:
                status = "failed"
                try:
                    body = b""
                    async for chunk in response.body_iterator:
                        body += chunk
                    error_message = body.decode("utf-8", errors="ignore")[:500]
                    # 重建响应
                    from starlette.responses import Response as StarletteResponse
                    response = StarletteResponse(
                        content=body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                    )
                except Exception:
                    error_message = f"HTTP {response.status_code}"
        except Exception as e:
            status = "failed"
            error_message = str(e)[:500]
            raise

        # 写入日志
        if should_log_this:
            self._write_log(request, method, path, client_ip, status, error_message)

        return response

