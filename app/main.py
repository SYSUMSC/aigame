import os
import sys

from fastapi.staticfiles import StaticFiles

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from admin.router import admin_router

from api.admin.router import admin_api_router
from api.user.router import user_router
from core.config import settings
from db.session import get_session, lifespan
from middleware.auth_middleware import AdminAuthMiddleware, UserAuthMiddleware
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_ADMIN_STR}/openapi.json",
    openapi_tags=[
        {"name": "Admin", "description": "后台api"},
        {"name": "User", "description": "前台api"},
    ], lifespan=lifespan)

app.add_middleware(AdminAuthMiddleware)
app.add_middleware(UserAuthMiddleware)
# session中间件，用于admin api和admin 前端
app.add_middleware(SessionMiddleware, secret_key='aigame')


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=200,
        content={
            "code": 1,
            "msg": exc.detail,
            "data": None
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200,
        content={
            "code": 1,
            "msg": "请求参数验证失败",
            "data": str(exc.errors())
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "code": 1,
            "msg": str(exc),
            "data": None
        }
    )
# 后台api
app.include_router(admin_api_router, prefix=settings.API_ADMIN_STR)
# 用户api
app.include_router(user_router, prefix=settings.API_USER_STR)
# admin静态文件目录
app.mount("/admin/static", StaticFiles(directory="admin/static"), name="admin_static")
# 包含admin路由
app.include_router(admin_router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="API documentation",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)