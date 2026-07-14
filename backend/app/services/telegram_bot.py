"""Telegram Bot API helpers for Stars (XTR) payments."""
import hashlib

import httpx

from app.core.config import settings


def _api(method: str) -> str:
    return f"https://api.telegram.org/bot{settings.bot_token}/{method}"


def webhook_secret() -> str:
    """Deterministic secret token Telegram echoes back in a header."""
    return hashlib.sha256(f"wh:{settings.secret_key}".encode()).hexdigest()[:40]


async def create_stars_invoice_link(stars: int, payload: str, title: str) -> str:
    """Invoice link for `stars` Telegram Stars (currency XTR)."""
    body = {
        "title": title,
        "description": f"{stars} ★",
        "payload": payload,
        "provider_token": "",  # empty for Telegram Stars (XTR)
        "currency": "XTR",
        "prices": [{"label": f"{stars} Stars", "amount": stars}],
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(_api("createInvoiceLink"), json=body)
        r.raise_for_status()
        data = r.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("description", "createInvoiceLink failed"))
    return data["result"]


async def answer_pre_checkout(query_id: str, ok: bool = True, error: str = "") -> None:
    body = {"pre_checkout_query_id": query_id, "ok": ok}
    if not ok and error:
        body["error_message"] = error
    # Telegram requires an answer within ~10s; keep well under that.
    async with httpx.AsyncClient(timeout=8) as client:
        r = await client.post(_api("answerPreCheckoutQuery"), json=body)
        try:
            if not r.json().get("ok"):
                print(f"[bot] answerPreCheckoutQuery not ok: {r.text}")
        except Exception:
            pass


async def set_webhook() -> None:
    """Point the bot's webhook at our backend so we receive payment updates."""
    if not settings.bot_token:
        return
    url = f"{settings.public_base_url}{settings.api_prefix}/telegram/webhook"
    body = {
        "url": url,
        "secret_token": webhook_secret(),
        "allowed_updates": ["pre_checkout_query", "message"],
        "drop_pending_updates": False,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(_api("setWebhook"), json=body)
        try:
            print(f"[bot] setWebhook -> {r.json()}")
        except Exception:
            print(f"[bot] setWebhook status {r.status_code}")
