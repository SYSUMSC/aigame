from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

admin_router = APIRouter()
templates = Jinja2Templates(directory="admin/templates")

@admin_router.get("/admin/")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "username": "Admin"})


@admin_router.get("/admin/console")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("console.html", {"request": request, "username": "Admin"})