from logging.config import fileConfig

from app.db.session import engine  # 导入你项目中的异步engine
from app.schemas.competition import Competition
from app.schemas.config import Config
from app.schemas.participation import Participation
from app.schemas.problem import Problem
from app.schemas.problem_type import ProblemType
from app.schemas.submission import Submission
from app.schemas.team import Team
# 导入所有的模型
from app.schemas.user import User
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel

from alembic import context

# Alembic Config对象，提供访问 .ini 文件中的配置
config = context.config

# 解释配置文件中的日志设置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目标metadata，指定SQLModel的metadata，以便autogenerate功能使用
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """
    以'离线'模式运行迁移。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    以'在线'模式运行迁移，在这种情况下我们需要创建引擎并关联连接。
    """
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    """
    执行迁移。
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # 如果是在线模式，确保异步运行
    import asyncio
    asyncio.run(run_migrations_online())
