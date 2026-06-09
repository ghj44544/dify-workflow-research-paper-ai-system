from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaperBase(BaseModel):
    title: str | None = None
    authors: str | None = None
    year: str | None = None
    keywords: str | None = None
    research_problem: str | None = None
    method: str | None = None
    dataset: str | None = None
    metrics: str | None = None
    contribution: str | None = None
    limitation: str | None = None
    conclusion: str | None = None


class PaperCreate(PaperBase):
    file_name: str
    file_path: str
    file_size: int


class PaperResponse(PaperBase):
    id: int
    file_name: str
    file_path: str
    file_size: int
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)
