from fastapi import APIRouter, Depends

from core.security import oauth2_scheme_user as oauth2_scheme

from .auth import auth_router
from .info import info_router
from .team import team_router
from .competion import competition_router

user_router = APIRouter()

user_router.include_router(auth_router)
user_router.include_router(info_router)
user_router.include_router(team_router)
user_router.include_router(competition_router)
