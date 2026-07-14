#!/usr/bin/env bash
# Server-side full deploy. Run from the project dir:  bash deploy/update.sh <BOT_TOKEN>
# Creates .env with generated secrets ONLY if it doesn't exist (never overwrites,
# so a server-only CRYPTO_PAY_TOKEN survives), then rebuilds and starts.
# It does NOT wipe the database — new tables are added by create_all on startup.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."   # -> project root (/opt/kazino)

TOKEN="${1:-}"

if [ ! -f .env ]; then
  if [ -z "$TOKEN" ]; then
    echo "ERROR: no .env and no bot token. Usage: bash deploy/update.sh <BOT_TOKEN>" >&2
    exit 1
  fi
  echo "==> Creating .env (first run, secrets auto-generated)"
  cat > .env <<EOF
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
BOT_TOKEN=$TOKEN
SITE_ADDRESS=titorovka.icu
ACME_EMAIL=${ACME_EMAIL:-admin@titorovka.icu}
# Add CRYPTO_PAY_TOKEN=... here for Crypto Bot payments.
EOF
else
  echo "==> .env already exists — keeping it (secrets & CRYPTO_PAY_TOKEN preserved)"
fi

echo "==> Building and starting (database preserved)"
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
echo "==> Done."
