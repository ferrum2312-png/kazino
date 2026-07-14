"""GRAM (ex-TON) -> Telegram Stars exchange rate.

The GRAM/USD price is parsed from KuCoin and Bybit spot markets and averaged,
then divided by the Star price in USD (settings.star_usd_price; 50 Stars = $0.75
-> $0.015). That yields "stars per GRAM", tracking the live market.
"""
import time

import httpx

from app.core.config import settings

_cache: dict = {"ts": 0.0, "usd": 0.0}


async def _kucoin_price(client: httpx.AsyncClient) -> float | None:
    url = (
        "https://api.kucoin.com/api/v1/market/orderbook/level1"
        f"?symbol={settings.kucoin_symbol}"
    )
    r = await client.get(url)
    r.raise_for_status()
    data = r.json().get("data")
    if data and data.get("price"):
        return float(data["price"])
    return None


async def _bybit_price(client: httpx.AsyncClient) -> float | None:
    url = (
        "https://api.bybit.com/v5/market/tickers"
        f"?category=spot&symbol={settings.bybit_symbol}"
    )
    r = await client.get(url)
    r.raise_for_status()
    j = r.json()
    lst = (j.get("result") or {}).get("list") or []
    if lst and lst[0].get("lastPrice"):
        return float(lst[0]["lastPrice"])
    return None


async def get_coin_usd() -> float:
    """Averaged GRAM/USD price from KuCoin + Bybit, cached."""
    now = time.time()
    if _cache["usd"] > 0 and (now - _cache["ts"]) < settings.rate_cache_seconds:
        return _cache["usd"]

    prices: list[float] = []
    async with httpx.AsyncClient(timeout=10) as client:
        for fetch in (_kucoin_price, _bybit_price):
            try:
                p = await fetch(client)
                if p and p > 0:
                    prices.append(p)
            except Exception:
                pass

    if not prices:
        if _cache["usd"] > 0:
            return _cache["usd"]  # serve stale rather than fail
        raise RuntimeError("Could not fetch GRAM price from KuCoin/Bybit")

    price = sum(prices) / len(prices)
    _cache["usd"] = price
    _cache["ts"] = now
    return price


async def stars_per_coin() -> float:
    return await get_coin_usd() / settings.star_usd_price


async def coin_to_stars(amount: float) -> int:
    """Whole Stars that `amount` GRAM is worth (floored)."""
    return int(amount * await stars_per_coin())


async def rate_info() -> dict:
    usd = await get_coin_usd()
    return {
        "coin_usd": round(usd, 4),
        "star_usd": settings.star_usd_price,
        "stars_per_coin": round(usd / settings.star_usd_price, 2),
    }
