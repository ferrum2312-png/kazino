# 🎰 Kazino

A mobile-first crypto-casino demo built on **React (Vite) + FastAPI + Redis + PostgreSQL**.

Matches the dark-neon Telegram-style UI: a home hub with game cards
(Розыгрыши, Ральф Арена, ПВП Дуэль, Краш, Мины) plus two fully playable
provably-fair games — **Crash** (realtime, WebSocket) and **Mines**.

> Play money only. New accounts start with **1000 ★**. No real payments.

---

## Stack

| Layer     | Tech                                                        |
|-----------|-------------------------------------------------------------|
| Frontend  | React 18, Vite 6, React Router, Zustand                     |
| Backend   | FastAPI, SQLAlchemy 2 (async), Pydantic v2, JWT auth        |
| Realtime  | WebSocket + Redis (crash round state & history)             |
| Database  | PostgreSQL 16                                               |
| Infra     | Docker Compose                                              |

---

## Quick start (Docker — recommended)

Requires **Docker Desktop** only.

```bash
docker compose up --build
```

Then open:

- **App:** http://localhost:5173
- **API docs:** http://localhost:8000/docs

Tables are created automatically on first boot. Register a user in the UI and
you'll get 1000 ★ to play with.

---

## Manual dev setup (no Docker)

You need **Python 3.12+**, **Node 20+**, a **PostgreSQL** and a **Redis** running locally.

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    |    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit DATABASE_URL / REDIS_URL if needed
uvicorn app.main:app --reload
```

The backend expects:
- Postgres at `postgresql+asyncpg://kazino:kazino@localhost:5432/kazino`
- Redis at `redis://localhost:6379/0`

(override both in `backend/.env`.)

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` (including the WebSocket) to `http://localhost:8000`,
so no CORS juggling is needed in dev.

---

## Project layout

```
kazino/
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── main.py              # app + lifespan (starts crash loop)
│   │   ├── core/               # config, security (JWT, hashing)
│   │   ├── db/                 # async engine, session, Base
│   │   ├── models/             # User, Transaction, Crash*, MinesGame
│   │   ├── schemas/            # Pydantic request/response models
│   │   ├── routers/            # auth, users, catalog, crash, mines
│   │   └── services/
│   │       ├── fair.py         # provably-fair HMAC-SHA256 helpers
│   │       ├── wallet.py       # balance mutations + ledger
│   │       ├── mines.py        # mines multiplier math
│   │       └── crash_engine.py # realtime round loop + WS manager
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/client.js       # fetch wrapper + WS url helper
        ├── store/useStore.js   # zustand auth/balance store
        ├── components/         # Header, Banner, GameCard, BottomNav, Toast
        └── pages/              # Home, Login, Crash, Mines, Wallet, Profile
```

---

## How the games work

### Crash (realtime)
A single server loop cycles rounds: **betting (6s) → running → crash**.
The multiplier grows exponentially and busts at a pre-committed point.
Clients connect to `ws /api/games/crash/ws`, authenticate with their JWT,
place a bet during the betting window, and cash out (or set auto-cashout)
before the bust. Round state and the last 30 results live in Redis.

### Mines
Classic 5×5 grid. Pick a bet and number of mines, reveal safe tiles to grow
the multiplier, cash out any time. Mine positions are derived from a hidden
server seed (revealed when the round ends) so every game is verifiable.

### Provably fair
Each round commits to `sha256(server_seed)` up front. Crash points and mine
layouts come from `HMAC-SHA256(server_seed, "client_seed:nonce")`. After the
round the `server_seed` is revealed so you can recompute the result. See
[`backend/app/services/fair.py`](backend/app/services/fair.py).

---

## API overview

| Method | Path                          | Notes                          |
|--------|-------------------------------|--------------------------------|
| POST   | `/api/auth/register`          | returns JWT                    |
| POST   | `/api/auth/login`             | OAuth2 password form → JWT     |
| GET    | `/api/users/me`               | current user                   |
| POST   | `/api/users/me/deposit`       | demo top-up                    |
| GET    | `/api/catalog/games`          | home-screen cards              |
| POST   | `/api/games/mines/start`      | start a mines round            |
| POST   | `/api/games/mines/reveal`     | reveal a tile                  |
| POST   | `/api/games/mines/cashout`    | bank the current multiplier    |
| GET    | `/api/games/crash/history`    | last 30 crash points           |
| WS     | `/api/games/crash/ws`         | realtime crash                 |

Full interactive docs at `/docs`.

---

## Notes & next steps

- Swap the emoji/gradient card art for real artwork by dropping images into
  `frontend/public/` and pointing `GameCard`'s `.art` background at them.
- `Розыгрыши`, `Ральф Арена`, `ПВП Дуэль` are stubbed (a "coming soon" screen);
  their catalog entries and routes are already wired up.
- For production: put Alembic migrations in front of `init_models`, set a real
  `SECRET_KEY`, add rate limiting, and serve the built frontend behind Nginx.
