<<<<<<< HEAD
# FastAPI
=======
# 📖 API de Livros (Books Management API)

Uma **REST API production-ready** construída com **FastAPI** e **PostgreSQL** com boas práticas de backend profissional.

## ⚡ Quick Start (30 segundos)

```bash
cd /home/guiroth29/API_Test
./setup.sh    # Setup inicial (instala Docker automaticamente se necessário)
./run.sh      # Rodar API (http://localhost:8000)
```

Documentação interativa em: **http://localhost:8000/docs**

> ℹ️ **Instalação Automática:** Os scripts (`setup.sh`, `run.sh`, `test.sh`) agora verificam automaticamente se Docker está instalado e tentam instalá-lo se necessário. Se o Docker não puder ser instalado automaticamente (ex: limitações de permissão), será guiado para instalar manualmente.

---

## 🤖 Auto-Instalação de Dependências

Quando você executa `./setup.sh`, `./run.sh` ou `./test.sh`, os scripts fazem automaticamente:

### 1. **Verificação de Docker**
- ✅ Verifica se Docker está instalado
- ✅ Se não estiver, detecta o sistema operacional
- ✅ **Tenta instalar automaticamente** usando o gerenciador de pacotes correto

### 2. **Suporte a Múltiplos SOs**
Os scripts funcionam em:
- **Linux (Fedora/RHEL/CentOS):** `sudo dnf install docker docker-compose`
- **Linux (Ubuntu/Debian):** `sudo apt-get install docker.io docker-compose`
- **Linux (openSUSE):** `sudo zypper install docker docker-compose`
- **Linux (Arch):** `sudo pacman -S docker docker-compose`
- **macOS:** `brew install docker docker-compose`

### 3. **Tratamento de Erros**
Se a instalação automática falhar (ex: sem permissão sudo), o script:
- ✅ Informará claramente o motivo
- ✅ Mostrará o comando que deveria ser executado
- ✅ Fornecerá link para instalação manual

**Exemplo:**
```bash
$ ./test.sh -v

⚠️  Docker não encontrado! Tentando instalar automaticamente...

📦 Detectado: Fedora/RHEL/CentOS
Executando: sudo dnf install -y docker docker-compose

Aguardando...
✅ Docker instalado com sucesso!
   Docker version 27.0.0, build 1234567
```

---

## 📦 Instalação de Pré-requisitos

### 1. **Docker** (obrigatório)

**Linux (Fedora/RHEL):**
```bash
sudo dnf install docker docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
# Dar permissão sem sudo:
sudo usermod -aG docker $USER
newgrp docker
# Verificar:
docker --version && docker compose version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose -y
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
docker --version
```

**macOS:**
```bash
# Via Homebrew:
brew install docker docker-compose
# Ou via Docker Desktop: https://www.docker.com/products/docker-desktop
```

**Windows:**
- Download Docker Desktop: https://www.docker.com/products/docker-desktop
- Instale e reinicie o computador

### 2. **Python 3.11+** (obrigatório)

**Linux (Fedora):**
```bash
sudo dnf install python3.11 python3.11-venv -y
python3.11 --version
```

**Linux (Ubuntu):**
```bash
sudo apt-get install python3.11 python3.11-venv -y
python3.11 --version
```

**macOS:**
```bash
brew install python@3.11
python3.11 --version
```

### 3. **Git** (opcional, para clonar repo)

**Linux:**
```bash
sudo dnf install git  # Fedora
# ou
sudo apt-get install git  # Ubuntu
```

**macOS:**
```bash
brew install git
```

---

## ✅ Requisitos Atendidos

### Tecnologias & Stack
- ✅ **FastAPI** - Framework web moderno e rápido
- ✅ **PostgreSQL** - Banco de dados relacional
- ✅ **SQLAlchemy ORM** - Abstração do banco segura
- ✅ **Pydantic** - Validação automática de dados
- ✅ **Connection Pool** - 10 conexões reutilizáveis + 20 overflow
- ✅ **Alembic** - Migrações de schema versionadas
- ✅ **Docker & Docker Compose** - Containerização
- ✅ **Testes com pytest** - 18+ casos de teste
- ✅ **Health checks** - /health e /healthz endpoints
- ✅ **Documentação automática** - Swagger UI em /docs
- ✅ **Async + Sync** - Endpoints otimizados para I/O
- ✅ **Injeção de dependências** - FastAPI Depends()
- ✅ **Tratamento de erros** - Status codes HTTP apropriados
- ✅ **Paginação** - Listar livros com página e tamanho
- ✅ **Busca** - Full-text search em título e autor

