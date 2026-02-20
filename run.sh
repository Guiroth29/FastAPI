#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

VENV_DIR="${VENV_DIR:-.venv}"
DB_MODE="auto"   # auto | postgres | sqlite
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

print_info() { echo -e "${BLUE}▶${NC} $1"; }
print_ok() { echo -e "${GREEN}✅${NC} $1"; }
print_warn() { echo -e "${YELLOW}⚠${NC}  $1"; }

usage() {
  cat <<'USAGE'
Uso: ./run.sh [opções]

Opções:
  --postgres   Força execução com PostgreSQL
  --sqlite     Força execução com SQLite local
  --host HOST  Host do uvicorn (default 0.0.0.0)
  --port PORT  Porta do uvicorn (default 8000)
  -h, --help   Exibe esta ajuda
USAGE
}

parse_args() {
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --postgres) DB_MODE="postgres" ;;
      --sqlite) DB_MODE="sqlite" ;;
      --host)
        shift
        HOST="$1"
        ;;
      --port)
        shift
        PORT="$1"
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "Opção inválida: $1"
        usage
        exit 1
        ;;
    esac
    shift
  done
}

has_compose() {
  if command -v docker-compose >/dev/null 2>&1; then
    return 0
  fi
  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

ensure_setup() {
  local setup_args=()
  if [ "$DB_MODE" = "postgres" ]; then
    setup_args+=(--postgres)
  elif [ "$DB_MODE" = "sqlite" ]; then
    setup_args+=(--sqlite)
  fi

  print_info "Executando setup pré-run"
  ./setup.sh "${setup_args[@]}"
  print_ok "Setup concluído"
}

decide_runtime_mode() {
  if [ "$DB_MODE" = "sqlite" ]; then
    export USE_SQLITE_FOR_TESTS=1
    return
  fi

  if [ "$DB_MODE" = "postgres" ]; then
    export USE_SQLITE_FOR_TESTS=0
    return
  fi

  # auto mode
  if has_compose; then
    export USE_SQLITE_FOR_TESTS=0
  else
    export USE_SQLITE_FOR_TESTS=1
    print_warn "Docker/Compose não disponível. API rodará com SQLite"
  fi
}

run_uvicorn() {
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"

  echo
  echo "API pronta para uso:"
  echo "- UI:      http://localhost:${PORT}/ui"
  echo "- Docs:    http://localhost:${PORT}/docs"
  echo "- Health:  http://localhost:${PORT}/health"
  echo

  exec uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
}

main() {
  parse_args "$@"
  ensure_setup
  decide_runtime_mode
  run_uvicorn
}

main "$@"
