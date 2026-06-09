from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import success_response
from app.schemas.qa_record import AskRequest, AskResponse, QARecordResponse
from app.services.paper_service import ask_paper, list_qa_records
from app.utils.text_utils import strip_think_blocks


router = APIRouter(prefix="/api/papers/{paper_id}", tags=["qa"])


@router.post("/ask")
async def ask_question(
    paper_id: int, payload: AskRequest, db: Session = Depends(get_db)
) -> dict:
    record = await ask_paper(db, paper_id, payload.question)
    data = AskResponse(
        paper_id=record.paper_id,
        question=record.question,
        answer=record.answer,
    ).model_dump()
    return success_response(data=data, message="问答成功")


@router.get("/qa-records")
async def get_qa_records(paper_id: int, db: Session = Depends(get_db)) -> dict:
    records = [
        _clean_record_response(QARecordResponse.model_validate(record).model_dump(mode="json"))
        for record in list_qa_records(db, paper_id)
    ]
    return success_response(data=records)


def _clean_record_response(record: dict) -> dict:
    record["answer"] = strip_think_blocks(record.get("answer"))
    return record