---

## 📋 Tecnologias

| Componente | Versão | Uso |
|-----------|--------|-----|
| **Python** | 3.11+ | Runtime |
| **FastAPI** | 0.104 | Framework web |
| **PostgreSQL** | 15 | Banco de dados |
| **SQLAlchemy** | 2.0 | ORM |
| **Pydantic** | v2 | Validação |
| **Alembic** | 1.12 | Migrações |
| **pytest** | 7.4 | Testes |
| **Docker** | latest | Containerização |

---

## 🏗️ Arquitetura

### Estrutura em Camadas

```
┌─────────────────────────────────────────┐
│  API LAYER (HTTP Endpoints)             │ routers/books.py
├─────────────────────────────────────────┤
│  SERVICE LAYER (Lógica de Negócio)      │ services/book_service.py
├─────────────────────────────────────────┤
│  ORM LAYER (Abstração do Banco)         │ models.py + SQLAlchemy
├─────────────────────────────────────────┤
│  DATABASE LAYER (Persistência)          │ PostgreSQL
└─────────────────────────────────────────┘
```

**Por que?**
- Separação de responsabilidades
- Fácil testar cada camada
- Fácil trocar tecnologia (banco, validação, etc)

### Fluxo de Requisição (Exemplo: POST /books/)

```
1. Cliente envia JSON
   POST /books/ { "title": "...", "author": "...", "isbn": "..." }

2. FastAPI recebe + Pydantic valida
   ✅ title >= 1 caractere?
   ✅ author >= 1 caractere?
   ✅ isbn 10-20 caracteres?

3. Router injeta dependencies
   Depends(get_session) → Session do pool

4. BookService.create_book() executa
   ✅ ISBN já existe?
   ✅ Se não, INSERT no banco

5. ORM (SQLAlchemy) executa SQL
   INSERT INTO books (title, author, isbn, ...) VALUES (...)

6. Resposta retorna
   201 Created + JSON com livro criado + id (UUID) + timestamps
```

---

## 📁 Estrutura de Arquivos

### Código Fonte

```
app/
├── main.py              - Inicialização FastAPI, lifespan, health checks
├── config.py            - Variáveis de ambiente (.env)
├── database.py          - Engine, pool, SessionFactory
├── models.py            - ORM Book (tabela SQL em Python)
├── schemas.py           - Pydantic schemas (validação entrada/saída)
├── dependencies.py      - Injeção de dependência (Session)
├── routers/
│   └── books.py         - 7 endpoints CRUD + search + health
└── services/
    └── book_service.py  - Lógica de negócio, validações
```

### Banco de Dados

```
alembic/
├── env.py               - Configuração Alembic
├── script.py.mako       - Template para migrations
└── versions/
    └── 001_initial.py   - Criação tabela books com índices
```

### Testes & Scripts

```
tests/
└── test_books.py        - 18+ testes (CRUD, pagina, search, erros)

scripts/
└── seed_data.py         - Popular banco com 6 livros exemplo
```

### Automação

```
setup.sh                 - Setup inicial (Python, Docker, banco, deps)
run.sh                   - Rodar tudo (setup + migrations + seed + API)
test.sh                  - Rodar testes com pytest
clean.sh                 - Deletar venv, containers, caches
```

### Configuração

```
docker-compose.yml       - PostgreSQL + API
Dockerfile               - Imagem Python da API
requirements.txt         - Dependências Python
pyproject.toml          - Configuração Poetry
alembic.ini             - Configuração Alembic
.env                    - Variáveis de ambiente (local)
.env.example            - Template de .env
```

---

## 🚀 Como Rodar

