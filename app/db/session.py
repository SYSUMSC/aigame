from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select

from core.config import settings
from core.security import get_password_hash
from schemas.config import Config

DATABASE_URL = settings.DATABASE_URI
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        async with async_session() as session:
            # 检查并创建默认的admin_user和admin_pwd
            admin_user = await session.execute(select(Config).where(Config.k == "admin_user"))
            if not admin_user.first():
                session.add(Config(k="admin_user", v="admin"))
            admin_pwd = await session.execute(select(Config).where(Config.k == "admin_pwd"))
            if not admin_pwd.first():
                session.add(Config(k="admin_pwd", v=get_password_hash("123456")))
            await session.commit()
    yield