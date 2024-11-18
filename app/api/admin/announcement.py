from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import secrets

from core.security import get_password_hash
from db.session import get_session
# from app.schemas.user import User, UserSchema, UserSearchSchema
from app.schemas.announcement import Announcement, AnnouncementSchema, AnnouncementSearchSchema

from ..models import BatchDeleteRequest, ResponseModel

ann_router = APIRouter()

@ann_router.post("/announcement", response_model=ResponseModel, tags=["Admin"])
async def create_announcement(announcement: AnnouncementSchema, session: AsyncSession = Depends(get_session)):
    try:
        # if user.password is None:
        #     user.password = secrets.token_urlsafe(10)  # 生成随机密码
        if announcement.date is None:
            announcement.date = datetime.now(timezone.utc).to_string()
        # announcement id => need to fix
        # if announcement.id is None:
        #     announcement.id = 
        announcement_db = Announcement()
        session.add(announcement_db)
        await session.commit()
        await session.refresh(announcement_db)
        return ResponseModel(code=0, 
                            #  msg="用户创建成功，默认密码是"+user.password,
                             msg="公告创建成功, id是" + announcement_db.id,
                             data=announcement_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@ann_router.delete("/announcement/{ann_id}", response_model=ResponseModel, tags=["Admin"])
async def delete_user(ann_id: int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Announcement).where(Announcement.id == ann_id)
        result = await session.execute(statement)
        # user_db = result.scalar_one_or_none()
        announcement_db = result.scalar_one_or_none()
        if not announcement_db:
            return ResponseModel(code=1, msg="公告未找到")
        await session.delete(announcement_db)
        await session.commit()
        return ResponseModel(code=0, msg="公告删除成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@ann_router.delete("/announcement", response_model=ResponseModel, tags=["Admin"])
async def delete_announcements(request: BatchDeleteRequest, session: AsyncSession = Depends(get_session)):
    try:
        ann_ids = request.ids
        statement = select(Announcement).where(Announcement.id.in_(ann_ids))
        result = await session.execute(statement)
        announcement_db = result.scalars().all()
        for ann in announcement_db:
            await session.delete(ann)
        await session.commit()
        return ResponseModel(code=0, msg="Announcement delete successfully", count=len(announcement_db))
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@ann_router.post("/announcement/search", response_model=ResponseModel, tags=["Admin"])
async def search_users(search: AnnouncementSearchSchema, page: int = 1, limit: int = 10, session: AsyncSession = Depends(get_session)):
    try:
        query = select(Announcement)
        filters = []
        for field, value in search.model_dump(exclude_unset=True).items():
            if isinstance(value, str):
                filters.append(getattr(Announcement, field).like(f"%{value}%"))
            else:
                filters.append(getattr(Announcement, field) == value)
        query = query.where(*filters)
        total_statement = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_statement)
        total = total_result.scalar()
        query = query.offset((page - 1) * limit).limit(limit)
        result = await session.execute(query)
        announcements = result.scalars().all()
        return ResponseModel(code=0, msg="Search Successfully", data=[announcements.model_dump() for ann in announcements], count=total)
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))