### Opção 1: Automático com Scripts (Recomendado)

**Setup inicial (preparar ambiente):**
```bash
cd /home/guiroth29/API_Test
chmod +x *.sh          # Dar permissão nos scripts
./setup.sh             # 1️⃣ Setup: Python, Docker, banco
```

**Rodar API (dia a dia):**
```bash
./run.sh               # ▶️ Rodar tudo (setup + migrations + seed + API)
```

**Testar:**
```bash
./test.sh              # ✅ Rodar tests com pytest
./test.sh --cov        # Com cobertura (coverage)
```

**Limpar:**
```bash
./clean.sh             # 🧹 Deletar tudo (containers, venv, caches)
```

### Opção 2: Docker Compose (Simples)

```bash
cd /home/guiroth29/API_Test
docker-compose up --build
```

Aguarde ~30 segundos, depois:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Banco: localhost:5432

Parar:
```bash
docker-compose down      # Parar containers
docker-compose down -v   # Parar + deletar volumes (banco)
```

### Opção 3: Desenvolvimento Local (Manual)

**1. Python + Dependências**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Banco de Dados (Docker)**
```bash
docker-compose up postgres -d
sleep 5  # Aguardar banco ficar pronto
```

**3. Migrações + Seed**
```bash
alembic upgrade head              # Criar tabelas
python -m scripts.seed_data       # Popular com dados
```

**4. API**
```bash
uvicorn app.main:app --reload
```

**5. Parar banco**
```bash
docker-compose down
```

---

## 🔌 Endpoints da API

### Health Check

**GET /health** (Status do banco)
```bash
curl http://localhost:8000/health
```
Resposta:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**GET /healthz** (Compatibilidade Kubernetes)
```bash
curl http://localhost:8000/healthz
```

---

### Livros (CRUD)

**1. Listar Livros (com Paginação)** - ASYNC
```bash
GET /books/?page=1&page_size=10

curl "http://localhost:8000/books/?page=1&page_size=5"
```
Resposta:
```json
{
  "current_page": 1,
  "page_size": 5,
  "total_pages": 2,
  "total_records": 8,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Clean Code",
      "author": "Robert C. Martin",
      "isbn": "978-0132350884",
      "description": "....",
      "pages": 464,
      "published_year": 2008,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

**2. Buscar Livros (Texto)** - SYNC
```bash
GET /books/search?q=clean&page=1&page_size=10

curl "http://localhost:8000/books/search?q=clean"
```
Busca por título ou autor.

---

**3. Obter um Livro** - ASYNC
```bash
GET /books/{book_id}

curl "http://localhost:8000/books/550e8400-e29b-41d4-a716-446655440000"
```

---

**4. Criar Livro** - SYNC
```bash
POST /books/

curl -X POST http://localhost:8000/books/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Pragmatic Programmer",
    "author": "David Thomas",
    "isbn": "978-0201616224",
    "description": "Your Journey to Mastery",
    "pages": 352,
    "published_year": 1999
  }'
```
Status: **201 Created**

---

**5. Atualizar Livro (Completo)** - PUT - ASYNC
```bash
PUT /books/{book_id}

curl -X PUT http://localhost:8000/books/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code - 2nd Edition",
    "author": "Robert C. Martin",
    "pages": 500,
    "published_year": 2024
  }'
```

---

**6. Atualizar Livro (Parcial)** - PATCH - SYNC
```bash
PATCH /books/{book_id}

curl -X PATCH http://localhost:8000/books/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "pages": 500
  }'
```
Atualiza só os campos informados.

---

**7. Deletar Livro** - ASYNC
```bash
DELETE /books/{book_id}

