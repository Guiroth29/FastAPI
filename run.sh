#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "🚀 Subindo ambiente Docker em background..."

docker compose down -v

# Start detached so the script can print status and exit cleanly
docker compose up --build -d

API_URL="http://localhost:8000"
HEALTH_URL="$API_URL/health"
DOCS_URL="$API_URL/docs"
REDOC_URL="$API_URL/redoc"

echo "Aguardando a API ficar disponível (timeout 60s)..."
RETRIES=60
SLEEP=1
count=0
until curl -sS "$HEALTH_URL" >/dev/null 2>&1; do
	count=$((count + 1))
	if [ "$count" -ge $RETRIES ]; then
		echo "⚠️  Timeout: a API não respondeu em $((RETRIES * SLEEP))s"
		echo " - Verifique containers: docker compose ps"
		echo " - Ver logs: docker compose logs -f"
		exit 1
	fi
	sleep $SLEEP
done

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  ✨ API INICIADA COM SUCESSO ✨               ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  🌐 Documentação Interativa: $DOCS_URL                     ║"
echo "║  📚 API Docs Alternativa:  $REDOC_URL                     ║"
echo "║  🏥 Health Check:           $HEALTH_URL                     ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  🚦 Para ver logs em tempo real:                               ║"
echo "║     docker compose logs -f                                     ║"
echo "║  🛑 Para parar tudo:                                           ║"
echo "║     docker compose down -v                                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

exit 0