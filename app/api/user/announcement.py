from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.models import ResponseModel
from db.session import get_session
from app.schemas.user import User, UserSchema
from app.schemas.announcement import Announcement, AnnouncementSchema
from core.security import get_current_user, get_password_hash

announce_router = APIRouter()

@announce_router.get("/announcements", response_model=ResponseModel, tags=["Announcement"])

async def get_announcement(current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    try:
        # 检查当前用户是否合法
        statement = select(User).where(User.username == current_user)
        result = await session.execute(statement)
        user_db = result.scalar_one_or_none()
        if not user_db:
            return ResponseModel(code=1, msg="用户未找到")

        return ResponseModel(code=0, msg="用户信息获取成功", data=[{
            # content
            date,
            content
        }])

    except Exception as e:
        return ResponseModel(code=1, msg=str(e))