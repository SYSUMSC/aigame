from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from core.security import (get_current_admin, get_current_user,
                           oauth2_scheme_user, verify_password)
from core.utils import load_config_from_db
from db.session import get_session


class AdminAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # 使用 get_session 获取数据库会话
        async for session in get_session():
            if request.url.path.startswith("/api/admin") and not request.url.path.startswith("/api/admin/login") \
                and not request.url.path.startswith(("/docs", "/redoc")) \
                and not request.url.path.startswith("/api/user") \
                and not request.url.path.startswith("/admin") \
                and not request.url.path.startswith("/user") \
                and not request.url.path.endswith("/openapi.json"):
                try:
                    # 检查会话中的 session_name 和 session_pwd
                    session_name = request.session.get('session_name')
                    session_pwd = request.session.get('session_pwd')

                    if not session_name or not session_pwd:
                        return JSONResponse(
                            status_code=200,
                            content={
                                "code": 1,
                                "msg": "未授权，未登录",
                                "data": None
                            }
                        )

                    # 从数据库中加载管理员用户信息进行验证
                    config_dict = await load_config_from_db(session)
                    admin_user = config_dict.get("admin_user")
                    admin_pwd = config_dict.get("admin_pwd")
                    if session_name != admin_user or not verify_password(session_pwd, admin_pwd):
                        return JSONResponse(
                            status_code=200,
                            content={
                                "code": 1,
                                "msg": "未授权，登录信息无效",
                                "data": None
                            }
                        )

                except Exception as e:
                    return JSONResponse(
                        status_code=200,
                        content={
                            "code": 1,
                            "msg": "未授权：" + str(e),
                            "data": None
                        }
                    )
        return await call_next(request)

class UserAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/user") and not request.url.path.startswith("/api/user/login") \
             and not request.url.path.startswith("/api/user/register") \
            and not request.url.path.startswith(("/docs", "/redoc")) \
            and not request.url.path.startswith("/api/admin") \
            and not request.url.path.startswith("/admin") \
            and not request.url.path.startswith("/user") \
            and not request.url.path.endswith("/openapi.json"):
            try:
                user = await get_current_user(request)
                request.state.user = user
            except Exception as e:
                return JSONResponse(
                    status_code=200,
                    content={
                        "code": 1,
                        "msg": "未授权："+str(e),
                        "data": None
                    }
                )
        return await call_next(request)