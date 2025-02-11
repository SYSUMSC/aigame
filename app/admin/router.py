from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.models import *
from app.core.utils import load_config_from_db
from app.schemas.announcement import Announcement
from app.schemas.competition import Competition
from app.schemas.config import Config
from app.schemas.problem_type import ProblemType
from app.schemas.user import User
from db.session import get_session

admin_router = APIRouter()
templates = Jinja2Templates(directory="admin/templates")

@admin_router.get("/admin/")
async def index(request: Request, session: AsyncSession = Depends(get_session)):
    try:
        # 从数据库中读取管理员用户名
        statement = select(Config).where(Config.k == "admin_user")
        result = await session.execute(statement)
        config = result.scalar_one_or_none()

        if not config:
            return ResponseModel(code=1, msg="管理员用户未找到")

        admin_name = config.v  # 获取管理员用户名

    except Exception as e:
        # 处理可能出现的错误
        return {"code": 1, "msg": str(e), "data": None}

    # 渲染模板并传递管理员用户名
    return templates.TemplateResponse("index.html", {"request": request, "admin_name": admin_name})


@admin_router.get("/admin/console")
async def console(request: Request):
    return templates.TemplateResponse("console.html", {"request": request})

@admin_router.get("/admin/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 队伍
@admin_router.get("/admin/team")
async def team(request: Request):
    return templates.TemplateResponse("team.html", {"request": request})
@admin_router.get("/admin/team_form")
async def team_form(request: Request, session: AsyncSession = Depends(get_session)):
    # 使用 AsyncSession 进行异步查询
    try:
        statement = select(User)
        result = await session.execute(statement)  # 确保 await 用于异步调用
        users = result.scalars().all()  # 获取查询结果的所有数据
    except Exception as e:
        # 处理可能出现的错误
        return {"code": 1, "msg": str(e), "data": None}

    # 渲染模板并传递用户列表
    return templates.TemplateResponse("team_form.html", {"request": request, "users": users})
# 用户
@admin_router.get("/admin/user")
async def user(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})
@admin_router.get("/admin/user_form")
async def user_form(request: Request):
    return templates.TemplateResponse("user_form.html", {"request": request})

# 题目
@admin_router.get("/admin/problem")
async def problem(request: Request):
    return templates.TemplateResponse("problem.html", {"request": request})
@admin_router.get("/admin/problem_form")
async def problem_form(request: Request, session: AsyncSession = Depends(get_session)):
    try:
        # 获取所有比赛
        statement = select(Competition)
        result = await session.execute(statement)
        competitions = result.scalars().all()

        # 获取所有题目类型
        problem_type_statement = select(ProblemType)
        problem_type_result = await session.execute(problem_type_statement)
        problem_types = problem_type_result.scalars().all()

        # 将比赛和题目类型列表转换为模板需要的格式
        competition_options = [{"value": comp.id, "label": comp.name} for comp in competitions]
        problem_type_options = [{"value": pt.id, "label": pt.name} for pt in problem_types]

        return templates.TemplateResponse("problem_form.html", {"request": request, "competitions": competition_options, "problem_types": problem_type_options})
    except Exception as e:
        return {"code": 1, "msg": str(e), "data": None}

# 比赛
@admin_router.get("/admin/competition")
async def competition(request: Request):
    return templates.TemplateResponse("competition.html", {"request": request})
@admin_router.get("/admin/competition_form")
async def competition_form(request: Request):
    return templates.TemplateResponse("competition_form.html", {"request": request})


# 题目类型
@admin_router.get("/admin/problem_type")
async def problem_type(request: Request):
    return templates.TemplateResponse("problem_type.html", {"request": request})

@admin_router.get("/admin/problem_type_form")
async def problem_type_form(request: Request):
    return templates.TemplateResponse("problem_type_form.html", {"request": request})

# 设置
@admin_router.get("/admin/setting")
async def setting(request: Request, session: AsyncSession = Depends(get_session)):
    try:
        smtp_config = await load_config_from_db(session)
    except Exception as e:
        return {"code": 1, "msg": str(e), "data": None}
    view = {"request": request, "smtp_config": smtp_config, "title":"设置", "url":"setting"}
    return templates.TemplateResponse("setting.html", view)

# 公告
@admin_router.get("/admin/announcement")
async def announcement(request: Request, session: AsyncSession = Depends(get_session)): 
    try:
        statement = select(Announcement)
        result = await session.execute(statement)
        announcements = result.scalars().all()

        announcement_list = [{"title": ann.title, "date": ann.date, "content": ann.content} for ann in announcements]

        return templates.TemplateResponse("announcement.html", {"request": request, "announcements": announcement_list})
    except Exception as e:
        return {"code": 1, "msg": str(e), "data": None}




# 公告管理
@admin_router.get("/admin/announcement_form")
async def announcement_form(request: Request, session: AsyncSession = Depends(get_session)):
    try:
        # 获取所有公告
        statement = select(Announcement)
        result = await session.execute(statement)
        announcements = result.scalars().all()

        announcement_form = [{"title": ann.title, "date": ann.date, "content": ann.content} for ann in announcements]

        return templates.TemplateResponse("announcement_form.html", {"request": request, "announcements": announcement_form})
    except Exception as e:
        return {"code": 1, "msg": str(e), "data": None}