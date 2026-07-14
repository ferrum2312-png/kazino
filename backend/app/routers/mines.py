import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.deps import get_current_user
from app.models.game import MinesGame
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.game import (
    MinesActionRequest,
    MinesRevealRequest,
    MinesStartRequest,
    MinesState,
)
from app.services import fair
from app.services.mines import multiplier as mines_multiplier
from app.services.wallet import apply_transaction

router = APIRouter(prefix="/games/mines", tags=["mines"])

GRID_SIZE = 25


def _to_state(game: MinesGame, reveal_secret: bool = False) -> MinesState:
    revealed_count = len(game.revealed or [])
    next_mult = None
    if game.active and revealed_count < (GRID_SIZE - game.mines):
        next_mult = mines_multiplier(GRID_SIZE, game.mines, revealed_count + 1)
    return MinesState(
        game_id=game.id,
        bet=float(game.bet),
        mines=game.mines,
        grid_size=game.grid_size,
        revealed=game.revealed or [],
        multiplier=game.multiplier,
        next_multiplier=next_mult,
        payout=float(game.payout),
        active=game.active,
        won=game.won,
        server_seed_hash=game.server_seed_hash,
        mine_positions=None if game.active else game.mine_positions,
        server_seed=None if game.active else game.server_seed,
    )


async def _load_game(db: AsyncSession, game_id: int, user: User) -> MinesGame:
    game = await db.get(MinesGame, game_id)
    if game is None or game.user_id != user.id:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.post("/start", response_model=MinesState)
async def start(
    payload: MinesStartRequest,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    server_seed = fair.new_server_seed()
    client_seed = secrets.token_hex(8)
    nonce = secrets.randbelow(1_000_000)
    positions = fair.mine_positions(
        server_seed, client_seed, nonce, GRID_SIZE, payload.mines
    )

    await apply_transaction(
        db, current, -payload.bet, TransactionType.BET, game="mines"
    )

    game = MinesGame(
        user_id=current.id,
        bet=payload.bet,
        grid_size=GRID_SIZE,
        mines=payload.mines,
        mine_positions=positions,
        revealed=[],
        server_seed=server_seed,
        server_seed_hash=fair.server_seed_hash(server_seed),
        client_seed=client_seed,
        nonce=nonce,
        multiplier=1.0,
        payout=0,
        active=True,
        won=None,
    )
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return _to_state(game)


@router.post("/reveal", response_model=MinesState)
async def reveal(
    payload: MinesRevealRequest,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    game = await _load_game(db, payload.game_id, current)
    if not game.active:
        raise HTTPException(status_code=400, detail="Game already finished")
    if payload.tile in (game.revealed or []):
        raise HTTPException(status_code=400, detail="Tile already revealed")
    if payload.tile >= GRID_SIZE:
        raise HTTPException(status_code=400, detail="Tile out of range")

    if payload.tile in game.mine_positions:
        # Boom.
        game.active = False
        game.won = False
        game.multiplier = 0.0
        game.payout = 0
        game.revealed = [*(game.revealed or []), payload.tile]
        await db.commit()
        await db.refresh(game)
        return _to_state(game, reveal_secret=True)

    revealed = [*(game.revealed or []), payload.tile]
    game.revealed = revealed
    game.multiplier = mines_multiplier(GRID_SIZE, game.mines, len(revealed))

    # Auto-win if all safe tiles cleared.
    if len(revealed) == GRID_SIZE - game.mines:
        payout = float(game.bet) * game.multiplier
        game.active = False
        game.won = True
        game.payout = payout
        await apply_transaction(
            db, current, payout, TransactionType.WIN, game="mines"
        )

    await db.commit()
    await db.refresh(game)
    return _to_state(game)


@router.post("/cashout", response_model=MinesState)
async def cashout(
    payload: MinesActionRequest,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    game = await _load_game(db, payload.game_id, current)
    if not game.active:
        raise HTTPException(status_code=400, detail="Game already finished")
    if not (game.revealed or []):
        raise HTTPException(status_code=400, detail="Reveal at least one tile first")

    payout = float(game.bet) * game.multiplier
    game.active = False
    game.won = True
    game.payout = payout
    await apply_transaction(db, current, payout, TransactionType.WIN, game="mines")
    await db.commit()
    await db.refresh(game)
    return _to_state(game, reveal_secret=True)


@router.get("/active", response_model=MinesState | None)
async def active_game(
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import desc, select

    result = await db.execute(
        select(MinesGame)
        .where(MinesGame.user_id == current.id, MinesGame.active.is_(True))
        .order_by(desc(MinesGame.id))
        .limit(1)
    )
    game = result.scalar_one_or_none()
    return _to_state(game) if game else None
