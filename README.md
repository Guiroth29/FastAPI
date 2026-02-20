# API de Livros (FastAPI + PostgreSQL)

Projeto de backend com FastAPI para cadastro e consulta de livros, pensado para avaliação técnica e para estudo de boas práticas de API em produção.

## Para quem este README foi escrito
Este guia foi feito para dois públicos:
- quem nunca trabalhou com API e quer rodar/testar o projeto com segurança
- quem já programa e quer entender arquitetura, decisões técnicas e próximos passos

## O que é uma API (explicação rápida)
API (Application Programming Interface) é uma forma de dois sistemas conversarem.

Exemplo prático deste projeto:
- um cliente (browser, app, curl, Postman) envia uma requisição HTTP
- a API recebe, valida dados, consulta banco e devolve resposta JSON

Neste projeto, a API gerencia livros (`books`) com operações de criar, listar, buscar, atualizar e deletar.

## O que este projeto entrega hoje
- CRUD completo de livros
- endpoints síncronos e assíncronos
- paginação no formato exigido (`currentPage`, `pageSize`, `totalPages`, `totalRecords`, `data`)
- validação de entrada com Pydantic
- verificação de saúde da aplicação e do banco (`/health`, `/healthz`)
- seed de dados iniciais
- frontend simples para uso visual em `/ui`
- suporte a PostgreSQL (Docker) com fallback para SQLite
- scripts de automação para setup, execução e testes

## Tecnologias usadas e por quê
| Tecnologia | Papel no projeto | Por que foi escolhida | Alternativas comuns |
|---|---|---|---|
| FastAPI | Framework web | Muito rápido para APIs, tipagem forte e docs automáticas | Flask, Django REST |
| SQLAlchemy | ORM/engine SQL | Abstrai SQL com controle fino e padrão de mercado | SQLModel, Tortoise |
| PostgreSQL | Banco principal | Robusto para produção, índices e transações maduras | MySQL, MariaDB |
| SQLite | Banco fallback local | Zero setup para rodar rápido sem Docker | - |
| Alembic | Migrações de schema | Versiona mudanças do banco com histórico | Scripts SQL manuais |
| Pydantic | Validação/serialização | Mensagens de erro claras e integração nativa com FastAPI | Marshmallow |
| Docker Compose | Infra local | Reprodutibilidade fácil do banco | Instalação manual local |
| Pytest | Testes automatizados | Simples, poderoso e padrão de fato no Python | unittest |

## Arquitetura e justificativa
A aplicação usa arquitetura em camadas para separar responsabilidades e facilitar manutenção.

### Camadas
- `app/routers/`: recebe HTTP, valida parâmetros de rota/query/body e define status HTTP
- `app/services/`: regras de negócio (ex.: ISBN único) e coordenação de operações
- `app/models.py`: mapeamento ORM da tabela `books`
- `app/database.py`: engine, pool de conexões e sessão de banco
- `app/schemas.py`: contratos de entrada/saída (Pydantic)
- `app/dependencies.py`: injeção de sessão via `Depends(get_session)`
- `app/main.py`: inicialização da API, lifespan, health checks, frontend `/ui`

### Por que essa arquitetura
- reduz acoplamento (regra de negócio não fica misturada com HTTP)
- facilita testes unitários e de integração
- simplifica evolução futura (troca de banco, auth, cache, etc.)
- melhora legibilidade para onboarding de iniciantes

## Fluxo de uma requisição (exemplo)
Exemplo de `POST /books/`:
1. cliente envia JSON do livro
2. FastAPI + Pydantic validam campos
3. router chama `BookService`
4. service valida regra de negócio (ISBN duplicado)
5. SQLAlchemy persiste no banco
6. API retorna `201` com JSON padronizado

## Estrutura do projeto
```text
app/
  main.py
  config.py
  database.py
  models.py
  schemas.py
  dependencies.py
  routers/books.py
  services/book_service.py
  static/

alembic/
  env.py
  versions/001_initial.py

scripts/seed_data.py
tests/test_books.py
setup.sh
run.sh
test.sh
docker-compose.yml
```

## Pré-requisitos
Obrigatório:
- Python 3.11+ (scripts preparados para 3.14)

Opcional (recomendado):
- Docker + Docker Compose (para PostgreSQL local)

Observação:
- sem Docker, os scripts fazem fallback para SQLite automaticamente

## Começando do zero (passo a passo iniciante)
No terminal, dentro da pasta do projeto:

```bash
cd /home/guiroth29/API_Test
./setup.sh
./run.sh
```

Agora abra no navegador:
- Interface visual: `http://localhost:8000/ui`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

Para testar automaticamente:
```bash
./test.sh
```

## Modos de banco (PostgreSQL ou SQLite)
Padrão (`auto`): tenta PostgreSQL e cai para SQLite se necessário.

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

## Referência de comandos
### `setup.sh`
Objetivo: preparar ambiente (venv, dependências, banco, migração, seed).

Comandos:
```bash
./setup.sh
./setup.sh --postgres
./setup.sh --sqlite
./setup.sh --no-seed
./setup.sh --help
```

### `run.sh`
Objetivo: garantir setup e subir API.

