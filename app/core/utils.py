from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.session import get_session
from schemas.config import Config


async def load_config_from_db(session: AsyncSession):
    config_dict = {}
    result = await session.execute(select(Config))
    for config in result.scalars().all():
        config_dict[config.k] = config.v
    return config_dict

async def load_smtp_config_from_db(session: AsyncSession):
    smtp_config = {}
    result = await session.execute(select(Config).where(Config.k == "smtp_server"))
    smtp_config["smtp_server"] = result.scalars().first().v
    result = await session.execute(select(Config).where(Config.k == "smtp_port"))
    smtp_config["smtp_port"] = int(result.scalars().first().v)
    result = await session.execute(select(Config).where(Config.k == "smtp_user"))
    smtp_config["smtp_user"] = result.scalars().first().v
    result = await session.execute(select(Config).where(Config.k == "smtp_password"))
    smtp_config["smtp_password"] = result.scalars().first().v
    return smtp_config