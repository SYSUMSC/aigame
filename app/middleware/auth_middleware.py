from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.security import get_current_admin, get_current_user, oauth2_scheme_admin, oauth2_scheme_user

class AdminAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/admin") and not request.url.path.startswith("/api/admin/login") \
            and not request.url.path.startswith(("/docs", "/redoc")) \
            and not request.url.path.startswith("/api/user") \
            and not request.url.path.endswith("/openapi.json"):
            try:
                token = await oauth2_scheme_admin(request)
                user = await get_current_admin(token)
                request.state.user = user
            except Exception as e:
                return JSONResponse(
                    status_code=200,
                    content={
                        "code": 1,
                        "msg": "未授权",
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
            and not request.url.path.endswith("/openapi.json"):
            try:
                token = await oauth2_scheme_user(request)
                user = await get_current_user(token)
                request.state.user = user
            except Exception as e:
                return JSONResponse(
                    status_code=200,
                    content={
                        "code": 1,
                        "msg": "未授权",
                        "data": None
                    }
                )
        return await call_next(request)