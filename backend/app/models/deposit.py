from sqlalchemy import Float, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Payment(Base, TimestampMixin):
    """Off-chain payments (Telegram Stars, Crypto Bot). Credited exactly once
    via the unique (provider, external_id)."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)  # stars | cryptobot
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    stars: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    asset: Mapped[str | None] = mapped_column(String(16), nullable=True)

    __table_args__ = (
        UniqueConstraint("provider", "external_id", name="uq_payment_provider_ext"),
    )


class TonDeposit(Base, TimestampMixin):
    __tablename__ = "ton_deposits"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stable on-chain identifier so a deposit is credited exactly once.
    event_id: Mapped[str] = mapped_column(
        String(160), unique=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ton_amount: Mapped[float] = mapped_column(Float, nullable=False)
    stars: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)  # stars per GRAM at credit time
    sender: Mapped[str | None] = mapped_column(String(80), nullable=True)
