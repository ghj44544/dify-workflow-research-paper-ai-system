from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)


class AskResponse(BaseModel):
    paper_id: int
    question: str
    answer: str


class QARecordResponse(BaseModel):
    id: int
    paper_id: int
    question: str
    answer: str
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)
