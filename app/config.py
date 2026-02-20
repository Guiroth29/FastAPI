"""
Configuration Module - Gerenciamento de Variáveis de Ambiente

O PROBLEMA:
- Código não pode ter secrets hardcoded (inseguro)
- Diferente config por ambiente (dev/prod/test)
- Padrão: usar variáveis de ambiente .env

A SOLUÇÃO: Pydantic Settings
- Ler variáveis de ambiente
- Validar tipos (int, str, etc)
- Valores padrão
- Aplicação acessa via settings object

FLUXO:
1. Arquivo .env (não versionado, local apenas):
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=books_user
   ...

2. Python lê .env com python-dotenv (automático)

3. Código:
   settings = get_settings()  # Ler .env
   db_url = settings.database_url  # Acessar
   
SEGURANÇA:
- .env nunca vai para Git (.gitignore)
- Production: variáveis definidas no servidor
- Desenvolvimento: .env local com dados fake

TIPOS VALIDADOS:
- str: string
- int: inteiro
- Literal: apenas valores específicos
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal
import os


class Settings(BaseSettings):
    """
    Application settings lidas de variáveis de ambiente (.env).
    
    Pydantic valida automaticamente.
    Se variável não existir: usa valor padrão.
    Se tipo errado: erro na inicialização.
    
    EXEMPLO .env:
    DB_HOST=localhost
    DB_PORT=5432
    DB_USER=books_user
    DB_PASSWORD=secret123
    DB_NAME=books_database
    API_ENVIRONMENT=development
    """
    
    # DATABASE CONFIGS
    db_host: str = "localhost"    # Host PostgreSQL (padrão: localhost)
    db_port: int = 5432          # Porta PostgreSQL (padrão: 5432)
    db_user: str = "books_user"  # Usuário PostgreSQL
    db_password: str = "books_password"  # Senha (NUNCA em código! Usar .env)
    db_name: str = "books_db"    # Nome do banco de dados
    
    # API CONFIGS
    api_host: str = "0.0.0.0"              # Host para aceitar requisições
    api_port: int = 8000                   # Porta da API
    api_environment: Literal["development", "production"] = "development"  # Modo
    
    @property
    def database_url(self) -> str:
        """
        Construir URL de conexão PostgreSQL.
        
        Formato: postgresql+psycopg2://user:pass@host:port/dbname
        
        PSYCOPG2: driver PostgreSQL para Python/SQLAlchemy
        
        Exemplo:
        postgresql+psycopg2://books_user:books_password@localhost:5432/books_db
        
        SQLAlchemy lê essa URL e conecta no banco.
        """
        # Allow overriding to use SQLite for tests or local runs by setting
        # the env var USE_SQLITE_FOR_TESTS=1. This makes running tests
        # locally or in CI without PostgreSQL easier.
        if os.getenv("USE_SQLITE_FOR_TESTS") == "1":
            # File-based SQLite DB (persists across connections)
            return f"sqlite:///./test.db"

        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    @property
    def async_database_url(self) -> str:
        """
        Build async database URL (usa asyncpg em vez de psycopg2).
        
        asyncpg: driver assíncrono PostgreSQL
        Usado se quisermos async total (futuro).
        
        Por enquanto: usamos psycopg2 (síncrono).
        """
        if os.getenv("USE_SQLITE_FOR_TESTS") == "1":
            return f"sqlite+aiosqlite:///./test.db"

        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    class Config:
        """
        Configuração de Pydantic Settings.
        
        env_file = ".env": Ler arquivo .env
        env_file_encoding: Encoding do arquivo (UTF-8)
        case_sensitive = False: VAR_NAME = var_name (aceita ambos)
        
        Exemplo: na classe temos db_host
         No .env pode ser: DB_HOST ou db_host (ambos funcionam)
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings instance (cached - singleton pattern).
    
    LRU_CACHE: cache da função
    - primeira vez: cria Settings(), ler .env
    - próximas vezes: retorna do cache (não relê .env)
    - por quê? .env não muda durante execução
    
    SINGLETON: apenas uma instância Settings na memória
    - todas funções usam mesmo objeto
    - thread-safe (LRU_CACHE gerencia)
    
    Uso:
    settings = get_settings()
    db_url = settings.database_url
    """
    return Settings()
