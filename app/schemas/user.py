from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    name: str
    student_id: str = Field(unique=True)
    password: str
    is_active: bool = True
    team_id: int | None = Field(default=None, foreign_key="team.id")

class UserSchema(SQLModel):
    username: str
    email: str
    name: str
    student_id: str
    password: str | None = Field(default=None)
    is_active: bool = True
    team_id: int | None = None

class UserSearchSchema(SQLModel):
    username: str | None = None
    email: str | None = None
    name: str | None = None
    student_id: str | None = None
    is_active: bool | None = None