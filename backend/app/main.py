from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    health_routes,
    note_routes,
    paper_routes,
    qa_routes,
    research_assistant,
)
from app.core.config import settings
from app.core.database import init_db
from app.schemas.common import error_response


app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    message = str(exc.detail) if exc.detail else "请求失败"
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=message, code=exc.status_code),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_response(message=f"请求参数错误：{exc.errors()}", code=422),
    )


@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=error_response(message=f"服务器内部错误：{exc}", code=500),
    )


app.include_router(health_routes.router)
app.include_router(paper_routes.router)
app.include_router(qa_routes.router)
app.include_router(note_routes.router)
app.include_router(research_assistant.router)