curl -X DELETE http://localhost:8000/books/550e8400-e29b-41d4-a716-446655440000
```
Status: **204 No Content**

---

**Documentação Interativa:**
Abra http://localhost:8000/docs para testar todos endpoints no Swagger UI.

---

## 🧪 Testes

### ⚠️ Pré-requisito: Docker

Os testes precisam de **Docker/PostgreSQL** para rodar. Se Docker não estiver instalado, o script de teste mostrará uma mensagem clara com instruções de instalação.

Instale Docker antes de rodar testes. Veja seção "📦 Instalação de Pré-requisitos" acima.

---

### Rodar Testes

**Todos os testes:**
```bash
./test.sh
```

**Com cobertura (coverage):**
```bash
./test.sh --cov
```

**Modo verbose (detalhado):**
```bash
./test.sh -v
```

---

### O Que é Testado

**18+ Casos de Teste:**

1. ✅ **Criar livro** (happy path)
2. ✅ **Criar com ISBN duplicado** (erro 400)
3. ✅ **Listar livros** (todos + paginação)
4. ✅ **Paginação** (página 2, size 20)
5. ✅ **Obter livro por ID** (happy path)
6. ✅ **Obter livro inexistente** (erro 404)
7. ✅ **Atualizar livro** (PUT completo)
8. ✅ **Atualizar parcial** (PATCH)
9. ✅ **Deletar livro** (status 204)
10. ✅ **Buscar por texto** (search)
11. ✅ **Health check** (GET /health)
12. ✅ **Healthz endpoint** (GET /healthz)
13. ✅ **Root endpoint** (GET /)

**Padrão AAA:**
- Arrange: Preparar dados
- Act: Fazer ação
- Assert: Validar resultado

---

## 🔑 Conceitos Chave

### 1. **Async vs Sync**

| Endpoint | Tipo | Por quê |
|----------|------|--------|
| list_books | ASYNC | Lê do banco, pode esperar |
| search_books | SYNC | CPU-bound (busca texto) |
| get_book | ASYNC | Lê do banco |
| create_book | SYNC | Valida ISBN antes de INSERT |
| update_book | ASYNC | Lê + escreve |
| partial_update | SYNC | Validação antes de UPDATE |
| delete_book | ASYNC | Lê + deleta |

**Regra:**
- ASYNC: I/O-bound (banco, HTTP, file)
- SYNC: CPU-bound (validação, busca, calculo)

---

### 2. **Connection Pool**

**Configuração:**
```python
pool_size=10              # 10 conexões sempre abertas
max_overflow=20           # Até 20 extras se necessário
pool_pre_ping=True        # SELECT 1 antes de usar (health check)
pool_recycle=3600         # Reciclar conexão após 1h (timeout)
```

**Benefício:** Reutilizar conexões é 100x mais rápido que criar novas.

**Sem pool (ruim):**
```
Req1: nova conexão → query → fecha
Req2: nova conexão → query → fecha
Req3: nova conexão → query → fecha
      ↑ 3 conexões criadas! Lento!
```

**Com pool (bom):**
```
Pool: [conn1, conn2, ..., conn10]
Req1: pega conn1 → query → devolve
Req2: pega conn2 → query → devolve
Req3: pega conn3 → query → devolve
      ↑ Sem custo de criação! Rápido!
```

---

### 3. **Pydantic (Validação)**

Valida automaticamente quando cliente envia JSON:

```python
class BookCreate(BaseModel):
    title: str                    # Obrigatório, string
    author: str                   # Obrigatório, string
    isbn: str                     # Obrigatório
    # Validações:
    # - title: 1-255 caracteres
    # - author: 1-255 caracteres
    # - isbn: 10-20 caracteres (ISBN válido)
```

**Exemplos:**

❌ JSON inválido (title vazio):
```json
{ "title": "", "author": "...", "isbn": "..." }
```
→ Erro 422: `title` must have at least 1 character

✅ JSON válido:
```json
{ "title": "O Programador Pragmático", "author": "David Thomas", "isbn": "978-0201616224" }
```
→ Sucesso 201

---

### 4. **ORM (SQLAlchemy)**

**Sem ORM (SQL bruto - perigoso):**
```python
query = f"INSERT INTO books (title, author) VALUES ('{title}', '{author}')"
# SQL Injection! Se title = "x'); DROP TABLE books;--"
```

**Com ORM (seguro):**
```python
book = Book(title=title, author=author)
db.add(book)
db.commit()
# Parametrizado automaticamente! Seguro!
```

---

### 5. **Injeção de Dependência**

**Problema (sem injeção):**
```python
def create_book():
    db = SessionLocal()  # Cria
    # ...
    db.close()  # Fecha
    # E se esquecer de fechar? Connection leak!
