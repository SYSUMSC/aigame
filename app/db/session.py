from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select

from app.core.config import settings
from app.core.security import get_password_hash
from app.schemas.config import Config
from app.db.init import init_test_data

DATABASE_URL = settings.DATABASE_URI
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # 使用 SessionLocal 创建一个异步会话
    async with SessionLocal() as session:
        # 检查并创建默认的 admin_user 和 admin_pwd
        admin_user = await session.execute(select(Config).where(Config.k == "admin_user"))
        if not admin_user.first():
            session.add(Config(k="admin_user", v="admin"))
        admin_pwd = await session.execute(select(Config).where(Config.k == "admin_pwd"))
        if not admin_pwd.first():
            session.add(Config(k="admin_pwd", v=get_password_hash("123456")))
        await session.commit()

        # 可选：生成测试数据
        await init_test_data(session)

    yield

