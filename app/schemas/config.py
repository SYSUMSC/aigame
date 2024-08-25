from sqlmodel import Field, SQLModel


class Config(SQLModel, table=True):
    k: str = Field(primary_key=True)
    v: str | None = None

class ConfigSchema(SQLModel):
    k: str
    v: str | None = None