#!/usr/bin/env bash
# Deploy or update Fabricator on the VPS
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not found. Run: sudo bash scripts/setup-vps.sh"
  exit 1
fi

COMPOSE="docker compose"
if ! docker compose version >/dev/null 2>&1; then
  COMPOSE="docker-compose"
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"

  gen_secret() { openssl rand -hex 32; }

  if command -v openssl >/dev/null 2>&1; then
    SECRET_KEY="$(gen_secret)"
    JWT_SECRET_KEY="$(gen_secret)"
    DB_PASS="$(gen_secret)"
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" .env
      sed -i '' "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${JWT_SECRET_KEY}|" .env
      sed -i '' "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${DB_PASS}|" .env
    else
      sed -i "s|^SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" .env
      sed -i "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${JWT_SECRET_KEY}|" .env
      sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${DB_PASS}|" .env
    fi
    echo "Generated SECRET_KEY, JWT_SECRET_KEY, and POSTGRES_PASSWORD in .env"
  fi

  echo ""
  echo "IMPORTANT: Edit .env and set DOMAIN, TRAINER_EMAIL, TRAINER_PASSWORD, CORS_ORIGINS"
  echo "Then re-run: bash scripts/deploy.sh"
  exit 0
fi

# Require non-placeholder trainer password in production
if grep -q "CHANGE_ME_STRONG_TRAINER_PASSWORD" .env 2>/dev/null; then
  echo "Set TRAINER_PASSWORD in .env before deploying."
  exit 1
fi

echo "Building and starting Fabricator..."
$COMPOSE pull db 2>/dev/null || true
$COMPOSE up -d --build --remove-orphans

echo ""
echo "Waiting for services..."
sleep 5
$COMPOSE ps

echo ""
if curl -sf http://127.0.0.1/api/v1/health >/dev/null 2>&1; then
  echo "Health check OK — http://$(hostname -I | awk '{print $1}')/"
else
  echo "Stack started. Check logs: $COMPOSE logs -f"
fi

echo ""
echo "Useful commands:"
echo "  $COMPOSE logs -f          # live logs"
echo "  $COMPOSE restart backend  # restart API"
echo "  $COMPOSE down             # stop all"
echo "  bash scripts/enable-ssl.sh # HTTPS with Let's Encrypt"
