import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

# from app.schemas.user import User, UserSchema, UserSearchSchema
from app.schemas.announcement import (Announcement, AnnouncementSchema,
                                      AnnouncementSearchSchema)
from core.security import get_password_hash
from db.session import get_session

from ..models import BatchDeleteRequest, ResponseModel

announce_router = APIRouter()

@announce_router.post("/announcement", response_model=ResponseModel, tags=["Admin"])
async def create_announcement(announcement: AnnouncementSchema, session: AsyncSession = Depends(get_session)):
    try:
        # 如果日期未设置，使用当前时间
        if announcement.date is None:
            announcement.date = datetime.now(timezone.utc)

        # 创建公告实例
        announcement_db = Announcement(**announcement.model_dump())
        session.add(announcement_db)
        await session.commit()
        await session.refresh(announcement_db)

        return ResponseModel(
            code=0,
            msg=f"公告创建成功, id是 {announcement_db.id}",
            data=announcement_db.model_dump()
        )
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
@announce_router.put("/announcement/{announcement_id}", response_model=ResponseModel, tags=["Admin"])
async def update_announcement(
    announcement_id: int,
    announcement: AnnouncementSchema,
    session: AsyncSession = Depends(get_session)
):
    try:
        # 查询公告
        statement = select(Announcement).where(Announcement.id == announcement_id)
        result = await session.execute(statement)
        announcement_db = result.scalar_one_or_none()

        if not announcement_db:
            return ResponseModel(code=1, msg="公告未找到")

        # 更新公告字段，仅更新传入的值
        announcement_data = announcement.model_dump(exclude_unset=True)
        for key, value in announcement_data.items():
            setattr(announcement_db, key, value)

        # 更新编辑时间
        announcement_db.date = datetime.now(timezone.utc)

        session.add(announcement_db)
        await session.commit()
        await session.refresh(announcement_db)

        return ResponseModel(
            code=0,
            msg="公告更新成功",
            data=announcement_db.model_dump()
        )
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
@announce_router.delete("/announcement/{ann_id}", response_model=ResponseModel, tags=["Admin"])
async def delete_user(ann_id: int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Announcement).where(Announcement.id == ann_id)
        result = await session.execute(statement)
        announcement_db = result.scalar_one_or_none()
        if not announcement_db:
            return ResponseModel(code=1, msg="公告未找到")
        await session.delete(announcement_db)
        await session.commit()
        return ResponseModel(code=0, msg="公告删除成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@announce_router.delete("/announcement", response_model=ResponseModel, tags=["Admin"])
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

@announce_router.post("/announcement/search", response_model=ResponseModel, tags=["Admin"])
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
        print(announcements)
        return ResponseModel(code=0, msg="Search Successfully", data=[ann.model_dump() for ann in announcements], count=total)
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))