Comandos:
```bash
./run.sh
./run.sh --postgres
./run.sh --sqlite
./run.sh --host 127.0.0.1 --port 8080
./run.sh --help
```

### `test.sh`
Objetivo: executar testes com auto fallback PostgreSQL -> SQLite.

Comandos:
```bash
./test.sh
./test.sh books
./test.sh --cov
./test.sh -k health
```

## Variáveis de ambiente (`.env`)
Se não existir `.env`, o `setup.sh` copia automaticamente de `.env.example`.

Campos principais:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `API_HOST`, `API_PORT`, `API_ENVIRONMENT`
- `USE_SQLITE_FOR_TESTS` (normalmente controlada pelos scripts)

## Como usar a interface (`/ui`)
A interface foi criada para facilitar uso sem precisar Postman.

Você consegue:
- checar status da API e banco
- criar novos livros
- buscar por título/autor
- navegar com paginação

## Endpoints disponíveis
| Método | Endpoint | Tipo | Descrição | Status principais |
|---|---|---|---|---|
| GET | `/` | assíncrono | links úteis da API | 200 |
| GET | `/health` | síncrono | saúde da API e conexão com banco | 200 |
| GET | `/healthz` | assíncrono | health alternativo (estilo Kubernetes) | 200 |
| GET | `/books/` | assíncrono | lista paginada de livros | 200 |
| GET | `/books/search` | síncrono | busca por título/autor (`q`) | 200 |
| GET | `/books/{book_id}` | assíncrono | detalhe de um livro | 200, 404 |
| POST | `/books/` | síncrono | cria livro | 201, 400, 422 |
| PUT | `/books/{book_id}` | assíncrono | atualiza livro | 200, 400, 404, 422 |
| PATCH | `/books/{book_id}` | síncrono | atualização parcial | 200, 400, 404, 422 |
| DELETE | `/books/{book_id}` | assíncrono | remove livro | 204, 404 |

## Exemplos de uso via curl
### Criar livro
```bash
curl -X POST http://localhost:8000/books/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "description": "A Handbook of Agile Software Craftsmanship",
    "pages": 464,
    "published_year": 2008
  }'
```

### Listar livros paginados
```bash
curl "http://localhost:8000/books/?page=1&page_size=10"
```

Exemplo de resposta:
```json
{
  "currentPage": 1,
  "pageSize": 10,
  "totalPages": 2,
  "totalRecords": 15,
  "data": [
    {
      "id": "uuid",
      "title": "Clean Code",
      "author": "Robert C. Martin",
      "isbn": "978-0132350884",
      "createdAt": "2026-02-20T12:00:00Z",
      "updatedAt": "2026-02-20T12:00:00Z"
    }
  ]
}
```

### Health check
```bash
curl http://localhost:8000/health
```

Resposta típica:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Testes automatizados
Arquivos de teste: `tests/test_books.py`.

Cobertura atual de comportamento:
- criação de livro
- bloqueio de ISBN duplicado
- paginação no formato exigido
- busca e leitura por ID
- atualização e deleção
- health e endpoint raiz

## Qualidade e boas práticas aplicadas
- type hints nas funções
- resposta e validação via schemas Pydantic
- status HTTP apropriados
- injeção de dependência para sessão de banco
- connection pool configurado para PostgreSQL
- migração versionada com Alembic

## Possíveis melhorias futuras
- autenticação/autorização (JWT e perfis de acesso)
- testes de carga e métricas (Prometheus/Grafana)
- cache (Redis) para endpoints de leitura
- logs estruturados e rastreabilidade (request-id)
- CI/CD com pipeline de lint + testes + build
- paginação por cursor para volume alto
- suporte a múltiplas entidades (usuários, empréstimos, categorias)
- tratamento global de erros com códigos de domínio
- documentação OpenAPI enriquecida com exemplos adicionais

## Troubleshooting rápido
### `psycopg.errors.UndefinedTable: relation "books" does not exist`
Esse caso pode ocorrer quando o estado do Alembic (`alembic_version`) está marcado, mas a tabela não existe fisicamente no banco.

O projeto já tem proteção automática para isso em `setup.sh` e no seed script.

Se você pegar esse erro em um ambiente antigo, execute:
```bash
docker compose down -v
./setup.sh --postgres
./run.sh --postgres
```

### `ModuleNotFoundError: No module named 'app'` no Alembic
Já corrigido em `alembic/env.py` e `alembic.ini`.

### Docker indisponível
Use modo SQLite:
```bash
./setup.sh --sqlite
./run.sh --sqlite
./test.sh
```

### Porta 8000 ocupada
```bash
./run.sh --port 8080
```

### Limpar banco SQLite local
```bash
rm -f test.db
```

## Status em relação aos requisitos da avaliação
- FastAPI + REST: ✅
- endpoints sync e async: ✅
- banco com engine e pool: ✅
- PostgreSQL com Docker Compose + volume + healthcheck: ✅
- configuração por ambiente (`.env` + `.env.example`): ✅
- ORM com tabela de domínio: ✅
- seed inicial documentado: ✅
- paginação no formato pedido: ✅
- endpoint de escrita com validação e status correto: ✅
- health check com teste de conectividade: ✅
- injeção de dependências: ✅
- Pydantic request/response: ✅
- testes com pytest: ✅
