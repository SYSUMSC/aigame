from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime, timezone

class Submission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    team_id: int = Field(foreign_key="team.id")
    problem_id: int = Field(foreign_key="problem.id")
    competition_id: int = Field(foreign_key="competition.id")
    submission_content: str  # 提交的内容
    score: int  # 该次提交的得分
    status: int  # 提交状态，例如 0: 待评测, 1: 已评测
    submit_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # 提交时间

class SubmissionSchema(SQLModel):
    user_id: int
    team_id: int
    problem_id: int
    competition_id: int
    submission_content: str
    score: int
    status: int  # 提交状态

class SubmissionSearchSchema(SQLModel):
    user_id: Optional[int] = None
    team_id: Optional[int] = None
    problem_id: Optional[int] = None
    competition_id: Optional[int] = None
    score: Optional[int] = None
    status: Optional[int] = None  # 提交状态