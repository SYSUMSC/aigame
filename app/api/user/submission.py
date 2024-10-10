# 这里不能加app. 否则有bug？
from schemas.problem import Problem
from schemas.submission import Submission
from schemas.participation import Participation  # 导入Participation模型
from schemas.user import User
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from db.session import get_session
from app.api.models import ResponseModel
from datetime import datetime, timezone
from core.security import get_current_user  # 确保你有这个函数
import os
import uuid

# 将路由器名称改为 submission_router
submission_router = APIRouter()

# 实现获取用户ID的函数
async def get_current_user_id(current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    statement = select(User).where(User.username == current_user)
    result = await session.execute(statement)
    user_db = result.scalar_one_or_none()

    if not user_db:
        raise HTTPException(status_code=400, detail="用户未找到")

    return user_db.id

# 实现获取team_id的函数
async def get_current_team_id(current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    statement = select(User).where(User.username == current_user)
    result = await session.execute(statement)
    user_db = result.scalar_one_or_none()

    if not user_db:
        raise HTTPException(status_code=400, detail="用户未找到")

    if not user_db.team_id:
        raise HTTPException(status_code=400, detail="用户没有加入任何队伍")

    return user_db.team_id

@submission_router.post("/problem/{problem_id}/submit", response_model=ResponseModel, tags=["Problem"])
async def submit_problem_file(
    problem_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
    team_id: int = Depends(get_current_team_id)
):
    try:
        # 检查 problem_id 是否存在
        statement = select(Problem).where(Problem.id == problem_id)
        result = await session.execute(statement)
        problem = result.scalar_one_or_none()
        if not problem:
            return ResponseModel(code=1, msg="赛题未找到")

        # 检查队伍是否报名比赛
        participation_statement = select(Participation).where(
            Participation.competition_id == problem.competition_id,
            Participation.team_id == team_id
        )
        participation_result = await session.execute(participation_statement)
        participation = participation_result.scalar_one_or_none()

        if not participation:
            return ResponseModel(code=1, msg="您的队伍尚未报名此比赛，无法提交文件")

        # 检查文件大小
        file_size = len(file.file.read())
        file.file.seek(0)  # 将文件指针重置到开头

        if file_size > 10 * 1024 * 1024:  # 10MB 限制
            return ResponseModel(code=1, msg="文件大小超过限制")

        # 保存文件内容，确保文件名唯一性
        upload_directory = os.path.join("uploads", str(problem_id))
        if not os.path.exists(upload_directory):
            os.makedirs(upload_directory)  # 如果目录不存在则创建

        file_name = f"{uuid.uuid4()}_{file.filename}"
        file_location = os.path.join(upload_directory, file_name)

        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        # 创建提交记录
        submission = Submission(
            user_id=user_id,
            team_id=team_id,
            problem_id=problem_id,
            competition_id=problem.competition_id,
            submission_content=file_name,  # 不返回完整路径，只返回文件名
            score=0,
            status=0,  # 状态为待评测
            submit_time=datetime.now(timezone.utc)
        )
        session.add(submission)
        await session.commit()

        return ResponseModel(code=0, msg="文件提交成功")

    except FileNotFoundError as e:
        return ResponseModel(code=1, msg="文件保存失败: 文件未找到")
    except PermissionError as e:
        return ResponseModel(code=1, msg="文件保存失败: 权限不足")
    except Exception as e:
        return ResponseModel(code=1, msg=f"文件上传失败: {str(e)}")
