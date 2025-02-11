from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Participation(SQLModel, table=True):
    __tablename__ = "participation"
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    competition_id: int = Field(foreign_key="competition.id")
    team_id: int | None = Field(default=None, foreign_key="team.id")
    score: int | None = None  # 最终得分
    join_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # 加入时间
    update_time : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # 更新分数时间

class ParticipationSchema(SQLModel):
    user_id: int
    competition_id: int
    team_id: int | None = None

class ParticipationSearchSchema(SQLModel):
    user_id: Optional[int] = None
    competition_id: Optional[int] = None
    team_id: Optional[int] = None