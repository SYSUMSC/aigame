from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.security import get_password_hash
from db.session import get_session
from schemas.user import User, UserSchema, UserSearchSchema

from ..response_model import ResponseModel

user_router = APIRouter()

@user_router.post("/user", response_model=ResponseModel, tags=["Admin"])
async def create_user(user: UserSchema, session: AsyncSession = Depends(get_session)):
    try:
        user_db = User(**user.model_dump())
        user_db.password = get_password_hash(user.password)
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)
        return ResponseModel(code=0, msg="用户创建成功", data=user_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@user_router.put("/user/{user_id}", response_model=ResponseModel, tags=["Admin"])
async def update_user(user_id: int, user: UserSchema, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        user_db = result.scalar_one_or_none()
        if not user_db:
            return ResponseModel(code=1, msg="用户未找到")
        user_data = user.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(user_db, key, value)
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)
        return ResponseModel(code=0, msg="用户更新成功", data=user_db.model_dump())
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@user_router.delete("/user/{user_id}", response_model=ResponseModel, tags=["Admin"])
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    try:
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        user_db = result.scalar_one_or_none()
        if not user_db:
            return ResponseModel(code=1, msg="用户未找到")
        await session.delete(user_db)
        await session.commit()
        return ResponseModel(code=0, msg="用户删除成功")
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@user_router.delete("/user", response_model=ResponseModel, tags=["Admin"])
async def delete_users(ids: str, session: AsyncSession = Depends(get_session)):
    try:
        user_ids = [int(id) for id in ids.split(",")]
        statement = select(User).where(User.id.in_(user_ids))
        result = await session.execute(statement)
        users_db = result.scalars().all()
        for user_db in users_db:
            await session.delete(user_db)
        await session.commit()
        return ResponseModel(code=0, msg="用户批量删除成功", count=len(users_db))
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))

@user_router.post("/user/search", response_model=ResponseModel, tags=["Admin"])
async def search_users(search: UserSearchSchema, page: int = 1, limit: int = 10, session: AsyncSession = Depends(get_session)):
    try:
        query = select(User)
        filters = []
        for field, value in search.model_dump(exclude_unset=True).items():
            if isinstance(value, str):
                filters.append(getattr(User, field).like(f"%{value}%"))
            else:
                filters.append(getattr(User, field) == value)
        query = query.where(*filters)
        total_statement = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_statement)
        total = total_result.scalar()
        query = query.offset((page - 1) * limit).limit(limit)
        result = await session.execute(query)
        users = result.scalars().all()
        return ResponseModel(code=0, msg="用户检索成功", data=[user.model_dump() for user in users], count=total)
    except Exception as e:
        return ResponseModel(code=1, msg=str(e))