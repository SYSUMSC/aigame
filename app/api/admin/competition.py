from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.session import get_session
from schemas.competition import Competition, CompetitionSchema, CompetitionSearchSchema

from ..models import BatchDeleteRequest, ResponseModel

competition_router = APIRouter()

@competition_router.post("/competition", response_model=ResponseModel, tags=["Admin"])
async def create_competition(competition: CompetitionSchema, session: AsyncSession = Depends(get_session)):
    try:
        competition_db = Competition(**competition.model_dump())
        session.add(competition_db)
        await session.commit()
        await session.refresh(competition_db)
        return ResponseModel(code=0, msg="比赛创建成功", data=competition_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@competition_router.put("/competition/{competition_id}", response_model=ResponseModel, tags=["Admin"])
async def update_competition(competition_id: int, competition: CompetitionSchema, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Competition).where(Competition.id == competition_id)
        result = await session.execute(statement)
        competition_db = result.scalar_one_or_none()
        if not competition_db:
            return ResponseModel(code=1, msg="比赛未找到")
        competition_data = competition.model_dump(exclude_unset=True)
        for key, value in competition_data.items():
            setattr(competition_db, key, value)
        session.add(competition_db)
        await session.commit()
        await session.refresh(competition_db)
        return ResponseModel(code=0, msg="比赛更新成功", data=competition_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@competition_router.delete("/competition/{competition_id}", response_model=ResponseModel, tags=["Admin"])
async def delete_competition(competition_id: int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Competition).where(Competition.id == competition_id)
        result = await session.execute(statement)
        competition_db = result.scalar_one_or_none()
        if not competition_db:
            return ResponseModel(code=1, msg="比赛未找到")
        await session.delete(competition_db)
        await session.commit()
        return ResponseModel(code=0, msg="比赛删除成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@competition_router.delete("/competition", response_model=ResponseModel, tags=["Admin"])
async def delete_competitions(request: BatchDeleteRequest, session: AsyncSession = Depends(get_session)):
    try:
        competition_ids = request.ids
        statement = select(Competition).where(Competition.id.in_(competition_ids))
        result = await session.execute(statement)
        competitions_db = result.scalars().all()
        for competition_db in competitions_db:
            await session.delete(competition_db)
        await session.commit()
        return ResponseModel(code=0, msg="比赛批量删除成功", count=len(competitions_db))
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@competition_router.post("/competition/search", response_model=ResponseModel, tags=["Admin"])
async def search_competitions(search: CompetitionSearchSchema, page: int = 1, limit: int = 10, session: AsyncSession = Depends(get_session)):
    try:
        query = select(Competition)
        filters = []
        for field, value in search.model_dump(exclude_unset=True).items():
            if value is None or value == "":
                continue
            if isinstance(value, str):
                filters.append(getattr(Competition, field).like(f"%{value}%"))
            else:
                filters.append(getattr(Competition, field) == value)
        query = query.where(*filters)
        total_statement = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_statement)
        total = total_result.scalar()
        query = query.offset((page - 1) * limit).limit(limit)
        result = await session.execute(query)
        competitions = result.scalars().all()
        return ResponseModel(code=0, msg="比赛检索成功", data=[competition.model_dump() for competition in competitions], count=total)
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
