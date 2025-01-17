from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models import ResponseModel
from core.security import verify_password
from core.utils import load_config_from_db
from db.session import get_session

auth_router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@auth_router.post("/login", response_model=ResponseModel, tags=["Admin"])
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session), fastapi_request: Request = None):
    try:
        config_dict = await load_config_from_db(session)

        admin_user = config_dict.get("admin_user")
        admin_pwd = config_dict.get("admin_pwd")

        if not admin_user or not admin_pwd:
            return ResponseModel(code=1, msg="管理员用户或密码未设置")

        if request.username != admin_user or not verify_password(request.password, admin_pwd):
            return ResponseModel(code=1, msg="用户名或密码错误")

        # 使用会话保存用户名和密码
        fastapi_request.session['session_name'] = request.username
        fastapi_request.session['session_pwd'] = request.password

        return ResponseModel(code=0, msg="登录成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@auth_router.post("/logout", response_model=ResponseModel, tags=["Admin"])
async def logout(fastapi_request: Request):
    try:
        fastapi_request.session.clear()  # 清除会话数据
        return ResponseModel(code=0, msg="退出登录成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
