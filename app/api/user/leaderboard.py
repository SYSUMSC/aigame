from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from db.session import get_session
from app.api.models import ResponseModel
from schemas.submission import Submission
from schemas.team import Team
from pydantic import BaseModel

class CompetitionRequest(BaseModel):
    competition_id: int

leaderboard_router = APIRouter()

@leaderboard_router.post("/competition/leaderboard", response_model=ResponseModel, tags=["Leaderboard"])
async def get_leaderboard(request: CompetitionRequest, session: AsyncSession = Depends(get_session)):
    try:
        competition_id = request.competition_id
        
        # 打印 competition_id 调试信息
        print(f"收到的 competition_id: {competition_id}")

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
        ).group_by(Submission.team_id, Team.name).order_by(func.sum(Submission.score).desc())

        result = await session.execute(query)
        leaderboard_data = result.all()

        leaderboard = [
            {
                "team_id": row.team_id,
                "name": row.name,
                "total_score": row.total_score
            }
            for row in leaderboard_data
        ]

        return ResponseModel(code=0, msg="排行榜获取成功", data=leaderboard)

    except Exception as e:
        print(f"错误信息: {str(e)}")  # 打印错误信息
        return ResponseModel(code=1, msg=f"获取排行榜时出错: {str(e)}")
