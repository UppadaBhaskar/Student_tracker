#!/usr/bin/env bash
# Enable HTTPS with Let's Encrypt (run after DNS points to this VPS)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo "Missing .env — run bash scripts/deploy.sh first"
  exit 1
fi

# shellcheck disable=SC1091
source .env

DOMAIN="${DOMAIN:-}"
EMAIL="${SSL_EMAIL:-$TRAINER_EMAIL}"

if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "yourdomain.com" ]; then
  echo "Set DOMAIN in .env to your real domain (e.g. fabricator.example.com)"
  exit 1
fi

COMPOSE="docker compose"
if ! docker compose version >/dev/null 2>&1; then
  COMPOSE="docker-compose"
fi

CERT_DIR="$ROOT_DIR/deploy/certbot"
mkdir -p "$CERT_DIR/conf" "$CERT_DIR/www"

echo "Stopping web container to free port 80..."
$COMPOSE stop web

docker run --rm \
  -p 80:80 \
  -v "$CERT_DIR/conf:/etc/letsencrypt" \
  -v "$CERT_DIR/www:/var/www/certbot" \
  certbot/certbot certonly --standalone \
  --preferred-challenges http \
  -d "$DOMAIN" \
  --email "$EMAIL" \
  --agree-tos \
  --non-interactive

cat > "$ROOT_DIR/deploy/nginx.ssl.conf" <<EOF
server {
    listen 80;
    server_name ${DOMAIN};
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://\$host\$request_uri; }
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    root /usr/share/nginx/html;
    index index.html;
    client_max_body_size 25M;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    location /api/ {
        proxy_pass http://backend:5000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

# Patch docker-compose override for SSL
cat > docker-compose.ssl.yml <<EOF
services:
  web:
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx.ssl.conf:/etc/nginx/conf.d/default.conf:ro
      - ./deploy/certbot/conf:/etc/letsencrypt:ro
EOF

# Update CORS to HTTPS origin
if grep -q "^CORS_ORIGINS=" .env; then
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|^CORS_ORIGINS=.*|CORS_ORIGINS=https://${DOMAIN}|" .env
  else
    sed -i "s|^CORS_ORIGINS=.*|CORS_ORIGINS=https://${DOMAIN}|" .env
  fi
fi

$COMPOSE -f docker-compose.yml -f docker-compose.ssl.yml up -d --build web
$COMPOSE restart backend

echo ""
echo "HTTPS enabled for https://${DOMAIN}"
echo "Renewal: add a cron job — certbot renew (see DEPLOY.md)"
