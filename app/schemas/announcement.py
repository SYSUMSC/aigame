# from typing import Union
# from datetime import datetime
# from sqlmodel import Field, SQLModel
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime

class Announcement(SQLModel, table=True):
    __tablename__ = "announcement"
    __table_args__ = {"extend_existing": True}
    id: int
    # announcement date
    date: datetime | None = Field(default = "", primary_key=datetime.now())
    announcement_id: int = Field(foreign_key="announcement.id")
    title: str
    content: str

class AnnouncementSchema(SQLModel):
    id: int
    date: str
    title: str
    content: str

# class UserSearchSchema(SQLModel):
#     username: str | None = None
#     email: str | None = None
#     name: str | None = None
#     student_id: str | None = None
#     is_active: bool | None = None

class AnnouncementSearchSchema(SQLModel):
    id: int | None = None
    date: str | None = None
    title: str | None = None
    content: str | None = None