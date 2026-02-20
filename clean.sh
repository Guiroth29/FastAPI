#!/bin/bash

# ============================================================================
# 🧹 LIMPAR TUDO - Remove containers, volumes, venv, cache
# ============================================================================
#
# USO: ./clean.sh
#
# Este script remove:
#   - Containers Docker
#   - Volumes (dados do banco)
#   - Ambiente virtual Python
#   - Cache Python (__pycache__)
#
# Use quando tudo ficar bagunçado e você quer começar do zero!
#
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              🧹 LIMPANDO TUDO - COMEÇAR DO ZERO 🧹           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

print_done() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_header

# Função para detectar docker-compose correto (suporta novo "docker compose")
get_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    elif command -v docker &> /dev/null && docker compose version &> /dev/null 2>&1; then
        echo "docker compose"
    else
        return 1
    fi
}

# Parar Docker
print_step "Parando containers Docker..."
DOCKER_COMPOSE=$(get_docker_compose)
if [ $? -eq 0 ]; then
    $DOCKER_COMPOSE down -v 2>/dev/null || true
fi
print_done "Containers parados"

# Remover venv
print_step "Removendo ambiente virtual Python..."
rm -rf venv
print_done "Venv removido"

# Remover cache Python
print_step "Removendo cache Python..."
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
print_done "Cache removido"

# Remover compiled Python
print_step "Removendo arquivos compilados..."
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.so" -delete 2>/dev/null || true
print_done "Compilados removidos"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✨ LIMPEZA CONCLUÍDA! ✨                     ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║  Próximo passo: ./setup.sh    (ou ./run.sh para rodar)       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
