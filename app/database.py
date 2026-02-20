"""
Database Configuration && Connection Management (Gerenciamento de Conexões)

CONNECTION POOL: problema que este arquivo resolve.

O PROBLEMA:
- Cada requisição precisa de conexão com banco
- Criar conexão é caro (handshake, autenticação, recursos)
- Se criar nova conexão por requisição: app lento
- Se reusar sem limite: risco de esgotamento de memory

A SOLUÇÃO: Connection Pool
- Manter X conexões abertas (pool_size=10)
- Quando requisição chega: usar conexão do pool
- Quando termina: devolver conexão ao pool (não fechar)
- Próxima requisição reutiliza sem overhead

POOL_SIZE vs MAX_OVERFLOW:
- pool_size=10: 10 conexões sempre abertas
- max_overflow=20: Se todas 10 em uso, abrir até 20 extras
- Total de conexões: até 30

EXEMPLO:
10 requisições simultâneas: usa 10 conexões do pool
15 requisições simultâneas: usa 10+5 (overflow)
31 requisições simultâneas: last deve esperar (queued)

SETTINGS deste POOL:
- pool_pre_ping=True: Antes de usar, fazer SELECT 1 (pingar banco)
  Por quê? Detectar conexões mortas/expiradas
- pool_recycle=3600: Fechar conexão após 1h (evitar timeout do firewall)

FLUXO:
1. Cliente faz requisição
2. get_session() injeta Session do pool
3. Session abre conexão do pool
4. Fazer queries
5. Fim da requisição
6. Session devolve conexão ao pool (autoclose)

CODE:
"""
from sqlalchemy import create_engine, Engine, select, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

# Base: classe que todos ORM models herdam
# Registra modelos para criação de tabelas
Base = declarative_base()

# Global variables (modificados por init_db())
engine: Engine | None = None
SessionLocal = None


def init_db() -> None:
    """
    Inicializar engine e session factory.
    
    Executado na inicialização da aplicação (via lifespan).
    
    CONNECTION POOL SETUP:
    - pool_size=10: Manter 10 conexões abertas
    - max_overflow=20: Até 20 conexões extra se necessário
    - pool_pre_ping=True: Verificar conexão antes de usar
    - pool_recycle=3600: Reciclar conexão após 1 hora
    
    SESSION SETUP:
    - autocommit=False: Transações manuais (db.commit())
    - autoflush=False: Não fazer INSERT/UPDATE até commit
    - expire_on_commit=False: Objetos permanecem após commit
    """
    global engine, SessionLocal
    
    settings = get_settings()
    
    # Create engine com connection pool
    # engine = máquina que cria conexões e queries
    engine = create_engine(
        settings.database_url,  # postgresql://user:pass@localhost/dbname
        echo=settings.api_environment == "development",  # Print SQL se dev
        # CONNECTION POOL SETTINGS:
        pool_size=10,           # 10 conexões base
        max_overflow=20,        # Até 20 extras
        pool_pre_ping=True,     # SELECT 1 antes de usar (health check)
        pool_recycle=3600,      # Fechar após 1 hora (evitar timeout)
    )
    
    # SessionLocal = fábrica de sessions
    # Cada request chama SessionLocal() para pegar session nova
    SessionLocal = sessionmaker(
        autocommit=False,               # Commit manual
        autoflush=False,                # Flush manual
        bind=engine,                    # Usar engine acima
        expire_on_commit=False,         # Objetos vivos após commit
    )
    
    logger.info("🛢️ Database engine initialized with pool")


def get_engine() -> Engine:
    """
    Get the database engine.
    Usado internamente por get_session().
    Se não inicializado: inicializar agora.
    """
    if engine is None:
        init_db()
    return engine


def get_session() -> Session:
    global SessionLocal

    if SessionLocal is None:
        init_db()

    db = SessionLocal()  # ✅ CORRETO
    return db


def create_all_tables() -> None:
    """Create all tables in the database."""
    engine_instance = get_engine()
    Base.metadata.create_all(bind=engine_instance)
    logger.info("Database tables created")


def check_db_connection() -> bool:
    """Check if database is accessible."""
    try:
        session = get_session()
        session.execute(text("SELECT 1"))
        session.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def drop_all_tables() -> None:
    """Drop all tables from the database (useful for testing)."""
    engine_instance = get_engine()
    Base.metadata.drop_all(bind=engine_instance)
    logger.info("Database tables dropped")
