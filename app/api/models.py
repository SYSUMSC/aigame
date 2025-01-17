from typing import List

from pydantic import BaseModel


class ResponseModel(BaseModel):
    code: int
    msg: str
    data: dict | list | None = None
    count: int | None = None

class BatchDeleteRequest(BaseModel):
    ids: List[int]

