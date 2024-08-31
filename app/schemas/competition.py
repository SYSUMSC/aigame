from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class Competition(SQLModel, table=True):
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
    status: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
