from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import success_response
from app.schemas.paper import PaperResponse
from app.services.paper_service import (
    delete_paper,
    get_paper_or_404,
    list_papers,
    upload_and_extract_paper,
)
from app.utils.file_utils import save_upload_file


router = APIRouter(prefix="/api/papers", tags=["papers"])


@router.post("/upload")
async def upload_paper(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> dict:
    file_info = await save_upload_file(file)
    paper, warning = await upload_and_extract_paper(db, file_info)
    message = "上传成功，信息抽取已完成" if not warning else warning
    return success_response(
        data=PaperResponse.model_validate(paper).model_dump(mode="json"),
        message=message,
    )


@router.get("")
async def get_papers(db: Session = Depends(get_db)) -> dict:
    papers = [
        PaperResponse.model_validate(paper).model_dump(mode="json")
        for paper in list_papers(db)
    ]
    return success_response(data=papers)


@router.get("/{paper_id}")
async def get_paper(paper_id: int, db: Session = Depends(get_db)) -> dict:
    paper = get_paper_or_404(db, paper_id)
    return success_response(
        data=PaperResponse.model_validate(paper).model_dump(mode="json")
    )


@router.delete("/{paper_id}")
async def remove_paper(paper_id: int, db: Session = Depends(get_db)) -> dict:
    delete_paper(db, paper_id)
    return success_response(message="删除成功")
