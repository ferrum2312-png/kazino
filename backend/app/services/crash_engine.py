"""Real-time Crash game engine.

A single background loop drives global rounds through three phases:
BETTING -> RUNNING -> CRASHED. State is mirrored into Redis (so any process can
read the current round / history) and broadcast to connected WebSocket clients.

Bets and cashouts are authenticated per-connection and settled against Postgres.
"""
import asyncio
import json
import math
import secrets
import time
from dataclasses import dataclass, field

from starlette.websockets import WebSocket, WebSocketState

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.models.game import CrashBet, CrashRound, RoundStatus
from app.models.transaction import TransactionType
from app.models.user import User
from app.services import fair
from app.services.redis_client import get_redis
from app.services.wallet import apply_transaction

GROWTH = 0.12          # exponential growth rate per second
CRASHED_PAUSE = 3.0    # seconds to display the bust before the next round
HISTORY_KEY = "crash:history"
STATE_KEY = "crash:state"


def multiplier_at(elapsed: float) -> float:
    return math.floor(math.exp(GROWTH * elapsed) * 100) / 100


@dataclass
class LiveBet:
    user_id: int
    username: str
    amount: float
    auto_cashout: float | None
    db_id: int
    cashed_out: float | None = None  # multiplier if cashed out


@dataclass
class CrashEngine:
    connections: set[WebSocket] = field(default_factory=set)
    conn_user: dict[WebSocket, int] = field(default_factory=dict)
    bets: dict[int, LiveBet] = field(default_factory=dict)  # user_id -> bet
    round_id: int | None = None
    nonce: int = 0
    server_seed: str = ""
    client_seed: str = ""
    crash_point: float = 1.0
    status: RoundStatus = RoundStatus.BETTING
    phase_ends: float = 0.0
    current_multiplier: float = 1.0
    _running: bool = False

    # ---- WebSocket plumbing ----
    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.connections.add(ws)
        await self._send(ws, self._state_message())

    def disconnect(self, ws: WebSocket) -> None:
        self.connections.discard(ws)
        self.conn_user.pop(ws, None)

    async def _send(self, ws: WebSocket, message: dict) -> None:
        if ws.application_state == WebSocketState.CONNECTED:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                self.disconnect(ws)

    async def broadcast(self, message: dict) -> None:
        dead = []
        text = json.dumps(message)
        for ws in list(self.connections):
            if ws.application_state != WebSocketState.CONNECTED:
                dead.append(ws)
                continue
            try:
                await ws.send_text(text)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    # ---- Messaging helpers ----
    def _state_message(self) -> dict:
        return {
            "type": "state",
            "round_id": self.round_id,
            "status": self.status.value,
            "multiplier": self.current_multiplier,
            "time_left": max(0.0, round(self.phase_ends - time.monotonic(), 2)),
            "server_seed_hash": fair.server_seed_hash(self.server_seed)
            if self.server_seed
            else None,
            "players": self._players_snapshot(),
        }

    def _players_snapshot(self) -> list[dict]:
        return [
            {
                "username": b.username,
                "amount": round(b.amount, 2),
                "cashed_out": b.cashed_out,
            }
            for b in self.bets.values()
        ]

    # ---- Client commands ----
    async def authenticate(self, ws: WebSocket, token: str) -> int | None:
        subject = decode_access_token(token)
        if subject is None:
            return None
        self.conn_user[ws] = int(subject)
        return int(subject)

    async def place_bet(
        self, user_id: int, amount: float, auto_cashout: float | None
    ) -> dict:
        if self.status != RoundStatus.BETTING:
            return {"type": "error", "message": "Betting is closed"}
        if user_id in self.bets:
            return {"type": "error", "message": "You already have a bet this round"}
        if amount <= 0:
            return {"type": "error", "message": "Invalid amount"}

        async with AsyncSessionLocal() as db:
            user = await db.get(User, user_id)
            if user is None:
                return {"type": "error", "message": "User not found"}
            try:
                await apply_transaction(
                    db, user, -amount, TransactionType.BET, game="crash"
                )
            except Exception:
                return {"type": "error", "message": "Insufficient balance"}
            bet = CrashBet(
                round_id=self.round_id,
                user_id=user_id,
                amount=amount,
                auto_cashout=auto_cashout,
            )
            db.add(bet)
            await db.commit()
            await db.refresh(bet)
            new_balance = float(user.balance)

        self.bets[user_id] = LiveBet(
            user_id=user_id,
            username=user.username,
            amount=amount,
            auto_cashout=auto_cashout,
            db_id=bet.id,
        )
        await self.broadcast({"type": "players", "players": self._players_snapshot()})
        return {"type": "bet_ok", "amount": amount, "balance": new_balance}

    async def cash_out(self, user_id: int) -> dict:
        if self.status != RoundStatus.RUNNING:
            return {"type": "error", "message": "Round is not running"}
        bet = self.bets.get(user_id)
        if bet is None or bet.cashed_out is not None:
            return {"type": "error", "message": "No active bet"}
        mult = self.current_multiplier
        payout = await self._settle_bet(bet, mult)
        await self.broadcast({"type": "players", "players": self._players_snapshot()})
        return {"type": "cashout_ok", "multiplier": mult, "payout": payout}

    async def _settle_bet(self, bet: LiveBet, mult: float) -> float:
        bet.cashed_out = mult
        payout = round(bet.amount * mult, 2)
        async with AsyncSessionLocal() as db:
            user = await db.get(User, bet.user_id)
            db_bet = await db.get(CrashBet, bet.db_id)
            if user and db_bet:
                await apply_transaction(
                    db, user, payout, TransactionType.WIN, game="crash"
                )
                db_bet.cashout_multiplier = mult
                db_bet.payout = payout
                db_bet.won = True
                await db.commit()
        return payout

    # ---- Round lifecycle ----
    async def _new_round(self) -> None:
        self.nonce += 1
        self.server_seed = fair.new_server_seed()
        self.client_seed = secrets.token_hex(8)
        self.crash_point = fair.crash_point(
            self.server_seed, self.client_seed, self.nonce
        )
        self.status = RoundStatus.BETTING
        self.current_multiplier = 1.0
        self.bets.clear()
        self.phase_ends = time.monotonic() + settings.crash_bet_seconds

        async with AsyncSessionLocal() as db:
            rnd = CrashRound(
                nonce=self.nonce,
                server_seed=self.server_seed,
                server_seed_hash=fair.server_seed_hash(self.server_seed),
                client_seed=self.client_seed,
                crash_point=self.crash_point,
                status=RoundStatus.BETTING,
            )
            db.add(rnd)
            await db.commit()
            await db.refresh(rnd)
            self.round_id = rnd.id

        await self._mirror_state()
        await self.broadcast(
            {
                "type": "betting",
                "round_id": self.round_id,
                "server_seed_hash": fair.server_seed_hash(self.server_seed),
                "duration": settings.crash_bet_seconds,
            }
        )

    async def _run_multiplier(self) -> None:
        self.status = RoundStatus.RUNNING
        await self._update_round_status(RoundStatus.RUNNING)
        await self.broadcast({"type": "running", "round_id": self.round_id})

        start = time.monotonic()
        tick = settings.crash_tick_ms / 1000
        while True:
            elapsed = time.monotonic() - start
            self.current_multiplier = multiplier_at(elapsed)

            if self.current_multiplier >= self.crash_point:
                self.current_multiplier = self.crash_point
                break

            # Auto-cashouts.
            for bet in list(self.bets.values()):
                if (
                    bet.cashed_out is None
                    and bet.auto_cashout is not None
                    and self.current_multiplier >= bet.auto_cashout
                ):
                    await self._settle_bet(bet, bet.auto_cashout)

            await self.broadcast(
                {"type": "tick", "multiplier": self.current_multiplier}
            )
            await asyncio.sleep(tick)

    async def _crash(self) -> None:
        self.status = RoundStatus.CRASHED
        await self._update_round_status(RoundStatus.CRASHED)
        # Losers are already debited; nothing more to pay them.
        await self._push_history(self.crash_point)
        await self.broadcast(
            {
                "type": "crashed",
                "round_id": self.round_id,
                "crash_point": self.crash_point,
                "server_seed": self.server_seed,  # reveal for verification
            }
        )
        await self._mirror_state()

    async def _update_round_status(self, status: RoundStatus) -> None:
        async with AsyncSessionLocal() as db:
            rnd = await db.get(CrashRound, self.round_id)
            if rnd:
                rnd.status = status
                await db.commit()

    async def _push_history(self, point: float) -> None:
        r = get_redis()
        await r.lpush(HISTORY_KEY, point)
        await r.ltrim(HISTORY_KEY, 0, 29)

    async def _mirror_state(self) -> None:
        r = get_redis()
        await r.set(STATE_KEY, json.dumps(self._state_message()))

    async def history(self) -> list[float]:
        r = get_redis()
        items = await r.lrange(HISTORY_KEY, 0, 29)
        return [float(x) for x in items]

    # ---- Main loop ----
    async def run_forever(self) -> None:
        self._running = True
        while self._running:
            try:
                await self._new_round()
                await asyncio.sleep(settings.crash_bet_seconds)
                await self._run_multiplier()
                await self._crash()
                await asyncio.sleep(CRASHED_PAUSE)
            except asyncio.CancelledError:
                break
            except Exception as exc:  # keep the loop alive on transient errors
                print(f"[crash] loop error: {exc}")
                await asyncio.sleep(1)

    def stop(self) -> None:
        self._running = False


engine = CrashEngine()
