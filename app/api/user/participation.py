from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


from app.api.models import ResponseModel

from db.session import get_session
from app.schemas.participation import Participation, ParticipationSchema
from app.schemas.user import User
from app.schemas.team import Team

from core.security import get_current_user

participation_router = APIRouter()

async def get_team_info(current_user:str,session: AsyncSession = Depends(get_session)):
    try:
        # 获取当前用户
        statement = select(User).where(User.username == current_user)
        result = await session.execute(statement)
        user_db = result.scalar_one_or_none()
        if not user_db:
            return ResponseModel(code=1, msg="用户未找到")
        # 获取队伍信息
        if not user_db.team_id:
            return ResponseModel(code=1, msg="用户不在任何队伍中")

        statement = select(Team).where(Team.id == user_db.team_id)
        result = await session.execute(statement)
        team_db = result.scalar_one_or_none()
        if not team_db:
            return ResponseModel(code=1, msg="队伍未找到")

        team_info = team_db.model_dump()
        return team_info["captain_id"] == user_db.id
    except Exception as e:
        return False

@participation_router.get("/participation", response_model=ResponseModel, tags=["User"])
async def get_participation(team_id:int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Participation).where(Participation.team_id == team_id)
        result = await session.execute(statement)
        participation_list = result.scalars().all()
        return ResponseModel(code=0, msg="参赛信息获取成功", data=[participation.model_dump() for participation in participation_list])
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@participation_router.post("/participation", response_model=ResponseModel, tags=["User"])
async def join_competition(participation: ParticipationSchema,current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    try:
        # 获取用户参赛信息
        isCaptain = await get_team_info(current_user,session)
        if not isCaptain:
            return ResponseModel(code=1, msg="用户不是队长")
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

