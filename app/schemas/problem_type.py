from sqlmodel import Field, SQLModel

class ProblemType(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

class ProblemTypeSchema(SQLModel):
    name: str
    description: str | None = None

class ProblemTypeSearchSchema(SQLModel):
    name: str | None = None
    description: str | None = None
