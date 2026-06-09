import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.paper import Paper
from app.models.paper_note import PaperNote
from app.models.qa_record import QARecord
from app.models.workflow_log import WorkflowLog
from app.schemas.paper import PaperCreate
from app.services.dify_service import DifyAPIError, DifyService
from app.utils.file_utils import remove_local_file
from app.utils.text_utils import strip_think_blocks


FIELD_ALIASES = {
    "title": ["title", "标题", "论文标题"],
    "authors": ["authors", "作者"],
    "year": ["year", "年份", "发表年份"],
    "keywords": ["keywords", "关键词"],
    "research_problem": ["research_problem", "researchProblem", "研究问题", "问题"],
    "method": ["method", "methods", "research_method", "研究方法", "方法"],
    "dataset": ["dataset", "datasets", "数据集"],
    "metrics": ["metrics", "metric", "实验指标", "评价指标", "指标"],
    "contribution": ["contribution", "contributions", "innovation", "创新点", "贡献"],
    "limitation": ["limitation", "limitations", "不足", "研究不足", "局限性"],
    "conclusion": ["conclusion", "结论"],
}


def create_workflow_log(
    db: Session,
    workflow_type: str,
    paper_id: int | None,
    request_content: Any = None,
    response_content: Any = None,
    status: str = "success",
    error_message: str | None = None,
) -> WorkflowLog:
    log = WorkflowLog(
        workflow_type=workflow_type,
        paper_id=paper_id,
        request_content=_to_json_text(request_content),
        response_content=_to_json_text(response_content),
        status=status,
        error_message=error_message,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def create_basic_paper(db: Session, file_info: dict[str, str | int]) -> Paper:
    paper = Paper(
        title=str(file_info["file_name"]),
        file_name=str(file_info["file_name"]),
        file_path=str(file_info["file_path"]),
        file_size=int(file_info["file_size"]),
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return paper


async def upload_and_extract_paper(
    db: Session, file_info: dict[str, str | int]
) -> tuple[Paper, str | None]:
    paper = create_basic_paper(db, file_info)
    dify_service = DifyService()

    request_content = {"paper_file": file_info["file_name"]}
    try:
        workflow_result = await dify_service.run_extract_workflow(str(file_info["file_path"]))
    except DifyAPIError as exc:
        warning = f"Dify 调用失败，已保存基础论文信息：{exc}"
        create_workflow_log(
            db,
            workflow_type="extract",
            paper_id=paper.id,
            request_content=request_content,
            status="failed",
            error_message=warning,
        )
        return paper, warning

    parse_warning = None
    try:
        extracted_data = parse_extraction_content(workflow_result["content"])
        apply_extracted_data(paper, extracted_data)
        db.commit()
        db.refresh(paper)
    except JSONDecodeError as exc:
        parse_warning = f"Dify 返回内容无法解析 JSON：{exc}"
    except Exception as exc:
        parse_warning = f"抽取结果写入失败：{exc}"

    create_workflow_log(
        db,
        workflow_type="extract",
        paper_id=paper.id,
        request_content=request_content,
        response_content=workflow_result["raw_response"],
        status="success",
        error_message=parse_warning,
    )
    return paper, parse_warning


def list_papers(db: Session) -> list[Paper]:
    return list(db.scalars(select(Paper).order_by(Paper.create_time.desc())).all())


def get_paper_or_404(db: Session, paper_id: int) -> Paper:
    paper = db.get(Paper, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="paper_id 不存在")
    return paper


def ensure_file_exists(file_path: str) -> None:
    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail=f"本地文件不存在：{file_path}")


def delete_paper(db: Session, paper_id: int) -> None:
    paper = get_paper_or_404(db, paper_id)
    file_path = paper.file_path
    db.delete(paper)
    db.commit()
    remove_local_file(file_path)


async def ask_paper(db: Session, paper_id: int, question: str) -> QARecord:
    paper = get_paper_or_404(db, paper_id)
    ensure_file_exists(paper.file_path)
    dify_service = DifyService()
    request_content = {"paper_file": paper.file_name, "question": question}

    try:
        workflow_result = await dify_service.run_qa_workflow(paper.file_path, question)
    except DifyAPIError as exc:
        create_workflow_log(
            db,
            workflow_type="qa",
            paper_id=paper.id,
            request_content=request_content,
            status="failed",
            error_message=str(exc),
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    answer = strip_think_blocks(workflow_result["content"])
    record = QARecord(paper_id=paper.id, question=question, answer=answer)
    db.add(record)
    db.commit()
    db.refresh(record)

    create_workflow_log(
        db,
        workflow_type="qa",
        paper_id=paper.id,
        request_content=request_content,
        response_content=workflow_result["raw_response"],
        status="success",
    )
    return record


def list_qa_records(db: Session, paper_id: int) -> list[QARecord]:
    get_paper_or_404(db, paper_id)
    stmt = (
        select(QARecord)
        .where(QARecord.paper_id == paper_id)
        .order_by(QARecord.create_time.desc())
    )
    return list(db.scalars(stmt).all())


async def create_paper_note(
    db: Session, paper_id: int, note_style: str | None
) -> PaperNote:
    paper = get_paper_or_404(db, paper_id)
    ensure_file_exists(paper.file_path)
    dify_service = DifyService()
    request_content = {"paper_file": paper.file_name, "note_style": note_style}

    try:
        workflow_result = await dify_service.run_note_workflow(paper.file_path, note_style)
    except DifyAPIError as exc:
        create_workflow_log(
            db,
            workflow_type="note",
            paper_id=paper.id,
            request_content=request_content,
            status="failed",
            error_message=str(exc),
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    note = PaperNote(
        paper_id=paper.id,
        note_style=note_style,
        content=strip_think_blocks(workflow_result["content"]),
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    create_workflow_log(
        db,
        workflow_type="note",
        paper_id=paper.id,
        request_content=request_content,
        response_content=workflow_result["raw_response"],
        status="success",
    )
    return note


def list_notes(db: Session, paper_id: int) -> list[PaperNote]:
    get_paper_or_404(db, paper_id)
    stmt = (
        select(PaperNote)
        .where(PaperNote.paper_id == paper_id)
        .order_by(PaperNote.create_time.desc())
    )
    return list(db.scalars(stmt).all())


def parse_extraction_content(content: Any) -> dict[str, Any]:
    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        raise JSONDecodeError("content is not JSON text", str(content), 0)

    text = strip_think_blocks(content)
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except JSONDecodeError as original_exc:
        decoder = json.JSONDecoder()
        start_positions = [
            index for index, char in enumerate(text) if char in ("{", "[")
        ]
        for start in start_positions:
            try:
                parsed, _ = decoder.raw_decode(text[start:])
            except JSONDecodeError:
                continue

            if isinstance(parsed, list) and parsed:
                parsed = parsed[0]
            if isinstance(parsed, dict):
                return parsed

        raise original_exc


def apply_extracted_data(paper: Paper, data: dict[str, Any]) -> None:
    normalized = {}
    for field, aliases in FIELD_ALIASES.items():
        value = _pick_value(data, aliases)
        if value is not None:
            normalized[field] = _normalize_value(value)

    for field, value in normalized.items():
        setattr(paper, field, value)


def _pick_value(data: dict[str, Any], aliases: list[str]) -> Any:
    for key in aliases:
        if key in data:
            return data[key]
    return None


def _normalize_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _to_json_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)
