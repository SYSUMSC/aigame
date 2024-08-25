from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.security import get_current_admin

class AdminAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/admin") and not request.url.path.startswith("/api/admin/login") \
            and not request.url.path.startswith(("/docs", "/redoc")) \
            and not request.url.path.startswith("/api/user") \
            and not request.url.path.endswith("/openapi.json"):
            try:
                access_token = None
                # 先尝试从请求头中获取 access_token
                if "access_token" in request.headers:
                    access_token = request.headers["access_token"]
                elif request.method == "POST":
                    if "application/json" in request.headers.get("Content-Type", ""):
                        # 从 POST 请求体中获取 access_token (JSON body)
                        access_token = (await request.json()).get("access_token")
                    elif "application/x-www-form-urlencoded" in request.headers.get("Content-Type", ""):
                        # 从 POST 请求体中获取 access_token (表单)
                        form = await request.form()
                        access_token = form.get("access_token")
                elif request.method == "GET":
                    # 从 GET 请求参数中获取 access_token
                    access_token = request.query_params.get("access_token")

                if not access_token:
                    return JSONResponse(
                        status_code=200,
                        content={
                            "code": 1,
                            "msg": "未授权，没传输access_token",
                            "data": None
                        }
                    )
                user = await get_current_admin(access_token)
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