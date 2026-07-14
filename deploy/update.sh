#!/usr/bin/env bash
# Server-side updater. Run from the project dir:  bash deploy/update.sh <BOT_TOKEN>
# Writes .env (auto-generates secrets), resets ONLY the Postgres volume so the
# new schema is created (the Caddy cert volume is preserved), rebuilds and starts.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."   # -> project root (/opt/kazino)

TOKEN="${1:-}"
if [ -z "$TOKEN" ]; then
  echo "ERROR: no bot token. Usage: bash deploy/update.sh <BOT_TOKEN>" >&2
  exit 1
fi

echo "==> Writing .env (secrets auto-generated)"
cat > .env <<EOF
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
BOT_TOKEN=$TOKEN
SITE_ADDRESS=titorovka.icu
ACME_EMAIL=ferrum2312@gmail.com
EOF

echo "==> Stopping stack (keeping volumes)"
docker compose -f docker-compose.prod.yml down || true

echo "==> Resetting the database volume (Caddy certificate is preserved)"
docker volume rm kazino_pgdata 2>/dev/null || true

echo "==> Building and starting"
docker compose -f docker-compose.prod.yml up -d --build

echo "==> Waiting for the backend to come up..."
sleep 10
echo
echo "----- containers -----"
docker compose -f docker-compose.prod.yml ps
echo
echo "----- backend logs (last 20) -----"
docker compose -f docker-compose.prod.yml logs backend --tail 20 || true
echo
echo "----- API check -----"
curl -s https://titorovka.icu/api/catalog/banner || true
echo
echo
echo "==> Done. Open your Mini App in Telegram to test the login."
