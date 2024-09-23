from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


from app.api.models import ResponseModel

from db.session import get_session
from schemas.competition import Competition, CompetitionSchema
from schemas.participation import Participation, ParticipationSchema

competition_router = APIRouter()

@competition_router.get("/competition", response_model=ResponseModel, tags=["User"])
async def get_competition(session: AsyncSession = Depends(get_session)):
    try:
        # 获取所有比赛信息
        statement = select(Competition)
        result = await session.execute(statement)
        print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        print(result)
        competition_list = result.scalars().all()
        print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        print(competition_list)
        return ResponseModel(code=0, msg="比赛信息获取成功", data=[competition.model_dump() for competition in competition_list])
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
    
