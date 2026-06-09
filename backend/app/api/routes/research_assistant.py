import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.research_assistant import (
    ResearchChatMessage,
    ResearchSavedPaper,
    ResearchSearchResult,
)
from app.schemas.common import success_response
from app.schemas.research_assistant import (
    ResearchAssistantChatRequest,
    ResearchAssistantChatResponse,
    ResearchChatMessageResponse,
    ResearchPaperItem,
    SaveResearchPaperRequest,
    SavedResearchPaperResponse,
)
from app.services.academic_search_service import (
    AcademicSearchError,
    build_search_query,
    search_openalex_papers,
)
from app.services.dify_service import DifyAPIError, DifyService
from app.utils.text_utils import strip_think_blocks


router = APIRouter(prefix="/api/research-assistant", tags=["research-assistant"])


@router.post("/chat")
async def chat_with_research_assistant(
    payload: ResearchAssistantChatRequest,
    db: Session = Depends(get_db),
) -> dict:
    user_message = payload.message.strip()
    _create_chat_message(db, "user", user_message)

    search_topic = build_search_query(user_message)
    try:
        papers = await search_openalex_papers(
            query=search_topic,
            recent_years=payload.recent_years,
            limit=payload.limit,
        )
    except AcademicSearchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    _save_search_results(db, user_message, search_topic, papers)

    clean_papers = [_clean_paper_for_frontend(paper) for paper in papers]
    try:
        answer = await DifyService().run_research_assistant_workflow(
            user_question=user_message,
            search_results=clean_papers,
            search_topic=search_topic,
            recent_years=payload.recent_years,
        )
    except DifyAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    answer = strip_think_blocks(answer)
    _create_chat_message(db, "assistant", answer)

    response = ResearchAssistantChatResponse(
        answer=answer,
        papers=[ResearchPaperItem(**paper) for paper in clean_papers],
        search_topic=search_topic,
        search_source="OpenAlex",
    )
    return success_response(data=response.model_dump(mode="json"))


@router.get("/messages")
async def get_research_assistant_messages(db: Session = Depends(get_db)) -> dict:
    stmt = select(ResearchChatMessage).order_by(ResearchChatMessage.create_time.asc())
    messages = [
        _clean_message_response(
            ResearchChatMessageResponse.model_validate(message).model_dump(mode="json")
        )
        for message in db.scalars(stmt).all()
    ]
    return success_response(data=messages)


@router.post("/save-paper")
async def save_research_paper(
    payload: SaveResearchPaperRequest,
    db: Session = Depends(get_db),
) -> dict:
    existing = _find_existing_saved_paper(db, payload)
    if existing:
        data = _saved_paper_to_response(existing)
        return success_response(data=data, message="该论文已收藏")

    saved = ResearchSavedPaper(
        title=payload.title,
        authors=json.dumps(payload.authors, ensure_ascii=False),
        year=payload.year,
        publication_date=payload.publication_date,
        venue=payload.venue,
        doi=payload.doi,
        url=payload.url,
        abstract=payload.abstract,
        cited_by_count=payload.cited_by_count,
        source=payload.source,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return success_response(data=_saved_paper_to_response(saved), message="收藏成功")


@router.get("/saved-papers")
async def get_saved_research_papers(db: Session = Depends(get_db)) -> dict:
    stmt = select(ResearchSavedPaper).order_by(ResearchSavedPaper.create_time.desc())
    papers = [_saved_paper_to_response(paper) for paper in db.scalars(stmt).all()]
    return success_response(data=papers)


@router.delete("/saved-papers/{paper_id}")
async def delete_saved_research_paper(
    paper_id: int,
    db: Session = Depends(get_db),
) -> dict:
    paper = db.get(ResearchSavedPaper, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="收藏论文不存在")

    db.delete(paper)
    db.commit()
    return success_response(message="删除成功")


def _create_chat_message(db: Session, role: str, content: str) -> ResearchChatMessage:
    message = ResearchChatMessage(role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def _save_search_results(
    db: Session,
    query: str,
    search_topic: str,
    papers: list[dict],
) -> None:
    for paper in papers:
        result = ResearchSearchResult(
            query=query,
            search_topic=search_topic,
            title=paper.get("title") or "未命名论文",
            authors=json.dumps(paper.get("authors") or [], ensure_ascii=False),
            year=paper.get("year"),
            publication_date=paper.get("publication_date") or "",
            venue=paper.get("venue") or "",
            doi=paper.get("doi") or "",
            url=paper.get("url") or "",
            abstract=paper.get("abstract") or "",
            cited_by_count=paper.get("cited_by_count") or 0,
            source=paper.get("source") or "openalex",
            raw_data=json.dumps(paper.get("raw_data") or {}, ensure_ascii=False, default=str),
        )
        db.add(result)
    db.commit()


def _clean_paper_for_frontend(paper: dict) -> dict:
    return {
        "title": paper.get("title") or "未命名论文",
        "authors": paper.get("authors") or [],
        "year": paper.get("year"),
        "publication_date": paper.get("publication_date") or "",
        "venue": paper.get("venue") or "",
        "doi": paper.get("doi") or "",
        "url": paper.get("url") or "",
        "abstract": paper.get("abstract") or "",
        "cited_by_count": paper.get("cited_by_count") or 0,
        "source": paper.get("source") or "openalex",
    }


def _find_existing_saved_paper(
    db: Session,
    payload: SaveResearchPaperRequest,
) -> ResearchSavedPaper | None:
    conditions = []
    if payload.doi:
        conditions.append(ResearchSavedPaper.doi == payload.doi)
    if payload.url:
        conditions.append(ResearchSavedPaper.url == payload.url)
    if not conditions:
        conditions.append(ResearchSavedPaper.title == payload.title)

    stmt = select(ResearchSavedPaper).where(or_(*conditions))
    return db.scalars(stmt).first()


def _saved_paper_to_response(paper: ResearchSavedPaper) -> dict:
    data = SavedResearchPaperResponse(
        id=paper.id,
        title=paper.title,
        authors=_loads_authors(paper.authors),
        year=paper.year,
        publication_date=paper.publication_date,
        venue=paper.venue or "",
        doi=paper.doi or "",
        url=paper.url or "",
        abstract=paper.abstract or "",
        cited_by_count=paper.cited_by_count,
        source=paper.source,
        create_time=paper.create_time,
    )
    return data.model_dump(mode="json")


def _clean_message_response(message: dict) -> dict:
    if message.get("role") == "assistant":
        message["content"] = strip_think_blocks(message.get("content"))
    return message


def _loads_authors(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []
