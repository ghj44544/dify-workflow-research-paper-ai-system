from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import success_response


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    return success_response(data={"app": settings.app_name}, message="ok")
