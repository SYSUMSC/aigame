from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.session import get_session
from schemas.participation import Participation, ParticipationSchema, ParticipationSearchSchema
from ..models import BatchDeleteRequest, ResponseModel

participation_router = APIRouter()

@participation_router.post("/participation", response_model=ResponseModel, tags=["Admin"])
async def create_participation(participation: ParticipationSchema, session: AsyncSession = Depends(get_session)):
    try:
        participation_db = Participation(**participation.model_dump())
        session.add(participation_db)
        await session.commit()
        await session.refresh(participation_db)
        return ResponseModel(code=0, msg="参与记录创建成功", data=participation_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@participation_router.put("/participation/{participation_id}", response_model=ResponseModel, tags=["Admin"])
async def update_participation(participation_id: int, participation: ParticipationSchema, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Participation).where(Participation.id == participation_id)
        result = await session.execute(statement)
        participation_db = result.scalar_one_or_none()
        if not participation_db:
            return ResponseModel(code=1, msg="参与记录未找到")
        participation_data = participation.model_dump(exclude_unset=True)
        for key, value in participation_data.items():
            setattr(participation_db, key, value)
        session.add(participation_db)
        await session.commit()
        await session.refresh(participation_db)
        return ResponseModel(code=0, msg="参与记录更新成功", data=participation_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@participation_router.delete("/participation/{participation_id}", response_model=ResponseModel, tags=["Admin"])
async def delete_participation(participation_id: int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Participation).where(Participation.id == participation_id)
        result = await session.execute(statement)
        participation_db = result.scalar_one_or_none()
        if not participation_db:
            return ResponseModel(code=1, msg="参与记录未找到")
        await session.delete(participation_db)
        await session.commit()
        return ResponseModel(code=0, msg="参与记录删除成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@participation_router.post("/participation/search", response_model=ResponseModel, tags=["Admin"])
async def search_participations(search: ParticipationSearchSchema, page: int = 1, limit: int = 10, session: AsyncSession = Depends(get_session)):
    try:
        query = select(Participation)
        filters = []
        for field, value in search.model_dump(exclude_unset=True).items():
            if value is None or value == "":
                continue
            filters.append(getattr(Participation, field) == value)
        query = query.where(*filters)
        total_statement = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_statement)
        total = total_result.scalar()
        query = query.offset((page - 1) * limit).limit(limit)
        result = await session.execute(query)
        participations = result.scalars().all()
        return ResponseModel(code=0, msg="参与记录检索成功", data=[participation.model_dump() for participation in participations], count=total)
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
