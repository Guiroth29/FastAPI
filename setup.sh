#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

VENV_DIR="${VENV_DIR:-.venv}"
DB_MODE="auto"   # auto | postgres | sqlite
RUN_SEED=1

print_info() { echo -e "${BLUE}▶${NC} $1"; }
print_ok() { echo -e "${GREEN}✅${NC} $1"; }
print_warn() { echo -e "${YELLOW}⚠${NC}  $1"; }
print_err() { echo -e "${RED}❌${NC} $1"; }

usage() {
  cat <<'USAGE'
Uso: ./setup.sh [opções]

Opções:
  --postgres   Força setup com PostgreSQL (falha se Docker/Compose indisponível)
  --sqlite     Força setup com SQLite local
  --no-seed    Não executa seed de dados
  -h, --help   Exibe esta ajuda
USAGE
}

parse_args() {
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --postgres) DB_MODE="postgres" ;;
      --sqlite) DB_MODE="sqlite" ;;
      --no-seed) RUN_SEED=0 ;;
      -h|--help) usage; exit 0 ;;
      *) print_err "Opção inválida: $1"; usage; exit 1 ;;
    esac
    shift
  done
}

ensure_env_file() {
  if [ ! -f .env ]; then
    if [ -f .env.example ]; then
      cp .env.example .env
      print_warn "Arquivo .env não existia. Copiado de .env.example"
    else
      print_err "Nenhum .env ou .env.example encontrado"
      exit 1
    fi
  fi
}

load_env_vars() {
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
}

ensure_venv() {
  local sys_py_minor
  local venv_py_minor
  local req_hash
  local cached_hash=""
  local hash_file="$VENV_DIR/.requirements.hash"

  if ! command -v python3 >/dev/null 2>&1; then
    print_err "Python3 não encontrado no PATH"
    exit 1
  fi

  sys_py_minor="$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"

  if [ -x "$VENV_DIR/bin/python" ]; then
    if ! "$VENV_DIR/bin/python" -c 'import pydantic_core._pydantic_core' >/dev/null 2>&1; then
      print_warn "Ambiente virtual inválido detectado. Recriando $VENV_DIR"
      rm -rf "$VENV_DIR"
    else
      venv_py_minor="$("$VENV_DIR/bin/python" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
      if [ "$venv_py_minor" != "$sys_py_minor" ]; then
        print_warn "Versão Python do venv ($venv_py_minor) difere do sistema ($sys_py_minor). Recriando"
        rm -rf "$VENV_DIR"
      fi
    fi
  fi

  if [ ! -x "$VENV_DIR/bin/python" ]; then
    print_info "Criando ambiente virtual em $VENV_DIR"
    python3 -m venv "$VENV_DIR"
  fi

  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"

  if command -v sha256sum >/dev/null 2>&1; then
    req_hash="$(sha256sum requirements.txt | awk '{print $1}')"
  else
    req_hash="$(shasum -a 256 requirements.txt | awk '{print $1}')"
  fi

  if [ -f "$hash_file" ]; then
    cached_hash="$(cat "$hash_file")"
  fi

  if [ "$req_hash" != "$cached_hash" ] || ! python -c 'import fastapi,sqlalchemy,alembic,pytest' >/dev/null 2>&1; then
    print_info "Instalando dependências"
    python -m pip install --quiet --upgrade pip setuptools wheel
    python -m pip install --quiet -r requirements.txt
    echo "$req_hash" > "$hash_file"
  else
    print_ok "Dependências já atualizadas"
  fi

  print_ok "Ambiente Python pronto"
}

detect_compose() {
  if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
    return 0
  fi

  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
    return 0
  fi

  COMPOSE_CMD=()
  return 1
}

wait_for_postgres() {
  local retries=40
  local db_user="${DB_USER:-books_user}"
  local db_name="${DB_NAME:-books_db}"

  for _ in $(seq 1 "$retries"); do
    if "${COMPOSE_CMD[@]}" exec -T postgres pg_isready -U "$db_user" -d "$db_name" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

setup_postgres() {
  if ! detect_compose; then
    if [ "$DB_MODE" = "postgres" ]; then
      print_err "Docker/Compose não disponível para modo --postgres"
      exit 1
    fi

    DB_MODE="sqlite"
    print_warn "Docker/Compose indisponível. Fallback automático para SQLite"
    setup_sqlite
    return
  fi

  print_info "Subindo PostgreSQL via Docker Compose"
  "${COMPOSE_CMD[@]}" up -d postgres >/dev/null

  if ! wait_for_postgres; then
    if [ "$DB_MODE" = "postgres" ]; then
      print_err "PostgreSQL não ficou pronto a tempo"
      exit 1
    fi

    DB_MODE="sqlite"
    print_warn "PostgreSQL indisponível. Fallback automático para SQLite"
    setup_sqlite
    return
  fi

  export USE_SQLITE_FOR_TESTS=0

  print_info "Aplicando migrações"
  alembic upgrade head >/dev/null

  if [ "$RUN_SEED" -eq 1 ]; then
    print_info "Executando seed"
    python -m scripts.seed_data >/dev/null
  fi

  print_ok "PostgreSQL configurado"
}

setup_sqlite() {
  export USE_SQLITE_FOR_TESTS=1

  print_info "Configurando SQLite local"
  API_ENVIRONMENT=production python - <<'PY'
from app.database import create_all_tables, init_db
from scripts.seed_data import seed_books

init_db()
create_all_tables()
seed_books()
PY

  print_ok "SQLite configurado"
}

print_summary() {
  echo
  echo -e "${GREEN}Setup concluído.${NC}"
  if [ "$DB_MODE" = "sqlite" ]; then
    echo "Banco ativo: SQLite (USE_SQLITE_FOR_TESTS=1)"
    echo "Execute a API com: USE_SQLITE_FOR_TESTS=1 .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
  else
    echo "Banco ativo: PostgreSQL em Docker"
    echo "Execute a API com: .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
  fi
}

main() {
  parse_args "$@"
  ensure_env_file
  load_env_vars
  ensure_venv

  case "$DB_MODE" in
    sqlite) setup_sqlite ;;
    postgres|auto) setup_postgres ;;
    *) print_err "Modo de banco inválido: $DB_MODE"; exit 1 ;;
  esac

  print_summary
}

main "$@"
