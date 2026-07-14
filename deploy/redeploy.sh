#!/usr/bin/env bash
# Rebuild & restart WITHOUT touching the database or .env.
# Use this for code/UI changes when the DB schema hasn't changed, so player
# balances are preserved. Run from the project dir:  bash deploy/redeploy.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."   # -> project root (/opt/kazino)

if [ ! -f .env ]; then
  echo "ERROR: .env not found. Run the full deploy (deploy.bat) first." >&2
  exit 1
fi

echo "==> Rebuilding and restarting (database and .env are preserved)"
docker compose -f docker-compose.prod.yml up -d --build

echo "==> Waiting for services..."
sleep 8
echo
echo "----- containers -----"
docker compose -f docker-compose.prod.yml ps
echo
echo "----- backend logs (last 15) -----"
docker compose -f docker-compose.prod.yml logs backend --tail 15 || true
echo
echo "==> Done. Reopen the Mini App in Telegram to see the changes."
