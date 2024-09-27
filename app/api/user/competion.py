from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional, List

from app.api.models import ResponseModel
from db.session import get_session
from schemas.competition import Competition
from schemas.problem import Problem
from schemas.problem_type import ProblemType  # 确保你已经定义了ProblemType



competition_router = APIRouter()

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

@competition_router.get("/competition/{competition_id}", response_model=ResponseModel, tags=["User"])
async def get_competition_detail(competition_id: int, session: AsyncSession = Depends(get_session)):
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

@competition_router.get("/competition/{competition_id}/problems", response_model=ResponseModel, tags=["Problem"])
async def get_filtered_problems(
    competition_id: int = Path(..., description="The ID of the competition"),
    problem_type_id: Optional[int] = Query(None, description="Filter by problem type ID"),
    difficulty: Optional[int] = Query(None, description="Filter by difficulty"),
    session: AsyncSession = Depends(get_session)
):
    try:
        # 构建查询语句
        statement = select(Problem).where(Problem.competition_id == competition_id)

        # 根据筛选参数添加条件
        if problem_type_id:
            statement = statement.where(Problem.problem_type_id == problem_type_id)
        if difficulty is not None:
            statement = statement.where(Problem.difficulty == difficulty)

        result = await session.execute(statement)
        problem_list = result.scalars().all()
        return ResponseModel(code=0, msg="赛题列表获取成功", data=[problem.model_dump() for problem in problem_list])
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
    
@competition_router.get("/problem_types", response_model=ResponseModel, tags=["ProblemType"])
async def get_problem_types(session: AsyncSession = Depends(get_session)):
    try:
        # 获取所有问题类型
        statement = select(ProblemType)
        result = await session.execute(statement)
        problem_type_list = result.scalars().all()
        return ResponseModel(code=0, msg="问题类型列表获取成功", data=[problem_type.model_dump() for problem_type in problem_type_list])
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))