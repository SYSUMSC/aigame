from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy import select, join

from app.schemas.user import User
from db.session import get_session
from app.schemas.team import Team, TeamSchema, TeamSearchSchema

from ..models import BatchDeleteRequest, ResponseModel

team_router = APIRouter()

@team_router.post("/team", response_model=ResponseModel, tags=["Admin"])
async def create_team(team: TeamSchema, session: AsyncSession = Depends(get_session)):
    try:
        team_db = Team(**team.model_dump())
        session.add(team_db)
        await session.commit()
        await session.refresh(team_db)
        return ResponseModel(code=0, msg="队伍创建成功", data=team_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@team_router.put("/team/{team_id}", response_model=ResponseModel, tags=["Admin"])
async def update_team(team_id: int, team: TeamSchema, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Team).where(Team.id == team_id)
        result = await session.execute(statement)
        team_db = result.scalar_one_or_none()
        if not team_db:
            return ResponseModel(code=1, msg="队伍未找到")
        team_data = team.model_dump(exclude_unset=True)
        for key, value in team_data.items():
            setattr(team_db, key, value)
        session.add(team_db)
        await session.commit()
        await session.refresh(team_db)
        return ResponseModel(code=0, msg="队伍更新成功", data=team_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@team_router.delete("/team/{team_id}", response_model=ResponseModel, tags=["Admin"])
async def delete_team(team_id: int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Team).where(Team.id == team_id)
        result = await session.execute(statement)
        team_db = result.scalar_one_or_none()
        if not team_db:
            return ResponseModel(code=1, msg="队伍未找到")
        await session.delete(team_db)
        await session.commit()
        return ResponseModel(code=0, msg="队伍删除成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@team_router.delete("/team", response_model=ResponseModel, tags=["Admin"])
async def delete_teams(request: BatchDeleteRequest, session: AsyncSession = Depends(get_session)):
    try:
        team_ids = request.ids
        statement = select(Team).where(Team.id.in_(team_ids))
        result = await session.execute(statement)
        teams_db = result.scalars().all()
        for team_db in teams_db:
            await session.delete(team_db)
        await session.commit()
        return ResponseModel(code=0, msg="队伍批量删除成功", count=len(teams_db))
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@team_router.post("/team/search", response_model=ResponseModel, tags=["Admin"])
async def search_teams(search: TeamSearchSchema, page: int = 1, limit: int = 10, session: AsyncSession = Depends(get_session)):
    try:
        # 构建查询队伍的初始语句，并与 User 表进行 JOIN 操作以获取队长名字
        query = select(Team, User.name.label("captain_name")).join(User, Team.captain_id == User.id, isouter=True)

        # 应用搜索过滤条件
        filters = []
        for field, value in search.model_dump(exclude_unset=True).items():
            if value is None or value == "":
                continue
            elif isinstance(value, str) and field != "status":
                filters.append(getattr(Team, field).like(f"%{value}%"))
            else:
                filters.append(getattr(Team, field) == value)
        query = query.where(*filters)

        # 获取总数
        total_statement = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_statement)
        total = total_result.scalar()

        # 分页处理
        query = query.offset((page - 1) * limit).limit(limit)
        result = await session.execute(query)

        teams_with_captain = []
        for team, captain_name in result.all():
            team_data = team.model_dump()
            team_data["captain"] = captain_name  # 将captain_name附加到结果中
            teams_with_captain.append(team_data)

        return ResponseModel(code=0, msg="队伍检索成功", data=teams_with_captain, count=total)
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))