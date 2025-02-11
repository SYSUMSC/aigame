from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.models import ResponseModel
from app.schemas.competition import Competition
from app.schemas.problem import Problem
from app.schemas.problem_type import ProblemType  # 确保你已经定义了ProblemType
from db.session import get_session

competition_router = APIRouter()

class ProblemFilters(BaseModel):
    problem_type_id: Optional[int] = None
    difficulty: Optional[int] = None

competition_router = APIRouter()

@competition_router.post("/competition/{competition_id}/problems", response_model=ResponseModel, tags=["Problem"])
async def get_filtered_problems(
    competition_id: int = Path(..., description="The ID of the competition"),
    filters: ProblemFilters = Body(..., description="Filters for problems"),
    session: AsyncSession = Depends(get_session)
):
    try:
        # 构建查询语句
        statement = select(Problem).where(Problem.competition_id == competition_id)

        # 根据筛选参数添加条件，如果值为 None，则不添加该条件
        if filters.problem_type_id is not None:
            statement = statement.where(Problem.problem_type_id == filters.problem_type_id)
        if filters.difficulty is not None:
            statement = statement.where(Problem.difficulty == filters.difficulty)

        result = await session.execute(statement)
        problem_list = result.scalars().all()
        data = [problem.model_dump() for problem in problem_list]
        return ResponseModel(code=0, msg="赛题列表获取成功", data=data, count=len(data))
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@competition_router.get("/competition", response_model=ResponseModel, tags=["User"])
async def get_competition(session: AsyncSession = Depends(get_session)):
    try:
        # 获取所有比赛信息
        statement = select(Competition)
        result = await session.execute(statement)
        competition_list = result.scalars().all()
        return ResponseModel(code=0, msg="比赛信息获取成功", data=[competition.model_dump() for competition in competition_list])
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@competition_router.post("/competition/{competition_id}", response_model=ResponseModel, tags=["User"])
async def get_competition_detail(competition_id: int = Path(..., description="The ID of the competition"), session: AsyncSession = Depends(get_session)):
    try:
        # 获取比赛详情
        statement = select(Competition).where(Competition.id == competition_id)
        result = await session.execute(statement)
        competition_db = result.scalar_one_or_none()
        if not competition_db:
            return ResponseModel(code=1, msg="比赛未找到")

        # 获取赛题列表
        problem_statement = select(Problem).where(Problem.competition_id == competition_id)
        problem_result = await session.execute(problem_statement)
        problem_list = problem_result.scalars().all()

        competition_details = competition_db.model_dump()
        competition_details['problems'] = [problem.model_dump() for problem in problem_list]
        return ResponseModel(code=0, msg="比赛详情获取成功", data=competition_details)
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@competition_router.post("/problem_types", response_model=ResponseModel, tags=["ProblemType"])
async def get_problem_types(session: AsyncSession = Depends(get_session)):
    try:
        # 获取所有问题类型
        statement = select(ProblemType)
        result = await session.execute(statement)
        problem_type_list = result.scalars().all()
        return ResponseModel(code=0, msg="问题类型列表获取成功", data=[problem_type.model_dump() for problem_type in problem_type_list])
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
