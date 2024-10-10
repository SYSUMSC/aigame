from typing import Optional, Union
from sqlmodel import Field, SQLModel, Relationship

class Problem(SQLModel, table=True):

    id: int | None = Field(default=None, primary_key=True)
    name: str
    problem_type_id: int = Field(foreign_key="problemtype.id")  # 修改为外键
    content: str  # 题目描述
    score: int  # 分数
    difficulty: int  # 难度类型
    port: int = Field(unique=True)  # docker容器的端口
    status: int
    competition_id: int = Field(foreign_key="competition.id")

    problem_type: Optional["ProblemType"] = Relationship(back_populates="problems")  # 定义关系

class ProblemSchema(SQLModel):
    name: str
    problem_type_id: int  # 引用problem_type的id
    content: str
    score: int
    difficulty: int
    port: int
    status: int
    competition_id: int

class ProblemSearchSchema(SQLModel):
    name: Optional[str] = None
    problem_type_id: Optional[int] = None  # 搜索时根据ID来关联
    difficulty: Optional[Union[int, str]] = None
    status: Optional[str] = None
    competition_id: Optional[Union[int, str]] = None