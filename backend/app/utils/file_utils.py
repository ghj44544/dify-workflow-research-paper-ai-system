from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import HTTPException, UploadFile

from app.core.config import settings


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def validate_file_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        allowed = "、".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"文件格式不支持，仅允许：{allowed}")
    return suffix


async def save_upload_file(file: UploadFile) -> dict[str, str | int]:
    original_name = file.filename or "uploaded_file"
    validate_file_extension(original_name)

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = Path(original_name).name
    saved_name = f"{uuid4().hex}_{safe_name}"
    file_path = upload_dir / saved_name

    file_size = 0
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                await out_file.write(chunk)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"文件保存失败：{exc}") from exc
    finally:
        await file.close()

    return {
        "file_path": str(file_path),
        "file_name": original_name,
        "file_size": file_size,
    }


def remove_local_file(file_path: str) -> None:
    path = Path(file_path)
    if path.exists() and path.is_file():
        path.unlink()
