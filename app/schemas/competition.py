from typing import Optional, Union
from datetime import datetime
from sqlmodel import Field, SQLModel

class Competition(SQLModel, table=True):
    __tablename__ = "competition"
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    name: str
    start_time: datetime
    end_time: datetime
    status: int
    description: Optional[str] = None

class CompetitionSchema(SQLModel):
    name: str
    start_time: datetime
    end_time: datetime
    status: int
    description: Optional[str] = None

class CompetitionSearchSchema(SQLModel):
    name: Optional[str] = None
    status: Optional[Union[int, str]] = None
    start_time: Optional[Union[datetime, str]] = None
    end_time: Optional[Union[datetime, str]] = None