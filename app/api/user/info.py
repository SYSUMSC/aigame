from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.models import ResponseModel
from app.schemas.user import User, UserSchema
from core.security import get_current_user, get_password_hash
from db.session import get_session

info_router = APIRouter()

@info_router.get("/info", response_model=ResponseModel, tags=["User"])
async def get_user_info(current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    try:
        # 获取当前用户信息
        statement = select(User).where(User.username == current_user)
        result = await session.execute(statement)
        user_db = result.scalar_one_or_none()
        if not user_db:
            return ResponseModel(code=1, msg="用户未找到")

        return ResponseModel(code=0, msg="用户信息获取成功", data=user_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@info_router.put("/info", response_model=ResponseModel, tags=["User"])
async def update_user_info(
    name: str = None,
    student_id: str = None,
    avatar: UploadFile = File(None),
    password: str = None,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        # 获取当前用户信息
        statement = select(User).where(User.username == current_user)
        result = await session.execute(statement)
        user_db = result.scalar_one_or_none()
        if not user_db:
            return ResponseModel(code=1, msg="用户未找到")

        # 更新用户信息
        if name is not None:
            user_db.name = name
        if student_id is not None:
            user_db.student_id = student_id
        if avatar is not None:
            # 保存头像文件
            avatar_content = await avatar.read()
            user_db.avatar = avatar_content
        if password is not None:
            user_db.password = get_password_hash(password)

        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)

        return ResponseModel(code=0, msg="用户信息更新成功", data=user_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))