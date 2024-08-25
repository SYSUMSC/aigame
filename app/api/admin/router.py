from fastapi import APIRouter, Depends

from app.core.security import oauth2_scheme_admin as oauth2_scheme

from .auth import auth_router
from .team import team_router
from .user import user_router
from .competition import competition_router
from .problem import problem_router

admin_api_router = APIRouter()

admin_api_router.include_router(auth_router)
admin_api_router.include_router(user_router, dependencies=[Depends(oauth2_scheme)])
admin_api_router.include_router(team_router, dependencies=[Depends(oauth2_scheme)])
admin_api_router.include_router(competition_router, dependencies=[Depends(oauth2_scheme)])
admin_api_router.include_router(problem_router, dependencies=[Depends(oauth2_scheme)])
