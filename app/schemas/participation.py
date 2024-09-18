from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime, timezone

class Participation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    competition_id: int = Field(foreign_key="competition.id")
    team_id: int | None = Field(default=None, foreign_key="team.id")
    score: int | None = None  # 最终得分
    join_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # 加入时间

class ParticipationSchema(SQLModel):
    user_id: int
    competition_id: int
    team_id: int | None = None

class ParticipationSearchSchema(SQLModel):
    user_id: Optional[int] = None
    competition_id: Optional[int] = None
    team_id: Optional[int] = None