# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlmodel import select
# from db.session import get_session
# from schemas.problem import Problem
# from schemas.submission import Submission, SubmissionSchema
# from app.api.models import ResponseModel
# from datetime import datetime, timezone

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

#         # 保存文件内容
#         file_location = f"uploads/{problem_id}/{file.filename}"
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
    
#     except Exception as e:
#         return ResponseModel(code=1, msg=f"文件上传失败: {str(e)}")
