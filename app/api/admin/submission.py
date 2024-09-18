from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.session import get_session
from schemas.submission import Submission, SubmissionSearchSchema
from ..models import ResponseModel

submission_router = APIRouter()

@submission_router.post("/submission/search", response_model=ResponseModel, tags=["Admin"])
async def search_submissions(search: SubmissionSearchSchema, page: int = 1, limit: int = 10, session: AsyncSession = Depends(get_session)):
    try:
        query = select(Submission)
        filters = []
        for field, value in search.model_dump(exclude_unset=True).items():
            if value is None or value == "":
                continue
            filters.append(getattr(Submission, field) == value)
        query = query.where(*filters)
        total_statement = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_statement)
        total = total_result.scalar()
        query = query.offset((page - 1) * limit).limit(limit)
        result = await session.execute(query)
        submissions = result.scalars().all()
        return ResponseModel(code=0, msg="提交记录检索成功", data=[submission.model_dump() for submission in submissions], count=total)
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
@submission_router.delete("/submission/{submission_id}", response_model=ResponseModel, tags=["Admin"])
async def delete_submission(submission_id: int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(Submission).where(Submission.id == submission_id)
        result = await session.execute(statement)
        submission_db = result.scalar_one_or_none()
        if not submission_db:
            return ResponseModel(code=1, msg="提交记录未找到")
        await session.delete(submission_db)
        await session.commit()
        return ResponseModel(code=0, msg="提交记录删除成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@submission_router.delete("/submission", response_model=ResponseModel, tags=["Admin"])
async def delete_submissions(request: BatchDeleteRequest, session: AsyncSession = Depends(get_session)):
    try:
        submission_ids = request.ids
        statement = select(Submission).where(Submission.id.in_(submission_ids))
        result = await session.execute(statement)
        submissions_db = result.scalars().all()
        for submission_db in submissions_db:
            await session.delete(submission_db)
        await session.commit()
        return ResponseModel(code=0, msg="提交记录批量删除成功", count=len(submissions_db))
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))
