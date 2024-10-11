from sqlmodel import Field, Relationship, SQLModel
class ProblemType(SQLModel, table=True):
    __tablename__ = "problemtype"
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    problems: list["Problem"] = Relationship(back_populates="problem_type")  # 反向关系

class ProblemTypeSchema(SQLModel):
    name: str
    description: str | None = None

class ProblemTypeSearchSchema(SQLModel):
    name: str | None = None
    description: str | None = None
