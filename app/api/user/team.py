import random
import string
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.models import ResponseModel
from db.session import get_session
from schemas.team import Team, TeamSchema
from schemas.user import User
from core.security import get_current_user

team_router = APIRouter()
# 生成邀请码的工具函数
def generate_invite_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
@team_router.post("/create_invite_code", response_model=ResponseModel, tags=["User"])
async def create_invite_code(current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
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
            return ResponseModel(code=1, msg="用户不是队长，无法创建邀请码")

        # 生成唯一的邀请码
        invite_code = generate_invite_code()

        # 检查邀请码是否重复
        statement = select(Team).where(Team.invite_code == invite_code)
        result = await session.execute(statement)
        existing_code = result.scalar_one_or_none()
        while existing_code:
            invite_code = generate_invite_code()
            statement = select(Team).where(Team.invite_code == invite_code)
            result = await session.execute(statement)
            existing_code = result.scalar_one_or_none()

        # 更新队伍的邀请码
        team_db.invite_code = invite_code
        session.add(team_db)
        await session.commit()
        await session.refresh(team_db)

        return ResponseModel(code=0, msg="邀请码创建成功", data={"invite_code": invite_code})
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
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
async def join_team(invite_code: str = Form(...), current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
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
    
@team_router.post("/transfer_captain", response_model=ResponseModel, tags=["Team"])  
async def transfer_captain(new_captain_id: int, current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):  
    try:  
        # 获取当前用户  
        statement = select(User).where(User.username == current_user)  
        current_user_db = await session.execute(statement).scalar_one()  
  
        # 检查当前用户是否在队伍中  
        if not current_user_db.team_id:  
            raise HTTPException(status_code=400, detail="用户不在任何队伍中")  
  
        # 获取当前用户所在的队伍  
        team_statement = select(Team).where(Team.id == current_user_db.team_id)  
        team_db = await session.execute(team_statement).scalar_one()  
  
        # 检查当前用户是否是队长  
        if team_db.captain_id != current_user_db.id:  
            raise HTTPException(status_code=403, detail="用户不是队长，无法进行转让")  
  
        # 验证新队长是否在队伍中  
        new_captain_statement = select(User).where(User.id == new_captain_id, User.team_id == team_db.id)  
        new_captain_db = await session.execute(new_captain_statement).scalar_one_or_none()  
        if not new_captain_db:  
            raise HTTPException(status_code=400, detail="新队长未找到或不在队伍中")  
  
        # 更新队伍的队长  
        team_db.captain_id = new_captain_id  
        session.add(team_db)  
        await session.commit()  
  
        return ResponseModel(code=0, msg="队伍转让成功")  
    except Exception as e:  
        return ResponseModel(code=1, msg=str(e))