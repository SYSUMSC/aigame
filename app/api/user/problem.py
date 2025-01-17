from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.models import ResponseModel
from app.schemas.problem import Problem
from db.session import get_session

if TYPE_CHECKING:
    from app.schemas.problem import Problem

from fastapi import APIRouter, Body, Depends, HTTPException, Path

problem_router = APIRouter()

@problem_router.post("/problem/{problem_id}", response_model=ResponseModel, tags=["Problem"])
async def get_problem_detail(
    problem_id: int = Path(..., description="The ID of the problem"),  # 使用 Path 获取 URL 参数
    session: AsyncSession = Depends(get_session)
):
    try:
        # 获取赛题详情
        statement = select(Problem).where(Problem.id == problem_id)
        result = await session.execute(statement)  # 确保使用 await
        problem_db = result.scalar_one_or_none()
        await session.refresh(problem_db,["problem_type"]) # 等待加载关联对象

        if not problem_db:
            return ResponseModel(code=1, msg="赛题未找到")

        # 通过关系获取问题类型
        problem_type = problem_db.problem_type

        return ResponseModel(
            code=0,
            msg="赛题详情获取成功",
            data={"problem": problem_db.model_dump(), "problem_type": problem_type.model_dump() if problem_type else None}
        )
    except Exception as e:
        return ResponseModel(code=1, msg=f"Error occurred: {str(e)}")
