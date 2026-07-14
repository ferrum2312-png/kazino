"""Crypto Pay (@CryptoBot) API helpers."""
import hashlib
import hmac

import httpx

from app.core.config import settings
from app.services.ton_rates import stars_per_coin


async def asset_to_stars(asset: str, amount: float) -> int:
    """Convert a Crypto Pay asset amount to whole Stars."""
    asset = (asset or "").upper()
    try:
        if asset in ("USDT", "USDC", "USD"):
            return int(amount / settings.star_usd_price)
        if asset in ("TON", "GRAM"):
            return int(amount * await stars_per_coin())
    except Exception:
        return 0
    return 0


def _headers() -> dict:
    return {"Crypto-Pay-API-Token": settings.crypto_pay_token}


def _url(method: str) -> str:
    return f"{settings.crypto_pay_base}/api/{method}"


async def create_invoice(asset: str, amount: float, payload: str, description: str) -> dict:
    body = {
        "asset": asset,
        "amount": str(amount),
        "payload": payload,
        "description": description,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(_url("createInvoice"), json=body, headers=_headers())
        r.raise_for_status()
        data = r.json()
    if not data.get("ok"):
        raise RuntimeError(str(data.get("error", "createInvoice failed")))
    return data["result"]


async def get_paid_invoices(count: int = 100) -> list[dict]:
    params = {"status": "paid", "count": count}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(_url("getInvoices"), params=params, headers=_headers())
        r.raise_for_status()
        data = r.json()
    if not data.get("ok"):
        return []
    return data["result"].get("items", [])


def verify_webhook(body_bytes: bytes, signature: str) -> bool:
    """Verify a Crypto Pay webhook signature.

    secret = SHA256(token); check = HMAC_SHA256(secret, body).
    """
    if not signature or not settings.crypto_pay_token:
        return False
    secret = hashlib.sha256(settings.crypto_pay_token.encode()).digest()
    check = hmac.new(secret, body_bytes, hashlib.sha256).hexdigest()
    try:
        return hmac.compare_digest(check, signature)
    except TypeError:
        return False  # non-ASCII / malformed signature
