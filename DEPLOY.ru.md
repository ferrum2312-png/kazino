# 🚀 Развёртывание Kazino на сервере

Здесь разворачивается весь стек (Postgres + Redis + FastAPI + собранное React‑приложение
за Caddy) с автоматическим HTTPS. **Все шаги ты выполняешь сам** — либо в SSH‑терминале,
либо в веб‑консоли твоего хостинга.

---

## 0. Сначала — безопасность

Ты вставил **root‑пароль сервера прямо в чат**, поэтому считай его утёкшим:

```bash
# на сервере, под root:
passwd            # задай новый root-пароль
```

Затем перейди на вход по ключу (шаг 6). Парольный вход по SSH для root — это
главный способ, которым сервера угоняют боты.

Проверь также, что домен действительно указывает на этот сервер. С **твоего
собственного** компьютера (не через VPN):

```bash
nslookup titorovka.icu      # A-запись должна совпадать с публичным IP сервера
```

> Когда я резолвил `titorovka.icu`, вернулось `198.18.0.96` (зарезервированный
> «бенчмарочный» адрес) — а **не** `2.26.125.173`, который ты называл. HTTPS
> заработает только когда публичная A‑запись домена будет указывать на реальный
> IP сервера. Сначала почини DNS.

---

## 1. Загрузи код на сервер

**Вариант A — скопировать со своего ПК** (запусти в PowerShell на своей машине,
из папки, где лежит `kazino/`):

```powershell
scp -r C:\Users\user\Desktop\kazino root@<IP_СЕРВЕРА>:/opt/kazino
```

**Вариант B — положить в git‑репозиторий** и склонировать на сервере:

```bash
ssh root@<IP_СЕРВЕРА>
git clone <ссылка-на-репозиторий> /opt/kazino
```

(Замени `<IP_СЕРВЕРА>` на **реальный** публичный IP сервера.)

---

## 2. Запуск одной командой (рекомендуется)

Зайди по SSH и запусти скрипт — он поставит Docker, сгенерирует секреты,
откроет firewall и всё запустит:

```bash
ssh root@<IP_СЕРВЕРА>
cd /opt/kazino
export SITE_ADDRESS=titorovka.icu
export ACME_EMAIL=ты@почта.ру          # реальный ящик, который тебе принадлежит
bash deploy/setup.sh
```

Готово. Проверь, что всё поднялось:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web   # смотрим, как Caddy получает сертификат
```

Когда DNS будет указывать на сервер и сертификат выпустится — открывай
**https://titorovka.icu**.

---

## 2b. Ручной путь (если хочешь видеть каждый шаг)

```bash
cd /opt/kazino

# Установить Docker (пропусти, если уже стоит)
curl -fsSL https://get.docker.com | sh

# Создать файл с переменными и заполнить его
cp .env.prod.example .env
nano .env            # задай SECRET_KEY (openssl rand -hex 32), POSTGRES_PASSWORD, SITE_ADDRESS, ACME_EMAIL

# Собрать и запустить
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 3. Что открыто наружу

| Порт | Сервис | Публичный? |
|------|--------|-----------|
| 80 / 443 | Caddy (фронтенд + прокси `/api` + WebSocket) | ✅ да |
| 8000 | FastAPI backend | ❌ только внутри |
| 5432 | Postgres | ❌ только внутри |
| 6379 | Redis | ❌ только внутри |

Фронтенд общается с бэкендом на том же домене через `/api`, поэтому CORS и
доп. настройки не нужны. WebSocket краша (`/api/games/crash/ws`) проксируется
через Caddy автоматически.

---

## 4. HTTPS ещё нет? (DNS не готов)

Если домен пока не указывает на сервер, Caddy не сможет выпустить сертификат.
Чтобы протестировать по обычному HTTP, укажи в `.env`:

```
SITE_ADDRESS=:80
```

затем `docker compose -f docker-compose.prod.yml up -d`. Открывай по адресу
`http://<IP_СЕРВЕРА>`. Верни настоящий домен, когда DNS заработает.

---

## 5. Повседневные операции

```bash
# Логи
docker compose -f docker-compose.prod.yml logs -f backend

# Обновление после правок кода
git pull   # или заново scp
docker compose -f docker-compose.prod.yml up -d --build

# Остановить / запустить
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# Бэкап базы
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U kazino kazino > backup_$(date +%F).sql
```

---

## 6. Усиление SSH (сделай, когда всё заработает)

На сервере:

```bash
# Со своего ПК, если ключа ещё нет:  ssh-keygen -t ed25519
# Затем скопируй его на сервер:       ssh-copy-id root@<IP_СЕРВЕРА>

# На сервере отключи вход по паролю:
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
systemctl restart ssh
```

> ⚠️ Убедись, что вход по ключу работает во **втором** терминале, прежде чем
> закрывать текущую сессию — иначе можно заблокировать себе доступ.

---

## Примечания

- Это **демо на игровые фишки**. Реальной платёжной интеграции нет; новые
  пользователи получают 1000 ★. Не принимай реальные депозиты без лицензии,
  KYC/AML и настоящего платёжного провайдера — это регулируемая сфера, а не то,
  что можно наспех прикрутить.
- Смени `SECRET_KEY` и `POSTGRES_PASSWORD`, если они где‑то засветились.
