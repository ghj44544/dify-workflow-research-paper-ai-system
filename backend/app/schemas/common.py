from typing import Any, Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T | None = None


def success_response(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {"code": 200, "message": message, "data": data}


def error_response(message: str, code: int = 500) -> dict[str, Any]:
    return {"code": code, "message": message, "data": None}
