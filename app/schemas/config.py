from sqlmodel import Field, SQLModel


class Config(SQLModel, table=True):
    __tablename__ = "config"
    __table_args__ = {"extend_existing": True}
    k: str = Field(primary_key=True)
    v: str | None = None

class ConfigSchema(SQLModel):
    k: str
    v: str | None = None