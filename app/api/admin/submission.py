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
