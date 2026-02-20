#!/bin/bash

# ============================================================================
# 📦 SETUP INICIAL - Prepara tudo para rodar
# ============================================================================
#
# USO: ./setup.sh
#
# Este script:
#   1. Verifica Python
#   2. Verifica Docker
#   3. Cria venv
#   4. Instala dependências
#   5. Inicia PostgreSQL
#   6. Roda migrações
#   7. Carrega dados de exemplo
#
# Depois: ./run.sh (para iniciar a API)
#
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}▶ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ ERRO: $1${NC}"
    exit 1
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

# Header
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║               📦 SETUP INICIAL - COMEÇANDO... 📦              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# Verificar Python
# ============================================================================
print_step "1️⃣  Verificando Python..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado!"
fi

PYTHON_VERSION=$(python3 --version 2>&1)
print_success "$PYTHON_VERSION"

# ============================================================================
# Verificar Docker
# ============================================================================
print_step "2️⃣  Verificando Docker..."

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

# Instalar Docker se necessário
install_docker_if_needed

DOCKER_COMPOSE=$(get_docker_compose)
if [ $? -ne 0 ]; then
    print_error "❌ Docker Compose não encontrado!"
    echo ""
    echo "Opções:"
    echo "  1️⃣  Atualize Docker para versão >= 20.10"
    echo "  2️⃣  Ou instale docker-compose via pip: pip install docker-compose"
    echo ""
    exit 1
fi

print_success "Docker e Docker Compose ✓"

# ============================================================================
# Criar venv
# ============================================================================
print_step "3️⃣  Criando ambiente virtual..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Venv criado"
else
    print_success "Venv já existe"
fi

source venv/bin/activate

# ============================================================================
# Instalar dependências
# ============================================================================
print_step "4️⃣  Instalando dependências..."

# Fazer upgrade do pip
python -m pip install --quiet --upgrade pip setuptools wheel

# Instalar todas as dependências
python -m pip install -r requirements.txt --quiet 2>/dev/null

# Se falhar, tentar modo binário (para psycopg2)
if ! python -m pip install -r requirements.txt --quiet 2>/dev/null; then
    echo "Tentando instalação com binários pré-compilados..."
    python -m pip install --only-binary :all: fastapi sqlalchemy psycopg2-binary pydantic-settings python-dotenv alembic pytest --quiet 2>/dev/null
fi

# Verificar se pytest está disponível
if python -c "import pytest" 2>/dev/null; then
    PYTEST_STATUS="✓"
else
    python -m pip install pytest pytest-asyncio httpx --quiet 2>/dev/null
    PYTEST_STATUS="✓ (instalado neste momento)"
fi

print_success "Dependências instaladas ($PYTEST_STATUS)"

# ============================================================================
# Iniciar PostgreSQL
# ============================================================================
print_step "5️⃣  Iniciando PostgreSQL com Docker..."

$DOCKER_COMPOSE down -v 2>/dev/null || true
$DOCKER_COMPOSE up -d postgres

echo "Aguardando PostgreSQL iniciar..."
sleep 2

until $DOCKER_COMPOSE exec -T postgres pg_isready -U books_user &>/dev/null; do
    echo "  ⏳ Ainda aguardando..."
    sleep 2
done

print_success "PostgreSQL rodando"

# ============================================================================
# Rodar migrações
# ============================================================================
print_step "6️⃣  Aplicando migrações do banco..."

alembic upgrade head
print_success "Banco estruturado"

# ============================================================================
# Seed data
# ============================================================================
print_step "7️⃣  Carregando dados de exemplo..."

python -m scripts.seed_data
print_success "6 livros carregados"

# ============================================================================
# Tudo pronto!
# ============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✨ SETUP CONCLUÍDO! ✨                       ║${NC}"
echo -e "${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║  🚀 Próximo passo: ./run.sh                                   ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║  Isso vai iniciar a API em:                                  ║${NC}"
echo -e "${GREEN}║  http://localhost:8000/docs                                  ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Oferecer rodar agora
read -p "Quer rodar a API agora? (s/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    ./run.sh
fi
