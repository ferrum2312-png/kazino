"""Polling fallback for Crypto Pay invoices (in case the webhook isn't set).

Both this and the webhook credit through credit_payment, which is idempotent,
so a paid invoice is credited exactly once regardless of which path sees it.
"""
import asyncio

from app.core.config import settings
from app.services import crypto_pay
from app.services.payments_service import credit_payment


class CryptoPayWatcher:
    def __init__(self) -> None:
        self._running = False

    async def _poll_once(self) -> None:
        items = await crypto_pay.get_paid_invoices(count=100)
        for inv in items:
            our_payload = inv.get("payload") or ""
            if not our_payload.startswith("cb:"):
                continue
            try:
                user_id = int(our_payload.split(":")[1])
            except (IndexError, ValueError):
                continue
            asset = inv.get("asset") or ""
            amount = float(inv.get("amount") or 0)
            if amount <= 0:
                continue
            stars = await crypto_pay.asset_to_stars(asset, amount)
            await credit_payment(
                provider="cryptobot",
                external_id=str(inv.get("invoice_id")),
                user_id=user_id,
                stars=stars,
                amount=amount,
                asset=asset,
            )

    async def run_forever(self) -> None:
        if not settings.crypto_pay_token:
            print("[cryptopay] no token, watcher disabled")
            return
        self._running = True
        while self._running:
            try:
                await self._poll_once()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                print(f"[cryptopay] poll error: {exc}")
            await asyncio.sleep(settings.crypto_pay_poll_seconds)

    def stop(self) -> None:
        self._running = False


watcher = CryptoPayWatcher()
