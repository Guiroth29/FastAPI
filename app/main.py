"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import check_db_connection, create_all_tables, init_db
from app.routers import books
from app.schemas import HealthCheckResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize database resources before serving requests."""
    logger.info("Starting application")
    init_db()
    create_all_tables()
    yield
    logger.info("Stopping application")


app = FastAPI(
    title="API de Gerenciamento de Livros",
    description="REST API com FastAPI e PostgreSQL",
    version="1.1.0",
    lifespan=lifespan,
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(books.router)


@app.get("/health", response_model=HealthCheckResponse)
def health_check() -> HealthCheckResponse:
    """Synchronous health check endpoint."""
    db_connected = check_db_connection()
    return HealthCheckResponse(
        status="healthy" if db_connected else "unhealthy",
        database="connected" if db_connected else "disconnected",
    )


@app.get("/healthz", response_model=HealthCheckResponse)
async def healthz() -> HealthCheckResponse:
    """Asynchronous health check endpoint."""
    return health_check()


@app.get("/ui", include_in_schema=False)
def ui() -> FileResponse:
    """Serve a simple visual interface for manual API exploration."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Interface não encontrada")
    return FileResponse(index_path)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API links."""
    return {
        "message": "Bem-vindo à API de Gerenciamento de Livros",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
        "ui": "/ui",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException) -> JSONResponse:
    """Return HTTP exceptions in a consistent JSON shape."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
