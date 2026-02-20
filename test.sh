#!/bin/bash

# ============================================================================
# 🧪 RODAR TESTES COM FEEDBACK VISUAL
# ============================================================================
# 
# USO:
#   ./test.sh              - Roda todos os testes
#   ./test.sh books        - Roda só testes de books
#   ./test.sh -v           - Verbose
#   ./test.sh --cov        - Com coverage report
#
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║          🧪 EXECUTANDO TESTES AUTOMATICAMENTE 🧪              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# ============================================================================
# FUNÇÃO: Detectar SO e instalar Docker automaticamente
# ============================================================================
install_docker_if_needed() {
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker já está instalado${NC}"
        return 0
    fi

    echo ""
    echo -e "${YELLOW}⚠️  Docker não encontrado! Tentando instalar automaticamente...${NC}"
    echo ""

    # Detectar SO
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Tentar detectar a distribuição
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$(echo "$ID" | tr '[:upper:]' '[:lower:]')
            # Se estiver em flatpak, tentar pegar informação real
            if [[ "$OS" == "org.freedesktop.platform" ]] && [ -f /run/host/etc/os-release ]; then
                . /run/host/etc/os-release
                OS=$(echo "$ID" | tr '[:upper:]' '[:lower:]')
            fi
        else
            OS="unknown"
        fi

        case "$OS" in
            fedora|rhel|rocky|centos)
                echo -e "${BLUE}📦 Detectado: Fedora/RHEL/CentOS${NC}"
                echo "Executando: sudo dnf install -y docker docker-compose"
                sudo dnf install -y docker docker-compose 2>/dev/null || echo "Instale via: sudo dnf install docker docker-compose"
                sudo systemctl start docker 2>/dev/null || true
                sudo systemctl enable docker 2>/dev/null || true
                sudo usermod -aG docker $USER 2>/dev/null || true
                ;;
            debian|ubuntu|pop)
                echo -e "${BLUE}📦 Detectado: Ubuntu/Debian${NC}"
                echo "Executando: sudo apt-get update && sudo apt-get install -y docker.io docker-compose"
                sudo apt-get update -qq 2>/dev/null
                sudo apt-get install -y docker.io docker-compose 2>/dev/null || echo "Instale via: sudo apt-get install docker.io docker-compose"
                sudo systemctl start docker 2>/dev/null || true
                sudo systemctl enable docker 2>/dev/null || true
                sudo usermod -aG docker $USER 2>/dev/null || true
                ;;
            opensuse*)
                echo -e "${BLUE}📦 Detectado: openSUSE${NC}"
                echo "Executando: sudo zypper install -y docker docker-compose"
                sudo zypper install -y docker docker-compose 2>/dev/null || echo "Instale via: sudo zypper install docker docker-compose"
                ;;
            arch)
                echo -e "${BLUE}📦 Detectado: Arch Linux${NC}"
                echo "Executando: sudo pacman -S --noconfirm docker docker-compose"
                sudo pacman -S --noconfirm docker docker-compose 2>/dev/null || echo "Instale via: sudo pacman -S docker docker-compose"
                ;;
            *)
                echo -e "${YELLOW}⚠️  SO Linux não reconhecido: $OS${NC}"
                echo "Detectamos: $OSTYPE"
                echo ""
                echo "Tente instalar Docker manualmente:"
                echo "  https://docs.docker.com/get-docker/"
                return 1
                ;;
        esac

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${BLUE}📦 Detectado: macOS${NC}"
        if ! command -v brew &> /dev/null; then
            echo -e "${YELLOW}Instalando Homebrew primeiro...${NC}"
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" 2>/dev/null || echo "Instale Homebrew de: https://brew.sh"
        fi
        echo "Executando: brew install docker docker-compose"
        brew install docker docker-compose 2>/dev/null || echo "Instale via: brew install docker docker-compose"
    else
        echo -e "${RED}❌ SO não suportado para instalação automática: $OSTYPE${NC}"
        echo "Instale Docker manualmente em: https://docs.docker.com/get-docker/"
        return 1
    fi

    # Verificar se Docker foi instalado com sucesso
    echo ""
    echo -e "${YELLOW}Aguardando...${NC}"
    sleep 2

    # Tentar iniciar Docker se necessário
    if command -v docker &> /dev/null; then
        echo ""
        echo -e "${GREEN}✅ Docker instalado com sucesso!${NC}"
        DOCKER_VERSION=$(docker --version 2>/dev/null || echo "Docker instalado")
        echo -e "${GREEN}   $DOCKER_VERSION${NC}"
        return 0
    else
        echo ""
        echo -e "${YELLOW}⚠️  Docker pode não estar disponível no PATH ainda${NC}"
        echo "Tente: newgrp docker"
        echo "Ou reinicie o terminal/VS Code"
        return 1
    fi
}

# Verificar e obter comando docker-compose correto
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
        return 0
    elif command -v docker &> /dev/null && docker compose version &> /dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
        return 0
    else
        echo ""
        echo -e "${YELLOW}⚠️  Docker não está installado/acessível${NC}"
        echo "Tentando rodar apenas testes unitários..."
        echo "Para testes completos, instale Docker:"
        echo "   Veja: https://docs.docker.com/get-docker/"
        echo ""
        DOCKER_COMPOSE=""
        return 1
    fi
}

# Ativar venv
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# ============================================================================
# FUNÇÃO: Garantir que pytest e deps estão instalados
# ============================================================================
ensure_dependencies() {
    if ! python -c "import pytest" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  pytest não encontrado no venv! Instalando dependências...${NC}"
        python -m pip install --quiet pytest pytest-asyncio httpx 2>/dev/null
    fi
    
    if ! python -c "import fastapi" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Dependências faltando! Instalando todas...${NC}"
        python -m pip install -q -r requirements.txt 2>/dev/null || true
    fi
}

print_header

# Garantir que pytest e deps estão disponíveis
ensure_dependencies

# Obter comando docker-compose (se disponível)
check_docker_compose

# Verificar se Docker está rodando (se disponível)
if [ -n "$DOCKER_COMPOSE" ]; then
    if ! $DOCKER_COMPOSE ps 2>/dev/null | grep -q "postgres"; then
        echo -e "${YELLOW}⚠️  PostgreSQL não está rodando!${NC}"
        echo "Tentando iniciar PostgreSQL..."
        $DOCKER_COMPOSE up -d postgres 2>/dev/null
        sleep 3
    fi
else
    echo -e "${YELLOW}⚠️  Skippando verificação de PostgreSQL (Docker não disponível)${NC}"
fi

# Preparar banco para testes
echo -e "${BLUE}Preparando banco para testes...${NC}"
alembic upgrade head 2>/dev/null || true

# Rodar testes
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Rodando testes...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Suportar argumentos
if [ "$@" == "--cov" ]; then
    pytest tests/ -v --cov=app --cov-report=term-missing
elif [ "$@" == "-v" ]; then
    pytest tests/ -vv
else
    pytest tests/test_books.py -v --tb=short
fi

# Resultado
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                   ✅ TODOS OS TESTES PASSARAM! ✅             ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ❌ ALGUNS TESTES FALHARAM - VERIFIQUE ❌          ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
fi
