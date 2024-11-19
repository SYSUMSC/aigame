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
async def get_announcement(session: AsyncSession = Depends(get_session)):
    try:
        # 获取所有公告信息
        statement = select(Announcement)
        result = await session.execute(statement)
        items = result.scalars().all()
        return ResponseModel(code=0, msg="公告信息获取成功", data=[item.model_dump() for item in items])
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
