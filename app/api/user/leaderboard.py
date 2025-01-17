from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models import ResponseModel
from app.schemas.submission import Submission
from app.schemas.team import Team
from db.session import get_session


class CompetitionRequest(BaseModel):
    competition_id: int
    page: int = 1  # 默认第1页
    page_size: int = 10  # 默认每页10个队伍

leaderboard_router = APIRouter()

@leaderboard_router.post("/leaderboard", response_model=ResponseModel, tags=["Leaderboard"])
async def get_leaderboard(
    request: CompetitionRequest,
    session: AsyncSession = Depends(get_session)
):
    try:
        competition_id = request.competition_id
        page = request.page
        page_size = request.page_size

        if competition_id <= 0:
            raise ValueError("Invalid competition_id")

        offset = (page - 1) * page_size

        # 步骤1：找到每个队伍在每个题目的最新提交
        subquery = select(
            Submission.team_id,
            Submission.problem_id,
            func.max(Submission.submit_time).label('latest_submission_time')
        ).where(
            Submission.status == 1,
            Submission.competition_id == competition_id
        ).group_by(Submission.team_id, Submission.problem_id).subquery()

        # 步骤2：计算每个队伍的总分数
        query = select(
            Submission.team_id,
            Team.name,
            func.sum(Submission.score).label('total_score')
        ).join(
            subquery,
            (subquery.c.team_id == Submission.team_id) &
            (subquery.c.problem_id == Submission.problem_id) &
            (subquery.c.latest_submission_time == Submission.submit_time)
        ).join(
            Team, Team.id == Submission.team_id
        ).group_by(Submission.team_id, Team.name).order_by(func.sum(Submission.score).desc()).offset(offset).limit(page_size)

        result = await session.execute(query)
        leaderboard_data = result.all()

        if not leaderboard_data:
            raise HTTPException(status_code=404, detail="No submissions found for this competition")

        leaderboard = [
            {
                "team_id": row.team_id,
                "name": row.name,
                "total_score": row.total_score
            }
            for row in leaderboard_data
        ]

        return ResponseModel(code=0, msg="排行榜获取成功", data=leaderboard)

    except ValueError as ve:
        return ResponseModel(code=1, msg=f"请求参数错误: {str(ve)}")
    except HTTPException as he:
        raise he
    except Exception as e:
        return ResponseModel(code=1, msg=f"获取排行榜时出错: {str(e)}")
