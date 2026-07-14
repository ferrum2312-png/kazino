# 🎰 Kazino

Мобильное демо крипто‑казино на стеке **React (Vite) + FastAPI + Redis + PostgreSQL**.

Повторяет тёмно‑неоновый интерфейс в стиле Telegram: главный экран с карточками
игр (Розыгрыши, Ральф Арена, ПВП Дуэль, Краш, Мины) плюс две полностью играбельные
честные (provably‑fair) игры — **Краш** (реалтайм, WebSocket) и **Мины**.

> Только игровые фишки. Новым аккаунтам начисляется **1000 ★**. Реальных платежей нет.

---

## Стек

| Слой      | Технологии                                                  |
|-----------|-------------------------------------------------------------|
| Фронтенд  | React 18, Vite 6, React Router, Zustand                     |
| Бэкенд    | FastAPI, SQLAlchemy 2 (async), Pydantic v2, JWT‑авторизация |
| Реалтайм  | WebSocket + Redis (состояние раундов краша и история)       |
| База      | PostgreSQL 16                                               |
| Инфра     | Docker Compose                                              |

---

## Быстрый старт (Docker — рекомендуется)

Нужен только **Docker Desktop**.

```bash
docker compose up --build
```

Затем открой:

- **Приложение:** http://localhost:5173
- **Документация API:** http://localhost:8000/docs

Таблицы создаются автоматически при первом запуске. Зарегистрируй пользователя
в интерфейсе — получишь 1000 ★ для игры.

---

## Ручная установка (без Docker)

Нужны **Python 3.12+**, **Node 20+**, а также запущенные локально **PostgreSQL** и **Redis**.

### 1. Бэкенд

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    |    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # при необходимости поправь DATABASE_URL / REDIS_URL
uvicorn app.main:app --reload
```

Бэкенд ожидает:
- Postgres по адресу `postgresql+asyncpg://kazino:kazino@localhost:5432/kazino`
- Redis по адресу `redis://localhost:6379/0`

(оба можно переопределить в `backend/.env`.)

### 2. Фронтенд

```bash
cd frontend
npm install
npm run dev
```

Vite проксирует `/api` (включая WebSocket) на `http://localhost:8000`,
поэтому в разработке возиться с CORS не нужно.

---

## Структура проекта

```
kazino/
├── docker-compose.yml          # dev-стек
├── docker-compose.prod.yml     # prod-стек (Caddy + авто-HTTPS)
├── DEPLOY.ru.md                # инструкция по деплою
├── backend/
│   ├── app/
│   │   ├── main.py              # приложение + lifespan (запуск цикла краша)
│   │   ├── core/               # конфиг, безопасность (JWT, хеширование)
│   │   ├── db/                 # async-движок, сессия, Base
│   │   ├── models/             # User, Transaction, Crash*, MinesGame
│   │   ├── schemas/            # Pydantic-модели запросов/ответов
│   │   ├── routers/            # auth, users, catalog, crash, mines
│   │   └── services/
│   │       ├── fair.py         # честная генерация на HMAC-SHA256
│   │       ├── wallet.py       # изменение баланса + журнал операций
│   │       ├── mines.py        # математика множителей «Мин»
│   │       └── crash_engine.py # реалтайм-цикл раундов + менеджер WS
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/client.js       # обёртка над fetch + помощник для WS
        ├── store/useStore.js   # zustand-стор авторизации/баланса
        ├── components/         # Header, Banner, GameCard, BottomNav, Toast
        └── pages/              # Home, Login, Crash, Mines, Wallet, Profile
```

---

## Как устроены игры

### Краш (реалтайм)
Единый серверный цикл гоняет раунды: **приём ставок (6с) → полёт → взрыв**.
Множитель растёт экспоненциально и «взрывается» на заранее зафиксированной точке.
Клиенты подключаются к `ws /api/games/crash/ws`, авторизуются по JWT, делают
ставку во время окна приёма и забирают выигрыш (или ставят авто‑вывод) до взрыва.
Состояние раунда и последние 30 результатов хранятся в Redis.

### Мины
Классическое поле 5×5. Выбираешь ставку и число мин, открываешь безопасные клетки —
множитель растёт, забрать можно в любой момент. Позиции мин выводятся из скрытого
серверного сида (раскрывается по завершении раунда), так что каждую игру можно проверить.

### Честность (provably fair)
Каждый раунд заранее публикует `sha256(server_seed)`. Точки краша и раскладки мин
берутся из `HMAC-SHA256(server_seed, "client_seed:nonce")`. После раунда `server_seed`
раскрывается, и результат можно пересчитать. См.
[`backend/app/services/fair.py`](backend/app/services/fair.py).

---

## Обзор API

| Метод | Путь                          | Примечание                     |
|-------|-------------------------------|--------------------------------|
| POST  | `/api/auth/register`          | возвращает JWT                 |
| POST  | `/api/auth/login`             | OAuth2 password form → JWT     |
| GET   | `/api/users/me`               | текущий пользователь           |
| POST  | `/api/users/me/deposit`       | демо‑пополнение                |
| GET   | `/api/catalog/games`          | карточки главного экрана       |
| POST  | `/api/games/mines/start`      | старт раунда «Мин»             |
| POST  | `/api/games/mines/reveal`     | открыть клетку                 |
| POST  | `/api/games/mines/cashout`    | забрать текущий множитель      |
| GET   | `/api/games/crash/history`    | последние 30 точек краша       |
| WS    | `/api/games/crash/ws`         | реалтайм‑краш                  |

Полная интерактивная документация — на `/docs`.

---

## Заметки и что дальше

- Замени эмодзи/градиентные картинки карточек на настоящую графику: положи
  изображения в `frontend/public/` и укажи их в фоне `.art` у `GameCard`.
- `Розыгрыши`, `Ральф Арена`, `ПВП Дуэль` — заглушки (экран «Скоро»); их записи
  в каталоге и маршруты уже подключены.
- Для продакшена: поставь миграции Alembic перед `init_models`, задай реальный
  `SECRET_KEY`, добавь rate‑limiting и раздавай собранный фронтенд через Caddy/Nginx
  (см. [DEPLOY.ru.md](DEPLOY.ru.md)).
