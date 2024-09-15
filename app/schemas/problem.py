from typing import Optional, Union
from sqlmodel import Field, SQLModel

class Problem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    problem_type: str #赛题类型
    content: str #赛题描述
    score: int #分数
    difficulty: int #难度类型 旅行、经典、专家、大师（1-4）
    status: int
    competition_id: int = Field(foreign_key="competition.id")

class ProblemSchema(SQLModel):
    name: str
    problem_type: str
    content: str
    score: int
    difficulty: int
    status: int
    competition_id: int

class ProblemSearchSchema(SQLModel):
    name: Optional[str] = None
    problem_type: Optional[str] = None
    difficulty: Optional[Union[int, str]] = None
    status: Optional[str] = None
    competition_id: Optional[Union[int, str]] = None
