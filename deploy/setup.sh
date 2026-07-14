#!/usr/bin/env bash
# One-shot server bootstrap for the Kazino production stack.
# Run as root on a fresh Ubuntu/Debian server, from inside the project directory:
#   bash deploy/setup.sh
set -euo pipefail

cd "$(dirname "$0")/.."   # repo root

echo "==> Kazino deploy bootstrap"

# --- 1. Docker ---------------------------------------------------------------
if ! command -v docker >/dev/null 2>&1; then
  echo "==> Installing Docker..."
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
else
  echo "==> Docker already installed: $(docker --version)"
fi

# --- 2. .env -----------------------------------------------------------------
if [ ! -f .env ]; then
  echo "==> Creating .env with generated secrets..."
  SECRET_KEY="$(openssl rand -hex 32)"
  POSTGRES_PASSWORD="$(openssl rand -hex 16)"
  cat > .env <<EOF
SECRET_KEY=${SECRET_KEY}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
SITE_ADDRESS=${SITE_ADDRESS:-titorovka.icu}
ACME_EMAIL=${ACME_EMAIL:-admin@titorovka.icu}
EOF
  echo "    -> wrote .env (edit SITE_ADDRESS / ACME_EMAIL if needed)"
else
  echo "==> .env already exists, leaving it untouched"
fi

# --- 3. Firewall (best effort) ----------------------------------------------
if command -v ufw >/dev/null 2>&1; then
  echo "==> Configuring ufw (allow SSH, HTTP, HTTPS)..."
  ufw allow OpenSSH  || ufw allow 22/tcp || true
  ufw allow 80/tcp   || true
  ufw allow 443/tcp  || true
  yes | ufw enable   || true
fi

# --- 4. Launch ---------------------------------------------------------------
echo "==> Building and starting containers..."
docker compose -f docker-compose.prod.yml up -d --build

echo
echo "==> Done. Check status with:"
echo "    docker compose -f docker-compose.prod.yml ps"
echo "    docker compose -f docker-compose.prod.yml logs -f web"
echo
echo "Once DNS for \$SITE_ADDRESS points here, HTTPS is issued automatically."
