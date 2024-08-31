from typing import Optional
from sqlmodel import Field, SQLModel

class Problem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str #赛题描述
    problem_type: str #赛题类型
    score: int #分数
    difficulty: int #难度类型（0简单，1中等，2困难）
    status: int
    competition_id: int = Field(foreign_key="competition.id")

class ProblemSchema(SQLModel):
    name: str
    description: str
    problem_type: str
    content: str
    score: int
    difficulty: int
    status: int
    competition_id: int

class ProblemSearchSchema(SQLModel):
    name: Optional[str] = None
    problem_type: Optional[str] = None
    difficulty: Optional[int] = None
    status: Optional[str] = None
    competition_id: Optional[int] = None
