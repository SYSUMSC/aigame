from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from api.response_model import ResponseModel
from core.security import create_access_token, verify_password, get_current_admin
from core.utils import load_config_from_db
from db.session import get_session

auth_router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@auth_router.post("/login", response_model=ResponseModel, tags=["Admin"])
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    try:
        config_dict = await load_config_from_db(session)

        admin_user = config_dict.get("admin_user")
        admin_pwd = config_dict.get("admin_pwd")

        if not admin_user or not admin_pwd:
            return ResponseModel(code=1, msg="管理员用户或密码未设置")

        if request.username != admin_user or not verify_password(request.password, admin_pwd):
            return ResponseModel(code=1, msg="用户名或密码错误")

        access_token = create_access_token(data={"sub": request.username})
        return ResponseModel(code=0, msg="登录成功", data={"access_token": access_token, "token_type": "bearer"})
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))