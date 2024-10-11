from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.session import get_session
from app.schemas.problem_type import ProblemType, ProblemTypeSchema, ProblemTypeSearchSchema

from ..models import BatchDeleteRequest, ResponseModel

problem_type_router = APIRouter()

@problem_type_router.post("/problem_type", response_model=ResponseModel, tags=["Admin"])
async def create_problem_type(problem_type: ProblemTypeSchema, session: AsyncSession = Depends(get_session)):
    try:
        problem_type_db = ProblemType(**problem_type.dict())
        session.add(problem_type_db)
        await session.commit()
        await session.refresh(problem_type_db)
        return ResponseModel(code=0, msg="题目类型创建成功", data=problem_type_db.dict())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@problem_type_router.put("/problem_type/{problem_type_id}", response_model=ResponseModel, tags=["Admin"])
async def update_problem_type(problem_type_id: int, problem_type: ProblemTypeSchema, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(ProblemType).where(ProblemType.id == problem_type_id)
        result = await session.execute(statement)
        problem_type_db = result.scalar_one_or_none()
        if not problem_type_db:
            return ResponseModel(code=1, msg="题目类型未找到")
        for key, value in problem_type.dict(exclude_unset=True).items():
            setattr(problem_type_db, key, value)
        session.add(problem_type_db)
        await session.commit()
        await session.refresh(problem_type_db)
        return ResponseModel(code=0, msg="题目类型更新成功", data=problem_type_db.dict())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@problem_type_router.delete("/problem_type/{problem_type_id}", response_model=ResponseModel, tags=["Admin"])
async def delete_problem_type(problem_type_id: int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(ProblemType).where(ProblemType.id == problem_type_id)
        result = await session.execute(statement)
        problem_type_db = result.scalar_one_or_none()
        if not problem_type_db:
            return ResponseModel(code=1, msg="题目类型未找到")
        await session.delete(problem_type_db)
        await session.commit()
        return ResponseModel(code=0, msg="题目类型删除成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@problem_type_router.delete("/problem_type", response_model=ResponseModel, tags=["Admin"])
async def delete_problem_types(request: BatchDeleteRequest, session: AsyncSession = Depends(get_session)):
    try:
        problem_type_ids = request.ids
        statement = select(ProblemType).where(ProblemType.id.in_(problem_type_ids))
        result = await session.execute(statement)
        problem_types_db = result.scalars().all()
        for problem_type_db in problem_types_db:
            await session.delete(problem_type_db)
        await session.commit()
        return ResponseModel(code=0, msg="题目类型批量删除成功", count=len(problem_types_db))
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@problem_type_router.post("/problem_type/search", response_model=ResponseModel, tags=["Admin"])
async def search_problem_types(search: ProblemTypeSearchSchema, page: int = 1, limit: int = 10, session: AsyncSession = Depends(get_session)):
    try:
        query = select(ProblemType)
        filters = []
        for field, value in search.dict(exclude_unset=True).items():
            filters.append(getattr(ProblemType, field).like(f"%{value}%"))
        query = query.where(*filters)
        total_statement = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_statement)
        total = total_result.scalar()
        query = query.offset((page - 1) * limit).limit(limit)
        result = await session.execute(query)
        problem_types = result.scalars().all()
        return ResponseModel(code=0, msg="题目类型检索成功", data=[problem_type.dict() for problem_type in problem_types], count=total)
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
