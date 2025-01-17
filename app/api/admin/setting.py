from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

from app.api.models import ResponseModel
from app.schemas.config import Config, ConfigSchema
from db.session import get_session

setting_router = APIRouter()
@setting_router.post("/setting", response_model=ResponseModel, tags=["Admin"])
async def save_smtp_settings(
    smtp_server: str = Form(...),
    smtp_port: str = Form(...),
    smtp_user: str = Form(...),
    smtp_password: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    try:
        # 需要保存的SMTP配置信息
        smtp_data = {
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "smtp_user": smtp_user,
            "smtp_password": smtp_password
        }

        for key, value in smtp_data.items():
            statement = select(Config).where(Config.k == key)
            result = await session.execute(statement)
            config_db = result.scalar_one_or_none()
            if config_db:
                # 如果已有该配置，则更新
                config_db.v = value
            else:
                # 如果没有该配置，则新建
                new_config = Config(k=key, v=value)
                session.add(new_config)

        await session.commit()
        return ResponseModel(code=0, msg="SMTP配置信息保存成功")
    except Exception as e:
        await session.rollback()  # 如果出现错误则回滚
        return ResponseModel(code=1, msg=str(e))