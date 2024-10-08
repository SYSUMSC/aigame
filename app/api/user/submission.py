# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlmodel import select
# from db.session import get_session
# from schemas.problem import Problem
# from schemas.submission import Submission, SubmissionSchema
# from app.api.models import ResponseModel
# from datetime import datetime, timezone
# import os
# import uuid

# problem_router = APIRouter()

# @problem_router.post("/problem/{problem_id}/submit", response_model=ResponseModel, tags=["Problem"])
# async def submit_problem_file(
#     problem_id: int,
#     file: UploadFile = File(...),  # 接收上传文件
#     session: AsyncSession = Depends(get_session),
#     user_id: int = Depends(get_current_user_id),  # 假设有获取当前用户的函数
#     team_id: int = Depends(get_current_team_id)   # 假设有获取当前团队的函数
# ):
#     try:
#         # 检查 problem_id 是否存在
#         statement = select(Problem).where(Problem.id == problem_id)
#         result = await session.execute(statement)
#         problem = result.scalar_one_or_none()
#         if not problem:
#             return ResponseModel(code=1, msg="赛题未找到")

#         # 文件大小限制
#         if file.spool_max_size > 10 * 1024 * 1024:  # 10MB 限制
#             return ResponseModel(code=1, msg="文件大小超过限制")

#         # 保存文件内容，确保文件名唯一性
#         file_name = f"{uuid.uuid4()}_{file.filename}"
#         file_location = os.path.join("uploads", str(problem_id), file_name)
#         with open(file_location, "wb+") as file_object:
#             file_object.write(file.file.read())
        
#         # 创建提交记录
#         submission = Submission(
#             user_id=user_id,
#             team_id=team_id,
#             problem_id=problem_id,
#             competition_id=problem.competition_id,
#             submission_content=file_location,
#             score=0,  # 初始得分为0
#             status=0,  # 状态为待评测
#             submit_time=datetime.now(timezone.utc)
#         )
#         session.add(submission)
#         await session.commit()

#         return ResponseModel(code=0, msg="文件提交成功", data={"file_location": file_location})
    
#     except FileNotFoundError as e:
#         return ResponseModel(code=1, msg="文件保存失败: 文件未找到")
#     except PermissionError as e:
#         return ResponseModel(code=1, msg="文件保存失败: 权限不足")
#     except Exception as e:
#         return ResponseModel(code=1, msg=f"文件上传失败: {str(e)}")


# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlmodel import select
# from db.session import get_session
# from schemas.problem import Problem
# from schemas.submission import Submission
# from app.api.models import ResponseModel
# from datetime import datetime, timezone
# from core.security import get_current_user  # 确保你有这个函数
# import os
# import uuid

# problem_router = APIRouter()

# # 实现获取用户ID的函数
# async def get_current_user_id(current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
#     statement = select(User).where(User.username == current_user)
#     result = await session.execute(statement)
#     user_db = result.scalar_one_or_none()

#     if not user_db:
#         raise HTTPException(status_code=400, detail="用户未找到")
    
#     return user_db.id

# # 实现获取team_id的函数
# async def get_current_team_id(current_user: str = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
#     statement = select(User).where(User.username == current_user)
#     result = await session.execute(statement)
#     user_db = result.scalar_one_or_none()

#     if not user_db:
#         raise HTTPException(status_code=400, detail="用户未找到")

#     if not user_db.team_id:
#         raise HTTPException(status_code=400, detail="用户没有加入任何队伍")

#     return user_db.team_id

# @problem_router.post("/api/user/problem/{problem_id}/submit", response_model=ResponseModel, tags=["Problem"])
# async def submit_problem_file(
#     problem_id: int,
#     file: UploadFile = File(...),  # 接收上传文件
#     session: AsyncSession = Depends(get_session),
#     user_id: int = Depends(get_current_user_id),  # 获取当前用户的ID
#     team_id: int = Depends(get_current_team_id)   # 获取当前用户的队伍ID
# ):
#     try:
#         # 检查 problem_id 是否存在
#         statement = select(Problem).where(Problem.id == problem_id)
#         result = await session.execute(statement)
#         problem = result.scalar_one_or_none()
#         if not problem:
#             return ResponseModel(code=1, msg="赛题未找到")

#         # 文件大小限制
#         if file.spool_max_size > 10 * 1024 * 1024:  # 10MB 限制
#             return ResponseModel(code=1, msg="文件大小超过限制")

#         # 保存文件内容，确保文件名唯一性
#         file_name = f"{uuid.uuid4()}_{file.filename}"
#         file_location = os.path.join("uploads", str(problem_id), file_name)
#         with open(file_location, "wb+") as file_object:
#             file_object.write(file.file.read())
        
#         # 创建提交记录
#         submission = Submission(
#             user_id=user_id,
#             team_id=team_id,
#             problem_id=problem_id,
#             competition_id=problem.competition_id,
#             submission_content=file_location,
#             score=0,  # 初始得分为0
#             status=0,  # 状态为待评测
#             submit_time=datetime.now(timezone.utc)
#         )
#         session.add(submission)
#         await session.commit()

#         return ResponseModel(code=0, msg="文件提交成功", data={"file_location": file_location})
    
#     except FileNotFoundError as e:
#         return ResponseModel(code=1, msg="文件保存失败: 文件未找到")
#     except PermissionError as e:
#         return ResponseModel(code=1, msg="文件保存失败: 权限不足")
#     except Exception as e:
#         return ResponseModel(code=1, msg=f"文件上传失败: {str(e)}")


from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from db.session import get_session
from schemas.problem import Problem
from schemas.submission import Submission
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
    file: UploadFile = File(...),  # 接收上传文件
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),  # 获取当前用户的ID
    team_id: int = Depends(get_current_team_id)   # 获取当前用户的队伍ID
):
    try:
        # 检查 problem_id 是否存在
        statement = select(Problem).where(Problem.id == problem_id)
        result = await session.execute(statement)
        problem = result.scalar_one_or_none()
        if not problem:
            return ResponseModel(code=1, msg="赛题未找到")

        # 文件大小限制
        if file.spool_max_size > 10 * 1024 * 1024:  # 10MB 限制
            return ResponseModel(code=1, msg="文件大小超过限制")

        # 保存文件内容，确保文件名唯一性
        file_name = f"{uuid.uuid4()}_{file.filename}"
        file_location = os.path.join("uploads", str(problem_id), file_name)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        
        # 创建提交记录
        submission = Submission(
            user_id=user_id,
            team_id=team_id,
            problem_id=problem_id,
            competition_id=problem.competition_id,
            submission_content=file_location,
            score=0,  # 初始得分为0
            status=0,  # 状态为待评测
            submit_time=datetime.now(timezone.utc)
        )
        session.add(submission)
        await session.commit()

        return ResponseModel(code=0, msg="文件提交成功", data={"file_location": file_location})
    
    except FileNotFoundError as e:
        return ResponseModel(code=1, msg="文件保存失败: 文件未找到")
    except PermissionError as e:
        return ResponseModel(code=1, msg="文件保存失败: 权限不足")
    except Exception as e:
        return ResponseModel(code=1, msg=f"文件上传失败: {str(e)}")