```

**Solução (com injeção):**
```python
def create_book(db: Session = Depends(get_session)):
    # db é injetado
    # FastAPI fecha automaticamente!
```

```python
@contextmanager
def get_session():
    db = SessionLocal()  # Setup
    try:
        yield db         # Injetar
    finally:
        db.close()       # Cleanup garantido!
```

---

## 💡 Decisões de Design

### 1. **FastAPI em vez de Django**
- ✅ Async nativo (melhor performance)
- ✅ Auto-documentação (Swagger)
- ✅ Validação automática (Pydantic)
- ✅ Mais moderno (2023+)

### 2. **PostgreSQL em vez de SQLite**
- ✅ Production-ready
- ✅ Suporta concurrent requests
- ✅ Índices + performance
- ✅ Backup + replicação

### 3. **Connection Pool (10+20)**
- ✅ Otimização de performance
- ✅ Suporta picos de tráfico
- ✅ Evita "connection leak"

### 4. **Service Layer (Separação)**
- ✅ Lógica de negócio centralizada
- ✅ Fácil testar
- ✅ Reutilizável em múltiplos routers

### 5. **Alembic (Migrações)**
- ✅ Versionamento de schema
- ✅ Deploy seguro (sem perda de dados)
- ✅ Rollback possível

---

## 🚀 Possíveis Melhorias

### 1. **Autenticação & Autorização**
```python
# Adicionar JWT tokens
@app.post("/login")
def login(username: str, password: str):
    token = create_jwt_token(username)
    return {"access_token": token, "token_type": "bearer"}

# Proteger endpoints
@app.get("/books/")
def list_books(token: str = Depends(oauth2_scheme)):
    verify_token(token)
    ...
```

---

### 2. **Cache (Redis)**
```python
# Cachear lista de livros
@cache(ttl=300)  # 5 minutos
async def list_books(page: int = 1):
    ...
```

---

### 3. **Rate Limiting**
```python
# Limitar 100 requisições por minuto
@app.get("/books/")
@rate_limit("100/minute")
def list_books():
    ...
```

---

### 4. **Full-Text Search Avançado**
```python
# PostgreSQL tsvector para search otimizado
@app.get("/books/search")
def search_books(q: str):
    # Usar tsvector ao invés de LIKE
    # Muito mais rápido em dados grandes
```

---

### 5. **Paginação com Cursor**
```python
# Em vez de offset (lento em datasets grandes)
# Usar cursor-based pagination
@app.get("/books/")
def list_books(cursor: str = None, limit: int = 10):
    ...
```

---

### 6. **Soft Deletes**
```python
# Em vez de DELETE, apenas marcar como deletado
class Book(Base):
    deleted_at: DateTime = None

# Queries automaticamente excluem deleted_at IS NOT NULL
```

---

### 7. **Logs Estruturados**
```python
import structlog

logger = structlog.get_logger()
logger.info("book_created", book_id=book.id, user_id=user.id)
# Resultado: JSON estruturado, fácil buscar em logs
```

---

### 8. **Documentação OpenAPI Customizada**
```python
app = FastAPI(
    title="Books API",
    description="...",
    version="2.0.0",
    terms_of_service="...",
    contact={
        "name": "API Support",
        "url": "...",
        "email": "..."
    }
)
```

---

### 9. **CI/CD Pipeline**
```yaml
# GitHub Actions / GitLab CI
- Rodar testes automaticamente em cada push
- Fazer build da imagem Docker
- Deploy em staging/production
```

---

### 10. **Monitoramento & Observabilidade**
```python
# Prometheus + Grafana
from prometheus_client import Counter, Histogram

