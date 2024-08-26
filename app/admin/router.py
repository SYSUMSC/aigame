from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.session import get_session
from schemas.user import User
admin_router = APIRouter()
templates = Jinja2Templates(directory="admin/templates")

@admin_router.get("/admin/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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