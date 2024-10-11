from typing import Optional, Union
from sqlmodel import Field, SQLModel, Relationship

class Problem(SQLModel, table=True):
    __tablename__ = "problem"
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    name: str
    problem_type_id: int = Field(foreign_key="problemtype.id")  # 外键关联到 problemtype 表
    content: str  # 题目描述
    score: int  # 分数
    difficulty: int  # 难度类型 [{'value': '1', 'label': '旅行'}, {'value': '2', 'label': '经典'}, {'value': '3', 'label': '专家'}, {'value': '4', 'label': '大师'}]
    port: int = Field(unique=True)  # docker容器的端口
    status: int
    competition_id: int = Field(foreign_key="competition.id")

    problem_type: Optional["ProblemType"] = Relationship(back_populates="problems")  # 反向关系，与 ProblemType 中的 problems 对应


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