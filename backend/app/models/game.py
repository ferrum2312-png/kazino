import enum

from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class RoundStatus(str, enum.Enum):
    BETTING = "betting"
    RUNNING = "running"
    CRASHED = "crashed"


class CrashRound(Base, TimestampMixin):
    __tablename__ = "crash_rounds"

    id: Mapped[int] = mapped_column(primary_key=True)
    nonce: Mapped[int] = mapped_column(Integer, nullable=False)
    server_seed: Mapped[str] = mapped_column(String(64), nullable=False)
    server_seed_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    client_seed: Mapped[str] = mapped_column(String(64), nullable=False)
    crash_point: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[RoundStatus] = mapped_column(
        Enum(RoundStatus, name="round_status"), default=RoundStatus.BETTING
    )


class CrashBet(Base, TimestampMixin):
    __tablename__ = "crash_bets"

    id: Mapped[int] = mapped_column(primary_key=True)
    round_id: Mapped[int] = mapped_column(
        ForeignKey("crash_rounds.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    auto_cashout: Mapped[float | None] = mapped_column(Float, nullable=True)
    cashout_multiplier: Mapped[float | None] = mapped_column(Float, nullable=True)
    payout: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    won: Mapped[bool] = mapped_column(Boolean, default=False)


class MinesGame(Base, TimestampMixin):
    __tablename__ = "mines_games"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    bet: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    grid_size: Mapped[int] = mapped_column(Integer, default=25)
    mines: Mapped[int] = mapped_column(Integer, default=3)
    mine_positions: Mapped[list] = mapped_column(JSON, nullable=False)
    revealed: Mapped[list] = mapped_column(JSON, default=list)
    server_seed: Mapped[str] = mapped_column(String(64), nullable=False)
    server_seed_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    client_seed: Mapped[str] = mapped_column(String(64), nullable=False)
    nonce: Mapped[int] = mapped_column(Integer, nullable=False)
    multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    payout: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    won: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
