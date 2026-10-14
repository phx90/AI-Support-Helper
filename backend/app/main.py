import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.routes import router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging, logger
from app.database.base import engine

configure_logging()
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Intelligent RAG helpdesk and AI automation platform",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed", request_id=request_id, endpoint=request.url.path)
        raise
    response.headers["x-request-id"] = request_id
    logger.info(
        "request_completed",
        request_id=request_id,
        endpoint=request.url.path,
        status=response.status_code,
        latency_ms=round((time.perf_counter() - started) * 1000, 2),
    )
    return response


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message}}
    )


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "service": "backend"}
    except Exception:
        return JSONResponse(
            status_code=503, content={"status": "unavailable", "service": "backend"}
        )


app.include_router(router, prefix=settings.api_v1_prefix)
