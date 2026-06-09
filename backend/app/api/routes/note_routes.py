from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import success_response
from app.schemas.paper_note import NoteRequest, NoteResponse
from app.services.paper_service import create_paper_note, list_notes
from app.utils.text_utils import strip_think_blocks


router = APIRouter(prefix="/api/papers/{paper_id}", tags=["notes"])


@router.post("/note")
async def generate_note(
    paper_id: int, payload: NoteRequest, db: Session = Depends(get_db)
) -> dict:
    note = await create_paper_note(db, paper_id, payload.note_style)
    return success_response(
        data=_clean_note_response(NoteResponse.model_validate(note).model_dump(mode="json")),
        message="阅读笔记生成成功",
    )


@router.get("/notes")
async def get_notes(paper_id: int, db: Session = Depends(get_db)) -> dict:
    notes = [
        _clean_note_response(NoteResponse.model_validate(note).model_dump(mode="json"))
        for note in list_notes(db, paper_id)
    ]
    return success_response(data=notes)


def _clean_note_response(note: dict) -> dict:
    note["content"] = strip_think_blocks(note.get("content"))
    return note
