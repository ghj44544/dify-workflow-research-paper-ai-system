from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NoteRequest(BaseModel):
    note_style: str | None = "适合研究生阅读笔记"


class NoteResponse(BaseModel):
    id: int
    paper_id: int
    note_style: str | None = None
    content: str
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)
