from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.schemas.problem import Problem, ProblemSchema, ProblemSearchSchema

from ..response_model import ResponseModel

problem_router = APIRouter()

@problem_router.post("/problem", response_model=ResponseModel, tags=["Admin"])
async def create_problem(problem: ProblemSchema, session: AsyncSession = Depends(get_session)):
    try:
        problem_db = Problem(**problem.model_dump())
        session.add(problem_db)
        await session.commit()
        await session.refresh(problem_db)
        return ResponseModel(code=0, msg="题目创建成功", data=problem_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@problem_router.put("/problem/{problem_id}", response_model=ResponseModel, tags=["Admin"])
async def update_problem(problem_id: int, problem: ProblemSchema, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Problem).where(Problem.id == problem_id)
        result = await session.execute(statement)
        problem_db = result.scalar_one_or_none()
        if not problem_db:
            return ResponseModel(code=1, msg="题目未找到")
        problem_data = problem.model_dump(exclude_unset=True)
        for key, value in problem_data.items():
            setattr(problem_db, key, value)
        session.add(problem_db)
        await session.commit()
        await session.refresh(problem_db)
        return ResponseModel(code=0, msg="题目更新成功", data=problem_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@problem_router.delete("/problem/{problem_id}", response_model=ResponseModel, tags=["Admin"])
async def delete_problem(problem_id: int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Problem).where(Problem.id == problem_id)
        result = await session.execute(statement)
        problem_db = result.scalar_one_or_none()
        if not problem_db:
            return ResponseModel(code=1, msg="题目未找到")
        await session.delete(problem_db)
        await session.commit()
        return ResponseModel(code=0, msg="题目删除成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@problem_router.delete("/problem", response_model=ResponseModel, tags=["Admin"])
async def delete_problems(ids: str, session: AsyncSession = Depends(get_session)):
    try:
        problem_ids = [int(id) for id in ids.split(",")]
        statement = select(Problem).where(Problem.id.in_(problem_ids))
        result = await session.execute(statement)
        problems_db = result.scalars().all()
        for problem_db in problems_db:
            await session.delete(problem_db)
        await session.commit()
        return ResponseModel(code=0, msg="题目批量删除成功", count=len(problems_db))
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@problem_router.post("/problem/search", response_model=ResponseModel, tags=["Admin"])
async def search_problems(search: ProblemSearchSchema, page: int = 1, limit: int = 10, session: AsyncSession = Depends(get_session)):
    try:
        query = select(Problem)
        filters = []
        for field, value in search.model_dump(exclude_unset=True).items():
            if isinstance(value, str):
                filters.append(getattr(Problem, field).like(f"%{value}%"))
            else:
                filters.append(getattr(Problem, field) == value)
        query = query.where(*filters)
        total_statement = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_statement)
        total = total_result.scalar()
        query = query.offset((page - 1) * limit).limit(limit)
        result = await session.execute(query)
        problems = result.scalars().all()
        return ResponseModel(code=0, msg="题目检索成功", data=[problem.model_dump() for problem in problems], count=total)
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
