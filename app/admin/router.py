from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

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