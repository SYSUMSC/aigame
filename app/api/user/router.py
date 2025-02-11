from fastapi import APIRouter, Depends

from core.security import oauth2_scheme_user as oauth2_scheme

from .announcement import announce_router
from .auth import auth_router
from .competion import competition_router
from .info import info_router
from .leaderboard import leaderboard_router
from .participation import participation_router
from .problem import problem_router
from .submission import submission_router
from .team import team_router

user_router = APIRouter()

user_router.include_router(auth_router)
user_router.include_router(info_router)
user_router.include_router(team_router)
user_router.include_router(competition_router)
user_router.include_router(participation_router)
user_router.include_router(problem_router)
user_router.include_router(submission_router)
user_router.include_router(leaderboard_router)
user_router.include_router(announce_router)