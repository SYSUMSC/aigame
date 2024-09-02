from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.models import ResponseModel
from db.session import get_session
from schemas.team import Team, TeamSchema
from schemas.user import User
from core.security import get_current_user

team_router = APIRouter()
@team_router.post("/create_team", response_model=ResponseModel, tags=["User"])
async def create_team(request: Request, current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    try:
        body = await request.json()
        name = body.get("name")
        # 检查用户是否已经有队伍
        statement = select(User).where(User.username == current_user)
        result = await session.execute(statement)
        user_db = result.scalar_one_or_none()
        if not user_db:
            return ResponseModel(code=1, msg="用户未找到")

        if user_db.team_id:
            return ResponseModel(code=1, msg="用户已经在队伍中，无法创建新的队伍")

        # 创建新队伍
        new_team = Team(name=name, captain_id=user_db.id)
        session.add(new_team)
        await session.commit()
        await session.refresh(new_team)

        # 将用户加入队伍
        user_db.team_id = new_team.id
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)

        return ResponseModel(code=0, msg="队伍创建成功", data=new_team.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
@team_router.post("/join_team", response_model=ResponseModel, tags=["User"])
async def join_team(invite_code: str, current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    try:
        # 获取当前用户
        statement = select(User).where(User.username == current_user)
        result = await session.execute(statement)
        user_db = result.scalar_one_or_none()
        if not user_db:
            return ResponseModel(code=1, msg="用户未找到")

        # 检查用户是否已经在队伍中
        if user_db.team_id:
            return ResponseModel(code=1, msg="用户已经在队伍中")

        # 查找队伍
        statement = select(Team).where(Team.invite_code == invite_code)
        result = await session.execute(statement)
        team_db = result.scalar_one_or_none()
        if not team_db:
            return ResponseModel(code=1, msg="邀请码无效")

        # 加入队伍
        user_db.team_id = team_db.id
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)
        return ResponseModel(code=0, msg="加入队伍成功", data=team_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@team_router.get("/team_info", response_model=ResponseModel, tags=["User"])
async def get_team_info(current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    try:
        # 获取当前用户
        statement = select(User.username).where(User.username == current_user)
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

        # 获取队员列表
        statement = select(User).where(User.team_id == team_db.id)
        result = await session.execute(statement)
        members = result.scalars().all()

        team_info = team_db.model_dump()
        team_info["members"] = [member.model_dump() for member in members]
        return ResponseModel(code=0, msg="队伍信息获取成功", data=team_info)
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@team_router.post("/disband_team", response_model=ResponseModel, tags=["User"])
async def disband_team(current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    try:
        # 获取当前用户
        statement = select(User).where(User.username == current_user)
        result = await session.execute(statement)
        user_db = result.scalar_one_or_none()
        if not user_db:
            return ResponseModel(code=1, msg="用户未找到")

        # 检查用户是否是队长
        if not user_db.team_id:
            return ResponseModel(code=1, msg="用户不在任何队伍中")

        statement = select(Team).where(Team.id == user_db.team_id, Team.captain_id == user_db.id)
        result = await session.execute(statement)
        team_db = result.scalar_one_or_none()
        if not team_db:
            return ResponseModel(code=1, msg="用户不是队长，无法解散队伍")

        # 解散队伍
        statement = select(User).where(User.team_id == team_db.id)
        result = await session.execute(statement)
        members = result.scalars().all()
        for member in members:
            member.team_id = None
            session.add(member)
        await session.delete(team_db)
        await session.commit()
        return ResponseModel(code=0, msg="队伍解散成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@team_router.post("/remove_member", response_model=ResponseModel, tags=["User"])
async def remove_member(member_id: int, current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    try:
        # 获取当前用户
        statement = select(User).where(User.username == current_user)
        result = await session.execute(statement)
        user_db = result.scalar_one_or_none()
        if not user_db:
            return ResponseModel(code=1, msg="用户未找到")

        # 检查用户是否是队长
        if not user_db.team_id:
            return ResponseModel(code=1, msg="用户不在任何队伍中")

        statement = select(Team).where(Team.id == user_db.team_id, Team.captain_id == user_db.id)
        result = await session.execute(statement)
        team_db = result.scalar_one_or_none()
        if not team_db:
            return ResponseModel(code=1, msg="用户不是队长，无法移除成员")

        # 获取要移除的成员
        statement = select(User).where(User.id == member_id, User.team_id == team_db.id)
        result = await session.execute(statement)
        member_db = result.scalar_one_or_none()
        if not member_db:
            return ResponseModel(code=1, msg="成员未找到或不在队伍中")

        # 移除成员
        member_db.team_id = None
        session.add(member_db)
        await session.commit()
        await session.refresh(member_db)
        return ResponseModel(code=0, msg="成员移除成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@team_router.post("/leave_team", response_model=ResponseModel, tags=["User"])
async def leave_team(current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    try:
        # 获取当前用户
        statement = select(User).where(User.username == current_user)
        result = await session.execute(statement)
        user_db = result.scalar_one_or_none()
        if not user_db:
            return ResponseModel(code=1, msg="用户未找到")

        # 检查用户是否在队伍中
        if not user_db.team_id:
            return ResponseModel(code=1, msg="用户不在任何队伍中")

        # 检查用户是否是队长
        statement = select(Team).where(Team.id == user_db.team_id, Team.captain_id == user_db.id)
        result = await session.execute(statement)
        team_db = result.scalar_one_or_none()
        if team_db:
            return ResponseModel(code=1, msg="队长不能退出队伍，请先转让队长或解散队伍")

        # 退出队伍
        user_db.team_id = None
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)
        return ResponseModel(code=0, msg="退出队伍成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))