# API de Livros (FastAPI + PostgreSQL)

REST API para gerenciamento de livros com arquitetura em camadas, validação com Pydantic, migrações com Alembic e execução com Docker Compose.

## Versões usadas
- Python: `3.11+` (testado em `3.14`)
- FastAPI: `0.104.1`
- PostgreSQL: `15` (imagem `postgres:15-alpine`)

## Funcionalidades
- CRUD de livros (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`)
- Endpoints síncronos e assíncronos
- Paginação no formato exigido (`currentPage`, `pageSize`, `totalPages`, `totalRecords`, `data`)
- Health check com validação real do banco (`SELECT 1`)
- Seed de dados iniciais
- UI web simples em `/ui` para visualizar e criar livros

## Estrutura do projeto
```text
app/
  main.py                 # FastAPI app, lifespan, health, /ui
  config.py               # variáveis de ambiente
  database.py             # engine, pool e sessões
  models.py               # ORM (Book)
  schemas.py              # Pydantic schemas
  dependencies.py         # Depends(get_session)
  routers/books.py        # endpoints
  services/book_service.py# regras de negócio
  static/                 # frontend simples (/ui)

alembic/
  env.py
  versions/001_initial.py

scripts/seed_data.py
tests/test_books.py
```

## Fluxo único (setup + run + test)
Comandos principais:

```bash
./setup.sh
./run.sh
./test.sh
```

O `setup.sh` cria/repara `.venv`, instala dependências, aplica migrações e seed.

## Modos de banco
Padrão (`auto`): tenta PostgreSQL com Docker; se não conseguir, faz fallback para SQLite.

Forçar PostgreSQL:
```bash
./setup.sh --postgres
./run.sh --postgres
```

Forçar SQLite:
```bash
./setup.sh --sqlite
./run.sh --sqlite
```

Pular seed:
```bash
./setup.sh --no-seed
```

## Configuração de ambiente
Se `.env` não existir, o setup copia automaticamente de `.env.example`.

## URLs úteis
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`
- UI web: `http://localhost:8000/ui`

## Rodar testes
Recomendado:
```bash
./test.sh
```

Com cobertura:
```bash
./test.sh --cov
```

Opção direta com SQLite:
```bash
USE_SQLITE_FOR_TESTS=1 .venv/bin/pytest tests/test_books.py -v --tb=short
```

## Endpoints principais
- `GET /books/`
- `GET /books/search?q=...`
- `GET /books/{book_id}`
- `POST /books/`
- `PUT /books/{book_id}`
- `PATCH /books/{book_id}`
- `DELETE /books/{book_id}`
- `GET /health`
- `GET /healthz`

## Checklist de aderência aos requisitos da avaliação
- FastAPI com padrões REST: ✅
- Endpoints assíncronos e síncronos: ✅
- Engine SQLAlchemy com pool e reuso: ✅
- PostgreSQL em Docker Compose com porta, volume e healthcheck: ✅
- Configuração por variáveis de ambiente (`.env` + `.env.example`): ✅
- ORM com tabela principal (`books`): ✅
- Seed de dados documentado: ✅
- Paginação estruturada no formato pedido: ✅
- Endpoint de escrita com validação e status HTTP correto: ✅
- Health check de aplicação e banco: ✅
- Injeção de dependências (`Depends`): ✅
- Pydantic para request/response: ✅
- Testes com pytest em `tests/`: ✅
