from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Announcement(SQLModel, table=True):
    __tablename__ = "announcement"
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    date: datetime | None
    title: str
    content: str

class AnnouncementSchema(SQLModel):
    title: str
    content: str
    date: Optional[str] = None

class AnnouncementSearchSchema(SQLModel):
    date: str | None = None
    title: str | None = None
    content: str | None = None