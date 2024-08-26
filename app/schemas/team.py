from typing import List

from sqlmodel import Field, Relationship, SQLModel

from .user import User


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(unique=True)
    captain_id: int | None = Field(foreign_key="user.id")
    status: str | None = None
    invite_code: str | None = None

class TeamSchema(SQLModel):
    name: str | None = None
    captain_id: int | None = None
    status: str | None = None
    invite_code: str | None = None

class TeamSearchSchema(SQLModel):
    name: str | None = None
    captain_id: int | None = None
    status: str | None = None