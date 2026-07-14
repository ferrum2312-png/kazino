from pydantic import BaseModel, Field


# ---- Crash ----
class CrashBetRequest(BaseModel):
    amount: float = Field(gt=0)
    auto_cashout: float | None = Field(default=None, gt=1.0)


class CrashHistoryItem(BaseModel):
    id: int
    crash_point: float
    server_seed_hash: str


# ---- Mines ----
class MinesStartRequest(BaseModel):
    bet: float = Field(gt=0)
    mines: int = Field(default=3, ge=1, le=24)


class MinesRevealRequest(BaseModel):
    game_id: int
    tile: int = Field(ge=0, le=24)


class MinesActionRequest(BaseModel):
    game_id: int


class MinesState(BaseModel):
    game_id: int
    bet: float
    mines: int
    grid_size: int
    revealed: list[int]
    multiplier: float
    next_multiplier: float | None
    payout: float
    active: bool
    won: bool | None
    server_seed_hash: str
    # only present after the game ends
    mine_positions: list[int] | None = None
    server_seed: str | None = None
