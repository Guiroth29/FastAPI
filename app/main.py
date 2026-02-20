"""
FastAPI Main Application

Este arquivo é o ponto de entrada (entrypoint) da API.
Aqui configuramos:
1. Lifespan (startup/shutdown)
2. Routers (endpoints)
3. Health checks
4. Exception handlers
5. Logging

O fluxo:
1. Python executa este arquivo
2. FastAPI app é criado com lifespan
3. Lifespan roda setup (init_db, create_all_tables)
4. App fica pronto para requisições
5. Requisições chegam → routers processam
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from app.database import init_db, create_all_tables, check_db_connection
from app.schemas import HealthCheckResponse
from app.dependencies import get_session
from app.routers import books

# Configurar logging para ver mensagens no terminal
# INFO: Mensagens normais
# WARNING: Possíveis problemas
# ERROR: Erros sérios
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan Context Manager - Gerencia startup (inicialização) e shutdown (encerramento).
    
    O QUE ACONTECE:
    1. Quando FastAPI inicia:
       - init_db() cria o engine SQLAlchemy com connection pool
       - create_all_tables() executa CREATE TABLE para modelos (se não existirem)
    2. Yield: app fica pronto para requisições
    3. Quando FastAPI encerra:
       - Cleanup (não temos aqui, mas poderia fechar conexões)
    
    POR QUÊ LIFESPAN?
    - Garante que banco está pronto antes de aceitar requisições
    - Evita erro "database not initialized"
    - Limpo e centralizado
    
    ALTERNATIVAS:
    - eventos @app.on_event("startup") (mais antigo)
    - FastAPI routers (menos apropriado)
    """
    logger.info("🚀 Starting up application...")
    
    # Inicializar banco: criar engine com connection pool
    init_db()
    
    # Criar tabelas se não existirem
    create_all_tables()
    
    logger.info("✅ Application startup complete - banco pronto!")
    
    # YIELD: Significa "estou pronto, rodar app agora"
    yield
    
    # Após app encerrar:
    logger.info("🛑 Shutting down application")


# Criar aplicação FastAPI com lifespan
# FastAPI é um framework moderno que:
# - Auto gera documentação (Swagger em /docs)
# - Validação automática com Pydantic
# - Async/await nativo
# - Type hints (melhor IDE support)
app = FastAPI(
    title="API de Gerenciamento de Livros",
    description="Uma API REST production-ready para gerenciar livros",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(books.router)


@app.get("/health", response_model=HealthCheckResponse)
def health_check() -> HealthCheckResponse:
    """
    Health check endpoint (SYNC endpoint).
    
    Returns application status and database connectivity.
    """
    db_connected = check_db_connection()
    
    return HealthCheckResponse(
        status="healthy",
        database="connected" if db_connected else "disconnected",
    )


@app.get("/healthz", response_model=HealthCheckResponse)
async def healthz() -> HealthCheckResponse:
    """
    Kubernetes-style health check endpoint (ASYNC endpoint).
    
    Returns application status and database connectivity.
    """
    db_connected = check_db_connection()
    
    return HealthCheckResponse(
        status="healthy",
        database="connected" if db_connected else "disconnected",
    )


@app.get("/")
async def root() -> dict:
    """
    Root endpoint with API information (ASYNC endpoint).
    """
    return {
        "message": "Bem-vindo à API de Gerenciamento de Livros",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
