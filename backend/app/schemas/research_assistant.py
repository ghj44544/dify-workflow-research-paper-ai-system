from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResearchAssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=20)
    recent_years: int = Field(default=3, ge=1, le=10)


class ResearchPaperItem(BaseModel):
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    publication_date: str | None = None
    venue: str = ""
    doi: str = ""
    url: str = ""
    abstract: str = ""
    cited_by_count: int = 0
    source: str = "openalex"


class ResearchAssistantChatResponse(BaseModel):
    answer: str
    papers: list[ResearchPaperItem]
    search_topic: str
    search_source: str = "OpenAlex"


class ResearchChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)


class SaveResearchPaperRequest(ResearchPaperItem):
    pass


class SavedResearchPaperResponse(ResearchPaperItem):
    id: int
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)
