from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.response_model import ResponseModel
from core.security import (create_access_token, get_password_hash,
                               verify_password)
from db.session import get_session
from schemas.user import User, UserSchema

auth_router = APIRouter()

@auth_router.post("/register", response_model=ResponseModel, tags=["User"])
async def register(user: UserSchema, session: AsyncSession = Depends(get_session)):
    try:
        # 检查用户是否已存在
        existing_user = await session.execute(select(User).where(User.username == user.username))
        if existing_user.scalar_one_or_none():
            return ResponseModel(code=1, msg="用户名已存在")
        # 检查邮箱是否已存在
        existing_email = await session.execute(select(User).where(User.email == user.email))
        if existing_email.scalar_one_or_none():
            return ResponseModel(code=1, msg="邮箱已存在")

        # 检查学号是否已存在
        existing_student_id = await session.execute(select(User).where(User.student_id == user.student_id))
        if existing_student_id.scalar_one_or_none():
            return ResponseModel(code=1, msg="学号已存在")

        # 创建新用户
        user_db = User(**user.model_dump())
        user_db.password = get_password_hash(user.password)
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)
        return ResponseModel(code=0, msg="用户注册成功", data=user_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

class LoginRequest(BaseModel):
    username: str
    password: str
@auth_router.post("/login", response_model=ResponseModel, tags=["User"])
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    username = request.username
    password = request.password
    try:
        # 检查用户是否存在
        user = await session.execute(select(User).where(User.username == username))
        user_db = user.scalar_one_or_none()
        if not user_db or not verify_password(password, user_db.password):
            return ResponseModel(code=1, msg="用户名或密码错误")

        # 创建访问令牌
        access_token = create_access_token(data={"sub": user_db.username})
        return ResponseModel(code=0, msg="登录成功", data={"access_token": access_token, "token_type": "bearer"})
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))