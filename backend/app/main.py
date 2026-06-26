from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import chat, summary, upload
from app.config import settings
from app.exceptions import AppError
from app.schemas import ErrorResponse
from app.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    logger.info("Starting Compliance Copilot API (%s)", settings.environment)
    yield


app = FastAPI(
    title="Compliance Copilot API",
    description="Upload compliance PDFs, summarize them, and ask questions with RAG.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    payload = ErrorResponse(error=exc.message).model_dump()
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(HTTPException)
async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    payload = ErrorResponse(error=detail).model_dump()
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    message = exc.errors()[0].get("msg", "Invalid request") if exc.errors() else "Invalid request"
    payload = ErrorResponse(error="Validation failed", detail=message).model_dump()
    return JSONResponse(status_code=422, content=payload)


@app.exception_handler(Exception)
async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error")
    message = "An unexpected error occurred." if settings.is_production else str(exc)
    payload = ErrorResponse(error=message).model_dump()
    return JSONResponse(status_code=500, content=payload)


app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(summary.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
