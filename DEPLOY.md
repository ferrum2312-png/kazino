# 🚀 Deploying Kazino to a server

This deploys the whole stack (Postgres + Redis + FastAPI + built React app behind
Caddy) with automatic HTTPS. **You run these steps yourself** — either in an SSH
terminal or in your server provider's web console.

---

## 0. Before you start — security first

You pasted the server's **root password into a chat**, so treat it as leaked:

```bash
# on the server, as root:
passwd            # set a new root password
```

Then switch to key-based login (see step 6). Password auth over SSH for root is
the #1 way boxes get taken over by bots.

Also verify the domain actually points at this server. From your **own** machine
(not a VPN):

```bash
nslookup titorovka.icu      # the A record must equal the server's public IP
```

> When I resolved `titorovka.icu` it returned `198.18.0.96` (a reserved/benchmark
> address) — **not** the `2.26.125.173` you mentioned. HTTPS will only work once
> the domain's public A record points at the real server IP. Fix DNS first.

---

## 1. Get the code onto the server

**Option A — copy from your PC** (run in PowerShell on your machine, from the
folder that contains `kazino/`):

```powershell
scp -r C:\Users\user\Desktop\kazino root@<SERVER_IP>:/opt/kazino
```

**Option B — put it in a git repo** and clone it on the server:

```bash
ssh root@<SERVER_IP>
git clone <your-repo-url> /opt/kazino
```

(Replace `<SERVER_IP>` with the server's **real** public IP.)

---

## 2. One-shot bootstrap (recommended)

SSH in and run the bootstrap script — it installs Docker, generates secrets,
opens the firewall, and starts everything:

```bash
ssh root@<SERVER_IP>
cd /opt/kazino
export SITE_ADDRESS=titorovka.icu
export ACME_EMAIL=you@example.com          # a real inbox you own
bash deploy/setup.sh
```

That's it. Check it came up:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web   # watch Caddy get the cert
```

Visit **https://titorovka.icu** once DNS is pointed and the cert is issued.

---

## 2b. Manual path (if you prefer to see each step)

```bash
cd /opt/kazino

# Install Docker (skip if already installed)
curl -fsSL https://get.docker.com | sh

# Create the env file and fill it in
cp .env.prod.example .env
nano .env            # set SECRET_KEY (openssl rand -hex 32), POSTGRES_PASSWORD, SITE_ADDRESS, ACME_EMAIL

# Build & launch
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 3. What's exposed

| Port | Service | Public? |
|------|---------|---------|
| 80 / 443 | Caddy (frontend + `/api` proxy + WebSocket) | ✅ yes |
| 8000 | FastAPI backend | ❌ internal only |
| 5432 | Postgres | ❌ internal only |
| 6379 | Redis | ❌ internal only |

The frontend talks to the backend same-origin via `/api`, so no CORS or extra
config is needed. The crash WebSocket (`/api/games/crash/ws`) is proxied through
Caddy automatically.

---

## 4. No HTTPS yet? (DNS not ready)

If the domain isn't pointed at the server yet, Caddy can't issue a certificate.
To test over plain HTTP in the meantime, set in `.env`:

```
SITE_ADDRESS=:80
```

then `docker compose -f docker-compose.prod.yml up -d`. Reach it at
`http://<SERVER_IP>`. Switch back to the real domain once DNS resolves.

---

## 5. Everyday operations

```bash
# Logs
docker compose -f docker-compose.prod.yml logs -f backend

# Update after code changes
git pull   # or re-scp
docker compose -f docker-compose.prod.yml up -d --build

# Stop / start
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# Backup the database
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U kazino kazino > backup_$(date +%F).sql
```

---

## 6. Harden SSH (do this once it's working)

On the server:

```bash
# From your PC, if you don't have a key yet:  ssh-keygen -t ed25519
# Then copy it up:                            ssh-copy-id root@<SERVER_IP>

# On the server, disable password login:
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
systemctl restart ssh
```

> ⚠️ Make sure key login works in a **second** terminal before you close your
> current session, or you can lock yourself out.

---

## Notes

- This is a **play-money demo**. There is no real payment integration; new users
  get 1000 ★. Do not accept real deposits without proper licensing, KYC/AML,
  and a real payment provider — that's a legal/regulated domain, not something to
  bolt on casually.
- Rotate `SECRET_KEY` and `POSTGRES_PASSWORD` if they were ever shared.
