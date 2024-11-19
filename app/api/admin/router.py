from fastapi import APIRouter, Depends

from core.security import oauth2_scheme_admin as oauth2_scheme

from .auth import auth_router
from .team import team_router
from .user import user_router
from .competition import competition_router
from .problem import problem_router
from .problem_type import problem_type_router
from .submission import submission_router
from .participation import participation_router
from .setting import setting_router
from .announcement import announce_router

admin_api_router = APIRouter()

admin_api_router.include_router(auth_router)
# , dependencies=[Depends(oauth2_scheme)]
admin_api_router.include_router(user_router)
admin_api_router.include_router(team_router)
admin_api_router.include_router(competition_router)
admin_api_router.include_router(problem_router)
admin_api_router.include_router(problem_type_router)
admin_api_router.include_router(submission_router)
admin_api_router.include_router(participation_router)
admin_api_router.include_router(setting_router)
admin_api_router.include_router(announce_router)