"""On-chain deposit watcher.

Polls TonAPI for finalized incoming transfers to the owner address. A transfer
whose text comment is `dep:<userId>` is credited to that user as Stars, priced
with the live GRAM/USD rate. Attribution is by comment (the depositor names the
account to credit and pays for it), so there is no address-spoofing theft vector.
Each transfer is credited exactly once via a stable dedup key.
"""
import asyncio
import re

import httpx
from sqlalchemy import select
from sqlalchemy.exc import DataError, IntegrityError

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.deposit import TonDeposit
from app.models.transaction import TransactionType
from app.models.user import User
from app.services.ton_rates import stars_per_coin
from app.services.wallet import apply_transaction

_COMMENT_RE = re.compile(r"^dep:(\d+)$")
_MAX_STARS_PER_COIN = 1_000_000  # sanity band; reject absurd rate glitches


class DepositWatcher:
    def __init__(self) -> None:
        self._running = False
        self.owner_raw: str | None = None

    def _headers(self) -> dict:
        if settings.ton_api_key:
            return {"Authorization": f"Bearer {settings.ton_api_key}"}
        return {}

    async def _resolve_owner(self, client: httpx.AsyncClient) -> None:
        url = f"{settings.ton_api_base}/v2/accounts/{settings.ton_deposit_address}"
        r = await client.get(url, headers=self._headers())
        r.raise_for_status()
        addr = str(r.json().get("address", "")).lower()
        self.owner_raw = addr or None  # keep None on empty so it retries

    async def _poll_once(self, client: httpx.AsyncClient) -> None:
        if not self.owner_raw:
            return  # fail closed: never process without a resolved owner address

        url = (
            f"{settings.ton_api_base}/v2/accounts/"
            f"{settings.ton_deposit_address}/events?limit=100"
        )
        r = await client.get(url, headers=self._headers())
        r.raise_for_status()
        events = r.json().get("events", [])

        for ev in events:
            if ev.get("in_progress"):
                continue  # only credit finalized traces
            event_id = ev.get("event_id")
            if not event_id:
                continue
            for action in ev.get("actions", []):
                if action.get("type") != "TonTransfer" or action.get("status") != "ok":
                    continue
                tt = action.get("TonTransfer") or {}

                # Mandatory incoming check: recipient MUST be the owner address.
                recipient = str((tt.get("recipient") or {}).get("address", "")).lower()
                if recipient != self.owner_raw:
                    continue

                m = _COMMENT_RE.match((tt.get("comment") or "").strip())
                if not m:
                    continue
                amount_nano = int(tt.get("amount") or 0)
                if amount_nano <= 0:
                    continue

                user_id = int(m.group(1))
                # Stable dedup key: independent of action ordering.
                dedup_key = f"{event_id}:{amount_nano}:{user_id}"
                sender = str((tt.get("sender") or {}).get("address", ""))[:80]
                await self._credit(dedup_key, user_id, amount_nano, sender)

    async def _credit(
        self, dedup_key: str, user_id: int, amount_nano: int, sender: str
    ) -> None:
        async with AsyncSessionLocal() as db:
            exists = await db.execute(
                select(TonDeposit.id).where(TonDeposit.event_id == dedup_key)
            )
            if exists.scalar_one_or_none():
                return  # already credited

            user = await db.get(User, user_id)
            if user is None:
                return  # comment named an unknown user

            amount = amount_nano / 1e9
            try:
                rate = await stars_per_coin()
            except Exception:
                return  # no rate now -> leave uncredited, retried next poll
            if not (0 < rate < _MAX_STARS_PER_COIN):
                return  # rate glitch -> skip, retry later

            stars = int(amount * rate)
            if stars <= 0:
                return

            # ref kept short (Transaction.ref is VARCHAR(64)); dedup lives on event_id.
            await apply_transaction(
                db, user, stars, TransactionType.DEPOSIT, game="ton", ref=str(user_id)
            )
            db.add(
                TonDeposit(
                    event_id=dedup_key,
                    user_id=user_id,
                    ton_amount=amount,
                    stars=stars,
                    rate=rate,
                    sender=sender or None,
                )
            )
            try:
                await db.commit()
                print(f"[deposits] user {user_id}: {amount} GRAM -> {stars} ★")
            except (IntegrityError, DataError):
                await db.rollback()  # duplicate or malformed -> don't wedge the loop

    async def run_forever(self) -> None:
        if not settings.deposits_enabled:
            print("[deposits] watcher disabled")
            return
        self._running = True
        async with httpx.AsyncClient(timeout=15) as client:
            while self._running:
                try:
                    if self.owner_raw is None:
                        await self._resolve_owner(client)
                    await self._poll_once(client)
                except asyncio.CancelledError:
                    break
                except Exception as exc:
                    print(f"[deposits] poll error: {exc}")
                await asyncio.sleep(settings.deposit_poll_seconds)

    def stop(self) -> None:
        self._running = False


watcher = DepositWatcher()
