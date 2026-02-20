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
USE_SQLITE=0

print_header() {
  echo
  echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║                EXECUTANDO TESTES                    ║${NC}"
  echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
  echo
}

ensure_venv() {
  local sys_py_minor
  local venv_py_minor
  local req_hash
  local cached_hash=""
  local hash_file="$VENV_DIR/.requirements.hash"

  sys_py_minor="$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"

  if [ -x "$VENV_DIR/bin/python" ]; then
    if ! "$VENV_DIR/bin/python" -c "import sys; import pydantic_core._pydantic_core" >/dev/null 2>&1; then
      rm -rf "$VENV_DIR"
    else
      venv_py_minor="$("$VENV_DIR/bin/python" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
      if [ "$venv_py_minor" != "$sys_py_minor" ]; then
        rm -rf "$VENV_DIR"
      fi
    fi
  fi

  if [ ! -x "$VENV_DIR/bin/python" ]; then
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

  if [ "$req_hash" != "$cached_hash" ] || ! python -c "import fastapi,pytest,sqlalchemy" >/dev/null 2>&1; then
    python -m pip install --quiet --upgrade pip setuptools wheel
    python -m pip install --quiet -r requirements.txt
    echo "$req_hash" > "$hash_file"
  fi
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

start_postgres_if_possible() {
  if ! detect_compose; then
    USE_SQLITE=1
    echo -e "${YELLOW}Docker/Compose não disponível. Usando SQLite para testes.${NC}"
    return
  fi

  echo -e "${BLUE}Tentando subir PostgreSQL via Docker Compose...${NC}"
  if ! "${COMPOSE_CMD[@]}" up -d postgres >/dev/null 2>&1; then
    USE_SQLITE=1
    echo -e "${YELLOW}Não foi possível subir o container postgres. Usando SQLite.${NC}"
    return
  fi

  local ready=0
  for _ in $(seq 1 25); do
    if "${COMPOSE_CMD[@]}" exec -T postgres pg_isready -U books_user -d books_db >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 1
  done

  if [ "$ready" -eq 0 ]; then
    USE_SQLITE=1
    echo -e "${YELLOW}PostgreSQL não ficou pronto a tempo. Usando SQLite.${NC}"
    return
  fi

  unset USE_SQLITE_FOR_TESTS
  alembic upgrade head >/dev/null
  echo -e "${GREEN}PostgreSQL pronto e migrações aplicadas.${NC}"
}

resolve_pytest_args() {
  if [ "$#" -eq 0 ]; then
    PYTEST_ARGS=(tests/test_books.py -v --tb=short)
    return
  fi

  if [ "$1" = "books" ]; then
    shift
    PYTEST_ARGS=(tests/test_books.py "$@")
    return
  fi

  if [ "$1" = "--cov" ]; then
    shift
    PYTEST_ARGS=(tests/ -v --cov=app --cov-report=term-missing "$@")
    return
  fi

  PYTEST_ARGS=("$@")
}

run_tests() {
  export API_ENVIRONMENT=production

  if [ "$USE_SQLITE" -eq 1 ]; then
    export USE_SQLITE_FOR_TESTS=1
    rm -f test.db
    echo -e "${YELLOW}Rodando testes com SQLite (USE_SQLITE_FOR_TESTS=1).${NC}"
  else
    export USE_SQLITE_FOR_TESTS=0
    echo -e "${GREEN}Rodando testes com PostgreSQL.${NC}"
  fi

  if pytest "${PYTEST_ARGS[@]}"; then
    echo
    echo -e "${GREEN}✅ Todos os testes passaram.${NC}"
  else
    echo
    echo -e "${RED}❌ Alguns testes falharam.${NC}"
    exit 1
  fi
}

print_header
ensure_venv
start_postgres_if_possible
resolve_pytest_args "$@"
run_tests