requests_total = Counter('requests_total', '...')
request_duration = Histogram('request_duration', '...')
```

---

## 📊 Planos Futuros

### Curto Prazo (2-4 semanas)
- [ ] Adicionar autenticação JWT
- [ ] Adicionar cache com Redis
- [ ] Adicionar rate limiting
- [ ] Documentação API em OpenAPI

### Médio Prazo (1-3 meses)
- [ ] Full-text search avançado
- [ ] Paginação com cursor
- [ ] Soft deletes
- [ ] Logs estruturados com structlog

### Longo Prazo (3+ meses)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Monitoramento (Prometheus + Grafana)
- [ ] Testes de carga (k6/JMeter)
- [ ] Documentação em PDF
- [ ] SDK em Python/JavaScript
- [ ] GraphQL endpoint

---

## 📚 Leitura Recomendada

### Para entender o código:
1. Leia comentários em **app/main.py** (20 min)
2. Leia comentários em **app/routers/books.py** (30 min)
3. Leia comentários em **app/services/book_service.py** (20 min)
4. Leia comentários em **app/models.py** (15 min)

### Para entender arquitetura:
1. Seção "🏗️ Arquitetura" acima
2. Seção "🔑 Conceitos Chave" acima
3. Arquivo **ARCHITECTURE.md** (se existir)

### Para aprender FastAPI:
- https://fastapi.tiangolo.com

### Para aprender SQLAlchemy:
- https://docs.sqlalchemy.org

### Para aprender Pydantic:
- https://docs.pydantic.dev

---

## 🐛 Troubleshooting

### Erro: "Docker não encontrado"

**O que causa:**
- Docker não está instalado no sistema
- Docker está instalado, mas não está no PATH

**Solução Automática:**
```bash
./setup.sh      # Tentará instalar Docker automaticamente
# ou
./run.sh        # Também tentará instalar Docker
# ou
./test.sh       # Também tentará instalar Docker
```

Os scripts detectarão seu SO e tentarão instalar Docker usando o gerenciador de pacotes apropriado.

**Solução Manual (se automática falhar):**
```bash
# Verificar se Docker está instalado
docker --version

# Se não tiver Docker, instale:
# Linux (Fedora):
sudo dnf install -y docker docker-compose
sudo systemctl start docker

# Linux (Ubuntu):
sudo apt-get install -y docker.io docker-compose
sudo systemctl start docker

# macOS:
brew install docker docker-compose

# Windows:
# Download em: https://www.docker.com/products/docker-desktop
```

Se ainda tiver erro de permissão, rode:
```bash
sudo usermod -aG docker $USER
newgrp docker      # Ativar novo grupo
docker --version   # Verificar
```

---

### Erro: "docker-compose: comando não encontrado"
**Solução:**
```bash
# Verificar se Docker está instalado
docker --version

# Se não tiver Docker, instale:
# Veja seção "📦 Instalação de Pré-requisitos" acima

# Se Docker está instalado mas compose não, tente:
docker compose version  # Versão nova

# Se nenhum funcionar, instale docker-compose:
sudo pip install docker-compose
```

---

### Erro: "Connection refused" ao conectar no banco
**Solução:**
```bash
# Verificar se Docker está rodando
docker ps

# Se não vir postgres container:
docker-compose up postgres -d
sleep 5
```

---

### Erro: "Database does not exist"
**Solução:**
```bash
# Rodar migrations
alembic upgrade head

# Seeder dados
python -m scripts.seed_data
```

---

### Erro: "Address already in use" (porta 8000)
**Solução:**
```bash
# Encontrar processo na porta
lsof -i :8000

# Matar processo
kill -9 <PID>

# Ou usar porta diferente
uvicorn app.main:app --port 8001
```

---

### Erro: "ModuleNotFoundError: No module named 'app'"
**Solução:**
```bash
# Estar na pasta correta
cd /home/guiroth29/API_Test

# Ativar venv
source venv/bin/activate

# Rodar alembic
cd alembic
alembic upgrade head
```

---

## 📞 Contato / Dúvidas

Se tiver dúvidas:
1. Leia os comentários no código
2. Veja exemplos com curl acima
3. Teste no Swagger UI (http://localhost:8000/docs)
4. Rode os testes: `./test.sh`

---

## 📝 Licença

MIT - Sinta-se livre para usar em projetos pessoais e comerciais.

---

**Última atualização:** 19 de fevereiro de 2026
>>>>>>> e3bc2c3 (Initial commit)
