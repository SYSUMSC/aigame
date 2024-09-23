from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


from app.api.models import ResponseModel

from db.session import get_session
from schemas.participation import Participation, ParticipationSchema

participation_router = APIRouter()

@participation_router.get("/participation", response_model=ResponseModel, tags=["User"])
async def get_participation(team_id:int, session: AsyncSession = Depends(get_session)):
    try:
        # 获取用户参赛信息
        statement = select(Participation).where(Participation.team_id == team_id)
        result = await session.execute(statement)
        participation_list = result.scalars().all()
        return ResponseModel(code=0, msg="参赛信息获取成功", data=[participation.model_dump() for participation in participation_list])
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@participation_router.post("/participation", response_model=ResponseModel, tags=["User"])
async def join_competition(participation: ParticipationSchema, session: AsyncSession = Depends(get_session)):
    try:
        # 检查用户是否已参加比赛
        existing_participation = await session.execute(select(Participation).where(Participation.user_id == participation.user_id, Participation.competition_id == participation.competition_id))
        if existing_participation.scalar_one_or_none():
            return ResponseModel(code=1, msg="用户已参加比赛")
        
        # 创建新参赛记录
        participation_db = Participation(**participation.model_dump())
        session.add(participation_db)
        await session.commit()
        await session.refresh(participation_db)
        return ResponseModel(code=0, msg="参赛成功", data=participation_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
    
@participation_router.delete("/participation", response_model=ResponseModel, tags=["User"])
async def quit_competition(team_id: int, competition_id: int, session: AsyncSession = Depends(get_session)):
    # 退出比赛
    try:
        # 检查用户是否已参加比赛
        existing_participation = await session.execute(
            select(Participation).where(Participation.team_id == team_id, Participation.competition_id == competition_id)
        )
        participation_db = existing_participation.scalar_one_or_none()
        if not participation_db:
            return ResponseModel(code=1, msg="用户未参加比赛")
        
        # 删除参赛记录
        await session.delete(participation_db)
        await session.commit()

        # 再次检查是否删除成功
        existing_participation = await session.execute(
            select(Participation).where(Participation.team_id == team_id, Participation.competition_id == competition_id)
        )
        participation_db = existing_participation.scalar_one_or_none()
        if participation_db:
            return ResponseModel(code=1, msg="退出比赛失败")

        return ResponseModel(code=0, msg="退出比赛成功")
    except Exception as e:
        # 记录异常信息
        print(f"Error occurred: {e}")
        return ResponseModel(code=1, msg=str(e))

