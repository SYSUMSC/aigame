# from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from db.session import get_session
from schemas.problem import Problem
from app.api.models import ResponseModel
from schemas.problem_type import ProblemType

from fastapi import APIRouter, Depends, HTTPException, Body, Path

problem_router = APIRouter()

# @problem_router.post("/problem/detail", response_model=ResponseModel, tags=["Problem"])
# async def get_problem_detail(
#     problem_id: int = Body(..., embed=True),  # 使用 Body 获取 JSON 传递的参数
#     session: AsyncSession = Depends(get_session)
# ):
#     try:
#         # 获取赛题详情
#         statement = select(Problem).where(Problem.id == problem_id)
#         result = await session.execute(statement)
#         problem_db = result.scalar_one_or_none()

#         if not problem_db:
#             return ResponseModel(code=1, msg="赛题未找到")

#         # 通过关系获取问题类型
#         problem_type = problem_db.problem_type

#         return ResponseModel(
#             code=0, 
#             msg="赛题详情获取成功", 
#             data={"problem": problem_db.model_dump(), "problem_type": problem_type.model_dump() if problem_type else None}
#         )
#     except Exception as e:
#         return ResponseModel(code=1, msg=str(e))

# @problem_router.post("/problem/{problem_id}", response_model=ResponseModel, tags=["Problem"])
# async def get_problem_detail(
#     problem_id: int = Path(..., description="The ID of the problem"),  # 使用 Path 获取 URL 参数
#     session: AsyncSession = Depends(get_session)
# ):
#     try:
#         # 获取赛题详情
#         statement = select(Problem).where(Problem.id == problem_id)
#         result = await session.execute(statement)
#         problem_db = result.scalar_one_or_none()

#         if not problem_db:
#             return ResponseModel(code=1, msg="赛题未找到")

#         # 通过关系获取问题类型
#         problem_type = problem_db.problem_type

#         return ResponseModel(
#             code=0, 
#             msg="赛题详情获取成功", 
#             data={"problem": problem_db.model_dump(), "problem_type": problem_type.model_dump() if problem_type else None}
#         )
#     except Exception as e:
#         return ResponseModel(code=1, msg=str(e))
    
# # 感觉下面这段写的很好
# @problem_router.post("/problem/{problem_id}", response_model=ResponseModel, tags=["Problem"])
# async def get_problem_detail(
#     problem_id: int = Path(..., description="The ID of the problem"),  # 使用 Path 获取 URL 参数
#     session: AsyncSession = Depends(get_session)
# ):
#     try:
#         # 获取赛题详情
#         statement = select(Problem).where(Problem.id == problem_id)
#         result = await session.execute(statement)  # 确保使用 await
#         problem_db = result.scalar_one_or_none()

#         if not problem_db:
#             return ResponseModel(code=1, msg="赛题未找到")

#         # 通过关系获取问题类型
#         problem_type = problem_db.problem_type

#         return ResponseModel(
#             code=0, 
#             msg="赛题详情获取成功", 
#             data={"problem": problem_db.model_dump(), "problem_type": problem_type.model_dump() if problem_type else None}
#         )
#     except Exception as e:
#         return ResponseModel(code=1, msg=str(e))



# @problem_router.get("/problem/{problem_id}", response_model=ResponseModel, tags=["Problem"])
# async def get_problem_detail(problem_id: int, session: AsyncSession = Depends(get_session)):
#     try:
#         # 获取赛题详情
#         statement = select(Problem).where(Problem.id == problem_id)
#         result = await session.execute(statement)
#         problem_db = result.scalar_one_or_none()

#         if not problem_db:
#             return ResponseModel(code=1, msg="赛题未找到")

#         # 通过关系获取问题类型
#         problem_type = problem_db.problem_type

#         return ResponseModel(code=0, msg="赛题详情获取成功", data={"problem": problem_db.model_dump(), "problem_type": problem_type.model_dump()})
#     except Exception as e:
#         return ResponseModel(code=1, msg=str(e))

# @problem_router.post("/problem/detail", response_model=ResponseModel, tags=["Problem"])
# async def get_problem_detail_json(
#     problem_id: int = Body(..., embed=True),  # 使用 Body 获取 JSON 传递的参数
#     session: AsyncSession = Depends(get_session)
# ):
#     try:
#         # 获取赛题详情
#         statement = select(Problem).where(Problem.id == problem_id)
#         result = await session.execute(statement)
#         problem_db = result.scalar_one_or_none()

