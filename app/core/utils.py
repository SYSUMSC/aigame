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