#         if not problem_db:
#             return ResponseModel(code=1, msg="赛题未找到")

#         # 通过关系获取问题类型
#         problem_type = problem_db.problem_type

#         return ResponseModel(code=0, msg="赛题详情获取成功", data={"problem": problem_db.model_dump(), "problem_type": problem_type.model_dump()})
#     except Exception as e:
#         return ResponseModel(code=1, msg=str(e))

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlmodel import select
# from db.session import get_session
# from schemas.problem import Problem, ProblemSchema, ProblemSearchSchema
# from schemas.problem_type import ProblemType
# from app.api.models import ResponseModel

# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlmodel import select
# from db.session import get_session
# from schemas.problem import Problem
# from schemas.problem_type import ProblemType
# from app.api.models import ResponseModel

# problem_router = APIRouter()

# # 获取单个赛题详情
# @problem_router.get("/problem/{problem_id}", response_model=ResponseModel, tags=["Problem"])
# async def get_problem_detail(problem_id: int, session: AsyncSession = Depends(get_session)):
#     try:
#         # 获取赛题详情
#         statement = select(Problem).where(Problem.id == problem_id)
#         result = await session.execute(statement)
#         problem_db = result.scalar_one_or_none()

#         if not problem_db:
#             return ResponseModel(code=1, msg="赛题未找到")

#         # 获取关联的题目类型
#         problem_type = await session.get(ProblemType, problem_db.problem_type_id)

#         return ResponseModel(
#             code=0, 
#             msg="赛题详情获取成功", 
#             data={
#                 "problem": problem_db.model_dump(),
#                 "problem_type": problem_type.model_dump() if problem_type else None
#             }
#         )
#     except Exception as e:
#         return ResponseModel(code=1, msg=str(e))

# @problem_router.post("/problem/{problem_id}", response_model=ResponseModel, tags=["Problem"])
# async def get_problem_detail(
#     problem_id: int = Path(..., description="The ID of the problem"),  # 使用 Path 获取 URL 参数
#     session: AsyncSession = Depends(get_session)
# ):
#     try:
#         # 获取赛题详情
#         statement = select(Problem).where(Problem.id == problem_id)
#         result = await session.execute(statement)  # 确保使用 await
#         problem_db = result.scalar_one_or_none()

#         if not problem_db:
#             return ResponseModel(code=1, msg="赛题未找到")

#         # 通过关系获取问题类型
#         problem_type = problem_db.problem_type

#         return ResponseModel(
#             code=0, 
#             msg="赛题详情获取成功", 
#             data={"problem": problem_db.model_dump(), "problem_type": problem_type.model_dump() if problem_type else None}
#         )
#     except Exception as e:
#         return ResponseModel(code=1, msg=str(e))
import logging

# 在函数开始时定义日志输出
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@problem_router.post("/problem/{problem_id}", response_model=ResponseModel, tags=["Problem"])
async def get_problem_detail(
    problem_id: int = Path(..., description="The ID of the problem"),  # 使用 Path 获取 URL 参数
    session: AsyncSession = Depends(get_session)
):
    # # 在请求处理的开始处打印
    # print("Start fetching problem detail")  
    # print(f"Received problem_id: {problem_id}")  # 打印接收到的 problem_id

    # 记录日志
    logging.info("Start fetching problem detail")
    logging.info(f"Received problem_id: {problem_id}")  # 记录接收到的 problem_id

    try:
        # 获取赛题详情
        statement = select(Problem).where(Problem.id == problem_id)
        result = await session.execute(statement)  # 确保使用 await
        problem_db = result.scalar_one_or_none()

        if not problem_db:
            return ResponseModel(code=1, msg="赛题未找到")

        # 通过关系获取问题类型
        problem_type = problem_db.problem_type

        return ResponseModel(
            code=0, 
            msg="赛题详情获取成功", 
            data={"problem": problem_db.model_dump(), "problem_type": problem_type.model_dump() if problem_type else None}
        )
    # except Exception as e:
    #     return ResponseModel(code=1, msg=str(e))
    except Exception as e:
        logging.error(f"Exception occurred when fetching problem detail: {str(e)}")
        return ResponseModel(code=1, msg=f"Error occurred: {str(e)}")
